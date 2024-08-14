'''
+-------------------+        +-----------------------+        +------------------+        +------------------------+
|   Step 1: Install |        |  Step 2: Real-Time    |        |  Step 3: Pass    |        |  Step 4: Live Audio    |
|   Python Libraries|        |  Transcription with   |        |  Real-Time       |        |  Stream from ElevenLabs|
+-------------------+        |       AssemblyAI      |        |  Transcript to   |        |                        |
|                   |        +-----------------------+        |      OpenAI      |        +------------------------+
| - assemblyai      |                    |                    +------------------+                    |
| - openai          |                    |                             |                              |
| - elevenlabs      |                    v                             v                              v
| - mpv             |        +-----------------------+        +------------------+        +------------------------+
| - portaudio       |        |                       |        |                  |        |                        |
+-------------------+        |  AssemblyAI performs  |-------->  OpenAI generates|-------->  ElevenLabs streams   |
                             |  real-time speech-to- |        |  response based  |        |  response as live      |
                             |  text transcription   |        |  on transcription|        |  audio to the user     |
                             |                       |        |                  |        |                        |
                             +-----------------------+        +------------------+        +------------------------+

###### Step 1: Install Python libraries ######

brew install portaudio
pip install "assemblyai[extras]"
pip install elevenlabs==0.3.0b0
brew install mpv
pip install --upgrade openai
'''

import assemblyai as aai
from elevenlabs import generate, stream
from openai import OpenAI

class AI_Assistant:
    def __init__(self):
        aai.settings.api_key = "ASSEMBLYAI-API-KEY"
        self.openai_client = OpenAI(api_key = "OPENAI-API-KEY")
        self.elevenlabs_api_key = "ELEVENLABS-API-KEY"

        self.transcriber = None

        # Prompt
        self.full_transcript = [
            {"role":"system", "content":"You are a receptionist at a dental clinic. Be resourceful and efficient."},
        ]

###### Step 2: Real-Time Transcription with AssemblyAI ######
        
    def start_transcription(self):
        self.transcriber = aai.RealtimeTranscriber(
            sample_rate = 16000,
            on_data = self.on_data,
            on_error = self.on_error,
            on_open = self.on_open,
            on_close = self.on_close,
            end_utterance_silence_threshold = 1000
        )

        self.transcriber.connect()
        microphone_stream = aai.extras.MicrophoneStream(sample_rate =16000)
        self.transcriber.stream(microphone_stream)
    
    def stop_transcription(self):
        if self.transcriber:
            self.transcriber.close()
            self.transcriber = None

    def on_open(self, session_opened: aai.RealtimeSessionOpened):
        print("Session ID:", session_opened.session_id)
        return


    def on_data(self, transcript: aai.RealtimeTranscript):
        if not transcript.text:
            return

        if isinstance(transcript, aai.RealtimeFinalTranscript):
            self.generate_ai_response(transcript)
        else:
            print(transcript.text, end="\r")


    def on_error(self, error: aai.RealtimeError):
        print("An error occured:", error)
        return


    def on_close(self):
        #print("Closing Session")
        return

###### Step 3: Pass real-time transcript to OpenAI ######
    
    def generate_ai_response(self, transcript):

        self.stop_transcription()

        self.full_transcript.append({"role":"user", "content": transcript.text})
        print(f"\nPatient: {transcript.text}", end="\r\n")

        response = self.openai_client.chat.completions.create(
            model = "gpt-3.5-turbo",
            messages = self.full_transcript
        )

        ai_response = response.choices[0].message.content

        self.generate_audio(ai_response)

        self.start_transcription()
        print(f"\nReal-time transcription: ", end="\r\n")


###### Step 4: Generate audio with ElevenLabs ######
        
    def generate_audio(self, text):

        self.full_transcript.append({"role":"assistant", "content": text})
        print(f"\nAI Receptionist: {text}")

        audio_stream = generate(
            api_key = self.elevenlabs_api_key,
            text = text,
            voice = "Rachel",
            stream = True
        )

        stream(audio_stream)

greeting = "Thank you for calling Vancouver dental clinic. My name is Sandy, how may I assist you?"
ai_assistant = AI_Assistant()
ai_assistant.generate_audio(greeting)
ai_assistant.start_transcription()

        





    



    





