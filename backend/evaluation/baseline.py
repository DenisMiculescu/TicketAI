
import json
import time

from evaluate import load_tickets, calculate_metrics, BASE_DIR


BASELINE_RESULTS_PATH = BASE_DIR / "baseline_results.json"


CATEGORY_KEYWORDS = {
    "Security": [
        "ransomware", "phishing", "malware",
        "suspicious email", "password", "virus"
    ],
    "Database": [
        "database", "sql", "query", "queries"
    ],
    "Network": [
        "network", "wi-fi", "wifi", "vpn",
        "internet", "connection"
    ],
    "Hardware": [
        "monitor", "keyboard", "screen",
        "mouse", "physical server", "overheating",
        "printer"
    ],
    "Software": [
        "application", "excel", "software",
        "install", "crashes", "pdf reader"
    ]
}


TEAM_MAPPING = {
    "Network": "Network Support",
    "Hardware": "IT Support",
    "Software": "Application Support",
    "Database": "Database Administration",
    "Security": "Security Operations",
    "Other": "IT Support"
}


def classify_category(description):
    description = description.lower()

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description:
                return category

    return "Other"


def classify_priority(description):
    description = description.lower()

    critical_keywords = [
        "all employees",
        "entire company",
        "ransomware",
        "all company applications",
        "no customer orders",
        "across the organisation"
    ]

    high_keywords = [
        "entire department",
        "department",
        "multiple employees",
        "business operations",
        "major disruption"
    ]

    low_keywords = [
        "would like",
        "request",
        "information",
        "assistance",
        "where can i"
    ]

    if any(word in description for word in critical_keywords):
        return "Critical"

    if any(word in description for word in high_keywords):
        return "High"

    if any(word in description for word in low_keywords):
        return "Low"

    return "Medium"


def classify_ticket(description):
    category = classify_category(description)
    priority = classify_priority(description)
    team = TEAM_MAPPING[category]

    return {
        "category": category,
        "priority": priority,
        "team": team
    }


def run_baseline():
    tickets = load_tickets()
    results = []

    for ticket in tickets:
        start_time = time.perf_counter()

        prediction = classify_ticket(
            ticket["description"]
        )

        elapsed_time = time.perf_counter() - start_time

        category_correct = (
            prediction["category"] == ticket["expected_category"]
        )

        priority_correct = (
            prediction["priority"] == ticket["expected_priority"]
        )

        team_correct = (
            prediction["team"] == ticket["expected_team"]
        )

        result = {
            "id": ticket["id"],
            "description": ticket["description"],
            "expected": {
                "category": ticket["expected_category"],
                "priority": ticket["expected_priority"],
                "team": ticket["expected_team"]
            },
            "prediction": prediction,
            "category_correct": category_correct,
            "priority_correct": priority_correct,
            "team_correct": team_correct,
            "all_correct": (
                category_correct
                and priority_correct
                and team_correct
            ),
            "response_time": round(elapsed_time, 8)
        }

        results.append(result)

        status = "PASS" if result["all_correct"] else "FAIL"

        print(f"Ticket {ticket['id']}: {status}")

    return tickets, results

 
def main():
    tickets, results = run_baseline()

    metrics = calculate_metrics(
        tickets, results, []
    )

    report = {
        "metrics": metrics,
        "results": results,
        "failures": []
    }

    with open(
        BASELINE_RESULTS_PATH, "w", encoding="utf-8"
    ) as file:
        json.dump(report, file, indent=4)

    print("\n--- BASELINE RESULTS ---\n")

    for name, value in metrics.items():
        print(f"{name}: {value}")

    print(f"\nResults saved to: {BASELINE_RESULTS_PATH}")


if __name__ == "__main__":
    main()
