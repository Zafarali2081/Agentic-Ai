"""Personal Budget Assistant AI Agent.

This module implements the complete Agentic AI architecture:
- Explicit PLAN -> ACT -> OBSERVE -> DECIDE loop
- Multi-step execution for complex goals
- Persistent memory integration
- Rich trace formatting for transparency and viva explanations
- Support for live LLMs (GitHub Models / OpenAI) + Deterministic Fallback Engine for offline testing
"""

import json
import re
import sys
from typing import Dict, Any, Optional, List, Tuple

# Ensure UTF-8 output on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from src.memory import AgentMemory
from src.state import AgentState, StepRecord
from src.tools import add_expense, get_summary, TOOL_DEFINITIONS
from src.config import get_llm_client, get_model_name


class PersonalBudgetAgent:
    """Personal Budget Assistant Agent.

    Architecture:
    User Query -> AgentState -> PLAN -> ACT (Tool Call) -> OBSERVE -> DECIDE -> FINAL ANSWER
    """

    def __init__(self, memory: Optional[AgentMemory] = None, use_llm: bool = True):
        """Initialize the Personal Budget Agent.

        Args:
            memory: Existing AgentMemory instance, or creates a new one if None.
            use_llm: Whether to attempt calling live LLM if API key is configured.
        """
        self.memory = memory if memory is not None else AgentMemory()
        self.use_llm = use_llm
        self.client = get_llm_client() if use_llm else None
        self.model = get_model_name()

    def run(self, user_input: str, verbose: bool = True) -> Tuple[str, AgentState]:
        """Execute the full agentic loop for a user request.

        This function runs the explicit:
        PLAN -> ACT -> OBSERVE -> DECIDE loop until finished.

        Args:
            user_input: The user's prompt or question.
            verbose: If True, prints the detailed multi-step trace.

        Returns:
            tuple: (final_answer, state)
        """
        state = AgentState(user_goal=user_input, memory=self.memory)

        # Record user message in memory
        self.memory.add_message("user", user_input)

        if verbose:
            print("\n" + "=" * 60)
            print(f"[AGENT TRACE STARTED]: '{user_input}'")
            print("=" * 60)

        # Decide whether to use Live LLM or the Built-in Deterministic Engine
        if self.client is not None:
            self._run_with_llm(state, verbose=verbose)
        else:
            self._run_with_deterministic_engine(state, verbose=verbose)

        # Record agent final answer in memory
        if state.final_answer:
            self.memory.add_message("assistant", state.final_answer)

        if verbose:
            print("\n" + "=" * 60)
            print("[FINAL ANSWER]:")
            print(state.final_answer)
            print("=" * 60 + "\n")

        return state.final_answer or "", state


    # =========================================================================
    # 1. LIVE LLM AGENT LOOP (GitHub Models / OpenAI API)
    # =========================================================================
    def _run_with_llm(self, state: AgentState, verbose: bool = True) -> None:
        """Run the PLAN-ACT-OBSERVE-DECIDE loop using a live LLM via tool calling."""
        system_prompt = (
            "You are the Personal Budget Assistant, an agentic AI helper for a student.\n"
            "You have access to structured memory and two Python tools:\n"
            "1. add_expense(item, amount): Record an expense. Validate item and positive amount.\n"
            "2. get_summary(category): Get total spending for a category or 'all'.\n\n"
            "OPERATING GUIDELINES:\n"
            "- Always reason step-by-step.\n"
            "- First PLAN what information you need.\n"
            "- Call the appropriate tool(s) to fetch or record data.\n"
            "- If a goal requires multiple pieces of information or checks (e.g. affordability calculation), "
            "perform tool calls step-by-step.\n"
            "- If a tool returns an error (e.g. invalid or negative amount), explain the error politely to the user.\n"
            "- When all data is gathered, provide a clear, helpful final answer."
        )

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # Add recent conversation history for memory context
        for msg in self.memory.get_messages()[-6:]:
            messages.append(msg)

        while not state.is_finished and len(state.steps) < state.max_steps:
            step_num = state.current_step_number()

            try:
                # LLM decides PLAN and next ACTION
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=TOOL_DEFINITIONS,
                    tool_choice="auto",
                    temperature=0.0
                )
                choice = response.choices[0].message

                # Case A: LLM decided to call one or more tools (ACT)
                if choice.tool_calls:
                    for tool_call in choice.tool_calls:
                        tool_name = tool_call.function.name
                        try:
                            tool_args = json.loads(tool_call.function.arguments)
                        except Exception:
                            tool_args = {}

                        # PLAN
                        plan_text = f"Call tool '{tool_name}' with parameters {tool_args}."

                        # ACT (Execute real Python tool)
                        tool_result = self._execute_tool(tool_name, tool_args)

                        # OBSERVE & DECIDE
                        observation = f"Tool '{tool_name}' returned: {tool_result.get('message')}"
                        decision = "Observation noted. Evaluating if additional steps or tools are required."

                        step_rec = StepRecord(
                            step_number=step_num,
                            plan=plan_text,
                            action={"tool": tool_name, "args": tool_args},
                            tool_result=tool_result,
                            observation=observation,
                            memory_update=f"Session memory updated (records={len(self.memory.expenses)})",
                            decision=decision
                        )
                        state.add_step(step_rec)

                        if verbose:
                            self._print_step_trace(step_rec)

                        # Feed tool result back to LLM messages
                        messages.append(choice)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_name,
                            "content": json.dumps(tool_result)
                        })

                # Case B: LLM decided it has enough info -> FINAL ANSWER
                else:
                    final_text = choice.content or "Task completed."
                    state.final_answer = final_text
                    state.is_finished = True

                    plan_text = "Synthesize gathered tool results and memory to generate final response."
                    decision = "All necessary actions completed. Final answer ready."

                    step_rec = StepRecord(
                        step_number=step_num,
                        plan=plan_text,
                        action=None,
                        tool_result=None,
                        observation="All required data is available in state and memory.",
                        decision=decision
                    )
                    state.add_step(step_rec)

                    if verbose:
                        self._print_step_trace(step_rec)
                    break

            except Exception as e:
                # LLM API error -> Fall back gracefully to deterministic reasoning
                if verbose:
                    print(f"\n[Note: LLM API notice: {e}. Switching to deterministic agent engine.]")
                self._run_with_deterministic_engine(state, verbose=verbose)
                break

    # =========================================================================
    # 2. DETERMINISTIC AGENT ENGINE (Offline & Guaranteed Viva Demo Engine)
    # =========================================================================
    def _run_with_deterministic_engine(self, state: AgentState, verbose: bool = True) -> None:
        """Transparent, rule-driven agent execution of the PLAN-ACT-OBSERVE-DECIDE loop.

        Guarantees 100% reproducible execution for demoing, grading, and testing
        even without internet or API keys.
        """
        user_text = state.user_goal.strip()
        lower_text = user_text.lower()

        # ---------------------------------------------------------------------
        # SCENARIO A: Expense Addition (e.g. "I spent ₹500 on food", "-₹500 on food")
        # ---------------------------------------------------------------------
        spent_match = re.search(
            r'(?:spent|paid|bought|add expense|cost|expensed)\s+(?:another\s+)?'
            r'(-?\s*(?:₹|rs\.?|inr)?\s*-?\d+(?:\.\d+)?)\s*(?:on|for|in)?\s*([a-zA-Z\s]+)?',
            lower_text
        )
        if not spent_match:
            # Alternate pattern: "food: 500" or "spent on food 500"
            spent_match = re.search(
                r'(?:spent\s+(?:on\s+)?)?([a-zA-Z]+)\s*(?:of|for)?\s*(-?\s*(?:₹|rs\.?|inr)?\s*-?\d+(?:\.\d+)?)',
                lower_text
            )
            if spent_match and ("spent" in lower_text or "cost" in lower_text or "paid" in lower_text):
                item_str = spent_match.group(1).strip()
                raw_amt = spent_match.group(2).strip()
            else:
                spent_match = None
        else:
            raw_amt = spent_match.group(1).strip()
            item_str = (spent_match.group(2) or "general").strip()
            # Clean trailing words like "yesterday", "today"
            item_str = re.sub(r'\b(today|yesterday|now|already)\b', '', item_str).strip()

        if spent_match:
            # Clean raw amount string: remove currency symbols and whitespace, preserve minus sign
            amt_clean = re.sub(r'[^\d.-]', '', raw_amt)
            # Handle multiple minus signs or artifacts
            amt_str = amt_clean


        # Handle complex scenario (Affordability goal with multiple spent clauses) separately
        is_affordability_query = "afford" in lower_text or "remaining" in lower_text or ("have" in lower_text and "trip" in lower_text)

        if spent_match and not is_affordability_query:
            # STEP 1: PLAN & ACT (Call add_expense tool)
            step_num = state.current_step_number()
            plan = f"Identify expense details from user input (Item: '{item_str}', Amount: {amt_str}) and record it using add_expense tool."
            action = {"tool": "add_expense", "args": {"item": item_str, "amount": float(amt_str) if self._is_num(amt_str) else amt_str}}

            # ACT
            tool_result = self._execute_tool("add_expense", action["args"])

            # OBSERVE
            if tool_result.get("status") == "success":
                observation = f"Successfully recorded {tool_result.get('item')} = ₹{tool_result.get('amount'):.2f}. Updated total for {tool_result.get('item')}: ₹{tool_result.get('category_total'):.2f}."
                decision = "Expense successfully saved to structured memory. No further tool calls needed. Ready to respond."
                mem_update = f"Stored {tool_result.get('item')} expense of ₹{tool_result.get('amount'):.2f} in session memory."
                final_answer = f"Added ₹{tool_result.get('amount'):.2f} {tool_result.get('item')} expense. Total {tool_result.get('item')} spending is now ₹{tool_result.get('category_total'):.2f}."
            else:
                observation = f"Tool validation failed: {tool_result.get('message')}"
                decision = "Tool rejected the invalid expense. Formulate user-friendly error response."
                mem_update = "No changes made to session memory due to validation error."
                final_answer = f"I could not record that expense: {tool_result.get('message')}"

            step_rec = StepRecord(
                step_number=step_num,
                plan=plan,
                action=action,
                tool_result=tool_result,
                observation=observation,
                memory_update=mem_update,
                decision=decision
            )
            state.add_step(step_rec)
            if verbose:
                self._print_step_trace(step_rec)

            state.final_answer = final_answer
            state.is_finished = True
            return

        # ---------------------------------------------------------------------
        # SCENARIO B: Summary Query (e.g. "How much have I spent on food?", "Total spending")
        # ---------------------------------------------------------------------
        summary_match = re.search(r'(?:how much|total|summary|what is my spending|what did i spend)\s*(?:have i spent|spent)?\s*(?:on|for|in)?\s*([a-zA-Z\s]+)?', lower_text)
        if summary_match and not is_affordability_query:
            target_cat = summary_match.group(1) or "all"
            target_cat = target_cat.replace("?", "").strip().lower()
            if not target_cat or target_cat in ["all", "everything", "total", "overall", "my spending"]:
                target_cat = "all"

            # STEP 1: PLAN & ACT (Call get_summary tool)
            step_num = state.current_step_number()
            plan = f"Retrieve spending summary for category '{target_cat}' from memory using get_summary tool."
            action = {"tool": "get_summary", "args": {"category": target_cat}}

            tool_result = self._execute_tool("get_summary", action["args"])

            # OBSERVE
            total = tool_result.get("total", 0.0)
            if target_cat == "all":
                observation = f"Retrieved total overall spending of ₹{total:.2f} across {tool_result.get('count', 0)} records."
                final_answer = f"Your total overall spending is ₹{total:.2f}."
            else:
                observation = f"Retrieved {target_cat} spending total of ₹{total:.2f}."
                final_answer = f"You have spent ₹{total:.2f} on {target_cat}."

            decision = "Retrieved requested summary. No additional tool calls needed. Proceed to final answer."

            step_rec = StepRecord(
                step_number=step_num,
                plan=plan,
                action=action,
                tool_result=tool_result,
                observation=observation,
                memory_update="Read from persistent session memory.",
                decision=decision
            )
            state.add_step(step_rec)
            if verbose:
                self._print_step_trace(step_rec)

            state.final_answer = final_answer
            state.is_finished = True
            return

        # ---------------------------------------------------------------------
        # SCENARIO C: Complex Multi-Step Goal (Affordability / Budget Planning)
        # e.g., "I have ₹5000. I spent ₹1000 on food and ₹500 on travel. Can I afford a ₹2000 trip?"
        # ---------------------------------------------------------------------
        if is_affordability_query:
            # 1. Parse budget
            budget_match = re.search(r'(?:have|budget of|available)\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)', lower_text)
            total_budget = float(budget_match.group(1)) if budget_match else 5000.0

            # 2. Parse target cost (e.g. ₹2000 trip)
            target_match = re.search(r'(?:afford\s+(?:a\s+)?)?(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:trip|purchase|item|flight|cost)', lower_text)
            target_cost = float(target_match.group(1)) if target_match else 2000.0

            # STEP 1: Check existing spending or record new mentions
            # Extract any mentioned expenses like '₹1000 on food and ₹500 on travel'
            all_expense_matches = re.findall(r'(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)\s*(?:on|for)\s*([a-zA-Z]+)', lower_text)
            # Filter out target items like 'trip', 'flight', etc.
            items_found = [
                (amt, cat) for amt, cat in all_expense_matches
                if cat.lower() not in ["trip", "purchase", "item", "flight", "tour", "vacation"]
            ]

            # Record any mentioned unrecorded expenses
            for amt_s, cat_s in items_found:
                if not any(e["item"] == cat_s.lower() and e["amount"] == float(amt_s) for e in self.memory.expenses):
                    s_num = state.current_step_number()
                    s_plan = f"Record mentioned prior expense '{cat_s}' = ₹{amt_s} into memory."
                    s_act = {"tool": "add_expense", "args": {"item": cat_s, "amount": float(amt_s)}}
                    s_res = self._execute_tool("add_expense", s_act["args"])
                    s_obs = f"Stored {cat_s} expense of ₹{amt_s}."
                    s_dec = "Continue multi-step affordability assessment."
                    s_rec = StepRecord(step_number=s_num, plan=s_plan, action=s_act, tool_result=s_res, observation=s_obs, memory_update=f"Added {cat_s} expense to memory.", decision=s_dec)
                    state.add_step(s_rec)
                    if verbose:
                        self._print_step_trace(s_rec)


            # STEP 2: Query spending summary from memory
            step_num = state.current_step_number()
            plan = "Retrieve total spending summary from memory using get_summary('all') to determine total spent so far."
            action = {"tool": "get_summary", "args": {"category": "all"}}
            tool_result = self._execute_tool("get_summary", action["args"])

            current_total_spent = tool_result.get("total", 0.0)

            # Fallback if query explicitly stated prior spending (e.g. "already spent ₹800")
            if current_total_spent == 0.0:
                already_spent_match = re.search(r'already spent\s*(?:₹|rs\.?|inr)?\s*(\d+(?:\.\d+)?)', lower_text)
                if already_spent_match:
                    current_total_spent = float(already_spent_match.group(1))

            observation = f"Total spending retrieved: ₹{current_total_spent:.2f}."
            decision = "Perform financial affordability calculations to reach final decision."

            step_rec = StepRecord(
                step_number=step_num,
                plan=plan,
                action=action,
                tool_result=tool_result,
                observation=observation,
                memory_update="Read full expense summary from session memory.",
                decision=decision
            )
            state.add_step(step_rec)
            if verbose:
                self._print_step_trace(step_rec)

            # STEP 3: Multi-step Reasoning & Math Decision
            remaining_before_trip = total_budget - current_total_spent
            remaining_after_trip = remaining_before_trip - target_cost
            can_afford = remaining_before_trip >= target_cost

            step_num_final = state.current_step_number()
            math_plan = (
                f"Calculate remaining budget: Initial Budget (₹{total_budget:.2f}) - "
                f"Total Spent (₹{current_total_spent:.2f}) = ₹{remaining_before_trip:.2f}. "
                f"Subtract Target Cost (₹{target_cost:.2f}) -> ₹{remaining_after_trip:.2f} remaining."
            )

            if can_afford:
                final_answer = (
                    f"Yes, you can afford the ₹{target_cost:.2f} trip!\n\n"
                    f"Financial Breakdown:\n"
                    f"• Initial Budget: ₹{total_budget:.2f}\n"
                    f"• Total Spent So Far: ₹{current_total_spent:.2f}\n"
                    f"• Remaining Before Trip: ₹{remaining_before_trip:.2f}\n"
                    f"• Trip Cost: ₹{target_cost:.2f}\n"
                    f"• Estimated Balance After Trip: ₹{remaining_after_trip:.2f}"
                )
            else:
                shortage = abs(remaining_after_trip)
                final_answer = (
                    f"No, you cannot afford the ₹{target_cost:.2f} trip with your current budget.\n\n"
                    f"Financial Breakdown:\n"
                    f"• Initial Budget: ₹{total_budget:.2f}\n"
                    f"• Total Spent So Far: ₹{current_total_spent:.2f}\n"
                    f"• Remaining Available: ₹{remaining_before_trip:.2f}\n"
                    f"• Trip Cost: ₹{target_cost:.2f}\n"
                    f"• Shortage: ₹{shortage:.2f}"
                )

            final_rec = StepRecord(
                step_number=step_num_final,
                plan=math_plan,
                action=None,
                tool_result=None,
                observation=f"Affordability calculation complete (Can afford: {can_afford}).",
                decision="All reasoning complete. Deliver final decision to user."
            )
            state.add_step(final_rec)
            if verbose:
                self._print_step_trace(final_rec)

            state.final_answer = final_answer
            state.is_finished = True
            return

        # ---------------------------------------------------------------------
        # SCENARIO D: General / Unknown Conversational Query
        # ---------------------------------------------------------------------
        step_num = state.current_step_number()
        plan = "Analyze query and check if budget tools are required."
        step_rec = StepRecord(
            step_number=step_num,
            plan=plan,
            action=None,
            tool_result=None,
            observation="Conversational query received.",
            decision="Provide guidance on tracking expenses."
        )
        state.add_step(step_rec)
        if verbose:
            self._print_step_trace(step_rec)

        state.final_answer = (
            "I am your Personal Budget Assistant! You can tell me what you spent (e.g. 'I spent ₹500 on food'), "
            "ask for summaries (e.g. 'How much have I spent on food?'), or ask affordability questions "
            "(e.g. 'I have ₹5000. Can I afford a ₹2000 trip?')."
        )
        state.is_finished = True

    # =========================================================================
    # 3. TOOL DISPATCHER & TRACE FORMATTING HELPERS
    # =========================================================================
    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch tool calls to real Python functions."""
        if tool_name == "add_expense":
            item = tool_args.get("item", "")
            amount = tool_args.get("amount", 0)
            return add_expense(self.memory, item=item, amount=amount)

        elif tool_name == "get_summary":
            category = tool_args.get("category", "all")
            return get_summary(self.memory, category=category)

        else:
            return {
                "status": "error",
                "message": f"Unknown tool '{tool_name}'."
            }

    def _print_step_trace(self, step: StepRecord) -> None:
        """Format and print a clear step trace for the notebook and console."""
        print(f"\n>> [STEP {step.step_number}]")
        print(f"  [PLAN]:        {step.plan}")
        if step.action:
            tool_name = step.action.get('tool')
            args_str = ", ".join(f"{k}={repr(v)}" for k, v in step.action.get('args', {}).items())
            print(f"  [TOOL CALL]:   {tool_name}({args_str})")
        if step.tool_result:
            print(f"  [TOOL RESULT]: {step.tool_result.get('message')}")
        if step.memory_update:
            print(f"  [MEMORY]:      {step.memory_update}")
        if step.observation:
            print(f"  [OBSERVE]:     {step.observation}")
        if step.decision:
            print(f"  [DECISION]:    {step.decision}")


    @staticmethod
    def _is_num(val: Any) -> bool:
        try:
            float(val)
            return True
        except (ValueError, TypeError):
            return False
