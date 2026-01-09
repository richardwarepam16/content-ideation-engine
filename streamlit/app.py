import streamlit as st
import json
import asyncio
import websockets
import queue

# --- Page Configuration ---
st.set_page_config(
    page_title="Content Ideation Engine",
    page_icon="✨",
    layout="wide",
)

# --- WebSocket Configuration ---
import os

WEBSOCKET_URL = os.getenv("WEBSOCKET_URL", "ws://localhost:8000/ws/ideate")

# --- Agent Information ---
agent_names = {
    "researcher": "Trend Researcher",
    "analyst": "Audience Analyst",
    "writer": "Creative Writer"
}
# Reverse mapping for agent names to IDs
agent_ids = {v: k for k, v in agent_names.items()}

# --- Session State Initialization ---
if 'running' not in st.session_state:
    st.session_state.running = False
if 'agent_states' not in st.session_state:
    st.session_state.agent_states = {agent: "pending" for agent in agent_names.keys()}
if 'final_result' not in st.session_state:
    st.session_state.final_result = None
if 'error' not in st.session_state:
    st.session_state.error = None
if 'message_queue' not in st.session_state:
    st.session_state.message_queue = queue.Queue()


# --- UI Layout ---
# Header
st.title("✨ Content Ideation Engine")
st.caption("Powered by LangGraph, a2a Protocol, and multiple specialized AI agents.")

# Main content area
col1, col2 = st.columns([1, 2], gap="large")

with col1:
    st.subheader("Configuration")
    
    with st.form("ideation_form"):
        industry = st.text_input(
            "Industry/Niche", 
            placeholder="e.g., Technology, Marketing, Finance",
            disabled=st.session_state.running
        )
        target_audience = st.text_input(
            "Target Audience", 
            placeholder="e.g., B2B Founders, Content Creators",
            disabled=st.session_state.running
        )
        st.write("Content Formats")
        content_types_selection = {
            "Blog Post": st.checkbox("Blog Post", value=True, disabled=st.session_state.running),
            "Video Script": st.checkbox("Video Script", value=True, disabled=st.session_state.running),
            "Social Media Campaign": st.checkbox("Social Media Campaign", value=True, disabled=st.session_state.running)
        }

        submit_button = st.form_submit_button(
            "🚀 Generate Ideas", 
            use_container_width=True, 
            disabled=st.session_state.running
        )

    st.subheader("Agent Pipeline")
    agent_status_placeholders = {agent: st.empty() for agent in agent_names.keys()}

with col2:
    st.subheader("Results")
    results_placeholder = st.empty()

# --- UI Update Function ---
def update_ui():
    """Rerenders the agent status and results based on session state."""
    for agent_id, name in agent_names.items():
        state = st.session_state.agent_states.get(agent_id, "pending")
        
        if state == "running":
            icon = "⏳"
        elif state == "complete":
            icon = "✅"
        elif state == "error":
            icon = "❌"
        else: # pending
            icon = "⚪"
            
        # Using st.status for a cleaner, collapsable view
        with agent_status_placeholders[agent_id].status(f"**{name}** {icon}", state=state if state != 'pending' else 'running'):
            if state == "running":
                st.write("In progress...")
            elif state == "complete":
                st.write("Complete.")
            elif state == "error":
                st.write("An error occurred.")
            elif state == "pending":
                st.write("Waiting to start...")


    with results_placeholder.container():
        if st.session_state.error:
            st.error(f"An error occurred: {st.session_state.error}")
        
        if st.session_state.final_result:
            st.success("Ideation process completed!")
            ideas = st.session_state.final_result.get("ideas", [])
            st.write(f"Generated **{len(ideas)}** content ideas:")
            
            for i, idea in enumerate(ideas):
                with st.expander(f"**{idea.get('title', 'Untitled Idea')}** - {idea.get('format', 'N/A')}", expanded=i==0):
                    st.markdown(f"**Description:** {idea.get('description', 'No description provided.')}")
                    st.markdown(f"**Structure:** {idea.get('structure', 'Not specified.')}")
                    
                    keywords = idea.get('keywords', [])
                    if keywords:
                        st.write("**Keywords:**")
                        st.write(", ".join([f"`{kw}`" for kw in keywords]))

                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Confidence Score", f"{idea.get('confidence', 0)}%")
                    with col2:
                        trending_status = "🔥 Yes" if idea.get('trending') else "No"
                        st.metric("Trending Topic", trending_status)

        elif not st.session_state.running:
             st.info("Configure your parameters and click 'Generate Ideas' to start.")

import time
import threading
import logging
import queue # Import the queue module

