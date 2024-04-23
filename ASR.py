import subprocess

from scripts.languageModel import SentenceSplitter
from scripts.languageModel import CalculateProbability
from scripts.phonemicTranscription import phone_recognize_file
import pandas

class ASR(object):
    def __init__(self,unigram_file_path = './data/text/unigrams_log.tsv',
        bigram_file_path = './data/text/bigrams_log.tsv'):
        print("Initializing ASR Object...")
        # Create an instance of CalculateProbability
        calculator = CalculateProbability(unigram_file_path, bigram_file_path)
        self.splitter =SentenceSplitter(calculator)
        self.phoneme_file_location ='tmp/temp_phonemes.txt'
        self.lexical_file_location ='tmp/temp_lexicon.txt'
        self.lexical_model_path='lexical-model/model_released.pt'
        print("...Finished Initializing ASR Object")


    def translate_with_onmt(self,input_text):
        #Write the input text to the source fil
        with open(self.phoneme_file_location, 'w') as source_file:
            source_file.write(input_text)
        #run command to transcribe the phonenemes
        command = ['onmt_translate', '-model', self.lexical_model_path, '-src', self.phoneme_file_location, '-output', self.lexical_file_location]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error during translation: {e}")
            return None
        #try to read the result
        try:
            with open(self.lexical_file_location, 'r') as output_file:
                translated_text = output_file.read()
        except FileNotFoundError:
            print("Output file not found.")
            return None
        return translated_text.replace(" ","")

    def generatePhonemicTranscription(self, wav_file_location:str)->str:
        phoneme_data:pandas.DataFrame=phone_recognize_file(wav_file_location)

        return " ".join(phoneme_data["label"].tolist())
    def transcribeAudioFile(self, wav_file_location:str,splitterType="best first",width=3)->str:# can choose between beem search or best first
        print("Generating Phonemic transcription...")
        phonemes=self.generatePhonemicTranscription(wav_file_location)
        print("phonemes:",phonemes)
        print("Generating Lexical transcription...")
        lexemes=self.translate_with_onmt(input_text=phonemes)
        lexemes=lexemes.replace("\n","")
        lexemes=lexemes.replace(" ", "")
        print("lexemes:",lexemes)
        print("Splitting Data...")

        if splitterType == "best first":
            return self.splitter.best_first_split_sentence(sentence=lexemes,depth=width)
        elif splitterType == "beam search":
            return self.splitter.beam_search_split_sentence(sentence=lexemes,width=width)
        else:
            raise RuntimeError(f"Unknown splitter type: {splitterType}")


if __name__ == '__main__':
    asr =ASR()
    kannadaText=asr.transcribeAudioFile(wav_file_location="data/kn_in_male/knm_00180_00250075112.wav")
    print(kannadaText)
