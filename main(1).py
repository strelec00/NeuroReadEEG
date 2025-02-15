import random
import tkinter as tk
from pylsl import StreamInlet, resolve_stream
import csv
import threading
import time
import os

print(f"Data is saved in: {os.getcwd()}")

class RandomLetterApp:
    def __init__(self, root, marker_dict, lock, max_updates=4, markers_file="markers.csv"):
        self.root = root
        self.root.title("Random Letter Display")
        self.label = tk.Label(root, font=("Helvetica", 150))
        self.label.pack(pady=160)

        self.custom_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "R", "S",
                               "T", "U", "V", "Z"]
        self.letter_id = 0  # ID that increments with each letter display
        self.update_counter = 0
        self.max_updates = max_updates
        self.marker_dict = marker_dict
        self.lock = lock

        # Set up markers file for writing
        self.markers_file = markers_file
        self.file = open(self.markers_file, mode='w', newline='')
        self.writer = csv.DictWriter(self.file, fieldnames=["ID", "Letter"])
        self.writer.writeheader()

        self.letters = {letter: "unused" for letter in self.custom_letters}
        self.current_letter = None

        self.update_letter()

    def add_marker(self, letter):
        self.letter_id += 1  # Increment ID each time a letter is displayed
        with self.lock:
            self.marker_dict[self.letter_id] = letter  # Store letter with the new ID
        print(f"Marker added: {self.letter_id} - {letter}")

        self.writer.writerow({"ID": self.letter_id, "Letter": letter})

    def update_letter(self):
        if self.update_counter >= self.max_updates:
            self.label.config(text="App Stopped.", font=("Helvetica", 50), wraplength=800)
            self.label.update_idletasks()
            print("Maximum updates reached. Stopping the app.")
            self.root.quit()
            self.file.close()
            return

        unused_letters = [letter for letter, status in self.letters.items() if status == "unused"]

        if unused_letters:
            self.current_letter = random.choice(unused_letters)
            self.label.config(text=self.current_letter, font=("Helvetica", 150), wraplength=200)
            self.label.update_idletasks()
            self.letters[self.current_letter] = "used"

            self.add_marker(self.current_letter)
        else:
            self.label.config(text="Kreće novi red.", font=("Helvetica", 50), wraplength=800)
            self.label.update_idletasks()
            self.reset_letters()
            self.update_counter += 1

        self.root.after(1000, self.update_letter)

    def reset_letters(self):
        self.letters = {letter: "unused" for letter in self.custom_letters}

    def save_markers_to_file(self):
        print(f"Markers saved to {self.markers_file}")

def process_lsl_data(marker_dict, lock):
    print("Looking for an EEG stream...")
    streams = resolve_stream('type', 'EEG')
    inlet = StreamInlet(streams[0])

    with open('lsl_data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Timestamp", "Channel1", "Channel2", "Channel3", "Channel4", "Channel5", "Channel6", "Channel7",
             "Channel8", "Channel9", "Channel10", "Channel11", "Channel12", "Channel13", "Channel14", "Channel15",
             "Channel16", "Stimulus", "Letter"])

        print("Receiving data...")
        counterid = 0
        counter = 0
        last_id = 0
        last_letter = "NoLetter"

        try:
            while True:
                sample, lsl_timestamp = inlet.pull_sample()
                current_timestamp = time.time()
                stimulus = 0

                if int(counter) % 512 == 0:
                    counterid += 1

                with lock:
                    if last_id < counterid and counterid in marker_dict:
                        last_letter = marker_dict[counterid]
                        last_id = counterid

                writer.writerow([current_timestamp] + sample + [stimulus, last_letter])
                file.flush()  # **Force data to be written immediately**
                counter += 1

        except KeyboardInterrupt:
            print("\nData collection stopped.")
            file.flush()  # **Ensure all data is written**


def main():
    root = tk.Tk()
    root.geometry("1000x600")

    marker_dict = {}
    lock = threading.Lock()

    app = RandomLetterApp(root, marker_dict, lock, max_updates=4)

    lsl_thread = threading.Thread(target=process_lsl_data, args=(marker_dict, lock), daemon=True)
    lsl_thread.start()

    root.mainloop()
    app.save_markers_to_file()

if __name__ == "__main__":
    main()
