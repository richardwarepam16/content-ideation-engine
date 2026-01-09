# Content Ideation Engine

The Content Ideation Engine is a powerful, multi-agent system designed to generate creative and engaging content ideas. It leverages a team of AI agents, each with a specialized role, to brainstorm, research, and refine content concepts based on a given topic.

## Live Demo

You can chcek out the application here:



https://github.com/user-attachments/assets/743d7422-b09b-4768-9e09-4a5ce99421d6


*   **Multi-Agent System:** Utilizes a collaborative team of AI agents for comprehensive content ideation.
*   **Audience Analysis:** An Audience Analyst agent identifies and analyzes the target audience for the given topic.
*   **Trend Research:** A Trend Researcher agent discovers current trends and popular sub-topics related to the main theme.
*   **Creative Writing:** A Creative Writer agent brainstorms and generates a variety of content ideas, including titles, formats, and key talking points.
*   **Real-time Updates:** The application displays the agents' progress and results in real-time.
*   **Interactive UI:** A user-friendly interface to input topics and view the generated content ideas.

## Architecture

The project is built with a backend API and a Streamlit frontend.

*   **Backend:** A Python-based application using FastAPI. It orchestrates the multi-agent workflow using LangGraph, where each agent is an independent language model-powered entity. The agents communicate and pass information to each other to build upon the initial topic.

*   **Frontend:** A simple and interactive user interface built with Streamlit. It communicates with the backend via a WebSocket connection to provide real-time updates as the agents work.

## Technologies Used

**Backend:**
*   Python
*   FastAPI
*   LangGraph
*   Azure OpenAI
*   WebSockets

**Frontend:**
*   Streamlit

## Setup and Installation

### Prerequisites

*   Python 3.8+
*   An Azure OpenAI API key

### Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/content-ideation-engine.git
    cd content-ideation-engine/backend
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the `backend` directory by copying the example file:
    ```bash
    cp .env.example .env
    ```
    Open the `.env` file and add your Azure OpenAI API key and other required credentials.

5.  **Run the backend server:**
    ```bash
    uvicorn main:app --reload
    ```
    The backend will be running at `http://localhost:8000`.

### Streamlit Setup

1.  **Navigate to the streamlit directory:**
    ```bash
    cd ../streamlit
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```
    The Streamlit app will be running at `http://localhost:8501`.

## Usage

1.  Open your web browser and navigate to `http://localhost:8501`.
2.  Enter a topic you want to generate content ideas for in the input field.
3.  Click the "Generate" button.
4.  Watch as the AI agents collaborate to generate content ideas for you in real-time.

## Contributing

Contributions are welcome! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
