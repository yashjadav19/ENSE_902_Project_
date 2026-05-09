import streamlit as st
import json
import subprocess
import os
import sys

st.set_page_config(
    page_title="TalentFlow AI Agent System",
    page_icon="🤖",
    layout="wide"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_results():
    results_path = os.path.join(BASE_DIR, "results.json")
    if os.path.exists(results_path):
        with open(results_path, "r") as f:
            return json.load(f)
    return None


def load_employees():
    emp_path = os.path.join(BASE_DIR, "data", "employees.json")
    with open(emp_path, "r") as f:
        return json.load(f)


def load_memory():
    mem_path = os.path.join(BASE_DIR, "memory", "store.json")
    if os.path.exists(mem_path):
        with open(mem_path, "r") as f:
            return json.load(f)
    return {}


st.title("🤖 TalentFlow — AI-Powered HR Intelligence System")
st.caption("Multi-Agent LLM System for Proactive HR Analytics | ENSE 902 | University of Regina")

employees = load_employees()

with st.sidebar:
    st.header("System Controls")

    if st.button("▶ Run Full Agent System", type="primary", use_container_width=True):
        with st.spinner("Running AI agents... this takes 60-90 seconds for 15 employees..."):
            script_path = os.path.join(BASE_DIR, "run_system.py")
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                cwd=BASE_DIR
            )
            if result.returncode == 0:
                st.success("Analysis complete!")
            else:
                st.error("An error occurred during analysis.")
                st.code(result.stderr)
        st.rerun()

    st.divider()

    if st.button("🗑 Clear Agent Memory", use_container_width=True):
        mem_path = os.path.join(BASE_DIR, "memory", "store.json")
        with open(mem_path, "w") as f:
            json.dump({}, f)
        st.success("Memory cleared!")
        st.rerun()

    st.divider()
    st.header("About")
    st.write(
        "This system uses Claude AI agents to proactively identify HR risks "
        "that traditional HR software cannot detect."
    )
    st.metric("Total Employees", len(employees))

    memory = load_memory()
    employees_with_history = len(memory)
    st.metric("Employees with History", employees_with_history)

    if employees_with_history > 0:
        total_observations = sum(len(v) for v in memory.values())
        st.metric("Total Observations Stored", total_observations)

    st.divider()
    st.header("System Architecture")
    st.write("**Layer 1:** Employee Agent")
    st.caption("Analyzes individual data + memory history")
    st.write("**Layer 2:** Manager Agent")
    st.caption("Synthesizes team-wide patterns")
    st.write("**Memory:** JSON longitudinal store")
    st.caption("Tracks trend changes across runs")

results = load_results()

if not results:
    st.info("Click **▶ Run Full Agent System** in the sidebar to start the analysis. This will call the Claude AI agents and may take 60-90 seconds.")

    st.divider()
    st.subheader("Employee Roster Preview")
    st.caption("These are the 15 synthetic employees that will be analyzed")

    dept_groups = {}
    for emp in employees:
        dept = emp["department"]
        if dept not in dept_groups:
            dept_groups[dept] = []
        dept_groups[dept].append(emp)

    for dept, emps in dept_groups.items():
        st.write(f"**{dept} Department** (Manager: {emps[0]['manager']})")
        for emp in emps:
            skill_gaps = [s for s in emp["skillsRequired"] if s not in emp["skills"]]
            col1, col2, col3, col4 = st.columns([2, 1, 1, 2])
            col1.write(f"• {emp['name']} — {emp['role']}")
            col2.write(f"{emp['hoursWorkedThisWeek']} hrs/wk")
            col3.write(f"{emp['overtimeWeeksInARow']} OT weeks")
            col4.write(f"{len(skill_gaps)} skill gap(s)" if skill_gaps else "No skill gaps")
        st.divider()
    st.stop()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Employees", results["summary"]["totalEmployees"])
col2.metric("🔴 Urgent", results["summary"]["urgent"])
col3.metric("🟡 Monitor", results["summary"]["monitor"])
col4.metric("🟢 Healthy", results["summary"]["healthy"])

st.divider()

tab1, tab2, tab3 = st.tabs(["👤 Employee Agent Reports", "👔 Manager Agent Reports", "🧠 Agent Memory"])

