# Personal Budget Assistant — Agentic AI

The **Personal Budget Assistant** is an agentic AI system designed to help students track daily expenses, monitor category-wise spending, and answer complex financial planning questions (such as whether an upcoming trip or purchase is affordable). Unlike standard text-only chatbots, it operates using an explicit **PLAN → ACT → OBSERVE → DECIDE** execution loop, enabling multi-step reasoning where tool observations dynamically drive subsequent agent decisions.

The system utilizes two real Python tools: `add_expense(item, amount)` for recording verified costs into memory, and `get_summary(category)` for retrieving aggregated spending totals for a given category or all categories. Its persistent structured memory (`AgentMemory`) stores individual expense records alongside multi-turn conversation history within a session. This enables the agent to remember earlier financial entries (e.g., adding ₹500 and ₹300 sequentially on food) and query them across subsequent conversational turns to accurately answer user inquiries with up-to-date figures.

During development, an honest failure occurred when users entered negative expense amounts or formatted currency strings like `-₹500 on food`: initial naive parsing caused regex pattern mismatch and bypassed validation, while LLM function-calling occasionally passed string numbers that caused runtime arithmetic errors. To resolve this, strict schema validation and numeric sanitization were implemented inside `add_expense` and the agent reasoner, ensuring that non-numeric, zero, or negative expenses are rejected gracefully with informative error messages without corrupting memory or crashing the loop.

---

## How to Run the Project

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)
Copy `.env.example` to `.env` and provide your Groq API key, GitHub Personal Access Token, or OpenAI key (or leave empty to run in 100% offline deterministic mode):
```bash
cp .env.example .env
```

### 3. Run Automated Tests
```bash
python -m unittest discover -s tests -v
```

### 4. Run Streamlit Web Application (Interactive UI)
```bash
streamlit run app.py
```

### 5. Run Interactive CLI Agent or Demo
```bash
python main.py          # Interactive terminal chat
python main.py --demo   # Automated multi-step trace demo
```

### 6. Run the Jupyter Notebook Demo
```bash
jupyter notebook notebooks/personal_budget_agent_demo.ipynb
```

---

## Deploying on Streamlit Community Cloud (Free)

1. Push your repository to **GitHub**.
2. Go to [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
3. Click **"New app"**.
4. Select your repository, branch (`main`), and set **Main file path** to:
   ```text
   app.py
   ```
5. *(Optional)* Click **Advanced settings** -> **Secrets** and add your LLM API token:
   ```toml
   GROQ_API_KEY = "gsk_your_groq_api_key_here"
   # OR
   GITHUB_TOKEN = "your_github_token_here"
   # OR
   OPENAI_API_KEY = "your_openai_api_key_here"
   ```
6. Click **Deploy!** Your agent will be live with a shareable URL.
