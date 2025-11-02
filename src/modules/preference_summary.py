import json
from collections import Counter

class PreferenceSummary:
    def __init__(self, feedback_file="data/user_data.json"):
        self.feedback_file = feedback_file
        self.data = self._load_data()

    def _load_data(self):
        try:
            with open(self.feedback_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print("DEBUG: Error loading file:", e)
            return []

    def summarize(self):
        if not self.data:
            return "No feedback data found yet."

        liked_tones = []
        disliked_tones = []
        moods = []

        for entry in self.data:
            tone = entry.get("tone_used")
            mood = entry.get("detected_mood")
            feedback = entry.get("feedback")

            if feedback == "like":
                liked_tones.append(tone)
            elif feedback == "dislike":
                disliked_tones.append(tone)

            if mood:
                moods.append(mood)

        summary = []

        if liked_tones:
            most_liked = Counter(liked_tones).most_common(2)
            summary.append(f"You like {', '.join([t for t, _ in most_liked])} tones.")

        if disliked_tones:
            most_disliked = Counter(disliked_tones).most_common(2)
            summary.append(f"You dislike {', '.join([t for t, _ in most_disliked])} tones.")

        if moods:
            common_moods = Counter(moods).most_common(2)
            summary.append(f"You mostly interact when your mood is {', '.join([m for m, _ in common_moods])}.")

        return " ".join(summary)

if __name__ == "__main__":
    summary = PreferenceSummary()
    print(summary.summarize())

