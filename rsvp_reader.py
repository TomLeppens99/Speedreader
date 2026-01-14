#!/usr/bin/env python3
"""
RSVP Speed Reader - Rapid Serial Visual Presentation
A clean, minimalist speed reading application.
"""

import tkinter as tk
from tkinter import filedialog, font
import re


class RSVPReader:
    def __init__(self, root):
        self.root = root
        self.root.title("RSVP Speed Reader")
        self.root.configure(bg='#000000')

        # Set window size and center it
        self.window_width = 1000
        self.window_height = 700
        self.center_window()

        # Reading state
        self.words = []
        self.current_index = 0
        self.is_playing = False
        self.wpm = 300
        self.min_wpm = 60
        self.max_wpm = 1000
        self.wpm_step = 30

        # Sample text
        self.default_text = """The quick brown fox jumps over the lazy dog.
        Speed reading is a technique that allows you to read faster while maintaining comprehension.
        RSVP presents words one at a time at a fixed focal point, eliminating the need for eye movement.
        This allows your brain to focus entirely on processing the words rather than tracking them across a page.
        With practice, you can significantly increase your reading speed and absorb information more efficiently."""

        self.setup_ui()
        self.setup_bindings()
        self.load_text(self.default_text)

    def center_window(self):
        """Center the window on screen."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    def setup_ui(self):
        """Create the user interface."""
        # Main container
        self.main_frame = tk.Frame(self.root, bg='#000000')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Top control bar
        self.control_frame = tk.Frame(self.main_frame, bg='#1a1a1a', height=50)
        self.control_frame.pack(fill=tk.X, side=tk.TOP)
        self.control_frame.pack_propagate(False)

        # Control buttons
        btn_style = {'bg': '#2a2a2a', 'fg': '#ffffff', 'relief': 'flat',
                     'padx': 15, 'pady': 5, 'font': ('Helvetica', 10)}

        self.open_btn = tk.Button(self.control_frame, text="Open File",
                                   command=self.open_file, **btn_style)
        self.open_btn.pack(side=tk.LEFT, padx=10, pady=10)

        self.paste_btn = tk.Button(self.control_frame, text="Paste Text",
                                    command=self.paste_text, **btn_style)
        self.paste_btn.pack(side=tk.LEFT, padx=5, pady=10)

        # Speed control
        speed_frame = tk.Frame(self.control_frame, bg='#1a1a1a')
        speed_frame.pack(side=tk.LEFT, padx=20, pady=10)

        self.slower_btn = tk.Button(speed_frame, text="−", width=3,
                                     command=self.decrease_speed, **btn_style)
        self.slower_btn.pack(side=tk.LEFT)

        self.speed_label = tk.Label(speed_frame, text=f"{self.wpm} WPM",
                                     bg='#1a1a1a', fg='#888888',
                                     font=('Helvetica', 11), width=10)
        self.speed_label.pack(side=tk.LEFT, padx=10)

        self.faster_btn = tk.Button(speed_frame, text="+", width=3,
                                     command=self.increase_speed, **btn_style)
        self.faster_btn.pack(side=tk.LEFT)

        # Play/Pause button
        self.play_btn = tk.Button(self.control_frame, text="▶ Play",
                                   command=self.toggle_play, **btn_style)
        self.play_btn.pack(side=tk.LEFT, padx=20, pady=10)

        # Reset button
        self.reset_btn = tk.Button(self.control_frame, text="↺ Reset",
                                    command=self.reset, **btn_style)
        self.reset_btn.pack(side=tk.LEFT, padx=5, pady=10)

        # Help label
        help_text = "Space: Play/Pause | ←→: Navigate | ↑↓: Speed | R: Reset | O: Open"
        self.help_label = tk.Label(self.control_frame, text=help_text,
                                    bg='#1a1a1a', fg='#555555',
                                    font=('Helvetica', 9))
        self.help_label.pack(side=tk.RIGHT, padx=15, pady=10)

        # Display area
        self.display_frame = tk.Frame(self.main_frame, bg='#000000')
        self.display_frame.pack(fill=tk.BOTH, expand=True)

        # Canvas for word display
        self.canvas = tk.Canvas(self.display_frame, bg='#000000',
                                 highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Progress bar at bottom
        self.progress_frame = tk.Frame(self.main_frame, bg='#1a1a1a', height=40)
        self.progress_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.progress_frame.pack_propagate(False)

        # Progress bar canvas
        self.progress_canvas = tk.Canvas(self.progress_frame, bg='#1a1a1a',
                                          height=4, highlightthickness=0)
        self.progress_canvas.pack(fill=tk.X, padx=20, pady=8)

        # Progress info
        self.progress_label = tk.Label(self.progress_frame, text="0 / 0 words",
                                        bg='#1a1a1a', fg='#555555',
                                        font=('Helvetica', 10))
        self.progress_label.pack(side=tk.LEFT, padx=20)

        # WPM display in corner
        self.wpm_display = tk.Label(self.progress_frame, text=f"{self.wpm} wpm",
                                     bg='#1a1a1a', fg='#444444',
                                     font=('Helvetica', 14))
        self.wpm_display.pack(side=tk.RIGHT, padx=20)

        # Bind canvas resize
        self.canvas.bind('<Configure>', self.on_resize)

    def setup_bindings(self):
        """Setup keyboard shortcuts."""
        self.root.bind('<space>', lambda e: self.toggle_play())
        self.root.bind('<Right>', lambda e: self.next_word())
        self.root.bind('<Left>', lambda e: self.prev_word())
        self.root.bind('<Up>', lambda e: self.increase_speed())
        self.root.bind('<Down>', lambda e: self.decrease_speed())
        self.root.bind('r', lambda e: self.reset())
        self.root.bind('R', lambda e: self.reset())
        self.root.bind('o', lambda e: self.open_file())
        self.root.bind('O', lambda e: self.open_file())
        self.root.bind('<Escape>', lambda e: self.stop())

    def get_orp_index(self, word):
        """
        Calculate the Optimal Recognition Point (ORP) index.
        This is the letter that should be highlighted in red.
        Typically slightly left of center for better recognition.
        """
        length = len(word)
        if length <= 1:
            return 0
        elif length <= 3:
            return 1
        elif length <= 5:
            return 1
        elif length <= 9:
            return 2
        elif length <= 13:
            return 3
        else:
            return 4

    def draw_word(self, word):
        """Draw the word on canvas with ORP highlighted."""
        self.canvas.delete('all')

        if not word:
            return

        # Get canvas dimensions
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            return

        center_x = canvas_width // 2
        center_y = canvas_height // 2

        # Font setup
        font_size = min(72, max(48, canvas_width // 15))
        word_font = font.Font(family='Georgia', size=font_size, weight='normal')

        # Get ORP index
        orp_index = self.get_orp_index(word)

        # Calculate character widths
        char_widths = []
        for char in word:
            char_widths.append(word_font.measure(char))

        total_width = sum(char_widths)

        # Calculate starting position so ORP letter is at center
        orp_center = sum(char_widths[:orp_index]) + char_widths[orp_index] // 2
        start_x = center_x - orp_center

        # Draw guide lines
        line_color = '#333333'
        line_y_top = center_y - font_size - 20
        line_y_bottom = center_y + 30

        # Horizontal lines
        self.canvas.create_line(0, line_y_top, canvas_width, line_y_top,
                                 fill=line_color, width=1)
        self.canvas.create_line(0, line_y_bottom, canvas_width, line_y_bottom,
                                 fill=line_color, width=1)

        # Vertical focus line
        self.canvas.create_line(center_x, line_y_top, center_x, line_y_top - 30,
                                 fill=line_color, width=1)
        self.canvas.create_line(center_x, line_y_bottom, center_x, line_y_bottom + 30,
                                 fill=line_color, width=1)

        # Draw each character
        current_x = start_x
        for i, char in enumerate(word):
            if i == orp_index:
                color = '#e63946'  # Red for ORP
            else:
                color = '#ffffff'  # White for others

            self.canvas.create_text(current_x, center_y, text=char,
                                     font=word_font, fill=color, anchor='w')
            current_x += char_widths[i]

    def update_progress(self):
        """Update progress bar and label."""
        total = len(self.words)
        current = self.current_index + 1 if self.words else 0

        self.progress_label.config(text=f"{current} / {total} words")

        # Draw progress bar
        self.progress_canvas.delete('all')
        canvas_width = self.progress_canvas.winfo_width()

        if total > 0 and canvas_width > 0:
            progress = current / total
            bar_width = int(canvas_width * progress)
            self.progress_canvas.create_rectangle(0, 0, bar_width, 4,
                                                   fill='#e63946', outline='')

    def load_text(self, text):
        """Load and parse text into words."""
        # Clean and split text
        text = re.sub(r'\s+', ' ', text.strip())
        self.words = [w for w in text.split() if w]
        self.current_index = 0
        self.is_playing = False
        self.play_btn.config(text="▶ Play")

        if self.words:
            self.draw_word(self.words[0])
        self.update_progress()

    def open_file(self):
        """Open a text file."""
        self.stop()
        file_path = filedialog.askopenfilename(
            title="Select a text file",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                self.load_text(text)
            except Exception as e:
                print(f"Error loading file: {e}")

    def paste_text(self):
        """Open dialog to paste text."""
        self.stop()

        dialog = tk.Toplevel(self.root)
        dialog.title("Paste Text")
        dialog.configure(bg='#1a1a1a')
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 600) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 400) // 2
        dialog.geometry(f"+{x}+{y}")

        label = tk.Label(dialog, text="Paste your text below:",
                          bg='#1a1a1a', fg='#ffffff', font=('Helvetica', 11))
        label.pack(pady=10)

        text_widget = tk.Text(dialog, bg='#2a2a2a', fg='#ffffff',
                               insertbackground='#ffffff',
                               font=('Helvetica', 11), wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        def on_load():
            text = text_widget.get('1.0', tk.END)
            if text.strip():
                self.load_text(text)
            dialog.destroy()

        btn_frame = tk.Frame(dialog, bg='#1a1a1a')
        btn_frame.pack(pady=10)

        load_btn = tk.Button(btn_frame, text="Load Text", command=on_load,
                              bg='#e63946', fg='#ffffff', relief='flat',
                              padx=20, pady=8, font=('Helvetica', 10))
        load_btn.pack(side=tk.LEFT, padx=10)

        cancel_btn = tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                                bg='#2a2a2a', fg='#ffffff', relief='flat',
                                padx=20, pady=8, font=('Helvetica', 10))
        cancel_btn.pack(side=tk.LEFT, padx=10)

        text_widget.focus_set()

    def toggle_play(self):
        """Toggle play/pause state."""
        if self.is_playing:
            self.stop()
        else:
            self.play()

    def play(self):
        """Start playing words."""
        if not self.words:
            return
        if self.current_index >= len(self.words):
            self.current_index = 0

        self.is_playing = True
        self.play_btn.config(text="⏸ Pause")
        self.show_next_word()

    def stop(self):
        """Stop playing."""
        self.is_playing = False
        self.play_btn.config(text="▶ Play")

    def show_next_word(self):
        """Display next word and schedule following one."""
        if not self.is_playing or self.current_index >= len(self.words):
            self.stop()
            return

        word = self.words[self.current_index]
        self.draw_word(word)
        self.update_progress()

        self.current_index += 1

        # Calculate delay based on WPM
        delay = int(60000 / self.wpm)

        # Add extra time for longer words and punctuation
        if len(word) > 8:
            delay = int(delay * 1.2)
        if word[-1] in '.!?':
            delay = int(delay * 1.5)
        elif word[-1] in ',;:':
            delay = int(delay * 1.2)

        self.root.after(delay, self.show_next_word)

    def next_word(self):
        """Go to next word (manual)."""
        if self.words and self.current_index < len(self.words) - 1:
            self.current_index += 1
            self.draw_word(self.words[self.current_index])
            self.update_progress()
        elif self.words and self.current_index == len(self.words) - 1:
            # At last word, show it
            self.draw_word(self.words[self.current_index])
            self.update_progress()

    def prev_word(self):
        """Go to previous word."""
        if self.words and self.current_index > 0:
            self.current_index -= 1
            self.draw_word(self.words[self.current_index])
            self.update_progress()

    def reset(self):
        """Reset to beginning."""
        self.stop()
        self.current_index = 0
        if self.words:
            self.draw_word(self.words[0])
        self.update_progress()

    def increase_speed(self):
        """Increase reading speed."""
        if self.wpm < self.max_wpm:
            self.wpm = min(self.max_wpm, self.wpm + self.wpm_step)
            self.update_speed_display()

    def decrease_speed(self):
        """Decrease reading speed."""
        if self.wpm > self.min_wpm:
            self.wpm = max(self.min_wpm, self.wpm - self.wpm_step)
            self.update_speed_display()

    def update_speed_display(self):
        """Update speed labels."""
        self.speed_label.config(text=f"{self.wpm} WPM")
        self.wpm_display.config(text=f"{self.wpm} wpm")

    def on_resize(self, event):
        """Handle window resize."""
        if self.words and 0 <= self.current_index < len(self.words):
            self.draw_word(self.words[self.current_index])


def main():
    root = tk.Tk()
    root.minsize(800, 500)
    app = RSVPReader(root)
    root.mainloop()


if __name__ == "__main__":
    main()
