import pandas as pd
from sklearn.model_selection import train_test_split

def split_dataset(tsv_file, train_percent, vaidation_size=1000, max_phonemes_length=255):
    # Load the TSV file
    data = pd.read_csv(tsv_file, sep='\t')
    print(data.iloc[1])

    def preprocess_column(column_value):
        characters_to_remove = ["<start>", "<end>", "'", "[", "]", " "]
        for char in characters_to_remove:
            column_value = column_value.replace(char, '')
        result=' '.join(column_value.split(','))[1:-1]
        return result

    # Preprocess the data: Apply the preprocessing function to each column
    data['Parsed Sentence'] = data['Parsed Sentence'].apply(preprocess_column)
    data['Phonemes'] = data['Phonemes'].apply(preprocess_column)
    print(data.iloc[1])
    # Ensure that validation data is removed first

    data = data[data['Phonemes'].apply(lambda x: len(x) <= max_phonemes_length)]
    data = data[data['Parsed Sentence'].apply(lambda x: len(x) <= max_phonemes_length)]

    validation_data = data.sample(n=vaidation_size)
    remaining_data = data.drop(validation_data.index)

    # Calculate the size for train based on the remaining data after removing validation set
    train_size = int(len(remaining_data) * train_percent)

    # Perform the split
    train_data, test_data = train_test_split(remaining_data, train_size=train_size)

    # Output to files, with phonemes in the first column and parsed sentence in the second column
    train_data[['Phonemes', 'Parsed Sentence']].to_csv('train.tsv', sep='\t', index=False, header=False)
    validation_data[['Phonemes', 'Parsed Sentence']].to_csv('validate.tsv', sep='\t', index=False, header=False)
    test_data[['Phonemes', 'Parsed Sentence']].to_csv('test.tsv', sep='\t', index=False, header=False)

# Example usage
split_dataset('../data/testTrain/joined_data.tsv', train_percent=0.8, vaidation_size=3000)