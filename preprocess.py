import pandas as pd
from scipy.signal import butter, filtfilt
import numpy as np

fs = 512  # Sampling frequency

# Load the EEG data
lsl_df = pd.read_csv("lsl_data.csv")

# Ensure the "Letter" and "Stimulus" columns exist
if "Letter" not in lsl_df.columns:
    lsl_df["Letter"] = ""

if "Stimulus" not in lsl_df.columns:
    lsl_df["Stimulus"] = 0

# Load the letters file
letters_df = pd.read_csv("letter_timestamps.csv")

# Convert timestamps to numeric values
lsl_df["Timestamp"] = pd.to_numeric(lsl_df["Timestamp"], errors='coerce')
letters_df["First Timestamp"] = pd.to_numeric(letters_df["First Timestamp"], errors='coerce')

# Match the letters to EEG timestamps
for _, row in letters_df.iterrows():
    letter = row["Letter"]
    letter_timestamp = row["First Timestamp"]
    closest_index = (lsl_df["Timestamp"] - letter_timestamp).abs().idxmin()
    lsl_df.at[closest_index, "Letter"] = letter
    lsl_df.at[closest_index, "Stimulus"] = 1

# Define bandpass filter
def butter_bandpass(lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype="band")
    return b, a

def apply_filter(data, lowcut=1, highcut=30, fs=512, order=4):
    data = data - np.mean(data)  # Subtract the mean
    b, a = butter_bandpass(lowcut, highcut, fs, order)
    return filtfilt(b, a, data)

# Apply filter to EEG channels
for channel in lsl_df.columns[1:-2]:  # Assuming EEG channels are in columns 1 to -2
    lsl_df[channel] = apply_filter(lsl_df[channel].values, fs=fs)

# Save the preprocessed EEG data
lsl_df.to_csv("updated_lsl_data.csv", index=False)

print("Preprocessing complete. Data saved.")
