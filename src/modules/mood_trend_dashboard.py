# -------------------- mood_trend_dashboard.py --------------------
import json
import os
from datetime import datetime
import matplotlib.pyplot as plt
from collections import Counter

class MoodTrendDashboard:
    def __init__(self, feedback_file="data/user_data.json"):
        self.feedback_file = feedback_file
        self.data = self._load_data()

    def _load_data(self):
        """Load feedback data from JSON."""
        if not os.path.exists(self.feedback_file):
            print(f"DEBUG: No data file found at {self.feedback_file}")
            return []

        try:
            with open(self.feedback_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    print(f"DEBUG: Loaded {len(data)} feedback entries.")
                    return data
                else:
                    print("DEBUG: Invalid data structure.")
                    return []
        except Exception as e:
            print(f"DEBUG: Error loading data: {e}")
            return []

    def prepare_mood_trend(self, data):
        """Prepare mood frequency by date."""
        mood_by_date = {}

        for entry in data:
            mood = entry.get("detected_mood", "unknown")
            ts = entry.get("timestamp")
            if not ts:
                continue
            try:
                date = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").date()
            except ValueError:
                continue

            if date not in mood_by_date:
                mood_by_date[date] = Counter()
            mood_by_date[date][mood] += 1

        if not mood_by_date:
            print("DEBUG: No mood data found.")
            return None

        return mood_by_date

    def plot_mood_trends(self):
        """Return a Matplotlib Figure for embedding in Tkinter."""
        data = self._load_data()
        if not data:
            print("No feedback data found.")
            return None

        mood_by_date = self.prepare_mood_trend(data)
        if not mood_by_date:
            print("No mood trend data available.")
            return None

        # Prepare data for plotting
        dates = sorted(mood_by_date.keys())
        moods = set()
        for counts in mood_by_date.values():
            moods.update(counts.keys())

        # Create figure
        fig, ax = plt.subplots(figsize=(8, 5))
        for mood in moods:
            counts = [mood_by_date[d].get(mood, 0) for d in dates]
            ax.plot(dates, counts, marker="o", label=mood)

        ax.set_title("Mood Trend Over Time", fontsize=14)
        ax.set_xlabel("Date", fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        ax.legend(title="Detected Mood")
        ax.grid(True)
        fig.tight_layout()

        return fig


    def show_dashboard(self):
        """Display the mood trend dashboard."""
        data = self._load_data()
        if not data:
            print("No feedback data found.")
            return

        mood_by_date = self.prepare_mood_trend(data)
        if not mood_by_date:
            print("No mood trend data available.")
            return

        # Prepare data for plotting
        dates = sorted(mood_by_date.keys())
        moods = set()
        for counts in mood_by_date.values():
            moods.update(counts.keys())

        for mood in moods:
            counts = [mood_by_date[d].get(mood, 0) for d in dates]
            plt.plot(dates, counts, marker="o", label=mood)

        plt.title("Mood Trend Over Time", fontsize=14)
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Frequency", fontsize=12)
        plt.legend(title="Detected Mood")
        plt.grid(True)
        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    dashboard = MoodTrendDashboard(feedback_file="data/user_data.json")
    dashboard.show_dashboard()
