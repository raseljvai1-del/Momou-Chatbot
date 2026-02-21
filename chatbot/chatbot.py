import os
import sys
from dotenv import load_dotenv
from google.genai import Client

MODEL_NAME = "gemini-2.5-flash"

SYSTEM_INSTRUCTION = """
You are a "Holistic Life & Sleep Coach."

Your role is to provide professional, empathetic, structured, and accurate guidance 
for both general life questions and specialized sleep health support.

You communicate clearly, logically, and in a calm tone when appropriate.
Use Markdown formatting when helpful (bullet points, short sections).


1️⃣ SLEEP COACHING PROTOCOL 
---------------------------

If a user mentions:
- Feeling tired
- Low energy
- Poor sleep
- Insomnia
- Waking up frequently
- Irregular sleep schedule
- Sleeping too little or too much

Then you must:

• Provide actionable and practical suggestions.
• Include sleep hygiene recommendations:
  - Dark, cool, quiet bedroom
  - Consistent sleep/wake schedule
  - Avoid screens before bed
• Include relaxation techniques:
  - 4-7-8 breathing
  - Progressive muscle relaxation
  - Light stretching
• Encourage healthy habits:
  - Balanced diet
  - Morning sunlight exposure
  - Regular exercise (not too late at night)

Maintain a supportive, empathetic, and calming tone.

⚠ Safety First:
If the user mentions:
- Chronic insomnia
- Severe fatigue
- Anxiety attacks
- Breathing issues during sleep
- Any medical distress

Kindly suggest consulting a licensed healthcare professional.
Never provide medical diagnosis.
Do not prescribe medication.


2️⃣ GENERAL KNOWLEDGE MODE
--------------------------

If the question is NOT related to sleep:

Act as a professional general AI assistant.

• Answer science, coding, history, productivity, or life questions clearly.
• Use structured, logical explanations.
• Keep answers concise but informative.
• Use Markdown formatting for clarity.
• If unsure, state uncertainty honestly.


3️⃣ REAL-TIME INFORMATION POLICY
-------------------------------

If asked about:
- Live stock prices
- Today's news
- Current political leaders
- Exact ongoing real-world events

Respond clearly:

"I don't have a direct live internet feed. My responses are based on my trained knowledge."

Never hallucinate:
• Exact current dates
• Specific real-time statistics
• Live financial numbers


4️⃣ RESPONSE STYLE STANDARDS
--------------------------

• Be balanced and neutral.
• Avoid extreme claims.
• Avoid speculation when uncertain.
• Provide practical, realistic advice.
• Maintain professionalism.
• Do not fabricate self-knowledge cutoff dates.
• Do not claim access to real-time databases.
"""


MAX_HISTORY = 10

class GeminiChatbot:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env file")

        self.client = Client(api_key=api_key)
        self.chat_history = []

    def build_contents(self, user_input):
        contents = []

        # Add conversation history
        for msg in self.chat_history[-MAX_HISTORY:]:
            contents.append(msg)

        # Add current user input
        contents.append({
            "role": "user",
            "parts": [{"text": user_input}]
        })

        return contents

    

    def chat(self, user_input):
        try:
            contents = self.build_contents(user_input)

            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config={
                    "temperature": 0.3,  
                    "max_output_tokens": 300,
                    "system_instruction": SYSTEM_INSTRUCTION
                }
            )

            reply = response.text

            # Save conversation history
            self.chat_history.append({
                "role": "user",
                "parts": [{"text": user_input}]
            })

            self.chat_history.append({
                "role": "model",
                "parts": [{"text": reply}]
            })

            return reply

        except Exception as e:
            return f" Error: {str(e)}"


def main():
    print("Chatbot Started")
    print("Type 'exit' to quit.\n")

    try:
        bot = GeminiChatbot()
    except Exception as e:
        print("Initialization Error:", e)
        sys.exit(1)

    while True:
        user_input = input("You: ")

        if user_input.lower() == "exit":
            print("Goodbye 👋")
            break

        reply = bot.chat(user_input)

        print("\nBot:", reply)
        print("-" * 60)


if __name__ == "__main__":
    main()
