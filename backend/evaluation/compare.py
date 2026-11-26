
import json

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def load_metrics(filename):
    with open(BASE_DIR / filename, "r", encoding="utf-8") as file:
        return json.load(file)["metrics"]


ai = load_metrics("results.json")
baseline = load_metrics("baseline_results.json")

metrics = [
    "category_accuracy",
    "priority_accuracy",
    "team_accuracy",
    "exact_match_accuracy",
    "end_to_end_accuracy",
    "request_success_rate",
    "average_response_time"
]

print("\n--- AI VS RULE-BASED BASELINE ---\n")

print(f"{'Metric':<28}{'AI':>12}{'Baseline':>12}")
print("-" * 52)

for metric in metrics:
    ai_value = str(ai[metric])
    baseline_value = str(baseline[metric])

    print(
        f"{metric:<28}"
        f"{ai_value:>12}"
        f"{baseline_value:>12}"
    )
