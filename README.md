# AI Bot Demo Project

## Overview

This demo project shows two custom AI bots with their own knowledge bases for two clients:

1. Tech Company IT Support Bot (`client1`)
2. Health Clinic FAQ Bot (`client2`)

You can upload documents for each client, build embeddings, and ask questions using a Streamlit chat UI.

---

## Setup

1. Clone the repo and `cd` to the project folder.

2. Create and activate a Python virtual environment:
python -m venv venv
venv\Scripts\activate

3. Install required packages:
pip install -r requirements.txt

4. Get OpenAI API key and set it as environment variable:
set OPENAI_API_KEY=your_openai_api_key

5. Prepare upload folders:
mkdir -p backend/data/client1 backend/data/client2
mkdir -p backend/embeddings/client1 backend/embeddings/client2

6. Start the backend FastAPI server:
python main.py

7. Open a new terminal and start the Streamlit frontend:
streamlit run frontend/streamlit_app.py

8. Open a new terminal and Upload files
curl.exe -X POST "http://localhost:8000/upload/" -F client_id=client1 -F files=@test_data/client1_sample.txt
