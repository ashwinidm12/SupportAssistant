📦 Support Assistant – AI-Powered Order Helpdesk

A WhatsApp-style Customer Support Chatbot built with Streamlit, Offline FAQ Intelligence, and Optional Groq/Gemini AI Integration.

🚀 Project Overview

Support Assistant is an AI-powered helpdesk chatbot designed with a WhatsApp-like chat UI, voice input support, and intelligent offline FAQ matching.
It can also connect to Groq Llama 3.1, Google Gemini, or OpenAI if API keys are available.

The system works in three modes:

Online AI Mode (preferred)
✔ GROQ_API_KEY → Groq Llama 3.1
✔ GEMINI_API_KEY → Google Gemini
✔ OPENAI_API_KEY → OpenAI GPT

Offline FAQ Mode (when no API key)
✔ Uses your dataset (faqs.json, dataset.csv)
✔ Searches and responds using similarity matching

Hybrid Mode
✔ Offline + Online fallback chain

✨ Key Features
🟢 WhatsApp-style responsive UI

Chat bubbles

User & assistant avatars

Right-aligned user messages

Left-aligned bot messages

🎤 Voice recording (WebRTC + MediaRecorder)

Press mic → record audio

Uploads to local server (upload_server.py)

Transcription using SpeechRecognition

🤖 Offline Smart FAQ Matching

Uses dataset:

faqs.json

faqs_large.json

dataset.csv

Fast query search without internet

Works even with 0 API keys

🌐 Optional Online AI

Automatically selects best available AI model

Chain logic:

IF GROQ_API_KEY exists → use Groq Llama 3.1
ELSE IF GEMINI_API_KEY exists → use Gemini
ELSE IF OPENAI_API_KEY exists → use OpenAI
ELSE → fallback offline (FAQ dataset)

📁 Upload Server

Handles audio uploads

Stores files inside /uploads/

🎛 Sidebar

Chat history

Quick help panel

System information

🗂 Project Folder Structure
support-assistant/
│ app.py
│ agent.py
│ agent_online.py
│ ui_components.py
│ voice_mic.py
│ upload_server.py
│ requirements.txt
│ README.md
│
├── assets/
│       architecture.png
│
├── data/
│       dataset.csv
│       faqs.json
│       faqs_large.json
│       orders_sample.csv
│
├── tools/
│       shopify_tool.py
│
├── uploads/
│       (auto-generated audio uploads)

🧠 System Architecture
flowchart TD

User -->|Text/Voice| UI[Streamlit WhatsApp UI]

UI --> Agent

Agent -->|Search| OfflineFAQ[Offline FAQ Matcher]
Agent -->|If API Key| OnlineAI[agent_online.py]

OnlineAI --> GroqAPI[(Groq API)]
OnlineAI --> GeminiAPI[(Gemini API)]
OnlineAI --> OpenAIAPI[(OpenAI API)]

OfflineFAQ --> Response
OnlineAI --> Response

Response --> UI

⚙️ Installation & Setup
1️⃣ Clone the repository
git clone https://github.com/YOUR_USERNAME/support-assistant.git
cd support-assistant

2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Create .env file

Create a file named .env:

GROQ_API_KEY=
GEMINI_API_KEY=
GEMINI_PROJECT=
OPENAI_API_KEY=


Leave keys empty to run offline mode.

▶️ Running the Application
streamlit run app.py

🌐 API Key Guide
✔ Groq (Free / Fast)

Get from: https://console.groq.com/keys

Set in .env:

GROQ_API_KEY=gsk_xxxxxxxxxxxxx

✔ Google Gemini (Free Tier)
GEMINI_API_KEY=AIzaSyXXXXXXXX

✔ OpenAI (Paid)
OPENAI_API_KEY=sk-proj-XXXXXXX

🧪 Testing Online Agent

Run:

python -c "from agent_online import get_online_answer; print(get_online_answer('Where is my order?'))"


If key is valid → returns an answer.
If invalid → falls back to offline dataset.

💬 UI Screenshots
WhatsApp-style UI

(Your actual screenshots should be added here)

assets/
   – chat_ui.png
   – faq_section.png
   – architecture.png

🛠 Technical Details
app.py

Main orchestrator

Renders UI

Handles chat flow

Manages state

agent.py

Offline FAQ matcher

Response generator

Dataset loader

agent_online.py

Groq

Gemini

OpenAI

Automatic fallback

voice_mic.py

Microphone button

Audio recording logic

Upload to upload server

upload_server.py

Local HTTP server

Stores audio files

ui_components.py

CSS styles

Chat bubbles

Sidebar

Suggestions grid

📝 How Offline FAQ Matching Works

User submits a question

Convert FAQs into vectors

Compare similarity (cosine)

Pick best match

Respond with stored answer

This ensures your bot always works, even without internet.

📡 Deployment Guide (GitHub Pages + Streamlit Cloud)
1️⃣ Push project to GitHub
git add .
git commit -m "Initial Commit"
git push origin main

2️⃣ Deploy on Streamlit Cloud

https://share.streamlit.io

Connect GitHub repo

Select app.py

Deploy

🎤 Viva / Panel Member Answers
Q: Why is there spacing in UI?

Because Streamlit injects container padding; we override with CSS to reduce spacing.

Q: Why mic may not work in some browsers?

Because microphone API requires HTTPS or localhost.
Mobile browsers restrict MediaRecorder; fallback exists via file upload.

Q: What if API keys are invalid?

The system automatically falls back to offline FAQ mode, ensuring 100% availability.

Q: Why choose Streamlit?

Fast prototyping, clean UI, built-in state management

🧾 License

MIT License (Free for academic use).

🎉 End of README