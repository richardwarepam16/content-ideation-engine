import streamlit as st
import websocket
import json
import threading
import time
import queue # Import the queue module
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Content Ideation Engine",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Backend API Configuration ---
WS_BACKEND_URL = "ws://localhost:8000/ws/ideate"

# --- Helper Functions and Mappings ---
# Corrected AGENT_NAMES_MAP maps short name to display name
AGENT_NAMES_MAP = {
    "researcher": "Trend Researcher",
    "analyst": "Audience Analyst",
    "writer": "Creative Writer"
}

AGENT_ICONS = {
    "researcher": "🔬",
    "analyst": "👥",
    "writer": "✍️"
}

CONTENT_FORMAT_ICONS = {
    "blog": "📝",
    "video": "🎥",
    "social": "📱"
}

# --- Session State Initialization ---
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False
if 'active_agent' not in st.session_state:
    st.session_state.active_agent = None
if 'agent_states' not in st.session_state:
    st.session_state.agent_states = {
        "researcher": "pending", "analyst": "pending", "writer": "pending"
    }
if 'ideation_result' not in st.session_state:
    st.session_state.ideation_result = None
if 'websocket_error' not in st.session_state:
    st.session_state.websocket_error = None
if 'stop_websocket_thread_event' not in st.session_state:
    st.session_state.stop_websocket_thread_event = threading.Event()
if 'messages_queue' not in st.session_state:
    st.session_state.messages_queue = queue.Queue()
if 'websocket_thread' not in st.session_state:
    st.session_state.websocket_thread = None

def get_agent_state_color(state):
    # Returns text color for markdown
    colors = {
        "pending": "grey",
        "running": "blue",
        "completed": "green",
        "error": "red"
    }
    return colors.get(state, "grey")

def listen_to_websocket(payload, messages_queue: queue.Queue, stop_event: threading.Event):
    try:
        ws = websocket.create_connection(WS_BACKEND_URL)
        messages_queue.put({"type": "status", "content": "WebSocket connected."})
        ws.send(json.dumps(payload))

        while not stop_event.is_set():
            message = ws.recv()
            data = json.loads(message)
            messages_queue.put(data) # Put all messages into the queue

    except websocket._exceptions.WebSocketConnectionClosedException:
        if not stop_event.is_set():
            messages_queue.put({"type": "error", "payload": "WebSocket connection closed unexpectedly."})
    except Exception as e:
        messages_queue.put({"type": "error", "payload": f"WebSocket error: {e}"})
    finally:
        if 'ws' in locals() and ws.connected:
            ws.close()
        stop_event.set() # Ensure stop event is set on thread exit
        messages_queue.put({"type": "status", "content": "WebSocket thread stopped."})


# --- Streamlit UI ---
st.title("✨ Content Ideation Engine")


st.sidebar.header("Configuration")

