import os

import pandas as pd



def combine_csv_files(folder_path):

    """

    Combine CSV files from a specified folder into a single DataFrame.

    Each row represents a file. The first column is the file's name, the second column is a list of phonemes

    separated by commas and enclosed in brackets, and the third column are the times in a similar format.



    Parameters:

    - folder_path: Path to the folder containing the CSV files.



    Returns:

    - A pandas DataFrame with the combined data.

    """

    # Check if the folder exists

    if not os.path.exists(folder_path):

        return pd.DataFrame(), "Folder does not exist."



    # List to hold data

    data = []



    # Iterate over each file in the folder

    for file in os.listdir(folder_path):

        if file.endswith(".csv"):

            file_path = os.path.join(folder_path, file)

            # Read the CSV file

            df = pd.read_csv(file_path)



            # Extract phonemes and time_diffs as lists

            phonemes = df['Phoneme'].tolist()

            time_diffs = df['time_diff'].tolist()



            # Append to data list

            data.append([file, phonemes, time_diffs])



    # Create a DataFrame from the combined data

    combined_df = pd.DataFrame(data, columns=['File Name', 'Phonemes', 'Time Differences'])



    return combined_df, ""


def combine_csv_files_from_folders(folders):
    combined_data = []

    for folder_path in folders:
        if not os.path.exists(folder_path):
            return f"Folder {folder_path} does not exist."

        for file in os.listdir(folder_path):
            if file.endswith(".csv"):
                file_path = os.path.join(folder_path, file)
                df = pd.read_csv(file_path)

                phonemes = df['Phoneme'].tolist()
                time_diffs = df['time_diff'].tolist()

                # Modify the phonemes and time_diffs lists
                phonemes = ['<start>'] + phonemes + ['<end>']
                time_diffs = [-1] + time_diffs + [-1]

                combined_data.append([file, phonemes, time_diffs])

    combined_df = pd.DataFrame(combined_data, columns=['Filename', 'Phonemes', 'Time Differences'])
    combined_df.to_csv("./data/testTrain/combined_data.tsv", sep='\t', index=False)

    return "Combined TSV file with start and end tokens saved successfully."


def clean_sentence(sentence):
    """
    Clean the sentence by removing unwanted characters and adding start and end tokens.
    """
    # Remove unwanted characters
    cleaned_sentence = ''.join([char for char in sentence if
                                char.isalnum() or char.isspace() or ord(char) in range(3200,
                                                                                       3200 + 128) or char in ",.!?"])
    # Split into characters and add start and end tokens
    cleaned_sentence = "<start>," + ",".join(cleaned_sentence) + ",<end>"
    return cleaned_sentence


def combine_transcript_files(file_paths, save_path):
    """
    Combine transcript files specified by file_paths into one large table and save it.

    Parameters:
    - file_paths: List of strings representing the paths to input files.
    - save_path: Path where the combined table should be saved.

    The function creates a table with 2 columns: the filename and the parsed sentence.
    """
    data = []

    for file_path in file_paths:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                filename, sentence = line.strip().split('\t')
                cleaned_sentence = clean_sentence(sentence)
                data.append([filename, cleaned_sentence])

    df = pd.DataFrame(data, columns=['Filename', 'Parsed Sentence'])

    # Save to TSV
    df.to_csv(save_path, sep='\t', index=False)

    return df

import pandas as pd

def natural_join_transcripts_and_phonemes(transcripts_df, phonemes_df):
    """
    Perform a natural join on two DataFrames based on the 'Filename' column.
    It adds the 'Segmented Sentence' column from the second DataFrame to the first.

    Parameters:
    - transcripts_df: DataFrame containing transcript information.
    - phonemes_df: DataFrame containing phoneme and time differences information.

    Returns:
    - A new DataFrame with the joined information.
    """
    # Adjust the 'Filename' column in the phonemes DataFrame to match the transcripts DataFrame
    phonemes_df['Filename'] = phonemes_df['Filename'].str.replace('.csv', '')

    # Merge the two DataFrames on the 'Filename' column
    joined_df = pd.merge(transcripts_df, phonemes_df, on='Filename', how='inner')

    return joined_df


if __name__ == "__main__":
    #used to create the x values
    # folders = ['./data/kn_in_female_trans',
    #            './data/kn_in_male_trans',
    #            './data/mile_kannada_test/test/audio_files_trans',
    #            './data/mile_kannada_train/train/audio_files_trans']
    #
    # message = combine_csv_files_from_folders(folders)
    # print(message)
    # exit()
    #make the y value table
    file_paths = [
       'data/line_index_female.tsv',
       'data/line_index_male.tsv',
       'data/mile_kannada_test/combined_sentences.tsv',
        'data/mile_kannada_train/combined_sentences.tsv'
    ]
    save_path = '../data/testTrain/combined_transcripts.tsv'
    combined_df = combine_transcript_files(file_paths, save_path)
    print(combined_df.head())



    #combine (x,y) pairs

    # Load the phoneme DataFrame
    phonemes_df = pd.read_csv('../data/testTrain/combined_data.tsv', sep='\t')
    print("Phonemes DataFrame loaded successfully.")

    # Load the transcripts DataFrame
    transcripts_df = pd.read_csv('../data/testTrain/combined_transcripts.tsv', sep='\t')
    print("Transcripts DataFrame loaded successfully.")

    # Perform natural join
    joined_df = natural_join_transcripts_and_phonemes(transcripts_df, phonemes_df)

    # Display the first few rows of the joined DataFrame
    print(joined_df.head())

    joined_df.to_csv('data/testTrain/joined_data.tsv', sep='\t', index=False)
    print("Joined DataFrame saved successfully.")