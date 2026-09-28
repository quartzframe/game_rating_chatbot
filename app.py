import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai

load_dotenv()

app = Flask(__name__)
client = None

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    client = genai.Client(api_key=api_key)

def fallback_reply(message):
    return (
        "I can help you rate and review games. "
        "Tell me the game name and, if possible, the platform (PC, PS5, Xbox, Switch, Mobile). "
        "Example: 'Rate GTA V on PC' or 'Is Minecraft worth playing?'"
    )

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"reply": "Please enter a game-related question."})

    if not client:
        return jsonify({
            "reply": fallback_reply(message) +
                     "\n\nGemini API key is not configured yet, so live AI responses are disabled."
        })

    system_prompt = """
You are GameRate AI, a friendly game-rating and game-review chatbot.

Your job:
1. Answer questions about video games, game ratings, reviews, gameplay,
   genres, platforms, features, pros/cons, and recommendations.
2. Give ratings out of 10 only when useful, and explain the rating using
   clear factors such as gameplay, graphics, story, replay value, performance,
   and overall experience.
3. Never pretend that a rating is an official critic/user score. Clearly
   describe it as your AI assessment unless the user provides a score.
4. If the user asks about a game that you do not know enough about, say so
   and ask for the platform or more details.
5. Keep answers concise, simple, and useful.
6. Do not answer unrelated questions. Politely redirect the user to games.
7. Do not invent current prices, live player counts, release updates, or
   review statistics. If current data is not provided, say that you cannot
   verify live data.
8. For a rating request, prefer this structure:
   Game:
   Platform:
   Overall Rating: X/10
   Gameplay:
   Graphics:
   Story:
   Replay Value:
   Pros:
   Cons:
   Verdict:
"""

    try:
        response = client.models.generate_content(
            model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            contents=system_prompt + "\n\nUser question:\n" + message
        )
        reply = response.text or "Sorry, I could not generate a response."
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({
            "reply": "AI service error. Please check your Gemini API key and try again."
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
