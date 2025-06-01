
import sounddevice as sd
import numpy as np
import aubio
import tkinter as tk

samplerate = 44100
win_s = 2048
hop_s = 512

pitch_o = aubio.pitch("yin", win_s, hop_s, samplerate)
pitch_o.set_unit("Hz")
pitch_o.set_silence(-40)

note_freqs = {
    "E": 82.4,
    "A": 110.0,
    "D": 146.8,
    "G": 196.0,
    "B": 246.9,
    "e": 329.6,
}

tolerance = 2.0
note_name = "A"
target_freq = note_freqs[note_name]

root = tk.Tk()
root.title("Guitar Tuner")
root.geometry("600x400")
root.configure(bg="black")

label_note = tk.Label(root, text=f"String: {note_name} ({target_freq} Hz)", font=("Helvetica", 20), fg="white", bg="black")
label_note.pack(pady=10)

label_pitch = tk.Label(root, text="Detected: -- Hz", font=("Helvetica", 20), fg="white", bg="black")
label_pitch.pack(pady=10)

label_result = tk.Label(root, text="Status: --", font=("Helvetica", 24), fg="white", bg="black")
label_result.pack(pady=20)

frame_buttons = tk.Frame(root, bg="black")
frame_buttons.pack(pady=10)

def set_note(note):
    global note_name, target_freq
    note_name = note
    target_freq = note_freqs[note]
    label_note.config(text=f"String: {note} ({target_freq} Hz)")

for note in ["E", "A", "D", "G", "B", "e"]:
    btn = tk.Button(frame_buttons, text=note, font=("Helvetica", 16),
                    command=lambda n=note: set_note(n), width=5)
    btn.pack(side="left", padx=5)

def update_display(pitch, result):
    label_pitch.config(text=f"Detected: {pitch:.1f} Hz")
    label_result.config(text=f"Status: {result}")
    if result == "In tune":
        label_result.config(fg="green")
    elif result == "Too sharp":
        label_result.config(fg="red")
    elif result == "Too flat":
        label_result.config(fg="blue")
    else:
        label_result.config(fg="white")

def callback(indata, frames, time, status):
    global target_freq
    samples = np.mean(indata, axis=1)
    pitch = pitch_o(samples)[0]
    amplitude = np.sum(samples**2)/len(samples)

    if pitch < 30 or pitch > 500 or amplitude < 0.001:
        return

    diff = pitch - target_freq
    if diff > tolerance:
        result = "Too sharp"
    elif diff < -tolerance:
        result = "Too flat"
    else:
        result = "In tune"

    update_display(pitch, result)

def start_audio():
    with sd.InputStream(channels=1, callback=callback,
                        blocksize=hop_s, samplerate=samplerate):
        root.mainloop()

try:
    start_audio()
except KeyboardInterrupt:
    print("Tuner stopped.")
