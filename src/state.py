"""Agent State Management.

The AgentState tracks the entire lifecycle of a single user turn:
- Current user goal / prompt
- Memory reference (access to persistent session expenses)
- List of step traces (plan, action, tool result, observation, decision)
- Completion flag and final answer
- Safety bound (max_steps) to prevent accidental runaway loops
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from src.memory import AgentMemory


@dataclass
class StepRecord:
    """Represents a single step in the agent's PLAN -> ACT -> OBSERVE -> DECIDE loop."""
    step_number: int
    plan: str
    action: Optional[Dict[str, Any]] = None  # e.g. {"tool": "add_expense", "args": {"item": "food", "amount": 500}}
    tool_result: Optional[Dict[str, Any]] = None  # Return dictionary from the tool
    observation: Optional[str] = None  # Agent's reflection on the tool output
    memory_update: Optional[str] = None  # Description of memory change
    decision: Optional[str] = None  # Next decision (continue vs finish)


@dataclass
class AgentState:
    """Main state object maintaining execution context for the agent."""
    user_goal: str
    memory: AgentMemory
    current_plan: str = ""
    steps: List[StepRecord] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    is_finished: bool = False
    final_answer: Optional[str] = None
    max_steps: int = 6  # Safety limit for multi-step tasks

    def add_step(self, step: StepRecord) -> None:
        """Append a completed step record to the state history."""
        self.steps.append(step)
        if step.tool_result:
            self.tool_results.append(step.tool_result)

    def current_step_number(self) -> int:
        """Return next step number (1-indexed)."""
        return len(self.steps) + 1
