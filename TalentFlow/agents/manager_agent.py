import anthropic
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    default_headers={"anthropic-org-id": "62f690b4-8f1a-4900-97ba-9eb8795c2d5a"}
)


def run_manager_agent(employee_insights, manager_name, department_name):
    urgent = [e for e in employee_insights if e["overallStatus"] == "urgent"]
    monitor = [e for e in employee_insights if e["overallStatus"] == "monitor"]
    healthy = [e for e in employee_insights if e["overallStatus"] == "healthy"]

    employee_summaries = "\n".join([
        f"- {e['employeeName']} ({e['role']}): status={e['overallStatus']}, burnout={e['burnoutRisk']}, skillGap={e['skillGapSeverity']}, trend={e['trend']}, alert='{e['managerAlert']}'"
        for e in employee_insights
    ])

    prompt = f"""
You are a senior HR intelligence agent responsible for synthesizing
individual employee agent reports and advising a department manager.
Your job is to identify team-wide patterns, prioritize actions, and
surface insights that no single employee report can reveal alone.

MANAGER: {manager_name}
DEPARTMENT: {department_name}
TEAM SIZE: {len(employee_insights)} employees

INDIVIDUAL EMPLOYEE AGENT REPORTS:
{employee_summaries}

TEAM STATISTICS:
- Urgent cases: {len(urgent)} employees
- Needs monitoring: {len(monitor)} employees
- Healthy: {len(healthy)} employees
- Urgent employee names: {', '.join([e['employeeName'] for e in urgent]) if urgent else 'None'}

YOUR ANALYSIS TASKS:
1. Identify the single most critical issue requiring immediate action
2. Detect any team-wide patterns (e.g., widespread burnout suggests workload problem, not individual issue)
3. Prioritize which employee needs manager attention first and why
4. Calculate a team health score from 1-10
5. Give one strategic recommendation for long-term team health

IMPORTANT: A pattern exists if 3+ employees share the same risk type.
If majority of team is in overtime, this is a systemic workload problem, not individual.

Return ONLY this exact JSON structure with no extra text:
{{
  "managerName": "{manager_name}",
  "departmentName": "{department_name}",
  "teamSize": {len(employee_insights)},
  "urgentCount": {len(urgent)},
  "monitorCount": {len(monitor)},
  "healthyCount": {len(healthy)},
  "teamHealthScore": 0,
  "criticalIssue": "the single most urgent issue requiring immediate action",
  "teamPattern": "specific pattern detected across employees, or No pattern detected",
  "priorityEmployee": "name of employee who needs attention most urgently",
  "priorityReason": "specific reason why this person needs attention first",
  "topThreeActions": [
    "specific action 1 for manager to take this week",
    "specific action 2 for manager to take this week",
    "specific action 3 for manager to take this week"
  ],
  "strategicRecommendation": "one longer-term recommendation for overall team health",
  "confidenceScore": 0.0
}}

Set teamHealthScore as integer 1-10.
Set confidenceScore between 0.7 and 1.0.
"""

    response = client.messages.create(
        model="claude-opus-4-1-20250805",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.content[0].text)
