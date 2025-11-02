import json
import tkinter as tk
from tkinter import ttk, messagebox
from collections import Counter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AnalyticsDashboard(tk.Toplevel):
    def __init__(self, master=None, feedback_file="data/user_data.json"):
        super().__init__(master)
        self.title("User Analytics Dashboard")
        self.geometry("700x500")
        self.feedback_file = feedback_file

        ttk.Label(self, text="AI Codes Companion — Analytics Dashboard",
                  font=("Helvetica", 14, "bold")).pack(pady=10)

        self.summary_label = ttk.Label(self, text="", wraplength=600, justify="center")
        self.summary_label.pack(pady=10)

        self.canvas_frame = ttk.Frame(self)
        self.canvas_frame.pack(fill="both", expand=True)

        ttk.Button(self, text="Refresh", command=self.update_dashboard).pack(pady=5)
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=5)

        self.update_dashboard()

    def load_feedback(self):
        try:
            with open(self.feedback_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def summarize_data(self, data):
        liked_tones, disliked_tones, moods = [], [], []
        for entry in data:
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
            most_liked = Counter(liked_tones).most_common(1)[0][0]
            summary.append(f"Most liked tone: {most_liked}")
        if disliked_tones:
            most_disliked = Counter(disliked_tones).most_common(1)[0][0]
            summary.append(f"Most disliked tone: {most_disliked}")
        if moods:
            most_common_mood = Counter(moods).most_common(1)[0][0]
            summary.append(f"Common mood: {most_common_mood}")
        return "\n".join(summary) if summary else "No feedback data yet."

    def draw_chart(self, data):
        tones = [d.get("tone_used") for d in data if d.get("tone_used")]
        moods = [d.get("detected_mood") for d in data if d.get("detected_mood")]

        tone_counts = Counter(tones)
        mood_counts = Counter(moods)

        fig = Figure(figsize=(6, 3))
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        ax1.bar(tone_counts.keys(), tone_counts.values())
        ax1.set_title("Tone Feedback")
        ax2.bar(mood_counts.keys(), mood_counts.values(), color="orange")
        ax2.set_title("Mood Distribution")

        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_dashboard(self):
        data = self.load_feedback()
        self.summary_label.config(text=self.summarize_data(data))
        self.draw_chart(data)

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    dashboard = AnalyticsDashboard(root)
    dashboard.mainloop()
