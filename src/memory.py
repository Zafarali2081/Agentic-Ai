"""Structured Session Memory for Personal Budget Assistant.

Why is Memory important for an AI Agent?
- A standard chatbot without memory forgets earlier messages as soon as a turn ends.
- The Personal Budget Assistant needs to remember:
  1. All expenses recorded during the conversation (e.g. food = ₹500, then food = ₹300).
  2. The conversational context across multiple turns.
- Memory here is STRUCTURED: it is not just raw text, but a typed collection of
  expense records and conversation logs that tools and the agent can read and update.
"""

from datetime import datetime
from typing import List, Dict, Any, Optional


class AgentMemory:
    """Manages structured session memory for expenses and conversation history."""

    def __init__(self):
        # Structured list of expense records
        # Each record: {"item": str, "amount": float, "timestamp": str}
        self.expenses: List[Dict[str, Any]] = []

        # Conversation history across turns in the same session
        # Each entry: {"role": "user" | "assistant" | "system", "content": str}
        self.conversation_history: List[Dict[str, str]] = []

    def record_expense(self, item: str, amount: float) -> Dict[str, Any]:
        """Store an expense record in structured memory.

        Args:
            item: Name or category of the expense (e.g., 'food', 'travel').
            amount: Positive numeric cost in Rupees (₹).

        Returns:
            dict: The stored record.
        """
        record = {
            "item": item.strip().lower(),
            "amount": float(amount),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.expenses.append(record)
        return record

    def get_expenses_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Retrieve all expenses matching a specific category (case-insensitive)."""
        cat_clean = category.strip().lower()
        if cat_clean == "all":
            return list(self.expenses)
        return [exp for exp in self.expenses if exp["item"] == cat_clean]

    def get_total_for_category(self, category: str) -> float:
        """Calculate total spending for a specific category or 'all'."""
        matched = self.get_expenses_by_category(category)
        return sum(exp["amount"] for exp in matched)

    def get_all_categories(self) -> List[str]:
        """Get unique list of recorded expense categories."""
        return sorted(list(set(exp["item"] for exp in self.expenses)))

    def get_structured_summary(self) -> Dict[str, Any]:
        """Return a structured summary breakdown of all spending in memory."""
        categories = self.get_all_categories()
        breakdown = {cat: self.get_total_for_category(cat) for cat in categories}
        total_overall = sum(breakdown.values())
        return {
            "categories": breakdown,
            "total_overall": total_overall,
            "total_records": len(self.expenses),
            "expenses": list(self.expenses)
        }

    def add_message(self, role: str, content: str) -> None:
        """Record a message in conversation history."""
        self.conversation_history.append({"role": role, "content": content})

    def get_messages(self) -> List[Dict[str, str]]:
        """Return full conversation history."""
        return list(self.conversation_history)

    def clear(self) -> None:
        """Reset all memory (useful for starting fresh sessions in demos)."""
        self.expenses.clear()
        self.conversation_history.clear()

    def __repr__(self) -> str:
        summary = self.get_structured_summary()
        return f"AgentMemory(records={len(self.expenses)}, total=₹{summary['total_overall']:.2f}, categories={list(summary['categories'].keys())})"
