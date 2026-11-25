import json
import time
import httpx

from pathlib import Path

API_URL = "http://127.0.0.1:8000/tickets/analyse"

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "test_tickets.json"
RESULTS_PATH = BASE_DIR / "results.json"


def load_tickets():
    with open(DATASET_PATH, "r", encoding="utf-8") as file:
        return json.load(file)

    
def evaluate_ticket(client, ticket):
    start_time = time.perf_counter()

    response = client.post(
        API_URL,
        json={"description": ticket["description"]}
    )

    response.raise_for_status()

    prediction = response.json()["classification"]

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

    return {
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
        "response_time": round(elapsed_time, 2)
    }


def run_evaluation():
    tickets = load_tickets()

    results = []
    failures = []

    print(f"Starting evaluation of {len(tickets)} tickets...\n")

    with httpx.Client(timeout=60.0) as client:
        for ticket in tickets:
            try:
                result = evaluate_ticket(client, ticket)
                results.append(result)

                status = (
                    "PASS" if result["all_correct"] else "FAIL"
                )

                print(
                    f"Ticket {ticket['id']}: {status} "
                    f"({result['response_time']}s)"
                )

            except (httpx.HTTPError, ValueError, KeyError) as e:
                failures.append({
                    "id": ticket["id"],
                    "error": str(e)
                })

                print(f"Ticket {ticket['id']}: ERROR - {e}")

            time.sleep(3)

    return tickets, results, failures


def calculate_metrics(tickets, results, failures):
    total = len(tickets)
    successful = len(results)

    category_correct = sum(
        result["category_correct"] for result in results
    )

    priority_correct = sum(
        result["priority_correct"] for result in results
    )

    team_correct = sum(
        result["team_correct"] for result in results
    )

    all_correct = sum(
        result["all_correct"] for result in results
    )

    def percentage(correct, count):
        return round(correct / count * 100, 2) if count else None

    average_response_time = (
        sum(r["response_time"] for r in results) / successful
        if successful else None
    )

    return {
        "total_tickets": total,
        "successful_requests": successful,
        "failed_requests": len(failures),

        "request_success_rate": percentage(successful, total),

        "category_accuracy": percentage(
            category_correct, successful
        ),

        "priority_accuracy": percentage(
            priority_correct, successful
        ),

        "team_accuracy": percentage(
            team_correct, successful
        ),

        "exact_match_accuracy": percentage(
            all_correct, successful
        ),

        "end_to_end_accuracy": percentage(
            all_correct, total
        ),

        "average_response_time": (
            round(average_response_time, 2)
            if average_response_time is not None else None
        )
    }


def main():
    tickets, results, failures = run_evaluation()

    metrics = calculate_metrics(
        tickets, results, failures
    )

    report = {
        "metrics": metrics,
        "results": results,
        "failures": failures
    }

    with open(RESULTS_PATH, "w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print("\n--- EVALUATION RESULTS ---\n")

    for name, value in metrics.items():
        print(f"{name}: {value}")

    print(f"\nResults saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
