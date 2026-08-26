"""Unit and Integration Tests for Personal Budget Assistant.

Verifies:
1. Tool 1: add_expense() validation and recording.
2. Tool 2: get_summary() calculations and 'all' filter.
3. Memory: persistence across multiple turns.
4. Agent: full PLAN -> ACT -> OBSERVE -> DECIDE loop.
5. All 6 Self-Test Rubric scenarios.
"""

import unittest
from src.memory import AgentMemory
from src.tools import add_expense, get_summary
from src.agent import PersonalBudgetAgent


class TestPersonalBudgetAssistant(unittest.TestCase):

    def setUp(self):
        """Reset memory and agent before each test."""
        self.memory = AgentMemory()
        self.agent = PersonalBudgetAgent(memory=self.memory, use_llm=False)

    # -------------------------------------------------------------------------
    # UNIT TESTS: Tools & Validation
    # -------------------------------------------------------------------------
    def test_tool_add_expense_valid(self):
        """Test adding a valid expense."""
        result = add_expense(self.memory, "food", 500)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["item"], "food")
        self.assertEqual(result["amount"], 500.0)
        self.assertEqual(len(self.memory.expenses), 1)

    def test_tool_add_expense_invalid_negative(self):
        """Test rejection of negative amounts."""
        result = add_expense(self.memory, "food", -500)
        self.assertEqual(result["status"], "error")
        self.assertIn("greater than zero", result["message"])
        self.assertEqual(len(self.memory.expenses), 0)

    def test_tool_add_expense_invalid_zero(self):
        """Test rejection of zero amount."""
        result = add_expense(self.memory, "food", 0)
        self.assertEqual(result["status"], "error")
        self.assertIn("greater than zero", result["message"])

    def test_tool_add_expense_invalid_empty_item(self):
        """Test rejection of empty item name."""
        result = add_expense(self.memory, "   ", 100)
        self.assertEqual(result["status"], "error")
        self.assertIn("empty", result["message"])

    def test_tool_get_summary_category_and_all(self):
        """Test category summaries and 'all' summary aggregation."""
        add_expense(self.memory, "food", 500)
        add_expense(self.memory, "food", 300)
        add_expense(self.memory, "travel", 200)

        # Test food summary
        food_sum = get_summary(self.memory, "food")
        self.assertEqual(food_sum["status"], "success")
        self.assertEqual(food_sum["total"], 800.0)
        self.assertEqual(food_sum["count"], 2)

        # Test travel summary
        travel_sum = get_summary(self.memory, "travel")
        self.assertEqual(travel_sum["total"], 200.0)
        self.assertEqual(travel_sum["count"], 1)

        # Test 'all' summary
        all_sum = get_summary(self.memory, "all")
        self.assertEqual(all_sum["total"], 1000.0)
        self.assertEqual(all_sum["count"], 3)

    # -------------------------------------------------------------------------
    # RUBRIC SELF-TESTS 1 TO 6: Agentic Flow & Memory Persistence
    # -------------------------------------------------------------------------
    def test_rubric_test_1_add_food_expense(self):
        """Test 1: 'I spent ₹500 on food.' -> add_expense is called."""
        answer, state = self.agent.run("I spent ₹500 on food.", verbose=False)
        self.assertTrue(state.is_finished)
        self.assertGreater(len(state.steps), 0)
        # Verify tool was called
        tool_calls = [s.action for s in state.steps if s.action]
        self.assertTrue(any(tc.get("tool") == "add_expense" for tc in tool_calls))
        self.assertEqual(self.memory.get_total_for_category("food"), 500.0)

    def test_rubric_test_2_and_3_memory_persistence(self):
        """Test 2 & 3: Sequential expenses and cross-turn memory query."""
        # Turn 1
        self.agent.run("I spent ₹500 on food.", verbose=False)
        self.assertEqual(len(self.memory.expenses), 1)

        # Turn 2 (in SAME session)
        self.agent.run("I spent ₹300 on food.", verbose=False)
        self.assertEqual(len(self.memory.expenses), 2)

        # Turn 3: Ask total spent on food
        answer, state = self.agent.run("How much have I spent on food?", verbose=False)
        self.assertTrue(state.is_finished)
        self.assertIn("800", answer)
        self.assertEqual(self.memory.get_total_for_category("food"), 800.0)

    def test_rubric_test_4_travel_expense(self):
        """Test 4: 'I spent ₹1000 on travel.' -> travel = ₹1000."""
        answer, state = self.agent.run("I spent ₹1000 on travel.", verbose=False)
        self.assertEqual(self.memory.get_total_for_category("travel"), 1000.0)
        self.assertIn("travel", answer.lower())

    def test_rubric_test_5_multi_step_affordability(self):
        """Test 5: Complex multi-step affordability calculation.
        'Can I afford a ₹2000 trip if I have ₹5000 and already spent ₹800?'
        Expected: 5000 - 800 - 2000 = 2200 remaining, affordable!
        """
        # Pre-seed memory with 800 food expense
        add_expense(self.memory, "food", 800)

        query = "Can I afford a ₹2000 trip if I have ₹5000 and already spent ₹800?"
        answer, state = self.agent.run(query, verbose=False)

        self.assertTrue(state.is_finished)
        self.assertGreater(len(state.steps), 1)  # Multi-step execution
        self.assertIn("yes", answer.lower())
        self.assertIn("2200", answer)

    def test_rubric_test_6_negative_expense_failure_handling(self):
        """Test 6: 'I spent -₹500 on food.' -> Tool rejects it, agent handles failure gracefully."""
        answer, state = self.agent.run("I spent -₹500 on food.", verbose=False)
        self.assertTrue(state.is_finished)
        self.assertEqual(len(self.memory.expenses), 0)  # No invalid expense saved
        self.assertIn("could not record", answer.lower())
        self.assertIn("greater than zero", answer.lower())


if __name__ == "__main__":
    unittest.main()
