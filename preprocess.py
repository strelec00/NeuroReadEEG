import pandas as pd
import numpy as np
from scipy.signal import butter, filtfilt

# Load the CSV file
df = pd.read_csv("lsl_data.csv")

# Ensure the Stimulus column exists
df["Stimulus"] = 0  # Default to 0

# Identify where the letter changes and set Stimulus to 1
df["Stimulus"] = (df["Letter"] != df["Letter"].shift(1)).astype(int)

# Define bandpass filter (0.1 - 30 Hz)
def butter_bandpass(lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype="band")
    return b, a

def apply_filter(data, lowcut=0.1, highcut=30, fs=512, order=4):
    """ Apply bandpass filter to EEG channels """
    b, a = butter_bandpass(lowcut, highcut, fs, order)
    return filtfilt(b, a, data)

# Assume sampling rate (fs) is 512 Hz (change if different)
fs = 512

# Apply filter to each EEG channel
for channel in df.columns[1:-2]:  # Assuming EEG channels are in columns 1 to -2
    df[channel] = apply_filter(df[channel].values, fs=fs)

# Save preprocessed EEG data
df.to_csv("preprocessed_eeg.csv", index=False)

print("Preprocessing complete! Filtered EEG data saved as 'preprocessed_eeg.csv'.")
