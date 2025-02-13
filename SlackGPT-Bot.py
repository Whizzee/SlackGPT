import os
import openai
from openai import OpenAIError
from slack_sdk import WebClient
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN or not OPENAI_API_KEY:
    raise ValueError("One or more required environment variables are missing. Please check your .env file.")

app = App(token=SLACK_BOT_TOKEN)
client = WebClient(token=SLACK_BOT_TOKEN)
openai.api_key = OPENAI_API_KEY

@app.event("app_mention")
def handle_message_events(body, logger):
    try:
        prompt = body["event"]["text"].split(">", 1)[1].strip()
        logger.info(f"Prompt received: {prompt}")
        response_text = generate_openai_response(prompt)
        logger.info(f"OpenAI Response: {response_text}")
        client.chat_postMessage(
            channel=body["event"]["channel"],
            thread_ts=body["event"]["ts"],
            text=f"Here you go: \n{response_text}"
        )
    except Exception as e:
        logger.error(f"Error processing mention event: {e}")
        client.chat_postMessage(
            channel=body["event"]["channel"],
            thread_ts=body["event"]["ts"],
            text="Your highness, Something went wrong. Try again fam."
        )

def generate_openai_response(prompt):
    """Generates a response using OpenAI's API."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1024,
            temperature=0.5,
        )
        return response["choices"][0]["message"]["content"].strip()
    except OpenAIError as e:
        print(f"OpenAI API Error: {e}")
        return "Sorry, I encountered an issue with OpenAI while processing your request."

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
