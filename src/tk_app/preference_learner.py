import json
from collections import Counter

class PreferenceLearner:
    def __init__(self, feedback_file="data/user_data.json"):
        self.feedback_file = feedback_file
        self.data = self._load_data()

    def _load_data(self):
        try:
            with open(self.feedback_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def analyze_preferences(self):
        if not self.data:
            return {"status": "No feedback yet."}

        liked_tones = []
        disliked_tones = []
        moods = []

        for entry in self.data:
            tone = entry.get("tone_used")
            mood = entry.get("detected_mood")
            feedback = entry.get("feedback")

            if feedback == "like" and tone:
                liked_tones.append(tone)
            elif feedback == "dislike" and tone:
                disliked_tones.append(tone)
            if mood:
                moods.append(mood)

        result = {
            "most_liked_tones": [t for t, _ in Counter(liked_tones).most_common(2)],
            "most_disliked_tones": [t for t, _ in Counter(disliked_tones).most_common(2)],
            "common_moods": [m for m, _ in Counter(moods).most_common(2)]
        }
        return result

    def recommend_tone(self):
        prefs = self.analyze_preferences()
        if "status" in prefs:
            return "neutral"
        if prefs["most_liked_tones"]:
            return prefs["most_liked_tones"][0]
        return "neutral"

if __name__ == "__main__":
    learner = PreferenceLearner()
    print("User preference analysis:")
    print(learner.analyze_preferences())
    print("Recommended tone:", learner.recommend_tone())
