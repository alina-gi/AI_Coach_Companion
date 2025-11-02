import json
import matplotlib.pyplot as plt
from collections import Counter
import os

class ToneAdaptationDashboard:
    def __init__(self, feedback_file="data/user_data.json"):
        self.feedback_file = feedback_file
        self.data = self._load_data()

    def _load_data(self):
        if not os.path.exists(self.feedback_file):
            print("[DEBUG] No feedback file found.")
            return []
        try:
            with open(self.feedback_file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("[DEBUG] Could not decode JSON.")
            return []

    def visualize_tone_preferences(self):
        if not self.data:
            print("No feedback data available for visualization.")
            return

        liked = []
        disliked = []

        for entry in self.data:
            tone = entry.get("tone_used")
            feedback = entry.get("feedback")
            if feedback == "like":
                liked.append(tone)
            elif feedback == "dislike":
                disliked.append(tone)

        liked_count = Counter(liked)
        disliked_count = Counter(disliked)

        tones = list(set(list(liked_count.keys()) + list(disliked_count.keys())))
        likes = [liked_count.get(t, 0) for t in tones]
        dislikes = [disliked_count.get(t, 0) for t in tones]

        # --- Create figure ---
        plt.figure(figsize=(8, 5))
        bar_width = 0.35
        x = range(len(tones))

        plt.bar(x, likes, width=bar_width, label='Likes', alpha=0.7)
        plt.bar([i + bar_width for i in x], dislikes, width=bar_width, label='Dislikes', alpha=0.7)

        plt.xlabel("Tone")
        plt.ylabel("Count")
        plt.title("AI Codes Companion — Tone Adaptation Summary")
        plt.xticks([i + bar_width / 2 for i in x], tones)
        plt.legend()
        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    dashboard = ToneAdaptationDashboard()
    dashboard.visualize_tone_preferences()