# --- WebSocket Client (Now runs in a background thread) ---
def websocket_worker(request_data, message_queue: queue.Queue):
    """
    This function runs in a separate thread.
    It connects to the websocket and puts updates into a thread-safe queue.
    It does NOT call st.rerun() or directly access st.session_state.
    """
    # Configure logging for this thread. Streamlit uses its own logger, 
    # so direct logging.basicConfig might conflict. For debugging, this is okay.
    # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
    thread_logger = logging.getLogger(threading.current_thread().name)
    thread_logger.setLevel(logging.INFO)
    if not thread_logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        thread_logger.addHandler(handler)


    async def client():
        thread_logger.info("Client function started.")
        try:
            message_queue.put({'type': 'set_running_state', 'value': True})
            thread_logger.info(f"Connecting to WebSocket at {WEBSOCKET_URL}.")
            async with websockets.connect(WEBSOCKET_URL) as websocket:
                thread_logger.info("WebSocket connected successfully.")
                await websocket.send(json.dumps(request_data))
                thread_logger.info(f"Request sent: {request_data}")
                
                while True:
                    try:
                        thread_logger.info("Waiting to receive message...")
                        message_raw = await asyncio.wait_for(websocket.recv(), timeout=60.0)
                        thread_logger.info(f"Received message: {message_raw}")
                        message = json.loads(message_raw)
                        
                        msg_type = message.get("type")
                        payload = message.get("payload")

                        if msg_type == "agent_update":
                            message_queue.put({'type': 'agent_update', 'payload': payload})
                        
                        elif msg_type == "final_result":
                            message_queue.put({'type': 'final_result', 'payload': payload})
                            thread_logger.info("Final result received. Breaking loop.")
                            break

                        elif msg_type == "error":
                            message_queue.put({'type': 'set_error', 'message': payload})
                            thread_logger.error(f"Error message received: {payload}. Breaking loop.")
                            break
                        
                        elif msg_type == "status":
                            thread_logger.info(f"Status update: {payload}")


                    except asyncio.TimeoutError:
                        thread_logger.warning("Timeout waiting for message. Breaking loop.")
                        message_queue.put({'type': 'set_error', 'message': "Connection timed out. The process is taking longer than expected."})
                        break
                    except websockets.exceptions.ConnectionClosed as e:
                        thread_logger.warning(f"Connection closed by server: {e.code} {e.reason}. Breaking loop.")
                        # This conditional was relying on st.session_state, now it won't.
                        # The main thread will decide if it's an unhandled error.
                        message_queue.put({'type': 'set_error', 'message': f"Connection to server was lost: {e.reason}"})
                        break
        
        except Exception as e:
            thread_logger.error(f"An exception occurred in client function: {e}", exc_info=True)
            message_queue.put({'type': 'set_error', 'message': f"Failed to connect or communicate with WebSocket: {e}"})
        
        finally:
            thread_logger.info("Client function finished. Setting running state to False via queue.")
            message_queue.put({'type': 'set_running_state', 'value': False})

    asyncio.run(client())


# --- UI Rendering ---
update_ui()


# --- Logic for form submission ---
if submit_button and not st.session_state.get('running'):
    content_type_mapping = {
        "Blog Post": "blog",
        "Video Script": "video",
        "Social Media Campaign": "social"
    }
    selected_content_types = [
        content_type_mapping[ct] for ct, is_selected in content_types_selection.items() if is_selected
    ]

    if not industry or not target_audience:
        st.warning("Please fill in both Industry and Target Audience fields.")
    elif not selected_content_types:
        st.warning("Please select at least one Content Format.")
    else:
        # Reset state for a new run
        st.session_state.final_result = None
        st.session_state.error = None
        st.session_state.agent_states = {agent: "pending" for agent in agent_names.keys()}
        
        # Initialize a new queue for this run and store it in session_state
        st.session_state.message_queue = queue.Queue()
        st.session_state.running = True # Set running state early, will be confirmed by thread

        request_data = {
            "industry": industry,
            "target_audience": target_audience,
            "content_types": selected_content_types
        }
        
        # Run the websocket client in a separate thread, passing the queue
        thread = threading.Thread(target=websocket_worker, args=(request_data, st.session_state.message_queue))
        thread.start()
        
        st.rerun()

# --- Polling for UI Updates ---
if st.session_state.get('running'):
    # Process all messages currently in the queue
    while not st.session_state.message_queue.empty():
        message = st.session_state.message_queue.get()
        msg_type = message.get('type')
        
        if msg_type == 'set_running_state':
            st.session_state.running = message.get('value')
        elif msg_type == 'set_error':
            st.session_state.error = message.get('message')
        elif msg_type == 'agent_update':
            payload = message.get('payload')
            agent_name_human_readable = payload.get("agent_name")
            agent_id = agent_ids.get(agent_name_human_readable) # Use the reverse mapping
            if agent_id: # Check if mapping was successful
                for k, v in st.session_state.agent_states.items():
                    if v == "running":
                        st.session_state.agent_states[k] = "complete"
                st.session_state.agent_states[agent_id] = "running"
        elif msg_type == 'final_result':
            st.session_state.final_result = message.get('payload')
            # Also mark the last running agent as completed
            for k, v in st.session_state.agent_states.items():
                if v == "running":
                    st.session_state.agent_states[k] = "complete"


    # If the app is still running, wait a second before the next poll.
    # If the app just finished, this sleep is skipped, but the rerun still happens.
    if st.session_state.get('running'):
        time.sleep(1)

    # Rerun to show the latest updates from the queue.
    # If running was set to False, this will be the final rerun.
    st.rerun()
