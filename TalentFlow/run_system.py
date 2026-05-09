import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from agents.employee_agent import run_employee_agent
from agents.manager_agent import run_manager_agent


def run_full_system():
    print("=== TalentFlow AI Agent System Starting ===\n")

    data_path = os.path.join(os.path.dirname(__file__), "data", "employees.json")
    with open(data_path, "r") as f:
        employees = json.load(f)

    departments = {}
    for emp in employees:
        dept = emp["department"]
        if dept not in departments:
            departments[dept] = {"employees": [], "manager": emp["manager"]}
        departments[dept]["employees"].append(emp)

    all_employee_insights = []
    all_manager_reports = []

    print("Step 1: Running employee agents...")
    for emp in employees:
        print(f"  Analyzing: {emp['name']}...")
        insight = run_employee_agent(emp)
        all_employee_insights.append(insight)
        print(f"  Result: {insight['overallStatus'].upper()} | Burnout: {insight['burnoutRisk']} | Trend: {insight['trend']}")

    print(f"\nCompleted {len(all_employee_insights)} employee analyses.\n")

    print("Step 2: Running manager agents per department...")
    for dept_name, dept_data in departments.items():
        dept_employee_insights = [
            i for i in all_employee_insights
            if any(e["department"] == dept_name and e["name"] == i["employeeName"] for e in employees)
        ]
        print(f"  Processing department: {dept_name}...")
        manager_report = run_manager_agent(
            dept_employee_insights,
            dept_data["manager"],
            dept_name
        )
        all_manager_reports.append(manager_report)
        print(f"  Team Health Score: {manager_report['teamHealthScore']}/10")

    results = {
        "employeeInsights": all_employee_insights,
        "managerReports": all_manager_reports,
        "summary": {
            "totalEmployees": len(all_employee_insights),
            "urgent": len([e for e in all_employee_insights if e["overallStatus"] == "urgent"]),
            "monitor": len([e for e in all_employee_insights if e["overallStatus"] == "monitor"]),
            "healthy": len([e for e in all_employee_insights if e["overallStatus"] == "healthy"])
        }
    }

    results_path = os.path.join(os.path.dirname(__file__), "results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    print("\n=== System Complete ===")
    print(f"Total: {results['summary']['totalEmployees']} employees analyzed")
    print(f"Urgent: {results['summary']['urgent']} | Monitor: {results['summary']['monitor']} | Healthy: {results['summary']['healthy']}")
    print("Results saved to results.json")

    return results


if __name__ == "__main__":
    run_full_system()
