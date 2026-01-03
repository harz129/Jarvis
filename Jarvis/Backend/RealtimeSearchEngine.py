import requests
from groq import Groq
import datetime
from dotenv import dotenv_values
import re
import os
import json
from typing import Dict, List, Optional, Tuple

# Try to import optional dependencies safely
try:
    from googlesearch import search
except ImportError:
    search = None

try:
    from pytrends.request import TrendReq
except ImportError:
    TrendReq = None

# Load environment variables
env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "AI Assistant")
GroqAPIKey = env_vars.get("GroqAPIKey")

# API Keys from .env (matching the file content seen earlier)
OpenWeatherMapKey = env_vars.get("OpenWeatherMapKey")
GNewsAPIKey = env_vars.get("GNewsAPIKey")
CricAPIKey = env_vars.get("CricAPIKey")
AlphaVantageKey = env_vars.get("AlphaVantageKey")

# Initialize Groq Client
client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}. You are a very accurate and advanced AI chatbot named {Assistantname}.
You have real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way. ***
*** IMPORTANT: Always provide financial values, prices, and currency in Indian Rupees (₹/INR) unless specifically asked otherwise. ***
*** Just answer the question from the provided data in a professional way. ***"""

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# ========== WEATHER FUNCTION ==========
def get_weather(city: str) -> str:
    if not OpenWeatherMapKey: return "Weather API key missing."
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OpenWeatherMapKey}&units=metric"
    try:
        response = requests.get(url, timeout=10).json()
        if str(response.get("cod")) == "200":
            weather = response["weather"][0]["description"]
            temp = response["main"]["temp"]
            feels_like = response["main"]["feels_like"]
            humidity = response["main"]["humidity"]
            return f"🌤️ The current weather in {city.title()} is {weather.capitalize()} with a temperature of {temp}°C (feels like {feels_like}°C) and {humidity}% humidity."
        
        # More descriptive errors
        if str(response.get("cod")) == "404":
            return f"Sorry, I couldn't find weather data for '{city}'. Please check the city name."
        elif str(response.get("cod")) == "401":
            return "Invalid Weather API Key. Please update your .env file."
        return f"Weather Error: {response.get('message', 'Unknown error')}"
    except Exception as e:
        return f"Error fetching weather: {e}"

# ========== NEWS FUNCTION ==========
def get_news(query: str = "latest") -> str:
    if not GNewsAPIKey: return "News API key missing."
    url = f"https://gnews.io/api/v4/search?q={query}&token={GNewsAPIKey}&lang=en&max=5"
    try:
        response = requests.get(url, timeout=10).json()
        articles = response.get("articles", [])
        if articles:
            news_str = f"📰 Latest news headlines for '{query}':\n"
            for i, article in enumerate(articles, 1):
                news_str += f"{i}. {article['title']} - {article['source']['name']}\n"
            return news_str
        return "No news found for your query."
    except Exception as e:
        return f"Error fetching news: {e}"

# ========== CRICKET FUNCTION ==========
def get_cricket_scores(query: str = None) -> str:
    if not CricAPIKey: return "Cricket API key missing."
    url = f"https://api.cricapi.com/v1/currentMatches?apikey={CricAPIKey}&offset=0"
    try:
        response = requests.get(url, timeout=10).json()
        matches = response.get("data", [])
        if not matches:
            return "No cricket match data available at the moment."
        
        # Categorize matches
        live_matches = [m for m in matches if "live" in m.get("status", "").lower() or "started" in m.get("status", "").lower()]
        ended_matches = [m for m in matches if "won" in m.get("status", "").lower() or "ended" in m.get("status", "").lower() or "drawn" in m.get("status", "").lower()]
        
        # If a specific match/team is mentioned
        if query and len(query) > 2:
            query_lower = query.lower()
            # Search in all matches (live and recent past)
            matching_matches = [m for m in matches if query_lower in m['name'].lower()]
            if matching_matches:
                match = matching_matches[0]
                return f"🏏 {match['name']}\nStatus: {match['status']}\nScore: {match['score'] if 'score' in match else 'Data unavailable'}"
            return f"No match found for '{query}'.\nRecent matches: " + ", ".join([m['name'] for m in matches[:3]])
        
        # Default behavior:
        # If user asked for "last match" or "result" specifically (handled via intent/query, but if general)
        if ended_matches:
            # First ended match is usually the most recent
            match = ended_matches[0]
            return f"🏏 Most Recent Finished Match: {match['name']}\nResult: {match['status']}\nLast Score: {match['score'] if 'score' in match else 'N/A'}"
        
        # If no ended matches, show the top current match
        match = matches[0]
        return f"🏏 Current Match: {match['name']}\nStatus: {match['status']}\nScore: {match['score'] if 'score' in match else 'N/A'}"
    except Exception as e:
        return f"Error fetching cricket scores: {e}"

# ========== CURRENCY CONVERSION ==========
def get_exchange_rate(from_currency="USD", to_currency="INR") -> float:
    if not AlphaVantageKey: return 0.0
    url = f"https://www.alphavantage.co/query?function=CURRENCY_EXCHANGE_RATE&from_currency={from_currency}&to_currency={to_currency}&apikey={AlphaVantageKey}"
    try:
        response = requests.get(url, timeout=10).json()
        rate = response.get("Realtime Currency Exchange Rate", {}).get("5. Exchange Rate")
        return float(rate) if rate else 83.5 # Fallback to a recent estimate if API fails
    except:
        return 83.5

# ========== STOCKS FUNCTION ==========
def get_stock_price(symbol: str) -> str:
    if not AlphaVantageKey: return "Stock API key missing."
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={AlphaVantageKey}"
    try:
        response = requests.get(url, timeout=10).json()
        quote = response.get("Global Quote", {})
        if quote:
            price = quote.get("05. price")
            change = quote.get("09. change")
            percent = quote.get("10. change percent")
            
            if price:
                usd_price = float(price)
                inr_rate = get_exchange_rate("USD", "INR")
                inr_price = usd_price * inr_rate
                
                return f"📈 Stock: {symbol.upper()}\n• Price: ₹{inr_price:,.2f} ({usd_price:.2f} USD)\n• Change: {change} ({percent})\n• Exchange Rate: 1 USD = ₹{inr_rate:.2f}"
                
        return f"Could not find stock data for symbol '{symbol}'."
    except Exception as e:
        return f"Error fetching stocks: {e}"

# ========== TRENDS FUNCTION ==========
def get_trending_topics() -> str:
    if TrendReq is None:
        return "Trending topics are unavailable because 'pytrends' is not installed."
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        # Attempting daily trending searches for India
        trending = pytrends.trending_searches(pn='india')
        if trending is not None and not trending.empty:
            topics = trending[0].tolist()[:10]
            return "🔥 Trending topics in India right now:\n" + "\n".join([f"{i+1}. {t}" for i, t in enumerate(topics)])
        return "No trending topics found currently."
    except Exception as e:
        print(f"Error in Trending: {e}")
        # Final fallback if pytrends fails completely
        return "Trending topics are currently unavailable due to a service error."

# ========== INTENT DETECTOR ==========
def detect_intent(prompt: str) -> Tuple[str, Optional[str]]:
    """Detect user intent from the prompt using regex for speed, fallback to LLM for complex queries"""
    prompt_lower = prompt.lower()
    
    # Simple regex rules
    # Simple regex rules
    # Enhanced regex rules
    if any(word in prompt_lower for word in ["weather", "temperature", "climate"]):
        # Match 'in [City]', 'of [City]', etc. and strip the preposition
        match = re.search(r"(?:in|of|weather|temperature|climate)\s+([a-zA-Z\s]+)", prompt_lower)
        if match:
            city = match.group(1).strip()
            city = re.sub(r"^(in|of|the|is|at|for)\s+", "", city)
            return "weather", city
    
    if any(word in prompt_lower for word in ["news", "headlines", "latest news"]):
        match = re.search(r"(?:about|on|for)\s+([a-zA-Z0-9\s]+)", prompt_lower)
        return "news", match.group(1).strip() if match else "latest"
    
    if any(word in prompt_lower for word in ["cricket", "score", "match", "result", "last match"]):
        # Extract team/match name if present after 'of', 'between', or 'last'
        match = re.search(r"(?:of|between|for|score|last|result)\s+([a-zA-Z\s]+)", prompt_lower)
        if match:
            query = match.group(1).strip()
            query = re.sub(r"^(the|of|for|match|score|result)\s+", "", query)
            return "cricket", query
        return "cricket", None
    
    if any(word in prompt_lower for word in ["stock", "price", "share"]):
        match = re.search(r"(?:of|for|price)\s+([a-zA-Z]+)", prompt_lower)
        if match:
            candidate = match.group(1).strip().upper()
            if candidate not in ["OF", "FOR", "THE", "PRICE"]:
                return "stocks", candidate
    
    if any(word in prompt_lower for word in ["trending", "popular now", "what's trending"]):
        return "trending", None

    # LLM Fallback for intent classification if regex fails but looks like a real-time request
    if any(word in prompt_lower for word in ["happen", "world", "now", "live"]):
        try:
            intent_system = """Return ONLY JSON: {"intent": "weather"|"news"|"cricket"|"stocks"|"trending"|"none", "parameter": "string"|null}"""
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "system", "content": intent_system}, {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            import json
            data = json.loads(response.choices[0].message.content)
            return data.get("intent", "none"), data.get("parameter")
        except: pass

    return "none", None

# ========== UTILITIES ==========
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return "\n".join(non_empty_lines)

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    return f"Use This Real-time Information if needed:\nDay: {current_date_time.strftime('%A')}\nDate: {current_date_time.strftime('%d %B %Y')}\nTime: {current_date_time.strftime('%H:%M:%S')}\n"

def GoogleSearch(query):
    if search is None:
        return "Search is unavailable because 'googlesearch-python' is not installed."
    try:
        results = list(search(query, advanced=True, num_results=5))
        Answer = f"The search results for '{query}' are:\n[start]\n"
        for i in results:
            Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"
        Answer += "[end]"
        return Answer
    except Exception as e:
        return f"Search Error: {e}"

# ========== CORE ENGINES ==========
def original_RealtimeSearchEngine(prompt):
    """Fallback logic using Google Search + LLM"""
    global SystemChatBot
    try:
        if not os.path.exists("Data"): os.makedirs("Data")
        with open(r"Data\ChatLog.json", "r", encoding='utf-8') as f:
            messages = json.load(f)
    except: messages = []

    messages.append({"role": "user", "content": prompt})
    search_context = GoogleSearch(prompt)
    
    temp_messages = SystemChatBot + [
        {"role": "system", "content": search_context},
        {"role": "system", "content": RealtimeInformation()}
    ] + messages

    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=temp_messages,
            temperature=0.7,
            max_tokens=2048,
            stream=True
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.strip().replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})

        with open(r"Data\ChatLog.json", "w", encoding='utf-8') as f:
            json.dump(messages, f, indent=4)

        return AnswerModifier(Answer)
    except Exception as e:
        print(f"Error in RealtimeSearch: {e}")
        return f"I couldn't perform the search right now. (Error: {e})"

def RealtimeSearchEngine(prompt):
    """Primary engine with built-in intent routing to real-time APIs"""
    intent, parameter = detect_intent(prompt)
    
    api_result = None
    if intent == "weather" and parameter:
        api_result = get_weather(parameter)
    elif intent == "news":
        api_result = get_news(parameter if parameter else "latest")
    elif intent == "cricket":
        api_result = get_cricket_scores(parameter)
    elif intent == "stocks" and parameter:
        api_result = get_stock_price(parameter)
    elif intent == "trending":
        api_result = get_trending_topics()
    elif "happening in the world" in prompt.lower():
        api_result = f"{get_news('world')}\n\n{get_trending_topics()}"
    
    if api_result:
        # Log to chat history even for API results
        try:
            if not os.path.exists("Data"): os.makedirs("Data")
            with open(r"Data\ChatLog.json", "r", encoding='utf-8') as f:
                messages = json.load(f)
        except: messages = []
        messages.append({"role": "user", "content": prompt})
        messages.append({"role": "assistant", "content": api_result})
        with open(r"Data\ChatLog.json", "w", encoding='utf-8') as f:
            json.dump(messages, f, indent=4)
        return api_result

    # Fallback to standard web search
    return original_RealtimeSearchEngine(prompt)

if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        if prompt.lower() in ["exit", "quit"]: break
        print(f"\n{RealtimeSearchEngine(prompt)}\n")