with st.sidebar.form("ideation_form"):
    industry = st.text_input("Industry/Niche", value=st.session_state.get('industry', ''), placeholder="e.g., Technology, Marketing, Finance")
    target_audience = st.text_input("Target Audience", value=st.session_state.get('target_audience', ''), placeholder="e.g., B2B Founders, Content Creators")
    
    st.markdown("Content Formats:")
    col1, col2, col3 = st.columns(3)
    with col1:
        blog_checked = st.checkbox("Blog Posts", value=st.session_state.get('blog_checked', True))
    with col2:
        video_checked = st.checkbox("Video Content", value=st.session_state.get('video_checked', True))
    with col3:
        social_checked = st.checkbox("Social Media", value=st.session_state.get('social_checked', True))
    
    content_types = []
    if blog_checked: content_types.append("blog")
    if video_checked: content_types.append("video")
    if social_checked: content_types.append("social")

    # Store form values in session state to persist
    st.session_state.industry = industry
    st.session_state.target_audience = target_audience
    st.session_state.blog_checked = blog_checked
    st.session_state.video_checked = video_checked
    st.session_state.social_checked = social_checked

    submitted = st.form_submit_button("Generate Ideas", disabled=st.session_state.is_processing)

    if submitted:
        if not industry or not target_audience or not content_types:
            st.warning("Please fill in all required fields and select at least one content type.")
        else:
            # Reset states for a new run
            st.session_state.is_processing = True
            st.session_state.active_agent = None
            st.session_state.agent_states = {
                "researcher": "pending", "analyst": "pending", "writer": "pending"
            }
            st.session_state.ideation_result = None
            st.session_state.websocket_error = None
            st.session_state.stop_websocket_thread_event.clear() # Clear event for new thread
            st.session_state.messages_queue = queue.Queue() # Clear queue for new run

            payload = {
                "industry": industry,
                "target_audience": target_audience,
                "content_types": content_types,
                "additional_context": ""
            }
            
            # Start WebSocket listener in a separate thread
            st.session_state.websocket_thread = threading.Thread(
                target=listen_to_websocket, 
                args=(payload, st.session_state.messages_queue, st.session_state.stop_websocket_thread_event,)
            )
            st.session_state.websocket_thread.start()
            st.rerun() # Force rerun to show spinner and initial states

# --- Process messages from the queue in the main thread ---
if st.session_state.is_processing:
    # Process one message from the queue per rerun to show updates more granularly
    if not st.session_state.messages_queue.empty():
        message = st.session_state.messages_queue.get()
        
        if message["type"] == "agent_update":
            agent_short_name = message["payload"]["agent_name"] # This should be "researcher", "analyst", etc.
            if agent_short_name:
                # Mark previous active agent as completed, and current as running
                for agent_key in st.session_state.agent_states:
                    if st.session_state.agent_states[agent_key] == "running":
                        st.session_state.agent_states[agent_key] = "completed"
                st.session_state.agent_states[agent_short_name] = "running"
                st.session_state.active_agent = agent_short_name # Update active agent
        elif message["type"] == "final_result":
            st.session_state.ideation_result = message["payload"]
            st.session_state.is_processing = False
            st.session_state.active_agent = None
            for agent_key in st.session_state.agent_states:
                if st.session_state.agent_states[agent_key] == "running":
                    st.session_state.agent_states[agent_key] = "completed"
            st.session_state.stop_websocket_thread_event.set()
        elif message["type"] == "error":
            st.session_state.websocket_error = message["payload"]
            st.session_state.is_processing = False
            st.session_state.active_agent = None
            for agent_key in st.session_state.agent_states:
                if st.session_state.agent_states[agent_key] == "running":
                    st.session_state.agent_states[agent_key] = "error"
            st.session_state.stop_websocket_thread_event.set()
        
        st.rerun() # Rerun immediately after processing a message

    # Check if the thread has finished (e.g., due to an internal error or completion)
    if st.session_state.websocket_thread and not st.session_state.websocket_thread.is_alive():
        if st.session_state.is_processing: # Only if still marked as processing
            st.session_state.is_processing = False 
            st.session_state.websocket_error = st.session_state.get('websocket_error') or "Processing stopped unexpectedly."
            st.rerun()


st.markdown("---")

# --- Main Content Area ---
st.header("Agent Execution Flow")

# Display current agent status
cols = st.columns(len(AGENT_NAMES_MAP))
for i, (agent_short_name, agent_display_name) in enumerate(AGENT_NAMES_MAP.items()):
    current_state = st.session_state.agent_states.get(agent_short_name, "pending")
    with cols[i]:
        st.markdown(
            f"##### {AGENT_ICONS.get(agent_short_name, 'ℹ️')} {agent_display_name}", 
            help=f"Status: {current_state.capitalize()}"
        )
        # Use st.progress for visual indication
        progress_value = 0
        if current_state == "running":
            progress_value = 50
        elif current_state == "completed":
            progress_value = 100
        st.progress(progress_value, text=current_state.capitalize())

