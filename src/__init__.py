"""Personal Budget Assistant - Agentic AI Package.

A transparent, educational AI agent implementing an explicit
PLAN -> ACT -> OBSERVE -> DECIDE loop with persistent memory and tools.
"""

from src.memory import AgentMemory
from src.tools import add_expense, get_summary
from src.state import AgentState, StepRecord
from src.agent import PersonalBudgetAgent
from src.config import get_llm_client, get_model_name

__all__ = [
    "AgentMemory",
    "add_expense",
    "get_summary",
    "AgentState",
    "StepRecord",
    "PersonalBudgetAgent",
    "get_llm_client",
    "get_model_name",
]
