"""Real Python Tools for Personal Budget Assistant.

This module implements the two required tools:
1. add_expense(item, amount)
2. get_summary(category)

Each tool:
- Performs strict input validation (non-empty string, numeric, positive amount).
- Interacts with real structured memory.
- Returns clear, informative dictionary responses that the agent can observe.
"""

from typing import Dict, Any, Union
from src.memory import AgentMemory


def add_expense(memory: AgentMemory, item: str, amount: Union[int, float, str]) -> Dict[str, Any]:
    """Record an expense into the agent's memory.

    Validation Rules:
    - 'item' must be a non-empty string.
    - 'amount' must be numeric.
    - 'amount' must be greater than zero.

    Args:
        memory: The AgentMemory instance holding session data.
        item: Category/item name (e.g. 'food', 'travel', 'books').
        amount: Cost in rupees (must be > 0).

    Returns:
        dict: Status, message, and recorded details.
    """
    # 1. Validate item name
    if not isinstance(item, str) or not item.strip():
        return {
            "status": "error",
            "message": "Item name cannot be empty. Please specify a valid expense item (e.g. 'food', 'travel')."
        }

    # 2. Validate amount is numeric
    try:
        numeric_amount = float(amount)
    except (ValueError, TypeError):
        return {
            "status": "error",
            "message": f"Invalid amount '{amount}'. Amount must be a valid number."
        }

    # 3. Validate amount > 0 (handle negative and zero cases)
    if numeric_amount <= 0:
        return {
            "status": "error",
            "message": "Amount must be greater than zero."
        }

    # Clean item name
    clean_item = item.strip().lower()

    # Record into memory
    record = memory.record_expense(clean_item, numeric_amount)

    # Compute updated category total to give helpful immediate feedback
    updated_total = memory.get_total_for_category(clean_item)

    return {
        "status": "success",
        "message": f"Expense added successfully: {clean_item} = ₹{numeric_amount:.2f}",
        "item": clean_item,
        "amount": numeric_amount,
        "category_total": updated_total,
        "record": record
    }


def get_summary(memory: AgentMemory, category: str = "all") -> Dict[str, Any]:
    """Retrieve the total spending for a specific category or for all categories combined.

    Args:
        memory: The AgentMemory instance holding session data.
        category: The category name to summarize (e.g., 'food', 'travel', or 'all').

    Returns:
        dict: Total spending, record count, and descriptive message.
    """
    # Validate category input
    if not isinstance(category, str) or not category.strip():
        category = "all"

    clean_category = category.strip().lower()

    if clean_category == "all":
        summary = memory.get_structured_summary()
        total = summary["total_overall"]
        count = summary["total_records"]
        categories = summary["categories"]
        if count == 0:
            msg = "Overall spending = ₹0.00 (no expenses recorded yet)."
        else:
            cat_details = ", ".join(f"{k.title()}: ₹{v:.2f}" for k, v in categories.items())
            msg = f"Overall spending = ₹{total:.2f} across {count} expense(s) ({cat_details})"
        return {
            "status": "success",
            "category": "all",
            "total": total,
            "count": count,
            "categories": categories,
            "message": msg
        }
    else:
        matched_expenses = memory.get_expenses_by_category(clean_category)
        total = sum(exp["amount"] for exp in matched_expenses)
        count = len(matched_expenses)
        return {
            "status": "success",
            "category": clean_category,
            "total": total,
            "count": count,
            "message": f"{clean_category.title()} spending = ₹{total:.2f}"
        }


# Tool definitions for LLM tool calling schema
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_expense",
            "description": "Record a new expense item and amount into the user's budget memory. Use this whenever the user mentions spending money.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item": {
                        "type": "string",
                        "description": "The category or item name of the expense, e.g. 'food', 'travel', 'books', 'rent'."
                    },
                    "amount": {
                        "type": "number",
                        "description": "The numeric amount spent in rupees (must be greater than 0)."
                    }
                },
                "required": ["item", "amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_summary",
            "description": "Get total spending summary for a specific category (e.g. 'food', 'travel') or 'all' for total overall spending.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Category name such as 'food', 'travel', 'entertainment', or 'all' for entire spending."
                    }
                },
                "required": ["category"]
            }
        }
    }
]
