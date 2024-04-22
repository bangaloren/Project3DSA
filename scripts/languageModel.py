import csv
import math


class CalculateProbability:
    def __init__(self, unigram_file_path, bigram_file_path, min_log_prob_unigram=-16.9, max_log_prob_bigram=-13.46):
        self.unigram_file_path = unigram_file_path
        self.bigram_file_path = bigram_file_path
        self.min_log_prob_unigram = min_log_prob_unigram
        self.max_log_prob_bigram = max_log_prob_bigram
        self.unigram_probabilities = self.load_unigram_probabilities()
        self.bigram_probabilities = self.load_bigram_probabilities()
        self.average_word_length=10

    def load_unigram_probabilities(self):
        unigram_probabilities = {}
        with open(self.unigram_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                unigram, log_prob = row[0], float(row[1])
                if log_prob >= self.min_log_prob_unigram:
                    unigram_probabilities[unigram] = log_prob
                else:
                    break
        return unigram_probabilities

    def load_bigram_probabilities(self):
        bigram_probabilities = {}
        with open(self.bigram_file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file, delimiter='\t')
            for row in reader:
                bigram_text, log_prob = row[0], float(row[1])
                if log_prob >= self.max_log_prob_bigram:
                    # Convert bigram text to a tuple of words
                    bigram = tuple(bigram_text.split())
                    bigram_probabilities[bigram] = log_prob
                else:
                    break
        return bigram_probabilities

    def calculate_unigram_probability(self, word:str):
        if word in self.unigram_probabilities:
            return self.unigram_probabilities[word]
        else:
            kannada_dependent_characters = ["್", "ಿ", "ಾ", "ು", "ೆ", "ಂ", "ೇ", "ೂ", "ೊ", "ೀ", "ೋ", "ೕ", "ೈ", "ೃ", "ೌ",
                                            "ಃ", "ೖ"]
            if word in kannada_dependent_characters:
                return -100.0
            return self.min_log_prob_unigram*2

    def calculate_bigram_probability(self, word:str, previous_word:str):
        if (previous_word,word) in self.bigram_probabilities:
            return self.bigram_probabilities[(previous_word,word)]
        else:
            return self.calculate_unigram_probability(word)*2.5


def combined_length(words:list)->int:
        return len(''.join(words))
class SentenceSplitter:
    def __init__(self, probability_calculator: CalculateProbability):
        self.probability_calculator = probability_calculator
        self.maxWordLength = 20


    def find_largest_bigram_log_prob(self, sentence:str, previous_word:str, start_index:int, depth)->float:

        if depth <= 0:
            return 0

        largest_probability = math.inf*-1.0
        for i in range(1, self.maxWordLength):
            if i+start_index > len(sentence):
                break
            next_word=sentence[start_index:start_index+i]
            phrase_probability = self.probability_calculator.calculate_bigram_probability(next_word,previous_word)
            phrase_probability+=self.find_largest_bigram_log_prob(sentence,next_word,i+start_index,depth-1)
            if phrase_probability > largest_probability:
                largest_probability = phrase_probability
        return largest_probability

    def best_first_split_sentence(self, sentence:str, depth=2)->str:
        output_sentence = ""

        previous_index:int=0
        index=0
        previous_word:str="<start>"
        while index<len(sentence):
            largest_probability = -math.inf
            for i in range(1,self.maxWordLength):
                word = sentence[previous_index:previous_index + i]
                depth_0_probability=self.probability_calculator.calculate_bigram_probability(word,previous_word)
                depth_1_probability=self.find_largest_bigram_log_prob(sentence, word, i,depth-1)
                total_probability=depth_0_probability+depth_1_probability

                if total_probability > largest_probability:
                    largest_probability = total_probability
                    index = previous_index + i
            previous_word = sentence[previous_index:index]
            output_sentence+=previous_word+" "

            previous_index=index

        return output_sentence



    def beam_search_split_sentence(self, sentence: str, width=4) -> str:
        best_sentences = [(0,[])]  # Each element is a tuple: (list of words, cumulative probability)
        best_finished_sentences = []

        while best_sentences and len(best_finished_sentences) < width:
            new_candidates = []
            for previous_prob,words in best_sentences:
                previous_word = words[-1] if words else "<start>"
                previous_sentence_length = combined_length(words)
                for i in range(1, self.maxWordLength):
                    if previous_sentence_length + i>len(sentence):
                        break  # Avoid going beyond sentence length

                    next_word = sentence[previous_sentence_length:previous_sentence_length + i]
                    if not next_word:
                        continue #if next
                    # Calculate probability of the next word
                    next_prob = self.probability_calculator.calculate_bigram_probability(next_word, previous_word)
                    new_cum_prob = previous_prob + next_prob
                    new_candidates.append((new_cum_prob,words + [next_word]))

            # Sort and prune to keep only the top width number of candidates
            new_candidates.sort(key=lambda wordProbPairs: wordProbPairs[0], reverse=True)
            best_sentences = new_candidates[0:width]

            # Move completed sentences to best_finished_sentences
            for index,candidate in enumerate(best_sentences):
                if self.is_sentence_complete(candidate[1], sentence):
                    best_finished_sentences.append(candidate)
                    best_sentences.pop(index)

        best_finished_sentences.sort(key=lambda x: x[1], reverse=True)
        return ' '.join(best_finished_sentences[0][1]) if best_finished_sentences else ""

    def is_sentence_complete(self, words, original_sentence):
        return combined_length(words) == len(original_sentence)


# Example usage:
if __name__ == '__main__':
    # Paths to the probability files
    unigram_file_path = '../data/text/unigrams_log.tsv'
    bigram_file_path = '../data/text/bigrams_log.tsv'

    # Create an instance of CalculateProbability
    calculator = CalculateProbability(unigram_file_path, bigram_file_path)

    # Example access to the loaded probabilities
    print(list(calculator.unigram_probabilities.items())[:5])  # Print first 5 filtered unigram probabilities
    print(list(calculator.bigram_probabilities.items())[:5])  # Print first 5 filtered bigram probabilities

    splitter = SentenceSplitter(calculator)
    print("Guessed:", splitter.best_first_split_sentence("ಭಾರತಕೂಡಬದಲಿಸಿದೆಹಾಗಾದರೆಈಗೇಕೆವಿವಾದ"))
    print("Correct:","ಭಾರತ ಕೂಡ ಬದಲಿಸಿದೆ ಹಾಗಾದರೆ ಈಗೇಕೆ ವಿವಾದ")
    print("Guessed:", splitter.best_first_split_sentence("ಚಿತ್ರಕ್ಕೆಅಭಿಷೇಕ್‌ಅಯ್ಯಂಗಾರ್‌ಕಥೆಚಿತ್ರಕಥೆಮತ್ತುಸಂಭಾಷಣೆಬರೆದಿದ್ದಾರೆ"))
    print("Correct:","ಚಿತ್ರಕ್ಕೆ ಅಭಿಷೇಕ್‌ ಅಯ್ಯಂಗಾರ್‌ ಕಥೆ ಚಿತ್ರಕಥೆ ಮತ್ತು ಸಂಭಾಷಣೆ ಬರೆದಿದ್ದಾರೆ")

    print("Guessed:", splitter.beam_search_split_sentence("ಭಾರತಕೂಡಬದಲಿಸಿದೆಹಾಗಾದರೆಈಗೇಕೆವಿವಾದ"))
    print("Correct:", "ಭಾರತ ಕೂಡ ಬದಲಿಸಿದೆ ಹಾಗಾದರೆ ಈಗೇಕೆ ವಿವಾದ")
    print("Guessed:",
          splitter.beam_search_split_sentence("ಚಿತ್ರಕ್ಕೆಅಭಿಷೇಕ್‌ಅಯ್ಯಂಗಾರ್‌ಕಥೆಚಿತ್ರಕಥೆಮತ್ತುಸಂಭಾಷಣೆಬರೆದಿದ್ದಾರೆ"))
    print("Correct:", "ಚಿತ್ರಕ್ಕೆ ಅಭಿಷೇಕ್‌ ಅಯ್ಯಂಗಾರ್‌ ಕಥೆ ಚಿತ್ರಕಥೆ ಮತ್ತು ಸಂಭಾಷಣೆ ಬರೆದಿದ್ದಾರೆ")

    print("Guessed:", splitter.beam_search_split_sentence("ನನ್ನಹೆಸರುನನ್ನಹೆಸರು",width=5))
    print("Guessed:", splitter.beam_search_split_sentence("ನನ್ನಹೆಸರುನನ್ನಹೆಸರು\n",width=5))



