# Personal Budget Assistant — Comprehensive Viva Guide

This guide is designed to help you confidently explain the **Personal Budget Assistant (Agentic AI)** project during your viva and practical exam.

---

## Part 1: Core Architectural Concepts (15 Key Points)

### 1. What is an AI Agent?
An **AI Agent** is an autonomous software entity that perceives its environment, makes decisions by reasoning through goals, takes actions using external tools (functions/APIs), observes the results, and adapts its next steps until the goal is achieved.

### 2. Difference Between a Chatbot and an AI Agent
| Feature | Traditional Chatbot | Agentic AI System (Our Project) |
| :--- | :--- | :--- |
| **Execution** | Single-turn text generation | Multi-step reasoning loop |
| **Tool Usage** | None (only generates text) | Calls real Python tools (`add_expense`, `get_summary`) |
| **Observation** | Cannot observe real-world side effects | Observes tool results to decide subsequent actions |
| **Memory** | Raw text buffer / forgets structured facts | Typed, structured session memory (`AgentMemory`) |
| **Decision Logic** | Passive completion | Autonomous planning, validation, and multi-step math |

### 3. What is the PLAN-ACT Loop?
The **PLAN-ACT loop** (specifically **PLAN → ACT → OBSERVE → DECIDE**) is the cyclic thought process of an agent:
1. **PLAN**: The agent assesses the user's goal and identifies what missing information or action is needed.
2. **ACT**: The agent executes an external action (calling a Python tool with validated arguments).
3. **OBSERVE**: The agent reads the return dictionary from the tool and reflects on its outcome.
4. **DECIDE**: The agent evaluates whether the goal is completed or if another step/tool call is required.

