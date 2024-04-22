import sys
from collections import Counter
import math

def calculate_probabilities(filepath):
    word_counts = Counter()
    bigram_counts = Counter()

    with open(filepath, 'r', encoding='utf-8') as file:
        punctuation_chars = '.,​"\'‘”?()“-:;\\~@#$%^&*[]{}=|/<>'
        translation_table = str.maketrans({char: ' ' for char in punctuation_chars})

        for line in file:
            processed_line = line.strip().translate(translation_table).split()
            processed_line = ["<start>"] + processed_line + ["<end>"]
            if processed_line:
                word_counts.update(processed_line)
                bigrams = [(processed_line[i], processed_line[i + 1]) for i in range(len(processed_line) - 1)]
                bigram_counts.update(bigrams)

    total_words = sum(word_counts.values())
    vocabulary_size = len(word_counts)

    word_log_probabilities = {word: math.log((count + 1) / (total_words + vocabulary_size)) for word, count in word_counts.items()}
    bigram_log_probabilities = {bigram: math.log((count + 1) / (word_counts[bigram[0]] + vocabulary_size)) for bigram, count in bigram_counts.items()}

    sorted_word_log_probs = sorted(word_log_probabilities.items(), key=lambda x: x[1], reverse=True)
    sorted_bigram_log_probs = sorted(bigram_log_probabilities.items(), key=lambda x: x[1], reverse=True)

    return sorted_word_log_probs, sorted_bigram_log_probs




if __name__ == '__main__':
    # Calculate probabilities
    unigram_log_probs, bigram_log_probs = calculate_probabilities("../data/text/combined_corpus.txt")

    # Save unigram probabilities
    with open('../data/text/unigrams_log.tsv', 'w', encoding='utf-8') as file:
        for word, log_prob in unigram_log_probs:
            file.write(f"{word}\t{log_prob}\n")

    # Save bigram probabilities
    with open('../data/text/bigrams_log.tsv', 'w', encoding='utf-8') as file:
        for bigram, log_prob in bigram_log_probs:
            bigram_text = ' '.join(bigram)  # Convert tuple to string
            file.write(f"{bigram_text}\t{log_prob}\n")
