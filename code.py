import streamlit as st
import time
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import os
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI

# Set up environment (replace with your actual Gemini API key)
api_key = os.environ.get("GOOGLE_API_KEY", "your_api_key")
if api_key:
    genai.configure(api_key=api_key)
    # Initialize Gemini model - using direct API to avoid compatibility issues
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.7, convert_system_message_to_human=True)
else:
    llm = None

# Define agent states
class AgentState(TypedDict):
    code: str
    messages: Annotated[Sequence[BaseMessage], lambda a, b: a + b]
    iteration: int
    max_iterations: int

# Create agent functions using direct Gemini API calls
def call_gemini(prompt: str) -> str:
    """Call Gemini API directly to avoid compatibility issues"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"

def code_parser_agent(state: AgentState):
    prompt = f"""You are a senior Python code parser. Analyze the structure of this code:

{state['code']}

Provide a concise analysis of the code structure, including:
- Functions defined
- Classes defined
- Loops and conditionals
- Import statements
- Overall code organization"""
    response = call_gemini(prompt)
    return {"messages": [AIMessage(content=response)]}

def bug_detection_agent(state: AgentState):
    last_message = state['messages'][-1].content
    prompt = f"""You are an expert bug hunter. Find potential errors in this code:

{state['code']}

Previous analysis:
{last_message}

Identify potential bugs including:
- Syntax errors
- Runtime errors
- Logical errors
- Potential exceptions
- Type mismatches
- Variable scope issues"""
    response = call_gemini(prompt)
    return {"messages": [AIMessage(content=response)]}

def bug_explainer_agent(state: AgentState):
    last_message = state['messages'][-1].content
    prompt = f"""Explain the bug in simple terms for a junior developer:

{last_message}

Provide:
- Simple explanation of the error
- Why it occurs
- When it might occur
- Real-world analogy to help understanding"""
    response = call_gemini(prompt)
    return {"messages": [AIMessage(content=response)]}

def socratic_guide_agent(state: AgentState):
    last_message = state['messages'][-1].content
    prompt = f"""Ask a Socratic question to help the user understand the root cause:

{last_message}

Formulate a question that:
- Encourages critical thinking
- Helps user discover the solution themselves
- Relates to programming concepts
- Is open-ended and thought-provoking"""
    response = call_gemini(prompt)
    return {"messages": [AIMessage(content=response)]}

def refiner_agent(state: AgentState):
    last_message = state['messages'][-1].content
    prompt = f"""Provide a specific hint to fix the bug without giving the full solution:

{last_message}

