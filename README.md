# RSVP Speed Reader

A beautiful, modern Rapid Serial Visual Presentation (RSVP) speed reading application.

## What is RSVP?

RSVP displays words one at a time at a fixed focal point, eliminating eye movement and allowing faster reading. The red highlighted letter marks the Optimal Recognition Point (ORP) where your eye naturally focuses.

## Features

- Modern dark interface with smooth controls
- Adjustable reading speed (60-1000 WPM)
- Optimal Recognition Point (ORP) highlighting in red
- Smart pacing (pauses longer for punctuation and long words)
- Progress bar tracking
- Load text files or paste custom text

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play / Pause |
| `→` | Next word |
| `←` | Previous word |
| `↑` | Increase speed (+25 WPM) |
| `↓` | Decrease speed (-25 WPM) |
| `R` | Reset to beginning |
| `O` | Open file |
| `V` | Paste text |
| `Esc` | Stop |

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python rsvp_reader.py
```

## Requirements

- Python 3.7+
- customtkinter
