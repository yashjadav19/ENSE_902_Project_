from flask import Flask, jsonify, request
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from agents.employee_agent import run_employee_agent
from agents.manager_agent import run_manager_agent

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)


def load_employees():
    with open(os.path.join(BASE_DIR, "data", "employees.json"), "r") as f:
        return json.load(f)


def load_results():
    try:
        with open(os.path.join(BASE_DIR, "results.json"), "r") as f:
            return json.load(f)
    except Exception:
        return None


@app.route("/api/employees", methods=["GET"])
def get_employees():
    employees = load_employees()
    return jsonify({"employees": employees, "total": len(employees)})


@app.route("/api/analyze/<employee_id>", methods=["GET"])
def analyze_employee(employee_id):
    employees = load_employees()
    emp = next((e for e in employees if e["id"] == employee_id), None)
    if not emp:
        return jsonify({"error": "Employee not found"}), 404
    insight = run_employee_agent(emp)
    return jsonify(insight)


@app.route("/api/analyze-team", methods=["GET"])
def analyze_team():
    employees = load_employees()
    insights = [run_employee_agent(emp) for emp in employees]
    departments = {}
    for emp in employees:
        dept = emp["department"]
        if dept not in departments:
            departments[dept] = {"employees": [], "manager": emp["manager"]}
        departments[dept]["employees"].append(emp)
    manager_reports = []
    for dept_name, dept_data in departments.items():
        dept_insights = [i for i in insights if any(
            e["department"] == dept_name and e["name"] == i["employeeName"]
            for e in employees
        )]
        report = run_manager_agent(dept_insights, dept_data["manager"], dept_name)
        manager_reports.append(report)
    return jsonify({"employeeInsights": insights, "managerReports": manager_reports})


@app.route("/api/results", methods=["GET"])
def get_results():
    results = load_results()
    if not results:
        return jsonify({"error": "No results yet. Run run_system.py first."}), 404
    return jsonify(results)


@app.route("/api/memory", methods=["GET"])
def get_memory():
    memory_path = os.path.join(BASE_DIR, "memory", "store.json")
    try:
        with open(memory_path, "r") as f:
            memory = json.load(f)
        return jsonify({"memory": memory, "employeeCount": len(memory)})
    except Exception:
        return jsonify({"memory": {}, "employeeCount": 0})


@app.route("/api/memory/clear", methods=["POST"])
def clear_memory():
    memory_path = os.path.join(BASE_DIR, "memory", "store.json")
    with open(memory_path, "w") as f:
        json.dump({}, f)
    return jsonify({"message": "Memory cleared successfully"})


if __name__ == "__main__":
    app.run(debug=True, port=3001)
