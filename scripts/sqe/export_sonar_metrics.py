"""Capture measured SonarQube values and their analysis revision, without secrets."""

import base64
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

METRICS = {
    "complexity": "Cyclomatic complexity summed over the analyzed source; not one function's value.",
    "cognitive_complexity": "Estimated difficulty of understanding control flow.",
    "duplicated_lines_density": "Percentage of analyzed lines in duplicated blocks.",
    "code_smells": "Maintainability findings under the configured quality profile.",
    "bugs": "Reliability findings; zero does not prove functional correctness.",
    "vulnerabilities": "Security findings that need individual review and disposition.",
    "coverage": "Imported overall coverage, including source outside the three-file critical denominator.",
    "sqale_index": "Estimated maintainability remediation effort in minutes.",
    "sqale_rating": "Maintainability rating: 1=A through 5=E.",
    "reliability_rating": "Reliability rating: 1=A through 5=E.",
    "security_rating": "Security rating: 1=A through 5=E.",
}


def main():
    host = os.environ["SONAR_HOST_URL"].rstrip("/")
    token = os.environ.get("SONAR_TOKEN")
    credentials = (token + ":") if token else (os.environ["SONAR_USER"] + ":" + os.environ["SONAR_PASSWORD"])
    auth = "Basic " + base64.b64encode(credentials.encode()).decode()

    def get(endpoint, **params):
        request = Request(host + "/api/" + endpoint + "?" + urlencode(params), headers={"Authorization": auth})
        with urlopen(request, timeout=30) as response:
            return json.load(response)

    project = os.environ.get("SONAR_PROJECT_KEY", "leaveflow")
    report = {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "analysis": get("project_analyses/search", project=project, ps=1),
        "metrics": get("measures/component", component=project, metricKeys=",".join(METRICS)),
        "quality_gate": get("qualitygates/project_status", projectKey=project),
        "files": get("measures/component_tree", component=project, metricKeys="complexity,coverage", qualifiers="FIL", ps=500),
        "issues": get("issues/search", componentKeys=project, resolved="false", ps=500),
    }
    output = Path(os.environ.get("SONAR_EVIDENCE_DIR", "docs/sqe/evidence/area1/sonarqube/measured"))
    output.mkdir(parents=True, exist_ok=True)
    (output / "metrics.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    analysis = report["analysis"]["analyses"][0]
    lines = ["# Measured SonarQube results", "", f"Analysis revision: `{analysis.get('revision', 'not supplied')}`.",
             f"Analysis date: {analysis['date']}. Captured: {report['captured_at']}.",
             "", "These are the server's recorded values for that revision, not a claim about a newer local branch.",
             "", "| Metric | Value | Interpretation |", "|---|---:|---|"]
    values = {m["metric"]: m.get("value", "unavailable") for m in report["metrics"]["component"]["measures"]}
    for metric, meaning in METRICS.items():
        lines.append(f"| {metric} | {values.get(metric, 'unavailable')} | {meaning} |")
    lines += ["", f"Quality gate: **{report['quality_gate']['projectStatus']['status']}**.",
              "", "Review the raw issue records in metrics.json. A passing gate can coexist with overall-code findings if its conditions cover only new code."]
    (output / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved SonarQube evidence for {analysis.get('revision')} to {output}")


if __name__ == "__main__":
    main()
