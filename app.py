"""Personal Budget Assistant — Streamlit Web Application.

A modern, interactive web UI demonstrating:
- Live PLAN -> ACT -> OBSERVE -> DECIDE loop trace visualization
- Persistent structured session memory
- Real-time spending metrics & category breakdown
- Quick-click sample goals for easy grading and demonstrations
"""

import os
import sys
import json
import pandas as pd
import streamlit as st

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.memory import AgentMemory
from src.agent import PersonalBudgetAgent
from src.config import get_api_credentials, get_llm_client

# =============================================================================
# 1. PAGE CONFIGURATION & STYLING
# =============================================================================
st.set_page_config(
    page_title="Personal Budget Assistant — Agentic AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for modern, clean card aesthetics and trace badges
st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748b;
        margin-bottom: 1.5rem;
    }
    /* Step trace cards */
    .trace-card {
        background-color: #f8fafc;
        border-left: 4px solid #2563eb;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 10px;
        font-size: 0.92rem;
    }
    .badge-plan {
        background-color: #dbeafe;
        color: #1e40af;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.78rem;
    }
    .badge-tool {
        background-color: #fef3c7;
        color: #92400e;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.78rem;
    }
    .badge-obs {
        background-color: #dcfce7;
        color: #166534;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.78rem;
    }
    .badge-dec {
        background-color: #f3e8ff;
        color: #6b21a8;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.78rem;
    }
    .badge-mem {
        background-color: #ffe4e6;
        color: #9f1239;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
        font-size: 0.78rem;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# 2. SESSION STATE INITIALIZATION
# =============================================================================
if "memory" not in st.session_state:
    st.session_state.memory = AgentMemory()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # List of {"role": str, "content": str, "steps": list}

if "api_key" not in st.session_state:
    default_key, _, _ = get_api_credentials()
    st.session_state.api_key = default_key or ""


# =============================================================================
# 3. SIDEBAR: LIVE DASHBOARD & CONTROLS
# =============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/budget.png", width=64)
    st.title("Budget Dashboard")
    st.caption("Live session data & controls")

    # Metrics Summary
    summary = st.session_state.memory.get_structured_summary()
    total_spent = summary["total_overall"]
    total_records = summary["total_records"]
    categories = summary["categories"]

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Total Spent", value=f"₹{total_spent:.2f}")
    with col2:
        st.metric(label="Entries Logged", value=total_records)

    st.markdown("---")

    # Category Breakdown Table
    st.subheader("📊 Category Spending")
    if categories:
        df_cat = pd.DataFrame(
            [{"Category": k.title(), "Total (₹)": f"₹{v:.2f}", "Raw": v} for k, v in categories.items()]
        )
        st.dataframe(df_cat[["Category", "Total (₹)"]], use_container_width=True, hide_index=True)
    else:
        st.info("No expenses recorded yet. Start chatting to add expenses!")

    # Recent Entries List
    if summary["expenses"]:
        with st.expander("📋 View All Recorded Expenses", expanded=False):
            df_exp = pd.DataFrame(summary["expenses"])
            df_exp["item"] = df_exp["item"].str.title()
            df_exp["amount"] = df_exp["amount"].apply(lambda x: f"₹{x:.2f}")
            df_exp = df_exp.rename(columns={"item": "Item", "amount": "Amount", "timestamp": "Logged At"})
            st.dataframe(df_exp, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Quick Prompt Shortcuts (for fast grading / testing)
    st.subheader("⚡ Quick Test Prompts")
    quick_prompts = [
        ("🍟 Add Food Expense", "I spent ₹500 on food."),
        ("🍔 Add Another Expense", "I spent another ₹300 on food."),
        ("❓ Query Food Total", "How much have I spent on food?"),
        ("🚗 Add Travel Expense", "I spent ₹1000 on travel."),
        ("✈️ Multi-step Affordability Goal", "I have ₹5000. I spent ₹1000 on food and ₹500 on travel. Can I afford a ₹2000 trip?"),
        ("⚠️ Test Negative Expense", "I spent -₹500 on food."),
    ]

    selected_prompt = None
    for label, prompt_text in quick_prompts:
        if st.button(label, use_container_width=True):
            selected_prompt = prompt_text

    st.markdown("---")

    # Settings & Reset Memory
    st.subheader("⚙️ Settings & API")
    custom_key = st.text_input("Groq / GitHub / OpenAI API Key:", value=st.session_state.api_key, type="password", help="Enter your Groq (gsk_...), GitHub Token, or OpenAI key. Leave blank to use the built-in deterministic offline engine.")
    if custom_key != st.session_state.api_key:
        st.session_state.api_key = custom_key
        if custom_key:
            if custom_key.startswith("gsk_"):
                os.environ["GROQ_API_KEY"] = custom_key
            else:
                os.environ["GITHUB_TOKEN"] = custom_key
        st.rerun()

    if st.session_state.api_key:
        if st.session_state.api_key.startswith("gsk_"):
            st.caption("🟢 **Groq LLM Active** (llama-3.3-70b)")
        elif st.session_state.api_key.startswith("ghp_") or st.session_state.api_key.startswith("github_"):
            st.caption("🟢 **GitHub Models Active** (gpt-4o-mini)")
        else:
            st.caption("🟢 **Live LLM Active**")
    else:
        st.caption("⚪ **Offline Deterministic Engine Active**")

    if st.button("🧹 Clear Session Memory", use_container_width=True, type="secondary"):
        st.session_state.memory.clear()
        st.session_state.chat_history.clear()
        st.success("Session memory cleared successfully!")
        st.rerun()


# =============================================================================
# 4. MAIN CHAT & TRACE INTERFACE
# =============================================================================
st.markdown('<div class="main-header">💰 Personal Budget Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">An Agentic AI assistant with an explicit <b>PLAN → ACT → OBSERVE → DECIDE</b> loop, real Python tools, and persistent memory.</div>', unsafe_allow_html=True)

# Information banner on agent tools & memory
with st.expander("ℹ️ How This Agent Works (Architecture & Rubric)", expanded=False):
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("**🛠️ Real Python Tools**\n- `add_expense(item, amount)`\n- `get_summary(category)`")
    with col_b:
        st.markdown("**🧠 Structured Memory**\n- Stores typed expense records\n- Persists context across turns")
    with col_c:
        st.markdown("**🔄 Agentic Loop**\n- Plan -> Act -> Observe -> Decide\n- Multi-step reasoning & math")

# Display Conversation History
for chat in st.session_state.chat_history:
    with st.chat_message(chat["role"]):
        st.write(chat["content"])

        # Display step trace if available
        if chat.get("steps"):
            with st.expander("🔍 View Multi-Step Agent Trace", expanded=False):
                for step in chat["steps"]:
                    st.markdown(f"**Step {step['step_number']}**")
                    st.markdown(f"<span class='badge-plan'>PLAN</span> {step['plan']}", unsafe_allow_html=True)
                    if step.get("action"):
                        args_str = ", ".join(f"{k}={repr(v)}" for k, v in step["action"].get("args", {}).items())
                        st.markdown(f"<span class='badge-tool'>TOOL CALL</span> `{step['action'].get('tool')}({args_str})`", unsafe_allow_html=True)
                    if step.get("tool_result"):
                        st.markdown(f"<span class='badge-obs'>TOOL RESULT</span> {step['tool_result'].get('message')}", unsafe_allow_html=True)
                    if step.get("memory_update"):
                        st.markdown(f"<span class='badge-mem'>MEMORY</span> {step['memory_update']}", unsafe_allow_html=True)
                    if step.get("observation"):
                        st.markdown(f"<span class='badge-obs'>OBSERVE</span> {step['observation']}", unsafe_allow_html=True)
                    if step.get("decision"):
                        st.markdown(f"<span class='badge-dec'>DECIDE</span> {step['decision']}", unsafe_allow_html=True)
                    st.markdown("---")


# =============================================================================
# 5. USER INPUT HANDLING & AGENT EXECUTION
# =============================================================================
user_query = st.chat_input("Ask a question or log an expense (e.g. 'I spent ₹500 on food')...")

# Check if a quick-prompt button was pressed
if selected_prompt:
    user_query = selected_prompt

if user_query:
    # 1. Display User Message
    st.chat_message("user").write(user_query)

    # 2. Instantiate Agent with shared session memory
    agent = PersonalBudgetAgent(
        memory=st.session_state.memory,
        use_llm=bool(st.session_state.api_key)
    )

    # 3. Run Agent Loop
    with st.spinner("🤖 Agent reasoning through PLAN -> ACT -> OBSERVE -> DECIDE..."):
        answer, state = agent.run(user_query, verbose=False)

    # 4. Serialize step traces for display
    steps_data = []
    for s in state.steps:
        steps_data.append({
            "step_number": s.step_number,
            "plan": s.plan,
            "action": s.action,
            "tool_result": s.tool_result,
            "observation": s.observation,
            "memory_update": s.memory_update,
            "decision": s.decision,
        })

    # 5. Save to Chat History
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": answer,
        "steps": steps_data
    })

    # 6. Display Agent Response & Trace
    with st.chat_message("assistant"):
        st.write(answer)
        if steps_data:
            with st.expander("🔍 View Multi-Step Agent Trace", expanded=True):
                for step in steps_data:
                    st.markdown(f"**Step {step['step_number']}**")
                    st.markdown(f"<span class='badge-plan'>PLAN</span> {step['plan']}", unsafe_allow_html=True)
                    if step.get("action"):
                        args_str = ", ".join(f"{k}={repr(v)}" for k, v in step["action"].get("args", {}).items())
                        st.markdown(f"<span class='badge-tool'>TOOL CALL</span> `{step['action'].get('tool')}({args_str})`", unsafe_allow_html=True)
                    if step.get("tool_result"):
                        st.markdown(f"<span class='badge-obs'>TOOL RESULT</span> {step['tool_result'].get('message')}", unsafe_allow_html=True)
                    if step.get("memory_update"):
                        st.markdown(f"<span class='badge-mem'>MEMORY</span> {step['memory_update']}", unsafe_allow_html=True)
                    if step.get("observation"):
                        st.markdown(f"<span class='badge-obs'>OBSERVE</span> {step['observation']}", unsafe_allow_html=True)
                    if step.get("decision"):
                        st.markdown(f"<span class='badge-dec'>DECIDE</span> {step['decision']}", unsafe_allow_html=True)
                    st.markdown("---")

    # Refresh to update sidebar metrics
    st.rerun()
