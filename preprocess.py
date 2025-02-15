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

# Segment the signal into epochs
epochs = []
stimulus_indices = lsl_df[lsl_df["Stimulus"] == 1].index

for idx in stimulus_indices:
    start = idx - int(0.2 * fs)  # 200 ms before the stimulus
    end = idx + int(0.8 * fs)    # 800 ms after the stimulus
    if start >= 0 and end < len(lsl_df):
        epoch = lsl_df.iloc[start:end, 1:-2].values  # Exclude non-EEG columns
        epochs.append(epoch)

epochs = np.array(epochs)

# Normalize the data
from sklearn.preprocessing import StandardScaler
X = epochs.reshape(epochs.shape[0], -1)  # Flatten epochs
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Save the processed epochs for classification
np.save('processed_epochs.npy', epochs)

print("Preprocessing complete. Data saved.")
