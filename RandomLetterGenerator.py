import tkinter as tk
import random


class RandomLetterApp:
    def __init__(self, root, N):
        self.root = root
        self.root.title("Random Letter Display")
        self.label = tk.Label(root, font=("Helvetica", 150))
        self.label.pack(pady=160)

        custom_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "R", "S", "T", "U", "V", "Z"]
        
        # Map with all letters set to "unused"
        self.letters = {letter: "unused" for letter in custom_letters}
        self.current_letter = None
        
        # Number of segments
        self.N = N 
        self.current_cycle = 0
        # Bind space key to reset function
        self.root.bind("<space>", self.on_space_press)
        
        # Start the letter updating loop
        self.update_letter()

    def update_letter(self):
        # Filter out only unused letters
        unused_letters = [letter for letter, status in self.letters.items() if status == "unused"]

        if unused_letters:
            # Select a random unused letter
            self.current_letter = random.choice(unused_letters)
            self.label.config(text=self.current_letter,font=("Helvetica", 150) ,wraplength=200)
            self.label.pack(pady=160)
            self.label.update_idletasks() 

            # Mark it as used for the next cycle if space is not pressed
            self.letters[self.current_letter] = "used"
        else:
            self.current_cycle += 1
            if self.current_cycle < self.N:
                self.label.config(text="Kreće novi red.", font=("Helvetica", 50),wraplength=800)
                self.label.pack(pady=235)
                self.label.update_idletasks() 
                self.reset_letters()
            else:
                self.label.config(text="Gotovo!", font=("Helvetica", 50), wraplength=800)
                self.label.pack(pady=235)
                self.label.update_idletasks()
                self.root.after(2000, self.root.quit)  # Close app after showing final message

        # Schedule the next update after 1 second
        self.root.after(250, self.update_letter)

    def on_space_press(self, event):
        # Print the current letter
        if self.current_letter:
            if self.label.cget("text") != "Kreće novi red.":
                print("Current Letter:", self.current_letter)
        
       


    def reset_letters(self):
        custom_letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "R", "S", "T", "U", "V", "Z"]
        self.letters = {letter: "unused" for letter in custom_letters}

# Run the tkinter application
N = 1
root = tk.Tk()
root.geometry("1000x600")
app = RandomLetterApp(root, N)
root.mainloop()
