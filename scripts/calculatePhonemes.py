from collections import Counter


def process_phonemes(phoneme_str):
    # Split the string into phonemes and handle the length marker
    phonemes = phoneme_str.split()
    processed_phonemes = []
    i = 0
    while i < len(phonemes):
        # Combine the phoneme with the length marker if it's present
        if i + 1 < len(phonemes) and phonemes[i + 1] == 'ː':
            processed_phonemes.append(phonemes[i] + phonemes[i + 1])
            i += 2  # Skip the next item since it's the length marker
        else:
            processed_phonemes.append(phonemes[i])
            i += 1
    return processed_phonemes


def count_phoneme_frequencies(tsv_file_path):
    phoneme_frequencies = Counter()

    with open(tsv_file_path, 'r', encoding='utf-8') as file:
        for line in file:
            _, phonemes = line.strip().split('\t')
            processed_phonemes = process_phonemes(phonemes)
            phoneme_frequencies.update(processed_phonemes)

    return phoneme_frequencies


tsv_file_path = '../dependencies/phonemic_output.txt'
frequencies = count_phoneme_frequencies(tsv_file_path)

for phoneme, freq in frequencies.items():
    print(f"{phoneme} {freq}")
