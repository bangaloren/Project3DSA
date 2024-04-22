import os
import pandas as pd
import allosaurus.app
from concurrent.futures import ProcessPoolExecutor


#based off of https://stackoverflow.com/questions/76421767/automatic-separation-between-consonants-and-vowels-in-speech-recording
def parse_timestamp_output(output):
    """
    Parses the timestamp output from the phoneme recognition model.
    """
    records = []
    lines = output.split('\n')
    for line in lines:
        if line.strip():  # Ensure the line is not empty
            tok = line.split(' ')
            start = float(tok[0])
            duration = float(tok[1])
            end = start + duration
            label = tok[2]
            records.append(dict(start=start, end=end, label=label))
    df = pd.DataFrame.from_records(records)
    return df


def phone_recognize_file(path, emit=1.2, lang='kan')->pd.DataFrame:
    """
    Recognizes phonemes from an audio file and returns them along with timestamps.
    """
    model = allosaurus.app.read_recognizer()
    out = model.recognize(path, lang, timestamp=True, emit=emit)
    phones = parse_timestamp_output(out)
    return phones


def get_output_path(input_path):
    """
    Modifies the input path for the output CSV file.
    """
    # Split the path and modify it for the output
    parts = os.path.split(input_path)
    new_dir = parts[0] + '_trans'
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)
    new_path = os.path.join(new_dir, os.path.splitext(parts[1])[0] + '.csv')
    return new_path


def phoneme_time_diff_to_csv(audio_path):
    """
    Processes the audio file to recognize phonemes, calculates the time difference between them,
    and stores the resulting table as a CSV file in a new folder.
    """
    # Process the audio file
    phoneme_df = phoneme_time_diff(audio_path)

    # Get the output CSV file path
    csv_path = get_output_path(audio_path)

    # Save the DataFrame to CSV
    phoneme_df.to_csv(csv_path, index=False)


def phoneme_time_diff(audio_path):
    """
    Takes an audio file path, processes it to recognize phonemes, and calculates
    the time difference between consecutive phonemes.
    Returns a pandas DataFrame with phonemes and the time difference.
    """
    # Recognize phonemes from the audio file
    phones_df = phone_recognize_file(audio_path)

    # Calculate time differences between consecutive phonemes
    phones_df['time_diff'] = phones_df['start'].diff().fillna(0)

    # Select and rename columns for the final DataFrame
    final_df = phones_df[['label', 'time_diff']].rename(columns={'label': 'Phoneme'})

    return final_df


def process_single_file(audio_path):
    """
    Wrapper function that calls phoneme_time_diff_to_csv for a single file.
    Designed to be used with concurrent processing.
    """
    print(f"Processing {audio_path}...")
    phoneme_time_diff_to_csv(audio_path)


def process_folder_and_save(folder_path):
    """
    Processes all audio files in the given folder in parallel, recognizes phonemes,
    calculates time differences, and saves the results in CSV files in a new folder.
    Utilizes multiprocessing to parallelize the task across CPU cores.
    Skips files that have already been processed.
    """
    # Check if the folder exists
    if not os.path.exists(folder_path):
        print(f"Folder {folder_path} does not exist.")
        return

    output_folder=folder_path+"_trans"

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Get a list of all WAV files in the folder
    audio_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.wav')]

    # Prepare a list of audio files that need processing
    to_process_files = []

    for audio_file in audio_files:
        # Construct the expected output file path
        output_file_path = os.path.join(output_folder, os.path.basename(audio_file)[:-4] + '.csv')
        # Check if the output file already exists
        if not os.path.exists(output_file_path):
            # If not, add to the list of files to process
            to_process_files.append(audio_file)
        else:
            print(f"Skipping {audio_file}, already processed.")

    # Number of workers is usually set to the number of CPU cores available
    num_workers = 2

    # Using ProcessPoolExecutor to run tasks in parallel
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # map function blocks until all tasks are completed
        executor.map(process_single_file, to_process_files)

    print("All files have been processed.")


if __name__=="__main__":
    folder_path = '../data/kn_in_male'
    process_folder_and_save(folder_path)
    folder_path = '../data/kn_in_female'
    process_folder_and_save(folder_path)
    folder_path = '../data/mile_kannada_test/test/audio_files'
    process_folder_and_save(folder_path)