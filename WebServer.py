import os

from flask import Flask, request, jsonify, app
from ASR import ASR
from flask_cors import CORS

from pydub import AudioSegment

class ASRServer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_routes()

    def saveFile(self, file):
        if file:
            file_path = os.path.join("tmp", file.filename)
            file.save(file_path)  # Save the original file first
            # Convert to WAV using pydub
            sound = AudioSegment.from_file(file_path)
            wav_path = os.path.join("tmp", "input.wav")
            sound.export(wav_path, format="wav")

    def setup_routes(self):
        self.asr_system = ASR()
        @self.app.route('/transcribe', methods=['POST'])
        def transcribe_audio():
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400

            file = request.files['file']
            if file.filename == '':
                return jsonify({'error': 'No selected file'}), 400

            # Extract splitter type from form data, default to "best first" if not provided
            splitter_type = request.form.get('splitterType', 'best first')
            width = int(request.form.get('width', 3))  # Default width to 3 if not provided

            self.saveFile(file)

            try:
                output = self.asr_system.transcribeAudioFile("tmp/input.wav",splitterType=splitter_type,width=width)
                return jsonify({'transcription': output})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    def run(self, host='0.0.0.0', port=5000, debug=True):
        self.app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    server = ASRServer()
    server.run()