if st.session_state.is_processing:
    # Display active agent name using the mapping
    active_agent_display_name = AGENT_NAMES_MAP.get(st.session_state.active_agent, 'Starting...')
    st.info(f"Currently processing: **{active_agent_display_name}**")
    # Add a stop button to terminate processing
    if st.button("Stop Processing"):
        st.session_state.stop_websocket_thread_event.set()
        st.session_state.is_processing = False
        st.session_state.active_agent = None
        st.session_state.websocket_error = "Processing stopped by user."
        if st.session_state.websocket_thread and st.session_state.websocket_thread.is_alive():
             st.session_state.websocket_thread.join(timeout=1) # Wait for thread to finish
        st.rerun()

st.markdown("---")
st.header("Generated Content Ideas")

if st.session_state.websocket_error:
    st.error(f"Error: {st.session_state.websocket_error}")
elif st.session_state.ideation_result:
    result = st.session_state.ideation_result
    
    # Display Error if any
    if result.get("error"):
        st.error(f"Error during ideation: {result['error']}")
    
    # Display Content Ideas
    if result.get("ideas"):
        
        cols = st.columns(2)
        for i, idea in enumerate(result["ideas"]):
            with cols[i % 2]:
                with st.expander(f"{CONTENT_FORMAT_ICONS.get(idea.get('format', 'blog'), '📝')} {idea.get('title', 'No Title')}", expanded=True):
                    st.markdown(f"**Format:** {idea.get('format', 'N/A').capitalize()}")
                    st.markdown(f"**Description:** {idea.get('description', 'N/A')}")
                    st.markdown(f"**Structure:** {idea.get('structure', 'N/A')}")
                    st.markdown(f"**Keywords:** {', '.join(idea.get('keywords', []))}")
                    st.markdown(f"**Engagement:** {idea.get('estimated_engagement', 'N/A')}")
                    st.progress(idea.get('confidence', 0) / 100, text=f"Confidence: {idea.get('confidence', 0)}%")
                    if idea.get('trending'):
                        st.info("🔥 Trending Topic")
        
    # Display Agent Logs (if available in the final result)
    if result.get("agent_logs"):
        st.subheader("Full Agent Execution Log (from final result)")
        for log_entry in result["agent_logs"]:
            # Corrected: AGENT_NAMES_MAP maps short_name to display_name
            agent_short_name_from_log = log_entry['agent_name'] # This should be the short name e.g., "researcher"
            agent_display_name_from_log = AGENT_NAMES_MAP.get(agent_short_name_from_log, agent_short_name_from_log)
            
            timestamp = datetime.fromtimestamp(log_entry['timestamp']).strftime('%H:%M:%S')
            st.markdown(f"**{timestamp} - {AGENT_ICONS.get(agent_short_name_from_log, 'ℹ️')} {agent_display_name_from_log}:** {log_entry['content']}")

    # Display Metadata
    if result.get("metadata"):
        st.subheader("Workflow Metadata")
        metadata_col1, metadata_col2, metadata_col3 = st.columns(3)
        with metadata_col1:
            st.metric("Trends Found", result["metadata"].get("trends_count", 0))
        with metadata_col2:
            st.metric("Personas Identified", len(result["metadata"].get("personas", [])))
        with metadata_col3:
            st.metric("A2A Messages", result["metadata"].get("a2a_messages", 0))
else:
    st.info("Submit your configuration in the sidebar to generate content ideas!")

st.markdown("---")

st.header("System Architecture")
st.info("""
This application leverages a multi-agent system orchestrated by LangGraph. 
It uses an a2a (agent-to-agent) communication protocol, where specialized AI agents 
(Trend Researcher, Audience Analyst, Creative Writer) collaborate to generate content ideas.
Each agent is powered by an LLM (e.g., Claude API via Azure OpenAI Service for the Python backend).
""")