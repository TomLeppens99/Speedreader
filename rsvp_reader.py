#!/usr/bin/env python3
"""
RSVP Speed Reader - Rapid Serial Visual Presentation
A beautiful, modern speed reading application.
"""

import customtkinter as ctk
from tkinter import filedialog, font as tkfont
import re


class RSVPReader(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title("RSVP Reader")
        self.configure(fg_color="#0a0a0a")

        # Window setup
        self.window_width = 1100
        self.window_height = 750
        self.center_window()

        # Reading state
        self.words = []
        self.current_index = 0
        self.is_playing = False
        self.wpm = 300
        self.min_wpm = 60
        self.max_wpm = 1000

        # Colors
        self.bg_color = "#0a0a0a"
        self.accent_color = "#e63946"
        self.text_color = "#f1f1f1"
        self.muted_color = "#4a4a4a"
        self.surface_color = "#141414"

        # Sample text
        self.default_text = """The art of reading quickly is not about rushing through words,
        but about training your eyes and mind to work more efficiently together.
        RSVP technology presents words at a single focal point, eliminating the need
        for your eyes to move across a page. This allows your brain to focus entirely
        on comprehension rather than the mechanical process of tracking text.
        With practice, most readers can double or even triple their reading speed
        while maintaining excellent comprehension. The key is the red focal point,
        which marks the optimal recognition point of each word. Start slow,
        find your comfortable pace, then gradually increase the speed as you adapt."""

        self.setup_ui()
        self.setup_bindings()
        self.load_text(self.default_text)

    def center_window(self):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        self.minsize(900, 600)

    def setup_ui(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color=self.bg_color)
        self.main_frame.pack(fill="both", expand=True)

        # Top spacer
        ctk.CTkFrame(self.main_frame, fg_color=self.bg_color, height=20).pack(fill="x")

        # Control bar
        self.control_frame = ctk.CTkFrame(self.main_frame, fg_color=self.surface_color,
                                           corner_radius=12, height=60)
        self.control_frame.pack(fill="x", padx=40, pady=(0, 20))
        self.control_frame.pack_propagate(False)

        # Left controls
        left_frame = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        left_frame.pack(side="left", padx=20, pady=12)

        self.open_btn = ctk.CTkButton(left_frame, text="Open", width=80,
                                       height=36, corner_radius=8,
                                       fg_color="#1f1f1f", hover_color="#2a2a2a",
                                       command=self.open_file)
        self.open_btn.pack(side="left", padx=(0, 8))

        self.paste_btn = ctk.CTkButton(left_frame, text="Paste", width=80,
                                        height=36, corner_radius=8,
                                        fg_color="#1f1f1f", hover_color="#2a2a2a",
                                        command=self.paste_text)
        self.paste_btn.pack(side="left")

        # Center controls (play/speed)
        center_frame = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        center_frame.pack(side="left", expand=True, pady=12)

        # Speed control
        speed_container = ctk.CTkFrame(center_frame, fg_color="transparent")
        speed_container.pack(side="left", padx=20)

        self.slower_btn = ctk.CTkButton(speed_container, text="−", width=36,
                                         height=36, corner_radius=8,
                                         fg_color="#1f1f1f", hover_color="#2a2a2a",
                                         font=ctk.CTkFont(size=18),
                                         command=self.decrease_speed)
        self.slower_btn.pack(side="left")

        self.speed_label = ctk.CTkLabel(speed_container, text="300",
                                         font=ctk.CTkFont(family="SF Mono, Menlo, monospace", size=16, weight="bold"),
                                         text_color=self.text_color, width=60)
        self.speed_label.pack(side="left", padx=12)

        self.faster_btn = ctk.CTkButton(speed_container, text="+", width=36,
                                         height=36, corner_radius=8,
                                         fg_color="#1f1f1f", hover_color="#2a2a2a",
                                         font=ctk.CTkFont(size=18),
                                         command=self.increase_speed)
        self.faster_btn.pack(side="left")

        wpm_label = ctk.CTkLabel(speed_container, text="wpm",
                                  font=ctk.CTkFont(size=12),
                                  text_color=self.muted_color)
        wpm_label.pack(side="left", padx=(4, 0))

        # Play button
        self.play_btn = ctk.CTkButton(center_frame, text="▶", width=50,
                                       height=36, corner_radius=8,
                                       fg_color=self.accent_color,
                                       hover_color="#c1303c",
                                       font=ctk.CTkFont(size=14),
                                       command=self.toggle_play)
        self.play_btn.pack(side="left", padx=10)

        # Reset button
        self.reset_btn = ctk.CTkButton(center_frame, text="↺", width=40,
                                        height=36, corner_radius=8,
                                        fg_color="#1f1f1f", hover_color="#2a2a2a",
                                        font=ctk.CTkFont(size=16),
                                        command=self.reset)
        self.reset_btn.pack(side="left")

        # Right - shortcuts hint
        right_frame = ctk.CTkFrame(self.control_frame, fg_color="transparent")
        right_frame.pack(side="right", padx=20, pady=12)

        shortcuts = ctk.CTkLabel(right_frame, text="Space: Play  ←→: Nav  ↑↓: Speed",
                                  font=ctk.CTkFont(size=11),
                                  text_color="#3a3a3a")
        shortcuts.pack()

        # Display canvas area
        self.canvas_frame = ctk.CTkFrame(self.main_frame, fg_color=self.bg_color)
        self.canvas_frame.pack(fill="both", expand=True, padx=40)

        # Use tkinter canvas for word rendering
        import tkinter as tk
        self.canvas = tk.Canvas(self.canvas_frame, bg=self.bg_color,
                                 highlightthickness=0, cursor="none")
        self.canvas.pack(fill="both", expand=True)

        # Bottom bar
        self.bottom_frame = ctk.CTkFrame(self.main_frame, fg_color=self.bg_color, height=80)
        self.bottom_frame.pack(fill="x", padx=40, pady=(20, 30))
        self.bottom_frame.pack_propagate(False)

        # Progress container
        progress_container = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        progress_container.pack(fill="x", pady=(0, 15))

        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(progress_container, height=3,
                                                corner_radius=2,
                                                fg_color="#1a1a1a",
                                                progress_color=self.accent_color)
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)

        # Bottom info row
        info_frame = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        info_frame.pack(fill="x")

        self.progress_label = ctk.CTkLabel(info_frame, text="0 of 0",
                                            font=ctk.CTkFont(size=13),
                                            text_color=self.muted_color)
        self.progress_label.pack(side="left")

        self.wpm_display = ctk.CTkLabel(info_frame, text="300 wpm",
                                         font=ctk.CTkFont(family="SF Mono, Menlo, monospace", size=15),
                                         text_color="#2a2a2a")
        self.wpm_display.pack(side="right")

        # Bind canvas resize
        self.canvas.bind('<Configure>', self.on_resize)

    def setup_bindings(self):
        self.bind('<space>', lambda e: self.toggle_play())
        self.bind('<Right>', lambda e: self.next_word())
        self.bind('<Left>', lambda e: self.prev_word())
        self.bind('<Up>', lambda e: self.increase_speed())
        self.bind('<Down>', lambda e: self.decrease_speed())
        self.bind('r', lambda e: self.reset())
        self.bind('R', lambda e: self.reset())
        self.bind('o', lambda e: self.open_file())
        self.bind('O', lambda e: self.open_file())
        self.bind('<Escape>', lambda e: self.stop())
        self.bind('v', lambda e: self.paste_text())
        self.bind('V', lambda e: self.paste_text())

    def get_orp_index(self, word):
        """Calculate the Optimal Recognition Point index."""
        # Strip punctuation for calculation
        clean = re.sub(r'[^\w]', '', word)
        length = len(clean)

        if length <= 1:
            return 0
        elif length == 2:
            return 0
        elif length == 3:
            return 1
        elif length <= 5:
            return 1
        elif length <= 7:
            return 2
        elif length <= 11:
            return 3
        else:
            return 4

    def draw_word(self, word):
        """Draw word with ORP highlighting."""
        self.canvas.delete('all')

        if not word:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:
            return

        center_x = canvas_width // 2
        center_y = canvas_height // 2

        # Font
        font_size = min(68, max(52, canvas_width // 16))
        try:
            word_font = tkfont.Font(family='Georgia', size=font_size)
        except:
            word_font = tkfont.Font(family='Times', size=font_size)

        # Calculate ORP
        orp_index = self.get_orp_index(word)

        # Get character measurements
        char_widths = [word_font.measure(c) for c in word]
        total_width = sum(char_widths)

        # Position so ORP letter is centered
        if orp_index < len(char_widths):
            orp_center = sum(char_widths[:orp_index]) + char_widths[orp_index] // 2
        else:
            orp_center = total_width // 2
        start_x = center_x - orp_center

        # Draw guide elements
        guide_color = "#252525"
        line_height = font_size + 30

        # Horizontal guides
        self.canvas.create_line(40, center_y - line_height // 2,
                                 canvas_width - 40, center_y - line_height // 2,
                                 fill=guide_color, width=1)
        self.canvas.create_line(40, center_y + line_height // 2,
                                 canvas_width - 40, center_y + line_height // 2,
                                 fill=guide_color, width=1)

        # Vertical focus indicator
        tick_length = 25
        self.canvas.create_line(center_x, center_y - line_height // 2,
                                 center_x, center_y - line_height // 2 - tick_length,
                                 fill=guide_color, width=1)
        self.canvas.create_line(center_x, center_y + line_height // 2,
                                 center_x, center_y + line_height // 2 + tick_length,
                                 fill=guide_color, width=1)

        # Draw characters
        current_x = start_x
        baseline_y = center_y + font_size // 4

        for i, char in enumerate(word):
            color = self.accent_color if i == orp_index else self.text_color
            self.canvas.create_text(current_x, baseline_y, text=char,
                                     font=word_font, fill=color, anchor='w')
            current_x += char_widths[i]

    def update_progress(self):
        """Update progress indicators."""
        total = len(self.words)
        current = self.current_index + 1 if self.words else 0

        self.progress_label.configure(text=f"{current} of {total}")

        if total > 0:
            self.progress_bar.set(current / total)
        else:
            self.progress_bar.set(0)

    def load_text(self, text):
        """Parse and load text."""
        text = re.sub(r'\s+', ' ', text.strip())
        self.words = [w for w in text.split() if w]
        self.current_index = 0
        self.is_playing = False
        self.play_btn.configure(text="▶")

        if self.words:
            self.draw_word(self.words[0])
        self.update_progress()

    def open_file(self):
        """Open text file dialog."""
        self.stop()
        file_path = filedialog.askopenfilename(
            title="Open Text File",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.load_text(f.read())
            except Exception as e:
                print(f"Error: {e}")

    def paste_text(self):
        """Show paste dialog."""
        self.stop()

        dialog = ctk.CTkToplevel(self)
        dialog.title("Paste Text")
        dialog.geometry("650x450")
        dialog.configure(fg_color=self.surface_color)
        dialog.transient(self)
        dialog.grab_set()

        # Center
        dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - 650) // 2
        y = self.winfo_y() + (self.winfo_height() - 450) // 2
        dialog.geometry(f"+{x}+{y}")

        # Header
        header = ctk.CTkLabel(dialog, text="Paste your text",
                               font=ctk.CTkFont(size=18, weight="bold"),
                               text_color=self.text_color)
        header.pack(pady=(25, 15))

        # Text area
        text_frame = ctk.CTkFrame(dialog, fg_color="#0a0a0a", corner_radius=10)
        text_frame.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        text_widget = ctk.CTkTextbox(text_frame, fg_color="#0a0a0a",
                                      text_color=self.text_color,
                                      font=ctk.CTkFont(size=14),
                                      corner_radius=10)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)

        # Buttons
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=(0, 25))

        def on_load():
            text = text_widget.get("1.0", "end")
            if text.strip():
                self.load_text(text)
            dialog.destroy()

        load_btn = ctk.CTkButton(btn_frame, text="Load Text", width=120,
                                  height=40, corner_radius=8,
                                  fg_color=self.accent_color,
                                  hover_color="#c1303c",
                                  command=on_load)
        load_btn.pack(side="left", padx=8)

        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", width=100,
                                    height=40, corner_radius=8,
                                    fg_color="#1f1f1f", hover_color="#2a2a2a",
                                    command=dialog.destroy)
        cancel_btn.pack(side="left", padx=8)

        text_widget.focus_set()

    def toggle_play(self):
        if self.is_playing:
            self.stop()
        else:
            self.play()

    def play(self):
        if not self.words:
            return
        if self.current_index >= len(self.words):
            self.current_index = 0

        self.is_playing = True
        self.play_btn.configure(text="⏸")
        self.show_next_word()

    def stop(self):
        self.is_playing = False
        self.play_btn.configure(text="▶")

    def show_next_word(self):
        if not self.is_playing or self.current_index >= len(self.words):
            self.stop()
            return

        word = self.words[self.current_index]
        self.draw_word(word)
        self.update_progress()
        self.current_index += 1

        # Calculate delay
        delay = int(60000 / self.wpm)

        # Adjust for word characteristics
        if len(word) > 8:
            delay = int(delay * 1.2)
        if word and word[-1] in '.!?':
            delay = int(delay * 1.5)
        elif word and word[-1] in ',;:':
            delay = int(delay * 1.2)

        self.after(delay, self.show_next_word)

    def next_word(self):
        if self.words and self.current_index < len(self.words) - 1:
            self.current_index += 1
            self.draw_word(self.words[self.current_index])
            self.update_progress()

    def prev_word(self):
        if self.words and self.current_index > 0:
            self.current_index -= 1
            self.draw_word(self.words[self.current_index])
            self.update_progress()

    def reset(self):
        self.stop()
        self.current_index = 0
        if self.words:
            self.draw_word(self.words[0])
        self.update_progress()

    def increase_speed(self):
        self.wpm = min(self.max_wpm, self.wpm + 25)
        self.update_speed_display()

    def decrease_speed(self):
        self.wpm = max(self.min_wpm, self.wpm - 25)
        self.update_speed_display()

    def update_speed_display(self):
        self.speed_label.configure(text=str(self.wpm))
        self.wpm_display.configure(text=f"{self.wpm} wpm")

    def on_resize(self, event):
        if self.words and 0 <= self.current_index < len(self.words):
            self.draw_word(self.words[self.current_index])


def main():
    app = RSVPReader()
    app.mainloop()


if __name__ == "__main__":
    main()
