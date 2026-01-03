# 🤖 Jarvis - Advanced AI Virtual Assistant

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/UI-PyQt5-green?logo=qt&logoColor=white)](https://www.riverbankcomputing.com/software/pyqt/)
[![AI-Powered](https://img.shields.io/badge/AI-Cohere%20%7C%20Groq%20%7C%20Gemini-orange)](https://cohere.com/)

**Jarvis** is a sophisticated, modular, and highly interactive AI-powered virtual assistant. Built with a robust decision-making engine, it seamlessly transitions between conversational AI, real-time web searching, and system-level automation. Featuring a modern PyQt5 interface and smooth voice interaction, Jarvis is designed to be your ultimate digital companion.

---

## 🌟 Key Features

### 🧠 Intelligent Decision Engine
Powered by **Cohere**, Jarvis utilizes a Multi-Layer Decision Model (DMM) to categorize your queries:
- **General**: Conversational AI for brainstorming, coding, and general knowledge.
- **Real-time**: Fetches latest news, weather, and live data from the web.
- **Task-oriented**: Executes system commands, reminders, and automations.

### 🎙️ Seamless Voice Interaction
- **Speech-to-Text (STT)**: High-accuracy voice recognition for hands-free operation.
- **Text-to-Speech (TTS)**: Natural-sounding responses powered by **Edge-TTS**.

### 🛠️ System Automation
- **App Management**: Open and close applications or websites (Facebook, YouTube, etc.).
- **System Controls**: Adjust volume, mute/unmute, and manage system states.
- **Reminders**: Set intelligent reminders with date and time recognition.

### 🎨 Creative Hub
- **Image Generation**: Generate stunning visuals using **Gemini AI**.
- **Video Generation**: Create high-quality videos from text prompts.

### 🌐 Real-time Information
Integrated search engine that crawls Google and YouTube to provide the most relevant and up-to-date answers.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- API Keys for:
  - **Cohere** (Primary Decision Model)
  - **Groq/OpenAI** (Chatbot Logic)
  - **Google Gemini** (Image Generation)

### Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/harz129/jarvis.git
   cd jarvis
   ```

2. **Install Dependencies**
   ```bash
   pip install -r Requirements.txt
   ```

3. **Configure Environment Variables**
   Create a `.env` file in the root directory and add your credentials:
   ```env
   CohereAPIKey=your_cohere_key
   GroqAPIKey=your_groq_key
   Assistantname=Jarvis
   Username=YourName
   APP_PASSWORD=your_secure_password
   ```

4. **Run the Application**
   ```bash
   python Main.py
   ```

---

## 📁 Project Structure

```text
Jarvis/
├── Main.py                 # Entry point (Thread management & Core logic)
├── Backend/
│   ├── Model.py            # Decision-making orchestration (Cohere)
│   ├── Chatbot.py          # Conversational LLM logic
│   ├── Automation.py       # System tasks & App control
│   ├── SpeechToText.py     # Voice recording & transcription
│   ├── TextToSpeech.py     # Voice synthesis (Edge-TTS)
│   ├── RealtimeSearch.py   # Web search & scraping
│   ├── ImageGeneration.py  # Gemini Image API integration
│   └── VideoGeneration.py  # AI Video generation workflows
├── Frontend/
│   ├── GUI.py              # PyQt5 Dashboard interface
│   └── Graphics/           # UI assets, icons, and animations
├── Data/                   # Chat history and persistent logs
├── Requirements.txt        # Python dependency list
└── .env                    # Configuration & API keys
```

---

## 🛡️ Security
Jarvis features a built-in authentication layer. On startup, you will be prompted for the `APP_PASSWORD` defined in your `.env` file to ensure your assistant and data remain private.

---

## 🛠️ Technology Stack
- **Core**: Python
- **GUI**: PyQt5, Rich
- **AI Models**: Cohere (DMM), Groq (LLM), Gemini (Images)
- **Automation**: PyAutoGUI, AppOpener, Selenium
- **Audio**: Edge-TTS, Pygame

---

## 🤝 Contributing
Contributions are welcome! If you have ideas for new features or improvements, feel free to fork the repository and submit a pull request.

## 📄 License
This project is for educational and personal use. Please check individual API licenses for commercial usage.

---
*Developed with ❤️ by Harz*