Offer:
- A clear but partial hint
- Direction to resources
- Similar examples
- Pseudo-code suggestion
- But NOT the complete solution"""
    response = call_gemini(prompt)
    return {"messages": [AIMessage(content=response)]}

def planner_agent(state: AgentState):
    new_iteration = state["iteration"] + 1
    if new_iteration >= state["max_iterations"]:
        content = "🔁 Maximum debugging cycles reached. Analysis complete."
    else:
        content = "🔄 Planning next debugging cycle..."
    return {"messages": [HumanMessage(content=content)], "iteration": new_iteration}

# Build LangGraph workflow
def create_workflow():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("code_parser", code_parser_agent)
    workflow.add_node("bug_detector", bug_detection_agent)
    workflow.add_node("bug_explainer", bug_explainer_agent)
    workflow.add_node("socratic_guide", socratic_guide_agent)
    workflow.add_node("refiner", refiner_agent)
    workflow.add_node("planner", planner_agent)
    
    # Set entry point
    workflow.set_entry_point("code_parser")
    
    # Define edges
    workflow.add_edge("code_parser", "bug_detector")
    workflow.add_edge("bug_detector", "bug_explainer")
    workflow.add_edge("bug_explainer", "socratic_guide")
    workflow.add_edge("socratic_guide", "refiner")
    workflow.add_edge("refiner", "planner")
    
    # Conditional edges
    def should_continue(state):
        if state["iteration"] >= state["max_iterations"]:
            return END
        return "code_parser"
    
    workflow.add_conditional_edges(
        "planner",
        should_continue,
        {
            "code_parser": "code_parser",
            END: END
        }
    )
    
    return workflow.compile()

# Streamlit UI
st.set_page_config(
    page_title="🤖 Level 5 Code Debugger", 
    layout="wide",
    page_icon="🤖"
)

# Custom CSS for styling
st.markdown("""
<style>
    :root {
        --primary: #25D366;
        --secondary: #128C7E;
        --dark: #0E1117;
        --darker: #090B10;
        --light: #1E1E2E;
        --lighter: #2D2D3A;
        --text: #F0F0F0;
    }
    
    .stApp {
        background-color: var(--dark);
        color: var(--text);
    }
    
    .stTextArea textarea {
        background-color: var(--light) !important;
        color: var(--text) !important;
        border: 1px solid var(--lighter);
    }
    
    .stButton>button {
        background-color: var(--primary) !important;
        color: white !important;
        font-weight: bold !important;
        border: none;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        background-color: var(--secondary) !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .stChatMessage {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        background-color: var(--light);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border-left: 4px solid;
    }
    
    .agent-title {
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .code-block {
        background-color: var(--lighter);
        padding: 12px;
        border-radius: 8px;
        margin: 12px 0;
        font-family: 'Fira Code', monospace;
        font-size: 0.9rem;
        overflow-x: auto;
    }
    
    .iteration-badge {
        background-color: var(--secondary);
        color: white;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8rem;
        margin-left: 10px;
    }
    
    .status-bar {
        padding: 10px 15px;
        border-radius: 8px;
        margin: 15px 0;
        font-weight: bold;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .success {
        background-color: rgba(37, 211, 102, 0.2);
        border: 1px solid var(--primary);
    }
    
    .warning {
        background-color: rgba(255, 165, 0, 0.2);
        border: 1px solid #FFA500;
    }
    
    .sidebar-section {
        padding: 15px;
        background-color: var(--light);
        border-radius: 10px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Agent icons and colors
AGENT_CONFIG = {
    "code_parser": {"icon": "🧩", "color": "#FFD700", "title": "Code Parser"},
    "bug_detector": {"icon": "🐛", "color": "#FF6347", "title": "Bug Detector"},
    "bug_explainer": {"icon": "📚", "color": "#1E90FF", "title": "Bug Explainer"},
    "socratic_guide": {"icon": "🧠", "color": "#9370DB", "title": "Socratic Guide"},
    "refiner": {"icon": "✨", "color": "#32CD32", "title": "Refiner"},
    "planner": {"icon": "📋", "color": "#FFA500", "title": "Planner"},
    "system": {"icon": "🤖", "color": "#808080", "title": "System"}
}

# Main app
def main():
    st.title("🤖 Level 5 Agentic Code Debugger")
    st.caption("Powered by Google Gemini, LangChain & LangGraph - Advanced AI Code Analysis")
    
    # Initialize session state
    if 'session_history' not in st.session_state:
        st.session_state.session_history = []
    if 'current_session' not in st.session_state:
        st.session_state.current_session = {"code": "", "messages": []}
    if 'max_iterations' not in st.session_state:
        st.session_state.max_iterations = 3
    if 'iteration_count' not in st.session_state:
        st.session_state.iteration_count = 0
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key_input = st.text_input("🔑 Google Gemini API Key", 
                                     value=os.environ.get("GOOGLE_API_KEY", ""), 
                                     type="password",
                                     help="Enter your Google Gemini API key")
        if api_key_input and api_key_input != os.environ.get("GOOGLE_API_KEY", ""):
            os.environ["GOOGLE_API_KEY"] = api_key_input
            genai.configure(api_key=api_key_input)
            st.success("✅ API key updated!")
        
        st.session_state.max_iterations = st.slider("Max Debugging Cycles", 1, 5, 3)
        st.divider()
        
        st.header("🧠 Agent Workflow")
        with st.expander("View Agent Details"):
            st.markdown("""
            ### 🧩 Code Parser
            - Structural analysis
            - Code organization
            - Function/class identification
            
            ### 🐛 Bug Detector
            - Error identification
            - Potential issues
            - Code smells
            
            ### 📚 Bug Explainer
            - Simplified explanations
            - Root cause analysis
            - Impact assessment
            
            ### 🧠 Socratic Guide
            - Thought-provoking questions
            - Learning facilitation
            - Concept reinforcement
            
            ### ✨ Refiner
            - Solution hints
            - Best practices
            - Partial solutions
            
            ### 📋 Planner
            - Iteration control
            - Workflow management
            - Termination decision
            """)
        
        st.divider()
        
        st.header("💾 Session History")
        if st.session_state.session_history:
            for i, session in enumerate(st.session_state.session_history):
                if st.button(f"Session {i+1}: {session['code'][:30]}...", key=f"session_{i}"):
                    st.session_state.current_session = session.copy()
                    st.rerun()
        else:
            st.info("No session history yet")
            
        st.divider()
        st.info("""
        **Instructions:**
        1. Paste Python code
        2. Click 'Debug Code'
        3. Watch agents analyze your code
        4. Review suggestions
        5. Iterate as needed
        """)
    
    # Chat display function
    def display_message(agent, content, iteration=None):
        config = AGENT_CONFIG.get(agent, AGENT_CONFIG["system"])
        with st.chat_message(name=agent, avatar=config["icon"]):
            title = f"{config['icon']} {config['title']}"
            if iteration is not None:
                title += f" <span class='iteration-badge'>Cycle {iteration}</span>"
            st.markdown(f"<div class='agent-title' style='color:{config['color']}'>{title}</div>", 
                        unsafe_allow_html=True)
            st.markdown(content)
    
    # Main content
    col1, col2 = st.columns([3, 2])
    
    with col1:
        with st.form("code_debugger"):
            code = st.text_area("**Paste Python Code:**", height=300,
                                placeholder="def calculate():\n    total = 0\n    for i in range(10):\n        total += i\n    return total / len(numbers)",
                                value=st.session_state.current_session["code"])
            submitted = st.form_submit_button("🚀 Debug Code", use_container_width=True)
    
    with col2:
        st.subheader("🧪 Sample Code")
        sample_col1, sample_col2 = st.columns(2)
        with sample_col1:
            if st.button("Division Error", use_container_width=True):
                st.session_state.current_session["code"] = """def divide_numbers(a, b):
    return a / b

result = divide_numbers(10, 0)"""
                st.rerun()
                
            if st.button("Type Error", use_container_width=True):
                st.session_state.current_session["code"] = """def get_max(numbers):
    max_num = numbers[0]
    for num in numbers:
        if num > max_num:
            max_num = num
    return max_num

print(get_max([5, 2, 8, '10', 3]))"""
                st.rerun()
                
        with sample_col2:
            if st.button("Variable Error", use_container_width=True):
                st.session_state.current_session["code"] = """def calculate_sum(a, b):
    result = a + b
    return res

print(calculate_sum(5, 10))"""
                st.rerun()
                
            if st.button("Scope Error", use_container_width=True):
                st.session_state.current_session["code"] = """def process_data():
    data = [1, 2, 3]
    for item in data:
        result = item * 2
    return result

print(process_data())"""
                st.rerun()
    
    # Display current code if available
    if st.session_state.current_session["code"]:
        with col1:
            st.code(st.session_state.current_session["code"], language="python")
    
    # Handle form submission
    if submitted and st.session_state.current_session["code"].strip():
        # Check if API key is set
        if not os.environ.get("GOOGLE_API_KEY"):
            st.error("⚠️ Please enter your Google Gemini API key in the sidebar first!")
            st.stop()
        # Save to session history
        if st.session_state.current_session not in st.session_state.session_history:
            st.session_state.session_history.append(st.session_state.current_session.copy())
        
        # Initialize agent state
        initial_state = AgentState(
            code=st.session_state.current_session["code"],
            messages=[],
            iteration=0,
            max_iterations=st.session_state.max_iterations
        )
        
        # Create chat container
        chat_container = st.container()
        
        # Initialize workflow
        agentic_workflow = create_workflow()
        
        # Display initial message
        with chat_container:
            display_message("system", "🚀 Starting Level 5 Agentic Debugging System...")
            time.sleep(0.5)
            display_message("system", f"🔁 Max Debugging Cycles: {st.session_state.max_iterations}")
        
        # Run the agentic workflow
        current_iteration = 0
        try:
            for output in agentic_workflow.stream(initial_state):
                for node, data in output.items():
                    if node != "__end__":
                        with chat_container:
                            # Get last message content
                            messages = data.get("messages", [])
                            if messages:
                                last_message = messages[-1].content
                                
                                # Track current iteration
                                if node == "planner":
                                    current_iteration = data.get("iteration", 0)
                                    st.session_state.iteration_count = current_iteration
                                
                                display_message(node, last_message, current_iteration)
                                time.sleep(0.7)  # Simulate processing time
        except Exception as e:
            with chat_container:
                st.error(f"Error in workflow execution: {str(e)}")
                st.info("Please check your API key and try again.")
        
        # Save session state
        st.session_state.current_session["messages"] = initial_state["messages"]
        st.session_state.session_history = [s for s in st.session_state.session_history 
                                          if s["code"] != st.session_state.current_session["code"]]
        st.session_state.session_history.append(st.session_state.current_session.copy())
        
        # Final status
        with chat_container:
            st.divider()
            if current_iteration >= st.session_state.max_iterations:
                st.markdown("<div class='status-bar warning'>⚠️ Maximum debugging cycles completed. All issues analyzed.</div>", 
                           unsafe_allow_html=True)
            else:
                st.markdown("<div class='status-bar success'>✅ Debugging completed successfully!</div>", 
                           unsafe_allow_html=True)
            
            st.subheader("📝 Final Recommendations")
            st.markdown("""
            - Review the agent suggestions above
            - Implement the recommended fixes
            - Test your code with different inputs
            - Consider edge cases mentioned by the agents
            - Refactor based on best practices suggested
            """)
            
            # Add to session history
            st.session_state.session_history.append({
                "code": st.session_state.current_session["code"],
                "messages": st.session_state.current_session["messages"]
            })
            
            st.divider()
            st.markdown(f"**🔁 Debugging Cycles Completed:** {current_iteration}")
            st.markdown(f"**🧠 Agents Involved:** {len(AGENT_CONFIG) - 1}")
            st.markdown(f"**📚 Total Recommendations:** {len(st.session_state.current_session['messages'])}")

if __name__ == "__main__":
    main()
