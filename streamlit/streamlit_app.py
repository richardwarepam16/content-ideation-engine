import streamlit as st
import requests  
import json
import time 

from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Content Ideation Engine",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Backend API Configuration ---
BACKEND_URL = "http://localhost:8000/api/ideate" 

# --- Helper Functions and Mappings ---
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
if 'agent_states' not in st.session_state: 
    st.session_state.agent_states = {
        "researcher": "pending", "analyst": "pending", "writer": "pending"
    }
if 'ideation_result_full' not in st.session_state: 
    st.session_state.ideation_result_full = None
if 'backend_error' not in st.session_state: 
    st.session_state.backend_error = None

# New state variables for controlled visual playback
if 'playback_active' not in st.session_state:
    st.session_state.playback_active = False
if 'glow_up_agents' not in st.session_state:
    st.session_state.glow_up_agents = ["researcher", "analyst", "writer"] # Hardcoded sequence
if 'glow_up_index' not in st.session_state:
    st.session_state.glow_up_index = 0


def get_agent_state_color(state):
    colors = {
        "pending": "grey",
        "running": "blue",
        "completed": "green",
        "error": "red"
    }
    return colors.get(state, "grey")

def send_ideation_request(industry, target_audience, content_types, additional_context=""):
    payload = {
        "industry": industry,
        "target_audience": target_audience,
        "content_types": content_types,
        "additional_context": additional_context
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(BACKEND_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error(f"Could not connect to the backend server. Please ensure the backend is running at {BACKEND_URL}")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error occurred: {e}. Response: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        return None

# --- Streamlit UI ---
st.title("✨ Content Ideation Engine")
st.markdown("---")

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
            st.session_state.is_processing = True
            st.session_state.agent_states = { # Reset all to pending initially
                "researcher": "pending", "analyst": "pending", "writer": "pending"
            }
            st.session_state.ideation_result_full = None
            st.session_state.backend_error = None 
            st.session_state.playback_active = False # Deactivate any ongoing playback
            st.session_state.glow_up_index = 0 # Reset playback index
            
            st.rerun() # Show pending state and spinner before backend call

            # --- Blocking Backend Call ---
            with st.spinner("Generating ideas... Please wait for the backend to complete the workflow."):
                full_response = send_ideation_request(industry, target_audience, content_types)
                if full_response:
                    st.session_state['ideation_result_full'] = full_response
                    if full_response.get("error"):
                        st.session_state.backend_error = full_response["error"]
                else:
                    st.session_state.backend_error = "Failed to get response from backend."
            
            st.session_state.is_processing = False # Backend call finished

            # --- Trigger visual-only sequential glow-up after backend response ---
            if not st.session_state.backend_error:
                st.session_state.playback_active = True # Activate playback
                st.rerun() # Trigger the first step of the visual animation
            else: # If there was a backend error
                 for agent_key in st.session_state.agent_states:
                    if st.session_state.agent_states[agent_key] == "pending":
                        st.session_state.agent_states[agent_key] = "error"
                 st.rerun() # Show error state in sidebar


# --- Agent Flow Display (in sidebar) ---
st.sidebar.markdown("---")
st.sidebar.header("Agent Execution Flow")

for agent_short_name, agent_display_name in AGENT_NAMES_MAP.items():
    current_state = st.session_state.agent_states.get(agent_short_name, "pending")
    st.sidebar.markdown(
        f"##### {AGENT_ICONS.get(agent_short_name, 'ℹ️')} {agent_display_name}"
    )
    if current_state == "completed":
        st.sidebar.success(f"✓ {current_state.capitalize()}")
    elif current_state == "running":
        st.sidebar.info(f"▶️ {current_state.capitalize()}...")
    elif current_state == "error":
        st.sidebar.error(f"❌ {current_state.capitalize()}!")
    else:
        st.sidebar.empty() 


# --- Controlled Playback Logic across reruns (Top-level, after all UI elements) ---
# This block manages the visual sequential glow-up animation
if st.session_state.get('playback_active', False) and not st.session_state.is_processing:
    # Ensure all agents are marked completed at the very end
    if st.session_state.glow_up_index >= len(st.session_state.glow_up_agents):
        for agent_key in st.session_state.agent_states:
            if st.session_state.agent_states[agent_key] == "running":
                st.session_state.agent_states[agent_key] = "completed"
        st.session_state.playback_active = False # Animation finished
        st.rerun() # Final rerun to show all completed status
        
    elif st.session_state.glow_up_index < len(st.session_state.glow_up_agents):
        current_agent_key = st.session_state.glow_up_agents[st.session_state.glow_up_index]
        
        # Mark all previous running agents as completed
        for key in st.session_state.agent_states:
            if st.session_state.agent_states[key] == "running" and key != current_agent_key:
                st.session_state.agent_states[key] = "completed"

        st.session_state.agent_states[current_agent_key] = "running"
        st.rerun() # Show agent running
        time.sleep(0.8) # Artificial delay for visual effect
        
        st.session_state.agent_states[current_agent_key] = "completed"
        st.session_state.glow_up_index += 1 # Move to next agent
        st.rerun() # Show agent completed and trigger next step


st.markdown("---")

# --- Main Content Area ---
st.header("Generated Content Ideas") 

if st.session_state.backend_error:
    st.error(f"Error: {st.session_state.backend_error}")
elif st.session_state.ideation_result_full and not st.session_state.playback_active: # Display content AFTER playback is inactive
    result = st.session_state.ideation_result_full
    
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
    if not st.session_state.is_processing and not st.session_state.playback_active:
        st.info("Submit your configuration in the sidebar to generate content ideas!")

st.markdown("---")

st.header("System Architecture")
st.info("""
This application leverages a multi-agent system orchestrated by LangGraph. 
It uses an a2a (agent-to-agent) communication protocol, where specialized AI agents 
(Trend Researcher, Audience Analyst, Creative Writer) collaborate to generate content ideas.
Each agent is powered by an LLM (e.g., Claude API via Azure OpenAI Service for the Python backend).
""")