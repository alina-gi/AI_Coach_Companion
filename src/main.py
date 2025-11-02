import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
from datetime import datetime
import os
from textblob import TextBlob  # add this import at the top with others
from response_engine import ResponseEngine
from modules.analytical_hub import AnalyticsHub


class AICoachCompanion:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Coach Companion")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')

        # --- Load memory on startup ---
        self.memory_file = "data/memory.json"
        self.memory_data = self.load_memory()

        # --- Load user feedback data on startup ---
        self.user_data_file = "data/user_data.json"
        self.user_feedback = self.load_user_data()

        # --- Initialize Response Engine ---
        self.engine = ResponseEngine(mode="local")

        # Chat history
        self.chat_history = []

        # Short-term memory (stores last few messages)
        self.context_window = []
        self.max_context = 5  # how many past exchanges to remember

        
        # Track last tone used in Auto mode
        self.last_auto_tone = None

         # ✅ Define main frame FIRST
        self.main_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.main_frame.pack(fill="both", expand=True)

        analytics_btn = tk.Button(
    self.main_frame,
    text="📊",
    font=("Segoe UI", 11, "bold"),
    bg="#1e1e1e",
    fg="white",
    relief="flat",
    command=self.open_analytics_hub,
    width=3
)
        analytics_btn.pack(side="right", padx=10, pady=0)



        # UI setup
        self.setup_ui()

        # Welcome message
        self.add_message("AI Coach", "Hello! I'm your AI Coach Companion. How can I help you today?", "system")


    def open_analytics_hub(self):
        analytics_window = tk.Toplevel(self.root)
        AnalyticsHub(analytics_window)

    # ---------- MEMORY SYSTEM ----------
    def load_memory(self):
        """Load memory file if exists, otherwise create a new one"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    return json.load(f)
            except:
                return {"user_name": "Taiba", "entries": []}
        else:
            return {"user_name": "Taiba", "entries": []}

    def save_memory(self):
        """Save memory to JSON file"""
        with open(self.memory_file, "w") as f:
            json.dump(self.memory_data, f, indent=4)


    def load_user_data(self):
        """Safely load persisted user feedback data from JSON file."""
        try:
            if os.path.exists(self.user_data_file):
                with open(self.user_data_file, "r") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    return []
            else:
                # Ensure data directory exists
                os.makedirs(os.path.dirname(self.user_data_file), exist_ok=True)
                return []
        except Exception:
            # On any parse or IO error, start fresh but don't crash UI
            return []

    def save_user_data(self):
        """Safely persist user feedback list to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.user_data_file), exist_ok=True)
            with open(self.user_data_file, "w") as f:
                json.dump(self.user_feedback, f, indent=4)
        except Exception as e:
            print("User data save error:", e)

    def save_user_feedback_entry(self, user_message, ai_response, feedback, detected_mood, tone_used):
        """Append one feedback entry and persist to disk."""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_message": user_message,
            "ai_response": ai_response,
            "feedback": feedback,
            "detected_mood": detected_mood,
            "tone_used": tone_used
        }
        self.user_feedback.append(entry)
        self.save_user_data()

        self.engine.refresh_user_preferences()



    def detect_mood(self, message):
        """Detect mood using sentiment polarity (TextBlob)"""
        try:
            blob = TextBlob(message)
            polarity = blob.sentiment.polarity  # -1 (negative) → +1 (positive)
            
            if polarity > 0.2:
                return "happy"
            elif polarity < -0.2:
                return "sad"
            else:
                return "neutral"
        except Exception as e:
            print("Mood detection error:", e)
            return "neutral"

    
    def log_interaction(self, user_message, ai_response, mood="unknown"):
        """Store the chat into memory"""
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "input": user_message,
            "response": ai_response,
            "mood": mood,
            "tags": []
        }
        self.memory_data["entries"].append(entry)
        self.save_memory()

    
    def setup_ui(self):
        """Set up the user interface components"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="AI Coach Companion", 
                              font=("Arial", 16, "bold"), 
                              bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=(0, 10))
        
        # Chat display area
        self.setup_chat_area(main_frame)
        
        # Tone selector
        self.setup_tone_selector(main_frame)
        
        # Input area
        self.setup_input_area(main_frame)
        

    
    def setup_chat_area(self, parent):
        """Set up the chat display area"""
        # Chat frame
        chat_frame = tk.Frame(parent, bg='#f0f0f0')
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Chat label
        chat_label = tk.Label(chat_frame, text="Chat", 
                             font=("Arial", 12, "bold"), 
                             bg='#f0f0f0', fg='#34495e')
        chat_label.pack(anchor='w', pady=(0, 5))
        
        # Chat text area with scrollbar
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=70,
            height=20,
            font=("Arial", 10),
            bg='white',
            fg='#2c3e50',
            state=tk.DISABLED,
            padx=10,
            pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for different message types
        self.chat_display.tag_configure("user", foreground="#2980b9", font=("Arial", 10, "bold"))
        self.chat_display.tag_configure("ai", foreground="#27ae60", font=("Arial", 10, "bold"))
        self.chat_display.tag_configure("system", foreground="#7f8c8d", font=("Arial", 9, "italic"))
        self.chat_display.tag_configure("timestamp", foreground="#95a5a6", font=("Arial", 8))
    
    def setup_tone_selector(self, parent):
        """Set up the tone selector"""
        tone_frame = tk.Frame(parent, bg='#f0f0f0')
        tone_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Tone label
        tone_label = tk.Label(tone_frame, text="Tone:", 
                             font=("Arial", 10, "bold"), 
                             bg='#f0f0f0', fg='#34495e')
        tone_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Tone selection variable
        self.tone_var = tk.StringVar(value="Balanced")
        
        # Tone radio buttons
        tones = ["Blunt", "Balanced", "Empathetic", "Auto"]
        for tone in tones:
            rb = tk.Radiobutton(
                tone_frame,
                text=tone,
                variable=self.tone_var,
                value=tone,
                bg='#f0f0f0',
                font=("Arial", 9),
                command=self.on_tone_change
            )
            rb.pack(side=tk.LEFT, padx=(0, 15))
        
        # Add "Show Memory" button below the tone selector
        memory_button = tk.Button(
            tone_frame,
            text="Show Memory",
            command=self.show_memory_popup,
            font=("Arial", 9),
            bg='#95a5a6',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        memory_button.pack(side=tk.LEFT, padx=(20, 0))
        
        # Add "Export Memory" button next to Show Memory
        export_button = tk.Button(
            tone_frame,
            text="Export Memory",
            command=self.export_memory,
            font=("Arial", 9),
            bg='#16a085',
            fg='white',
            relief=tk.FLAT,
            padx=15,
            pady=5,
            cursor='hand2'
        )
        export_button.pack(side=tk.LEFT, padx=(10, 0))
    
    def setup_input_area(self, parent):
        """Set up the input area with text box and send button"""
        input_frame = tk.Frame(parent, bg='#f0f0f0')
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Input text box
        self.input_text = tk.Text(
            input_frame,
            height=3,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg='white',
            fg='#2c3e50',
            padx=10,
            pady=8
        )
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Send button
        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            font=("Arial", 10, "bold"),
            bg='#3498db',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Bind Enter key to send message
        self.input_text.bind('<Control-Return>', lambda e: self.send_message())
        
        # Focus on input text
        self.input_text.focus()
    
    def add_message(self, sender, message, message_type="user"):
        """Add a message to the chat display"""
        self.chat_display.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_display.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Add sender and message
        self.chat_display.insert(tk.END, f"{sender}: ", message_type)
        self.chat_display.insert(tk.END, f"{message}\n\n")
        
        # Scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Store in chat history
        self.chat_history.append({
            "timestamp": timestamp,
            "sender": sender,
            "message": message,
            "type": message_type
        })

    def render_feedback_controls(self, user_message, ai_response, detected_mood, tone_used):
        """Render Like/Dislike buttons inline after an AI response."""
        # Create a small frame to hold the buttons side-by-side
        btn_frame = tk.Frame(self.chat_display, bg='white')

        like_btn = tk.Button(
            btn_frame,
            text="👍 Like",
            font=("Arial", 9),
            bg='#ecf9f1',
            fg='#2c3e50',
            relief=tk.FLAT,
            cursor='hand2'
        )

        dislike_btn = tk.Button(
            btn_frame,
            text="👎 Dislike",
            font=("Arial", 9),
            bg='#fdecea',
            fg='#2c3e50',
            relief=tk.FLAT,
            cursor='hand2'
        )

        def on_click(choice):
            # Persist feedback
            self.save_user_feedback_entry(
                user_message=user_message,
                ai_response=ai_response,
                feedback=choice,
                detected_mood=detected_mood,
                tone_used=tone_used
            )
            # Disable buttons after selection to prevent duplicates
            like_btn.config(state=tk.DISABLED)
            dislike_btn.config(state=tk.DISABLED)

        like_btn.config(command=lambda: on_click("like"))
        dislike_btn.config(command=lambda: on_click("dislike"))

        like_btn.pack(side=tk.LEFT, padx=(0, 6))
        dislike_btn.pack(side=tk.LEFT)

        # Insert the frame into the text widget inline
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.window_create(tk.END, window=btn_frame)
        self.chat_display.insert(tk.END, "\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def send_message(self):
        """Handle sending a message"""
        message = self.input_text.get("1.0", tk.END).strip()
        
        if not message:
            return
        
        # Detect mood from user message
        detected_mood = self.detect_mood(message)
        
        # Add user message to chat
        self.add_message("You", message, "user")
        
        # Display detected mood in chat
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"[Mood: {detected_mood.capitalize()}] ", "system")
        self.chat_display.insert(tk.END, "\n\n")
        self.chat_display.config(state=tk.DISABLED)
        
        # Clear input
        self.input_text.delete("1.0", tk.END)
        
        # Simulate AI response based on tone
        self.generate_ai_response(message, detected_mood)
    
    def generate_ai_response(self, user_message, mood="neutral"):
        """Generate AI response using ResponseEngine with context memory + auto tone"""
        selected_tone = self.tone_var.get()

        # --- Auto tone logic ---
        if selected_tone == "Auto":
            mood_to_tone = {
                "happy": "Balanced",
                "sad": "Empathetic",
                "neutral": "Blunt",
                "angry": "Blunt",
                "stressed": "Empathetic"
            }
            tone = mood_to_tone.get(mood, "Balanced")

            if not hasattr(self, "last_auto_tone"):
                self.last_auto_tone = None

            if tone != self.last_auto_tone:
                self.add_message("System", f"Tone switched to {tone} (Auto mode)", "system")
                self.last_auto_tone = tone
        else:
            tone = selected_tone

        # --- Context memory logic ---
        context_text = "\n".join(
            [f"You: {msg['user']} | Coach: {msg['ai']}" for msg in getattr(self, 'context_window', [])]
        )
        combined_input = f"{context_text}\nYou: {user_message}"

        # --- Generate response ---
        response = self.engine.generate_response(combined_input, tone, mood)
        self.add_message("AI Coach", response, "ai")
        self.log_interaction(user_message, response, mood)

        # --- Render feedback buttons for this AI response ---
        try:
            self.render_feedback_controls(
                user_message=user_message,
                ai_response=response,
                detected_mood=mood,
                tone_used=tone
            )
        except Exception as e:
            # Don't let UI fail if rendering feedback controls has issues
            print("Feedback UI error:", e)

        # --- Update short-term memory ---
        if not hasattr(self, 'context_window'):
            self.context_window = []
            self.max_context = 5

        self.context_window.append({"user": user_message, "ai": response})
        if len(self.context_window) > self.max_context:
            self.context_window.pop(0)



    
    def get_blunt_response(self, message):
        """Generate a blunt, direct response"""
        responses = [
            "Let's cut to the chase. What's the real issue here?",
            "Stop overthinking this. Here's what you need to do:",
            "I'll be straight with you - that approach won't work.",
            "Time to be honest with yourself. What's really holding you back?",
            "No sugar-coating: you need to take action, not just talk about it."
        ]
        return responses[len(message) % len(responses)]
    
    def get_empathetic_response(self, message):
        """Generate an empathetic, understanding response"""
        responses = [
            "I can hear that this is really important to you. Let's work through this together.",
            "It sounds like you're going through a challenging time. I'm here to support you.",
            "I understand how difficult this must be for you. Let's take this step by step.",
            "Your feelings are completely valid. Let's explore what's really going on here.",
            "I can sense the weight of this situation. You're not alone in this journey."
        ]
        return responses[len(message) % len(responses)]
    
    def get_balanced_response(self, message):
        """Generate a balanced, professional response"""
        responses = [
            "That's an interesting perspective. Let me help you think through this systematically.",
            "I see what you're getting at. Let's break this down into manageable parts.",
            "Good point. Let's explore this further and see what options we have.",
            "I understand your concern. Here's how we can approach this together.",
            "That's a valid consideration. Let's work on finding a solution that works for you."
        ]
        return responses[len(message) % len(responses)]
    
    def on_tone_change(self):
        """Handle tone selection change"""
        tone = self.tone_var.get()
        # Reset Auto tracking when switching modes (to show tone on first Auto message)
        self.last_auto_tone = None
        self.add_message("System", f"Tone changed to: {tone}", "system")
    
    def show_memory_popup(self):
        """Display a popup window showing all memory entries"""
        # Create a new window
        popup = tk.Toplevel(self.root)
        popup.title("Memory Entries")
        popup.geometry("700x500")
        popup.configure(bg='#f0f0f0')
        
        # Center the popup window
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")
        
        # Title
        title_label = tk.Label(popup, text="Memory Entries", 
                              font=("Arial", 14, "bold"), 
                              bg='#f0f0f0', fg='#2c3e50')
        title_label.pack(pady=10)
        
        # Scrolled text area
        text_area = scrolledtext.ScrolledText(
            popup,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Arial", 9),
            bg='white',
            fg='#2c3e50',
            padx=10,
            pady=10,
            state=tk.DISABLED
        )
        text_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Configure text tags for formatting
        text_area.config(state=tk.NORMAL)
        text_area.tag_configure("header", font=("Arial", 10, "bold"), foreground="#2c3e50")
        text_area.tag_configure("timestamp", font=("Arial", 8, "italic"), foreground="#7f8c8d")
        text_area.tag_configure("user_msg", foreground="#2980b9")
        text_area.tag_configure("ai_msg", foreground="#27ae60")
        text_area.tag_configure("separator", foreground="#bdc3c7")
        
        # Display memory entries
        entries = self.memory_data.get("entries", [])
        if not entries:
            text_area.insert(tk.END, "No memory entries yet.\n", "header")
        else:
            for i, entry in enumerate(entries, 1):
                timestamp = entry.get("timestamp", "Unknown time")
                user_msg = entry.get("input", "")
                ai_msg = entry.get("response", "")
                mood = entry.get("mood", "unknown")
                
                # Entry header
                text_area.insert(tk.END, f"\nEntry #{i}\n", "header")
                text_area.insert(tk.END, f"Timestamp: {timestamp} | Mood: {mood.capitalize()}\n", "timestamp")
                text_area.insert(tk.END, "-" * 70 + "\n", "separator")
                
                # User message
                text_area.insert(tk.END, "You: ", "header")
                text_area.insert(tk.END, f"{user_msg}\n", "user_msg")
                
                # AI response
                text_area.insert(tk.END, "AI Coach: ", "header")
                text_area.insert(tk.END, f"{ai_msg}\n\n", "ai_msg")
        
        text_area.config(state=tk.DISABLED)
        
        # Close button
        close_button = tk.Button(
            popup,
            text="Close",
            command=popup.destroy,
            font=("Arial", 10, "bold"),
            bg='#e74c3c',
            fg='white',
            relief=tk.FLAT,
            padx=20,
            pady=5,
            cursor='hand2'
        )
        close_button.pack(pady=10)
    
    def export_memory(self):
        """Export memory data to a JSON file"""
        try:
            # Ask user where to save the file
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Memory"
            )
            
            # If user cancelled, do nothing
            if not filename:
                return
            
            # Save the memory data to the selected file
            with open(filename, "w") as f:
                json.dump(self.memory_data, f, indent=4)
            
            # Show success message
            messagebox.showinfo(
                "Export Successful",
                f"Memory data has been exported to:\n{filename}",
                icon="info"
            )
            
        except Exception as e:
            # Show error message if something goes wrong
            messagebox.showerror(
                "Export Error",
                f"An error occurred while exporting memory:\n{str(e)}",
                icon="error"
            )


def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = AICoachCompanion(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
