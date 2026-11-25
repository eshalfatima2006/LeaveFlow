"""RCA experiment: OBSERVES outcomes (prints RCA lines, asserts nothing about the rule)."""
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
import json
import os
from threading import Barrier, BrokenBarrierError
from unittest import mock

from django.conf import settings
from django.db import connections
from django.test import TransactionTestCase
from leave.models import LeaveRequest
from leave.serializers import LeaveRequestSerializer
from tests.team.api.support import REQUESTS_URL, balance_view, decision_url, payload, row_state, token_client
from tests.team.fixtures.leave_data import build_people, make_request
from tests.team.postgres_safety import PROFILE

GATE = 2
TRIALS = 50


def load_tests(loader, tests, pattern):
    return tests if getattr(settings, "TEAM_TEST_PROFILE", None) == PROFILE else loader.suiteClass()


def say(**kw):
    print("RCA " + json.dumps({"variant": os.environ["RCA_VARIANT"], **kw}), flush=True)


def client_for(user):
    # Django's test client collects exceptions through a process-wide signal, so with
    # raise_request_exception=True one thread re-raises the other thread's error.
    c = token_client(user)
    c.raise_request_exception = False
    return c


def outcome(call):
    try:
        r = call()
        if r.status_code != 500:
            return f"{r.status_code}"
        exc = r.exc_info[1]
        return f"500 {type(exc).__name__} sqlstate={getattr(exc.__cause__, 'sqlstate', None)}"
    finally:
        connections.close_all()


def together(*calls):
    start = Barrier(len(calls))

    def go(call):
        start.wait(10)
        return outcome(call)
    with ThreadPoolExecutor(len(calls)) as pool:
        return sorted(f.result(timeout=30) for f in [pool.submit(go, c) for c in calls])


class Gate:
    """Holds each call until both arrive; gives up after GATE s, so a fix that serializes them is not failed by the test."""
    def __init__(self, target, name):
        self.b, self.target, self.name, self.real = Barrier(2), target, name, getattr(target, name)

    def __enter__(self):
        gate = self

        def wrapper(obj, *a, **k):
            try:
                gate.b.wait(GATE)
            except BrokenBarrierError:
                pass
            return gate.real(obj, *a, **k)
        self.p = mock.patch.object(self.target, self.name, wrapper)
        self.p.start()

    def __exit__(self, *a):
        self.p.stop()


class Rca(TransactionTestCase):
    def setUp(self):
        self.p = build_people("rca", allowances={"e2": 5})

    def submit(self, start, end):
        c = client_for(self.p.e1)
        return lambda: c.post(REQUESTS_URL, payload(str(start), str(end)), format="json")

    def decide(self, actor, pk, value="approved"):
        c = client_for(actor)
        return lambda: c.post(decision_url(pk), {"status": value}, format="json")

    def test_w1(self):
        with Gate(LeaveRequestSerializer, "create"):
            res = together(self.submit("2026-12-07", "2026-12-09"), self.submit("2026-12-08", "2026-12-10"))
        say(case="W1 overlapping, gated between check and insert", responses=res, rows=LeaveRequest.objects.count())
        LeaveRequest.objects.all().delete()
        tally, monday = Counter(), date(2027, 1, 4)
        for i in range(TRIALS):
            d = monday + timedelta(days=7 * i)
            tally["+".join(together(self.submit(d, d + timedelta(1)), self.submit(d, d + timedelta(1))))] += 1
        say(case=f"W1 identical, {TRIALS} pairs, natural timing", outcomes=dict(tally))
        LeaveRequest.objects.all().delete()
        say(case="W1 sequential: first, overlapping, adjacent", responses=[
            outcome(self.submit("2026-12-07", "2026-12-09")), outcome(self.submit("2026-12-09", "2026-12-10")),
            outcome(self.submit("2026-12-10", "2026-12-11"))])

    def pair(self):
        return [make_request(self.p.e2, start=date(2026, 12, d), end=date(2026, 12, d + 3)) for d in (7, 14)]

    def test_w2(self):
        a, b = self.pair()
        before = row_state(b.pk)
        res = [outcome(self.decide(self.p.m1, a.pk)), outcome(self.decide(self.p.m1, b.pk))]
        say(case="W2 sequential 4+4 days, allowance 5", responses=res, balance=balance_view(self.p.e2),
            second_row_unchanged=row_state(b.pk) == before)
        say(case="W2 reject the over-allowance request", responses=[outcome(self.decide(self.p.m1, b.pk, "rejected"))],
            balance=balance_view(self.p.e2))
        LeaveRequest.objects.all().delete()
        one = make_request(self.p.e2, start=date(2026, 12, 7), end=date(2026, 12, 11))
        say(case="W2 equality: 5 days, allowance 5", responses=[outcome(self.decide(self.p.m1, one.pk))],
            balance=balance_view(self.p.e2))
        LeaveRequest.objects.all().delete()
        a, b = self.pair()
        with Gate(LeaveRequest, "save"):
            res = together(self.decide(self.p.m1, a.pk), self.decide(self.p.admin, b.pk))
        say(case="W2 concurrent 4+4 days, gated before save", responses=res, balance=balance_view(self.p.e2))