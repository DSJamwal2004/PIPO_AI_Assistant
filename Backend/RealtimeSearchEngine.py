from googlesearch import search
from groq import Groq
from json import load, dump
import datetime 
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")

Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

client = Groq(api_key=GroqAPIKey)

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***
"""

# Load chat history
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)
    messages = []

# FIXED: Proper search result formatting
def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"
    for result in results:
        Answer += f"Title: {result.title}\nURL: {result.url}\nDescription: {result.description}\n\n"
    Answer += "[end]"
    return Answer

# Clean up whitespace
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"}, 
    {"role": "assistant", "content": "Hello, how can I help you?"}    
]  

# Real-time context
def Information():
    current_date_time = datetime.datetime.now()
    return (
        "Use This Real-time Information if needed:\n"
        f"Day: {current_date_time.strftime('%A')}\n"
        f"Date: {current_date_time.strftime('%d')}\n"
        f"Month: {current_date_time.strftime('%B')}\n"
        f"Year: {current_date_time.strftime('%Y')}\n"
        f"Time: {current_date_time.strftime('%H')} hours, "
        f"{current_date_time.strftime('%M')} minutes, "
        f"{current_date_time.strftime('%S')} seconds.\n"
    )

# Main function to get a real-time AI response
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    # Reload messages
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
    messages.append({"role": "user", "content": prompt}) 

    # Add search results as system prompt
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    # Call Groq LLM
    completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
        temperature=0.7,
        max_tokens=2048,
        top_p=1,
        stream=True,
        stop=None
    )
 
    Answer = ""
    for chunk in completion:
        if chunk.choices[0].delta.content:
            Answer += chunk.choices[0].delta.content

    Answer = Answer.strip().replace("</s>", "")
    messages.append({"role": "assistant", "content": Answer}) 

    # Save chat log
    with open(r"Data\ChatLog.json", "w") as f:
        dump(messages, f, indent=4)

    SystemChatBot.pop()
    return AnswerModifier(Answer)

# Run in a loop
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
