# -------------------- analytics_hub.py --------------------
import tkinter as tk
from tkinter import ttk
from modules.preference_summary import PreferenceSummary
from modules.mood_trend_dashboard import MoodTrendDashboard
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class AnalyticsHub:
    def __init__(self, master):
        self.master = master
        self.master.title("AI Companion - Analytics Hub")
        self.master.geometry("900x600")
        self.master.configure(bg="#1e1e1e")

        # Notebook (Tabs)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(expand=True, fill="both")

        # Create frames for tabs
        self.summary_frame = ttk.Frame(self.notebook)
        self.trend_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.summary_frame, text="📊 Feedback Summary")
        self.notebook.add(self.trend_frame, text="📈 Mood Trends")

        # Load both dashboards
        self.load_summary_dashboard()
        self.load_trend_dashboard()

    # -------------------- SUMMARY TAB --------------------
    def load_summary_dashboard(self):
        tk.Label(
            self.summary_frame,
            text="User Preference Summary",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg="#1e1e1e"
        ).pack(pady=10)

        summary = PreferenceSummary(feedback_file="data/user_data.json")
        text_summary = summary.summarize()

        tk.Message(
            self.summary_frame,
            text=text_summary,
            width=800,
            font=("Segoe UI", 12),
            fg="#dddddd",
            bg="#1e1e1e",
            justify="center"
        ).pack(pady=20)

    # -------------------- TREND TAB --------------------
    def load_trend_dashboard(self):
        tk.Label(
            self.trend_frame,
            text="Mood Trend Visualization",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg="#1e1e1e"
        ).pack(pady=10)

        trend = MoodTrendDashboard(feedback_file="data/user_data.json")
        fig = trend.plot_mood_trends()

        if fig:
            canvas = FigureCanvasTkAgg(fig, master=self.trend_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            tk.Label(
                self.trend_frame,
                text="No data available yet to visualize mood trends.",
                font=("Segoe UI", 12),
                fg="#bbbbbb",
                bg="#1e1e1e"
            ).pack(pady=20)


# -------------------- MAIN --------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = AnalyticsHub(root)
    root.mainloop()
