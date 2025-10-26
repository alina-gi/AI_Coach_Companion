# response_engine.py
from textblob import TextBlob
import random

class ResponseEngine:
    def __init__(self, mode="local"):
        self.mode = mode  # "local" for offline, "ai" for real model later

    def detect_mood(self, message):
        """Detect mood using sentiment polarity"""
        polarity = TextBlob(message).sentiment.polarity
        if polarity > 0.3:
            return "positive"
        elif polarity < -0.3:
            return "negative"
        else:
            return "neutral"

    def generate_local_response(self, message, tone):
        """Simple rule-based local response"""
        mood = self.detect_mood(message)
        templates = {
            "positive": [
                "That’s great! Keep that energy going.",
                "I like your attitude — positivity always helps.",
            ],
            "negative": [
                "That sounds tough, but let’s figure out a way forward.",
                "I get it — sometimes things just don’t feel right. What do you think caused it?",
            ],
            "neutral": [
                "Hmm, tell me more about that.",
                "Alright, let’s break this down together.",
            ]
        }

        tone_effect = {
            "Blunt": "Here’s my honest take: ",
            "Empathetic": "I understand how you feel. ",
            "Balanced": ""
        }

        response = tone_effect.get(tone, "") + random.choice(templates[mood])
        return response

    def generate_response(self, message, tone):
        """Main function — uses local or AI mode"""
        if self.mode == "local":
            return self.generate_local_response(message, tone)
        else:
            # Placeholder for future API integration (Phase 3)
            return self.generate_ai_response(message, tone)

    def generate_ai_response(self, message, tone):
        """Will later use OpenAI API or local LLM"""
        return "AI mode is not active yet — coming soon!"
