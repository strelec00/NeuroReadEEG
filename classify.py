import numpy as np
import pandas as pd
import mne

from scipy.signal import find_peaks

# Load the CSV data
df = pd.read_csv('updated_lsl_data.csv')

# Extract EEG data from Channels (excluding Timestamp, Stimulus, and Letter)
channel_names = df.columns[1:17].tolist()  # Channels: Channel1, Channel2, Channel3, Channel4
data = df[channel_names].values  # Shape must be (n_samples, n_channels)

# Create MNE Raw object
sfreq = 512  # Sampling frequency of the EEG data
info = mne.create_info(ch_names=channel_names, sfreq=sfreq, ch_types="eeg")
raw = mne.io.RawArray(data.T, info)  # Transpose the data (channels as rows)

# Filter the data to isolate P300 response (1-30 Hz)
raw.filter(1, 30, fir_design='firwin')

# Create events based on Stimulus (only consider events where Stimulus == 1)
stimulus_array = df['Stimulus'].values.astype(int)
event_indices = np.where(stimulus_array == 1)[0]  # Find indices where stimulus is 1
events = np.column_stack((event_indices, np.zeros(len(event_indices), dtype=int), stimulus_array[event_indices]))
events = events.astype(int)

# Define event ID (1 for stimulus)
event_id = {"Stimulus": 1}

# Epoch the data around stimulus events (-200ms to 800ms to capture P300)
epochs = mne.Epochs(raw, events, event_id, tmin=0.0, tmax=0.8, baseline=(None, None), preload=True)

# Extract the epoch data (EEG data around each event)
X = epochs.get_data()  # Shape: (n_epochs, n_channels, n_times)

# Reshape X to a 2D array (n_epochs, n_features) for analysis
X = X.reshape(X.shape[0], -1)  # Flatten each epoch into a single row

# Assign a unique ID to each occurrence of a letter
letter_occurrences = []
unique_letter_counter = {letter: 0 for letter in df['Letter'].unique()}
for idx in event_indices:
    letter = df['Letter'].iloc[idx]
    unique_letter_counter[letter] += 1
    # Create a unique ID by combining the letter and its occurrence number
    unique_id = f"{letter}_{unique_letter_counter[letter]}"
    letter_occurrences.append(unique_id)

# Ensure that y matches the number of epochs
assert len(letter_occurrences) == len(X), "The number of epochs and labels must match!"

# Use these unique IDs as the target variable
y = np.array(letter_occurrences)


# Now let's use peak detection to identify the P300 response around each event
# Peak detection function using dynamic threshold based on standard deviation

def detect_p300(epochs_data, threshold_factor=3.5):
    """Detects P300 peak using standard deviation-based threshold."""
    p300_peak_labels = []

    # Calculate the standard deviation across all channels and timepoints for each epoch
    for epoch in epochs_data:
        epoch_std = np.std(epoch)
        threshold = threshold_factor * epoch_std  # Set the threshold based on standard deviation

        # Find the maximum absolute value in the epoch (this is where we look for P300)
        peak_value = np.max(np.abs(epoch))

        # If the peak exceeds the threshold, classify it as a P300 response
        if peak_value > threshold:
            p300_peak_labels.append(1)  # P300 detected
        else:
            p300_peak_labels.append(0)  # No P300 detected

    return np.array(p300_peak_labels)


# Detect P300 for each epoch using dynamic threshold based on standard deviation
p300_labels = detect_p300(X)

# Create a mapping for the predicted labels (0 or 1) to the letter occurrences
# Since we are detecting the peak in the EEG, we will map the detected peaks to the letter occurrence
letter_predictions = []
for idx, label in zip(event_indices, p300_labels):
    letter = df['Letter'].iloc[idx]
    letter_predictions.append(letter if label == 1 else None)  # Only add letter if peak detected

# Now, we need to group predictions into batches of 22 and select the most likely letter
batch_size = 22
num_batches = len(letter_predictions) // batch_size  # Number of full batches of 22 predictions

# Split predictions into batches of 22 (or less for the final batch if needed)
batches = [letter_predictions[i * batch_size: (i + 1) * batch_size] for i in range(num_batches)]

# Majority voting for the batch
batch_predictions = []
for batch in batches:
    # Remove None values from the batch (since no letter was predicted for those events)
    filtered_batch = [letter for letter in batch if letter is not None]
    if len(filtered_batch) > 0:
        most_likely_letter = pd.Series(filtered_batch).mode()[0]  # Majority voting for the batch
    else:
        most_likely_letter = None  # If no letter was predicted, no majority vote
    batch_predictions.append(most_likely_letter)

# Print the predictions for each batch
print("Predicted letters for each batch:")
for i, predicted_batch in enumerate(batch_predictions, start=1):
    print(f"Batch {i}: {predicted_batch}")
