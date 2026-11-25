import { check, sleep } from 'k6'
import http from 'k6/http'
import { Counter, Rate, Trend } from 'k6/metrics'

const base = __ENV.SQE_K6_URL
if (!/^http:\/\/127\.0\.0\.1:\d+$/.test(base ?? '')) {
  throw new Error('Use the SQE runner and its disposable loopback backend.')
}
const vus = Number(__ENV.SQE_K6_VUS)
if (![1, 5].includes(vus)) throw new Error('Expected a workload of 1 or 5 VUs.')

const completed = new Counter('list_completed')
const latency = new Trend('list_latency', true)
const unexpected = new Rate('list_unexpected')

export const options = {
  scenarios: { list: { executor: 'constant-vus', vus, duration: '70s', gracefulStop: '5s' } },
  thresholds: { list_latency: ['p(95)<=500'], list_unexpected: ['rate<0.01'] },
  summaryTrendStats: ['avg', 'med', 'max', 'p(95)'],
}

export function setup() {
  const response = http.post(`${base}/api/auth/login/`, JSON.stringify({
    username: __ENV.SQE_K6_USER, password: __ENV.SQE_K6_PASSWORD,
  }), { headers: { 'Content-Type': 'application/json' } })
  if (response.status !== 200) throw new Error('Disposable fixture login failed.')
  return { headers: { Authorization: `Token ${response.json('token')}` } }
}

export default function (params) {
  const response = http.get(`${base}/api/requests/`, params)
  let rows
  if (response.status === 200) {
    try {
      rows = response.json()
    } catch {
      rows = null
    }
  }
  const success = check(response, {
    '200 with 20 team records': r => r.status === 200 && Array.isArray(rows) && rows.length === 20,
  })
  completed.add(1)
  latency.add(response.timings.duration)
  unexpected.add(!success)
  sleep(0.2)
}
