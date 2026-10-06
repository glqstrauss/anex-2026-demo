"""Print a Markdown summary of the last dbt run, for the GitHub Actions job summary."""

import json
from collections import Counter
from pathlib import Path

TARGET = Path("target")

run_results = json.loads((TARGET / "run_results.json").read_text())
manifest = json.loads((TARGET / "manifest.json").read_text())

results = run_results["results"]
total_models = sum(1 for node in manifest["nodes"].values() if node["resource_type"] == "model")
selected_models = sum(1 for r in results if r["unique_id"].startswith("model."))
statuses = Counter(r["status"] for r in results)

print("## dbt CI")
print()
print(f"Selected **{selected_models} of {total_models}** models; everything else deferred to prod.")
print()
print("| Status | Count |")
print("| --- | --- |")
for status, count in sorted(statuses.items()):
    print(f"| {status} | {count} |")


def short_message(message: str | None) -> str:
    """Pick the most useful line, e.g. the database error rather than dbt's 'Runtime Error in model ...' header."""
    lines = [line.strip() for line in (message or "").splitlines() if line.strip()]
    for line in lines[1:]:
        if "Error" in line:
            return line
    return lines[0] if lines else ""


failures = [r for r in results if r["status"] in ("error", "fail")]
if failures:
    print()
    print("### Failures")
    for r in failures:
        print(f"- `{r['unique_id']}`: {short_message(r.get('message'))}")