### 4. Where is Planning Implemented in Code?
In [`src/agent.py`](file:///c:/Users/zafar/OneDrive/Desktop/Agentic%20AI/src/agent.py):
- In LLM Mode: Handled via system prompt guidance and LLM function-calling decisions in `_run_with_llm()`.
- In Deterministic Mode: Handled inside `_run_with_deterministic_engine()` where `StepRecord.plan` is dynamically constructed for each step.

### 5. Where Does the Agent Decide the Next Action?
In [`src/agent.py`](file:///c:/Users/zafar/OneDrive/Desktop/Agentic%20AI/src/agent.py) inside the `while not state.is_finished` loop:
- After receiving a tool result, the agent populates `step.decision` and determines whether `state.is_finished = True` or if another iteration of tool calling/arithmetic is needed.

### 6. Where are the Two Tools Defined?
In [`src/tools.py`](file:///c:/Users/zafar/OneDrive/Desktop/Agentic%20AI/src/tools.py):
1. `add_expense(memory, item, amount)`
2. `get_summary(memory, category)`

### 7. How Does `add_expense()` Work?
Located in [`src/tools.py`](file:///c:/Users/zafar/OneDrive/Desktop/Agentic%20AI/src/tools.py#L20-L65):
1. Validates that `item` is a non-empty string.
2. Validates that `amount` is a valid positive number (`amount > 0`).
3. Calls `memory.record_expense(item, amount)` to persist the entry.
4. Returns a success dictionary containing the confirmation message and updated category total.
5. If invalid (e.g. negative or non-numeric), returns an error status dictionary with a user-friendly error message.

### 8. How Does `get_summary()` Work?
Located in [`src/tools.py`](file:///c:/Users/zafar/OneDrive/Desktop/Agentic%20AI/src/tools.py#L68-L109):
1. Accepts a category name (e.g. `'food'`, `'travel'`) or `'all'`.
2. Reads the stored expense list from `memory`.
3. Computes the sum for the selected category or total overall expenses.
4. Returns a status dictionary with total amount, item count, and a formatted summary message.

### 9. Where is Memory Stored?
In [`src/memory.py`](file:///c:/Users/zafar/OneDrive/Desktop/Agentic%20AI/src/memory.py) inside the `AgentMemory` class.
- Structured expenses are stored in `self.expenses: List[Dict[str, Any]]`.
- Conversation turns are stored in `self.conversation_history: List[Dict[str, str]]`.

### 10. How is Memory Retrieved?
Via dedicated methods on `AgentMemory`:
- `memory.get_total_for_category(category)`
- `memory.get_expenses_by_category(category)`
- `memory.get_structured_summary()`
- `memory.get_messages()`

### 11. How Does the Agent Use Previous Conversation Information?
The `AgentMemory` instance is shared across user turns in the session.
When Turn 1 records `food = ₹500` and Turn 2 records `food = ₹300`, the underlying memory maintains both records. When Turn 3 asks *"How much have I spent on food?"*, the agent calls `get_summary("food")` on the shared memory instance and retrieves the accumulated ₹800.

### 12. Give an Example of a Multi-Step Execution
Goal: *"I have ₹5000. I spent ₹1000 on food and ₹500 on travel. Can I afford a ₹2000 trip?"*
- **Step 1 (ACT)**: Calls `add_expense("food", 1000)` and `add_expense("travel", 500)` -> updates memory.
- **Step 2 (ACT)**: Calls `get_summary("all")` -> receives `Total Spent = ₹2800` (or ₹1500 if new session).
- **Step 3 (OBSERVE & MATH)**: Calculates `₹5000 - Total Spent - ₹2000 Trip Cost`.
- **Step 4 (DECIDE & FINAL)**: Determines remaining balance and confirms affordability with a complete breakdown.

### 13. Why is This Project an Agent Rather than a Chatbot?
1. It does not blindly generate text; it queries external Python tools for facts and figures.
2. It follows an explicit feedback loop where the outcome of Step 1 changes what happens in Step 2.
3. It has state management (`AgentState`) tracking goals, steps, tool outputs, and termination conditions.

### 14. What Happens When a Tool Fails?
When an invalid input is passed (e.g. `add_expense("food", -500)`):
1. `add_expense` returns `{"status": "error", "message": "Amount must be greater than zero."}`.
2. The agent observes this error during the `OBSERVE` phase.
3. The agent decides not to corrupt memory and informs the user politely in the final answer.

### 15. Why are API Keys Stored in Environment Variables?
Hardcoding API tokens in code risks accidental credential leakage when uploading to GitHub or sharing files. Using `os.getenv("GITHUB_TOKEN")` or `.env` (ignored by `.gitignore`) ensures security best practices.

---

## Part 2: Top 10 Likely Examiner Viva Questions & Answers

### Q1. Why did you not use LangChain or CrewAI?
> **Answer**: *"I implemented the PLAN-ACT loop directly in clean Python so that every step of the agent's reasoning, tool dispatching, and state transitions is fully transparent, understandable, and verifiable without hidden abstractions."*

### Q2. How does the agent know which tool to call?
> **Answer**: *"The agent analyzes the user's intent. If the user mentions spending or purchasing, it selects `add_expense`. If the user asks for totals or spending queries, it selects `get_summary`. In LLM mode, this is guided by the system prompt and function schemas in `TOOL_DEFINITIONS`."*

### Q3. What is the difference between raw conversation memory and structured memory?
> **Answer**: *"Raw conversation memory is just a list of chat messages. Structured memory (`AgentMemory`) maintains typed Python dictionaries (`{'item': 'food', 'amount': 500.0, 'timestamp': ...}`) that can be queried, filtered, and aggregated mathematically by tools."*

### Q4. How does the agent prevent infinite loops?
> **Answer**: *"We have a safety constraint in `AgentState.max_steps` (default 6). If the agent takes more than 6 steps without finishing, the loop terminates safely."*

### Q5. Can this agent run offline without an internet connection?
> **Answer**: *"Yes. While it supports live LLMs like GitHub Models or OpenAI, it also has a built-in deterministic execution engine that runs the identical PLAN-ACT-OBSERVE-DECIDE loop locally and offline for 100% reproducible testing."*

### Q6. What parameters does `add_expense` take and what validations are performed?
> **Answer**: *"It accepts `item` (string) and `amount` (number). It validates that the item is non-empty, the amount is numeric, and the amount is strictly greater than zero."*

### Q7. How does `get_summary` handle categories that don't exist?
> **Answer**: *"It queries the memory for matching records. If no matching records exist, it returns a total of ₹0.00 gracefully instead of throwing an unhandled exception."*

### Q8. What does `AgentState` do?
> **Answer**: *"It maintains the state of the current turn: the user's goal, the step-by-step history (`StepRecord`), tool results, completion status (`is_finished`), and the final answer."*

### Q9. Walk me through the code where the tool is actually executed.
> **Answer**: *"In `src/agent.py` inside the `_execute_tool(tool_name, tool_args)` method. It receives the tool name and argument dictionary and calls the actual Python function in `src/tools.py`."*

### Q10. How does the trace output prove that this is an agent?
> **Answer**: *"The trace output visibly prints each discrete step: `[PLAN]`, `[TOOL CALL]`, `[TOOL RESULT]`, `[OBSERVE]`, `[DECISION]`, and `[FINAL ANSWER]`, proving that multi-step reasoning took place rather than a single direct text generation."*
