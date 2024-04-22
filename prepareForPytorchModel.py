import pandas as pd
from sklearn.model_selection import train_test_split


def split_dataset(tsv_file, train_percent, validation_size=1000, max_phonemes_length=195):
    # Load the TSV file
    data = pd.read_csv(tsv_file, sep='\t')

    def preprocess_column(column_value):
        characters_to_remove = ["<start>", "<end>", "'", "[", "]", " "]
        for char in characters_to_remove:
            column_value = column_value.replace(char, '')
        result = ' '.join(column_value.split(','))[1:-1]
        return result

    # Preprocess the data: Apply the preprocessing function to each column
    data['Parsed Sentence'] = data['Parsed Sentence'].apply(preprocess_column)
    data['Phonemes'] = data['Phonemes'].apply(preprocess_column)

    # Filter out entries based on max_phonemes_length
    data = data[data['Phonemes'].apply(lambda x: len(x) <= max_phonemes_length)]
    data = data[data['Parsed Sentence'].apply(lambda x: len(x) <= max_phonemes_length)]

    # Separate a fixed validation set
    validation_data = data.sample(n=validation_size)
    remaining_data = data.drop(validation_data.index)

    # Split the remaining data into training and testing sets based on the given proportion
    train_size = int(len(remaining_data) * train_percent)
    train_data, test_data = train_test_split(remaining_data, train_size=train_size)

    # Save the data to separate files for phonemes (src) and sentences (tgt)
    train_data['Phonemes'].to_csv('lexical-model-data/src-train.txt', index=False, header=False)
    train_data['Parsed Sentence'].to_csv('lexical-model-data/tgt-train.txt', index=False, header=False)

    test_data['Phonemes'].to_csv('lexical-model-data/src-test.txt', index=False, header=False)
    test_data['Parsed Sentence'].to_csv('lexical-model-data/tgt-test.txt', index=False, header=False)


    validation_data['Phonemes'].to_csv('lexical-model-data/src-val.txt', index=False, header=False)
    validation_data['Parsed Sentence'].to_csv('lexical-model-data/tgt-val.txt', index=False, header=False)

    # If needed, you can also save the test_data in a similar fashion


# Example usage
split_dataset('../data/testTrain/joined_data.tsv', train_percent=0.8, validation_size=4000,max_phonemes_length=550)
