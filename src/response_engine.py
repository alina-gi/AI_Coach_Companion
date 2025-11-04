# response_engine.py
from textblob import TextBlob
import random
import json
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from tk_app.preference_learner import PreferenceLearner
from openai import OpenAI
from dotenv import load_dotenv



class ResponseEngine:
    def __init__(self, mode="api"):
        self.mode = mode
        self.analyzer = SentimentIntensityAnalyzer()  # ← Initialize VADER here

         # Load API key and initialize client
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("[WARNING] No OpenAI API key found. Running in local mode.")
        self.client = OpenAI(api_key=api_key) if api_key else None


        # Preference data loaded from user feedback
        self.user_feedback_path = "data/user_data.json"
        self.liked_tone_counts, self.liked_mood_counts = self._load_user_preferences()
        self.preference_learner = PreferenceLearner()
        print(f"[DotPi] ResponseEngine initialized in {self.mode.upper()} mode.")



    def _load_user_preferences(self):
        """Load user feedback and aggregate likes for tone and mood."""
        liked_tone_counts = {"Blunt": 0, "Empathetic": 0, "Balanced": 0}
        liked_mood_counts = {"positive": 0, "negative": 0, "neutral": 0}

        try:
            if os.path.exists(self.user_feedback_path):
                with open(self.user_feedback_path, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for entry in data:
                            try:
                                if entry.get("feedback") == "like":
                                    tone = entry.get("tone_used")
                                    mood = entry.get("detected_mood")
                                    if tone in liked_tone_counts:
                                        liked_tone_counts[tone] += 1
                                    # Normalize mood keys to our template keys
                                    if mood in ("positive", "negative", "neutral"):
                                        liked_mood_counts[mood] += 1
                                    elif mood in ("happy",):
                                        liked_mood_counts["positive"] += 1
                                    elif mood in ("sad",):
                                        liked_mood_counts["negative"] += 1
                            except Exception:
                                # Skip malformed entries
                                continue
        except Exception:
            # On any error, return zeroed prefs to avoid breaking logic
            pass
        #print("Liked tones:", liked_tone_counts)
        #print("Liked moods:", liked_mood_counts)


        return liked_tone_counts, liked_mood_counts

    def test_openai_connection(self, message="Hello DotPi!"):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a friendly AI coach."},
                    {"role": "user", "content": message}
                ]        )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"


    def _weighted_choice(self, weights_dict):
        """Return a key from weights_dict based on weighted random selection."""
        items = list(weights_dict.items())
        total = sum(max(w, 0) for _, w in items) or 1
        r = random.uniform(0, total)
        upto = 0
        for key, weight in items:
            w = max(weight, 0)
            if upto + w >= r:
                return key
            upto += w
        return items[-1][0]

    def detect_mood(self, message):
        """Smarter mood detection using VADER sentiment analysis."""
        try:
            scores = self.analyzer.polarity_scores(message)
            compound = scores["compound"]

            print("Scores:", scores, "Compound:", compound)


            if compound >= 0.3:
                return "positive"
            elif compound <= -0.3:
                return "negative"
            else:
                return "neutral"
        except Exception:
            return "neutral"


    def generate_local_response(self, message, tone, mood=None):
        """
        Local response generator.
        Accepts mood parameter but will still work if mood is None.
        """
        # If mood wasn't passed, try to detect it (fallback)
        if mood is None:
            mood = self.detect_mood(message)

        # map sentiments to our simple keys
        if mood in ("positive", "happy", "happy-ish"):
            base_key = "positive"
        elif mood in ("negative", "sad"):
            base_key = "negative"
        else:
            base_key = "neutral"

        templates = {
            "positive": [
                "That’s great! Keep that energy going.",
                "I like your attitude — positivity always helps.",
                "Nice progress — let’s build on that."
            ],
            "negative": [
                "That sounds tough, but let’s figure out a way forward.",
                "I get it — sometimes things just don’t feel right. What do you think caused it?",
                "I hear you. We'll take a small step together."
            ],
            "neutral": [
                "Hmm, tell me more about that.",
                "Alright, let’s break this down together.",
                "Okay — what's the most useful next step?"
            ]
        }

        tone_effect = {
            "Blunt": "Here’s my honest take: ",
            "Empathetic": "I understand how you feel. ",
            "Balanced": ""
        }

        # --- Weighted suggestion logic based on liked tone/mood ---
        # Start with small base weights to keep behavior stable
        weights = {"positive": 1, "negative": 1, "neutral": 1}

        # Preserve existing behavior by biasing toward detected/base_key
        weights[base_key] += 3

        # Boost if user liked this mood previously
        for mood_key, count in self.liked_mood_counts.items():
            if count > 0:
                weights[mood_key] += 10

        # Boost toward the detected/base_key if the current tone is among liked tones
        # (tone is fixed by caller; we only bias mood key selection)
        if tone in self.liked_tone_counts and self.liked_tone_counts[tone] > 0:
            weights[base_key] += 10

        # Choose the mood key using weighted random selection
        chosen_key = self._weighted_choice(weights)

        prefix = tone_effect.get(tone, "")
        choice = random.choice(templates.get(chosen_key, templates["neutral"]))
        return prefix + choice

    def generate_response(self, message, tone, mood=None):
        """Main function — accepts mood and switches between local or API."""
        if self.mode == "local":
            # Get preferred tone from learner
            preferred_tone = self.preference_learner.recommend_tone()
            #print(f"[DEBUG] Tone in use: {preferred_tone or tone}")  # Debug confirmation
            
            # Generate response with preferred tone if available
            return self.generate_local_response(message, preferred_tone or tone, mood)
        else:
            return self.generate_ai_response(message, tone, mood)



    # --- Refresh user preferences ---
    def refresh_user_preferences(self):
        """Reload liked tone and mood counts from user feedback file."""
        self.liked_tone_counts, self.liked_mood_counts = self._load_user_preferences()


    def generate_ai_response(self, message, tone, mood=None):
        """
        Generate AI-based response using OpenAI API,
        enhanced with DotPi's local tone + mood logic.
        Falls back to local generation if API call fails.
        """
        # 1️⃣ Detect mood if not provided
        if mood is None:
            mood = self.detect_mood(message)

        # 2️⃣ Get preferred tone (learned locally)
        preferred_tone = self.preference_learner.recommend_tone() or tone

        # 3️⃣ Build system prompt with mood + tone context
        system_prompt = (
            "You are DotPi — an intelligent, emotionally-aware AI coach. "
            "Your goal is to respond to the user in a tone that fits both their detected mood "
            "and their learned preference tone. "
            "Be concise, human-like, and emotionally attuned. "
            f"Detected mood: {mood}. "
            f"Preferred tone: {preferred_tone}. "
            "If user sounds down, be supportive. If positive, encourage them. "
            "Keep it conversational, no long paragraphs. "
        )

        try:
            # 4️⃣ Generate GPT-based response
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.8
            )

            ai_message = response.choices[0].message.content.strip()
            print(f"[DotPi][AI Mode] GPT response: {ai_message}")
            return ai_message

        except Exception as e:
            # 5️⃣ Safe fallback to local mode
            print(f"[DotPi] API error → Falling back to local mode: {e}")
            return self.generate_local_response(message, preferred_tone, mood)

    
