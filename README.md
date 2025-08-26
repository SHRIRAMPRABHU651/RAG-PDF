# 🤖 Level 5 Agentic Code Debugger

## Overview

This is a Streamlit-based agentic debugging application powered by **Google Gemini**, **LangChain**, and **LangGraph**. The system follows a multi-agent loop that analyzes user-submitted Python code, detects bugs, explains them, and suggests solutions iteratively using expert AI agents.

---

## 🔍 Features

* Multi-agent system built using **LangGraph**.
* Uses **Google Gemini API** (`gemini-pro`) for natural language processing.
* Elegant UI using **Streamlit** with sidebar configuration and theme customization.
* Includes **session history**, **sample code templates**, and **iteration control**.
* Iterative debugging workflow with up to 5 configurable cycles.

---

## 🧠 Agents Workflow

### 1. **Code Parser (`code_parser`)**

* Analyzes the structure of the code.
* Extracts functions, classes, imports, loops, and overall organization.

### 2. **Bug Detector (`bug_detector`)**

* Identifies potential:

  * Syntax Errors
  * Runtime Exceptions
  * Logical Bugs
  * Type Issues
  * Variable Scope Problems

### 3. **Bug Explainer (`bug_explainer`)**

* Explains the identified bug(s) in layman terms.
* Provides cause-effect breakdown.
* Offers real-world analogies.

### 4. **Socratic Guide (`socratic_guide`)**

* Encourages self-learning by asking open-ended questions.
* Promotes conceptual understanding.

### 5. **Refiner (`refiner`)**

* Offers:

  * Partial solutions
  * Code hints
  * Pseudo-code suggestions
  * Avoids giving the full solution

### 6. **Planner (`planner`)**

* Controls the agentic loop.
* Decides whether to continue or end the debugging cycle.

---

## 🔄 Agentic Workflow

The LangGraph `StateGraph` is composed with the following flow:

1. `code_parser` →
2. `bug_detector` →
3. `bug_explainer` →
4. `socratic_guide` →
5. `refiner` →
6. `planner` → \[conditional]

   * if iterations < max: go to `code_parser`
   * else: end

### 🛠️ State Management (`AgentState`)

```python
class AgentState(TypedDict):
    code: str
    messages: Annotated[Sequence[BaseMessage], lambda a, b: a + b]
    iteration: int
    max_iterations: int
```

### 🗂️ Flowchart (Design on Canva)

Design this flowchart visually on **Canva** using the following structure:

```plaintext
                +-------------------+
                |   code_parser     |
                +-------------------+
                         |
                         v
                +-------------------+
                |   bug_detector    |
                +-------------------+
                         |
                         v
                +-------------------+
                |  bug_explainer    |
                +-------------------+
                         |
                         v
                +-------------------+
                |  socratic_guide   |
                +-------------------+
                         |
                         v
                +-------------------+
                |     refiner       |
                +-------------------+
                         |
                         v
                +-------------------+
                |     planner       |
                +-------------------+
                     /        \
                    v          v
              END (✔)      code_parser (loop ↺)
```

Use color-coded boxes, directional arrows, and icons to represent agents for visual clarity.

---

## 🚀 How To Use

### 1. Set Up

* Clone or download the repository.
* Set your Google Gemini API key using the Streamlit sidebar.

### 2. Run the App

```bash
streamlit run app.py
```

### 3. Paste Python Code

* Use your own or try the built-in sample buttons.

### 4. Click "Debug Code"

* Watch agents analyze and respond in a conversational interface.

### 5. Review Recommendations

* Use the insights to fix your code.
* Iterate through cycles (up to 5).

---


## 🔐 Environment Variable

Set your API key as an environment variable:

```bash
export GOOGLE_API_KEY="your_api_key"
```

Or set it via `.env` using a tool like `python-dotenv`:

```env
GOOGLE_API_KEY=your_api_key
```

---

## 🧩 Dependencies

* `streamlit`
* `langchain`
* `langgraph`
* `google-generativeai`
* `langchain-google-genai`

---

## 📦 Folder Structure

```
📁 your_project/
├── app.py                  # Main Streamlit app
├── requirements.txt        # Python dependencies
├── README.md               # This file
```

---

## 📌 Future Improvements

* Add download/share feature for debugging reports.
* Include test case generation and code fix agent.
* Enable comparison between original and fixed code.

---

## 💡 Credits

* Built by [Shriram Prabhu J](https://www.linkedin.com/in/shriramprabhu-j-snsinstitution/) using OpenAI + Google GenAI.
* LangGraph and LangChain community for modular agent framework.

---


## 🧠 Learn More

* [LangGraph Docs](https://docs.langgraph.dev/)
* [Google Generative AI](https://ai.google.dev/)
* [Streamlit](https://streamlit.io/)

---

Happy Debugging! 🐛✨
