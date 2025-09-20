import os
from openai import OpenAI
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Initialize client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("AI_GATEWAY_URL")  # Gateway URL
)

def main():
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": "Solve 2+2 step by step"}
            ]
        )
        print("✅ Gateway test succeeded!")
        print("Response:\n", response.choices[0].message.content)
    except Exception as e:
        print("❌ Gateway test failed:", e)

if __name__ == "__main__":
    main()
