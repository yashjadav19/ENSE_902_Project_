import anthropic
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

MEMORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "memory", "store.json")


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_employee_history(employee_id):
    memory = load_memory()
    return memory.get(employee_id, [])


def append_to_history(employee_id, insight):
    memory = load_memory()
    if employee_id not in memory:
        memory[employee_id] = []
    memory[employee_id].append({
        "timestamp": datetime.now().isoformat(),
        "insight": insight
    })
    memory[employee_id] = memory[employee_id][-10:]
    save_memory(memory)


def run_employee_agent(employee):
    skill_gaps = [s for s in employee["skillsRequired"] if s not in employee["skills"]]
    days_since_training = (datetime.now() - datetime.strptime(employee["lastTrainingDate"], "%Y-%m-%d")).days
    history = get_employee_history(employee["id"])

    if history:
        history_context = f"PREVIOUS AGENT OBSERVATIONS ({len(history)} records):\n"
        for h in history:
            history_context += f"- {h['timestamp'][:10]}: burnout={h['insight']['burnoutRisk']}, status={h['insight']['overallStatus']}, trend={h['insight'].get('trend', 'unknown')}\n"
    else:
        history_context = "No previous observations — this is the first analysis for this employee."

    prompt = f"""
You are an intelligent HR assistant agent assigned to monitor one specific employee.
Your job is to analyze their data and produce a structured HR insight report.
Use both current data AND historical observations to detect trends over time.

{history_context}

CURRENT EMPLOYEE DATA:
Name: {employee['name']}
Role: {employee['role']}
Department: {employee['department']}
Years at Company: {employee['yearsAtCompany']}

WORKLOAD DATA:
- Hours worked this week: {employee['hoursWorkedThisWeek']}
- Hours worked last week: {employee['hoursWorkedLastWeek']}
- Hours worked two weeks ago: {employee['hoursWorkedTwoWeeksAgo']}
- Consecutive overtime weeks: {employee['overtimeWeeksInARow']}

SKILLS DATA:
- Current skills: {', '.join(employee['skills'])}
- Required skills for role: {', '.join(employee['skillsRequired'])}
- Identified skill gaps: {', '.join(skill_gaps) if skill_gaps else 'None'}
- Days since last training: {days_since_training}

LEAVE AND PERFORMANCE:
- Leave taken this year: {employee['leavesTakenThisYear']} out of {employee['leaveEntitlement']} days
- Performance rating: {employee['performanceRating']} out of 5.0
- Last performance review: {employee['lastPerformanceReview']}

IMPORTANT REASONING RULES:
- Burnout risk is HIGH if: overtime weeks >= 3 AND hours > 55, OR leave taken < 3 AND overtime >= 2
- Burnout risk is MEDIUM if: overtime weeks >= 2 OR hours consistently 48-55
- Skill gap is HIGH if: 3+ skills missing AND days since training > 365
- If previous observations show escalating burnout, increase urgency
- Trend is "deteriorating" if burnout or skill gap is worse than previous observations
- Trend is "improving" if situation is better than previous observations
- Trend is "stable" if no significant change
- Trend is "insufficient_data" if no history exists

Return ONLY this exact JSON structure with no extra text:
{{
  "employeeId": "{employee['id']}",
  "employeeName": "{employee['name']}",
  "role": "{employee['role']}",
  "department": "{employee['department']}",
  "burnoutRisk": "low | medium | high",
  "burnoutReason": "one detailed sentence explaining the burnout assessment",
  "skillGapSeverity": "none | low | medium | high",
  "skillGapDetails": "specific gaps identified and their business impact",
  "trainingRecommendation": "specific course, certification, or skill to pursue",
  "managerAlert": "one specific concrete action the manager should take this week",
  "trend": "improving | stable | deteriorating | insufficient_data",
  "overallStatus": "healthy | monitor | urgent",
  "confidenceScore": 0.0
}}

Set confidenceScore between 0.7 and 1.0 based on how complete the data is.
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    insight = json.loads(response.content[0].text)
    append_to_history(employee["id"], insight)
    return insight