with tab1:
    st.subheader("Individual Employee Agent Analysis")

    status_filter = st.selectbox("Filter by status", ["All", "urgent", "monitor", "healthy"])

    filtered = [
        i for i in results["employeeInsights"]
        if status_filter == "All" or i["overallStatus"] == status_filter
    ]
    st.caption(f"Showing {len(filtered)} of {len(results['employeeInsights'])} employees")

    for insight in filtered:
        status = insight["overallStatus"]

        if status == "urgent":
            icon = "🔴"
            label = "URGENT"
            expanded = True
        elif status == "monitor":
            icon = "🟡"
            label = "MONITOR"
            expanded = False
        else:
            icon = "🟢"
            label = "HEALTHY"
            expanded = False

        with st.expander(f"{icon} {insight['employeeName']} — {insight['role']} ({insight['department']}) — {label}", expanded=expanded):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Burnout Risk", insight["burnoutRisk"].upper())
            col2.metric("Skill Gap", insight["skillGapSeverity"].upper())
            col3.metric("Trend", insight["trend"])
            col4.metric("Confidence", f"{insight['confidenceScore']:.0%}")

            if status == "urgent":
                st.error(f"**Manager Alert:** {insight['managerAlert']}")
            elif status == "monitor":
                st.warning(f"**Manager Alert:** {insight['managerAlert']}")
            else:
                st.success(f"**Status:** {insight['managerAlert']}")

            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"**Burnout Reason:** {insight['burnoutReason']}")
                st.write(f"**Skill Gap Details:** {insight['skillGapDetails']}")
            with col_b:
                st.info(f"**Training Recommendation:** {insight['trainingRecommendation']}")

with tab2:
    st.subheader("Manager Agent — Department Reports")

    for report in results["managerReports"]:
        health = report["teamHealthScore"]
        if health >= 7:
            health_color = "🟢"
        elif health >= 4:
            health_color = "🟡"
        else:
            health_color = "🔴"

        st.subheader(f"📊 {report['departmentName']} Department — Manager: {report['managerName']}")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Team Health Score", f"{health_color} {report['teamHealthScore']}/10")
        col2.metric("🔴 Urgent", report["urgentCount"])
        col3.metric("🟡 Monitor", report["monitorCount"])
        col4.metric("🟢 Healthy", report["healthyCount"])

        st.error(f"**Critical Issue:** {report['criticalIssue']}")

        if report["teamPattern"] and report["teamPattern"].lower() != "no pattern detected":
            st.warning(f"**Team Pattern Detected:** {report['teamPattern']}")
        else:
            st.info("**Team Pattern:** No systemic pattern detected")

        col_left, col_right = st.columns(2)
        with col_left:
            st.write(f"**Priority Employee:** {report['priorityEmployee']}")
            st.write(f"**Why Priority:** {report['priorityReason']}")
        with col_right:
            st.write("**Top 3 Actions for Manager This Week:**")
            for i, action in enumerate(report["topThreeActions"], 1):
                st.write(f"{i}. {action}")

        st.info(f"**Strategic Recommendation:** {report['strategicRecommendation']}")
        st.caption(f"Confidence Score: {report['confidenceScore']:.0%}")
        st.divider()

with tab3:
    st.subheader("Agent Memory — Longitudinal Observation Store")
    st.write("The memory system stores up to 10 observations per employee across runs. This enables trend detection over time — a capability that rule-based HR tools fundamentally cannot provide.")

    memory = load_memory()

    if not memory:
        st.info("No memory stored yet. Run the agent system at least twice to see trend data accumulate.")
    else:
        st.metric("Employees with stored history", len(memory))

        emp_lookup = {emp["id"]: emp for emp in employees}

        for emp_id, history in memory.items():
            emp_name = emp_lookup.get(emp_id, {}).get("name", emp_id)
            emp_role = emp_lookup.get(emp_id, {}).get("role", "")

            with st.expander(f"🧠 {emp_name} — {emp_role} ({len(history)} observations)"):
                for i, record in enumerate(reversed(history)):
                    timestamp = record["timestamp"][:16].replace("T", " ")
                    ins = record["insight"]
                    trend_icon = {"improving": "📈", "deteriorating": "📉", "stable": "➡️", "insufficient_data": "❓"}.get(ins.get("trend", ""), "")
                    status_icon = {"urgent": "🔴", "monitor": "🟡", "healthy": "🟢"}.get(ins.get("overallStatus", ""), "")
                    st.write(
                        f"**Run {len(history) - i}** ({timestamp}) — "
                        f"{status_icon} {ins.get('overallStatus', 'N/A').upper()} | "
                        f"Burnout: {ins.get('burnoutRisk', 'N/A')} | "
                        f"Skill Gap: {ins.get('skillGapSeverity', 'N/A')} | "
                        f"Trend: {trend_icon} {ins.get('trend', 'N/A')}"
                    )
                if len(history) >= 2:
                    latest = history[-1]["insight"]
                    prev = history[-2]["insight"]
                    if latest.get("overallStatus") != prev.get("overallStatus"):
                        st.caption(f"Status changed: {prev.get('overallStatus')} → {latest.get('overallStatus')}")
