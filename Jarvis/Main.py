import os
import sys
from dotenv import load_dotenv

load_dotenv()

def _get_password(prompt="Password: "):
    print(prompt, end="", flush=True)
    password = ""

    if os.name == "nt":  # Windows
        import msvcrt
        while True:
            char = msvcrt.getch()
            if char in (b"\r", b"\n"):
                print()
                break
            elif char == b"\x08":  # Backspace
                if password:
                    password = password[:-1]
                    print("\b \b", end="", flush=True)
            else:
                password += char.decode("utf-8", errors="ignore")
                print("*", end="", flush=True)
    else:  # Linux / macOS
        import sys, termios, tty
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                char = sys.stdin.read(1)
                if char in ("\n", "\r"):
                    print()
                    break
                elif char == "\x7f":  # Backspace
                    if password:
                        password = password[:-1]
                        print("\b \b", end="", flush=True)
                else:
                    password += char
                    print("*", end="", flush=True)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

    return password


def __auth__():
    real_password = os.getenv("APP_PASSWORD")

    if not real_password:
        print("APP_PASSWORD missing in .env")
        sys.exit(1)

    entered = _get_password("Enter password: ")

    if entered != real_password:
        print("Access denied.")
        sys.exit(1)

    print("System loading...\n")


__auth__()


from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.ImageGeneration import gemini
from Backend.VideoGeneration import ignite_automation
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import threading
import json
import os
import requests

env_vars = dotenv_values(".env")
Username = env_vars.get("Username") or "User"
Assistantname = env_vars.get("Assistantname") or "Assistant"
DefaultMessage = f'''{Username}: Hello {Assistantname}, How are you?
{Assistantname}: Welcome {Username}, I am doing well. How may I help you?'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    try:
        if not os.path.exists('Data'): os.makedirs('Data')
        chat_log_path = r'Data\\ChatLog.json'
        if not os.path.exists(chat_log_path):
            with open(chat_log_path, 'w', encoding='utf-8') as f:
                json.dump([], f)

        with open(chat_log_path, "r", encoding='utf-8') as File:
            content = File.read()
            if len(content) < 5:
                with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
                    file.write("")
                with open(TempDirectoryPath("Responses.data"), 'w', encoding='utf-8') as file:
                    file.write(DefaultMessage)
    except Exception as e:
        print(f"Error in ShowDefaultChatIfNoChats: {e}")

def ReadChatLogJson():
    chat_log_path = r'Data\\ChatLog.json'
    if not os.path.exists(chat_log_path):
        with open(chat_log_path, 'w', encoding='utf-8') as f:
            json.dump([], f)
    with open(chat_log_path, 'r', encoding="utf-8") as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""

    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"

    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    File = open(TempDirectoryPath('Database.data'), "r", encoding='utf-8')
    Data = File.read()
    if len(str(Data)) > 0:
        lines = Data.split('\n')
        result = '\n'.join(lines)
        File.close()
        File = open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8')
        File.write(result)
        File.close()

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def MainExecution():
    TaskExecution = False

    ImageExecution = False
    VideoExecution = False

    ImageGenerationQuery = ""
    VideoGenerationQuery = ""


    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextToScreen(f"{Username}: {Query}")
    SetAssistantStatus("Thinking...")

    try:
        Decision = FirstLayerDMM(Query)

        print("")
        print(f"Decision: {Decision}")
        print("")

        G = any([i for i in Decision if i.startswith("general")])
        R = any([i for i in Decision if i.startswith("realtime")])

        Merged_query = " and ".join(["".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")])

        for queries in Decision:
            if "image" in queries:
                ImageGenerationQuery = str(queries)
                ImageExecution = True

        for queries in Decision:
                if "video" in queries:
                    # Strip the 'video' trigger word so it doesn't type 'video' into Leonardo
                    VideoGenerationQuery = queries.replace("video", "").strip()
                    VideoExecution = True

        for queries in Decision:
            if TaskExecution == False:
                if any(queries.startswith(func) for func in Functions):
                    run(Automation(list(Decision)))
                    TaskExecution = True

        if ImageExecution:
            SetAssistantStatus("Generating Image...")
            ShowTextToScreen(f"{Assistantname}: Generating image...")
            gemini(ImageGenerationQuery)
            SetAssistantStatus("Available...")
            return True

        if VideoExecution:
            SetAssistantStatus("Generating Video...")
            ShowTextToScreen(f"{Assistantname}: Generating video for '{VideoGenerationQuery}'...")
            # Now passing the actual query string
            ignite_automation(VideoGenerationQuery) 
            SetAssistantStatus("Available...")
            return True
        
        if G and R or R:
            SetAssistantStatus("Searching...")
            Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True
        
        else:
            for Queries in Decision:
                if "general" in Queries:
                    SetAssistantStatus("Thinking...")
                    QueryFinal = Queries.replace("general", "")
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    return True

                elif "realtime" in Queries:
                    SetAssistantStatus("Searching...")
                    QueryFinal = Queries.replace("realtime ", "")
                    Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    return True
                
                elif "exit" in Queries:
                    QueryFinal = "Okay, Bye!"
                    Answer = ChatBot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname}: {Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    SetAssistantStatus("Answering...")
                    os._exit(1)
    except Exception as e:
        print(f"Error in MainExecution: {e}")
        SetAssistantStatus("Error!")
        ShowTextToScreen(f"{Assistantname}: I encountered an error: {e}")
        SetAssistantStatus("Available...")

def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available...")

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()