import json
import keyboard
import time


import azure.cognitiveservices.speech as speechsdk

from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioConfig

from azure.cognitiveservices.speech.audio import AudioOutputConfig

import google.generativeai as genai



with open('key.json') as f:
    keys = json.load(f)

# Access individual keys
gemini = keys['gemini']
key1 = keys['key1']
region = keys['region']



genai.configure(api_key=gemini)






model = genai.GenerativeModel('gemini-pro')




# response = model.generate_content("What is the meaning of life? make the answer in 5 words")
# print(response.text)
# speech_synthesis_result = speech_synthesizer.speak_text_async(response.text).get()





class SpeechToTextManager:
    speech_config = None
    audio_config = None
    speech_recognizer = None
    speech_synthesizer = None

    def __init__(self):
            # Creates an instance of a speech config with specified subscription key and service region.
            try:
                self.speech_config = speechsdk.SpeechConfig(subscription=key1, region=region)
                self.audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
            except TypeError:
                exit("Ooops! You forgot to set AZURE_TTS_KEY or AZURE_TTS_REGION in your environment!")
            
            self.speech_config.speech_recognition_language="en-US"

    def speechtotext_from_mic_continuous(self, stop_key='p'):
            
            self.speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config, audio_config=self.audio_config)

            self.speech_recognizer = speechsdk.SpeechRecognizer(speech_config=self.speech_config)

            done = False
            
            # Optional callback to print out whenever a chunk of speech is being recognized. This gets called basically every word.
            #def recognizing_cb(evt: speechsdk.SpeechRecognitionEventArgs):
            #    print('RECOGNIZING: {}'.format(evt))
            #self.azure_speechrecognizer.recognizing.connect(recognizing_cb)

            # Optional callback to print out whenever a chunk of speech is finished being recognized. Make sure to let this finish before ending the speech recognition.
            #def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
            #   print('RECOGNIZED: {}'.format(evt))
            #self.speech_recognizer.recognized.connect(recognized_cb)

            # We register this to fire if we get a session_stopped or cancelled event.
            def stop_cb(evt: speechsdk.SessionEventArgs):
                print('CLOSING speech recognition on {}'.format(evt))
                nonlocal done
                done = True

            # Connect callbacks to the events fired by the speech recognizer
            self.speech_recognizer.session_stopped.connect(stop_cb)
            self.speech_recognizer.canceled.connect(stop_cb)

            # This is where we compile the results we receive from the ongoing "Recognized" events
            all_results = []
            def handle_final_result(evt):
                all_results.append(evt.result.text)
            self.speech_recognizer.recognized.connect(handle_final_result)

            # Perform recognition. `start_continuous_recognition_async asynchronously initiates continuous recognition operation,
            # Other tasks can be performed on this thread while recognition starts...
            # wait on result_future.get() to know when initialization is done.
            # Call stop_continuous_recognition_async() to stop recognition.
            result_future = self.speech_recognizer.start_continuous_recognition_async()
            result_future.get()  # wait for voidfuture, so we know engine initialization is done.
            print('Continuous Speech Recognition is now running, say something.')

            while not done:
                # METHOD 1 - Press the stop key. This is 'p' by default but user can provide different key
                if keyboard.read_key() == stop_key:
                    print("\nEnding azure speech recognition\n")
                    self.speech_recognizer.stop_continuous_recognition_async()
                    break
                
            

            final_result = " ".join(all_results).strip()
            print(f"\n\nHeres the result we got!\n\n{final_result}\n\n")
            return final_result






if __name__ == '__main__':

    
    speechtotext_manager = SpeechToTextManager()

    while True:
        result = speechtotext_manager.speechtotext_from_mic_continuous()
        print(f"\n\nHERE IS THE RESULT:\n{result}")
        time.sleep(10)



