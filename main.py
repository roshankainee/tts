import textwrap
import json
import os
import keyboard
import time
import pathlib
from rich import print as rprint

from IPython.display import Markdown

from new import SpeechToTextManager

import google.generativeai as genai


BACKUP_FILE = "ChatHistoryBackup.txt"
RESPONSE_HISTORY_FILE = "ResponseHistory.txt"


with open('key.json') as f:
    keys = json.load(f)

# Access individual keys
gemini = keys['gemini']

genai.configure(api_key=gemini)


model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])


speechtotext_manager = SpeechToTextManager()


def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


response_history = []

def save_response_history(history_list, filename):
    with open(filename, 'w') as file:
        for response in history_list:
            file.write(response + '\n')


if os.path.exists(RESPONSE_HISTORY_FILE):
    with open(RESPONSE_HISTORY_FILE, 'r') as file:
        response_history = file.read().splitlines()

response = chat.send_message("make all the response concise and in less than 5 sentences unless asked for")



rprint("[green]Starting the loop, press spacebar to begin")
while True:
    # Wait until user presses "space" key
    if keyboard.read_key() != "space":
        time.sleep(0.1)
        continue

    rprint("[green]User pressed spacebar key! Now listening to your microphone:")

    # Get question from mic
    mic_result = speechtotext_manager.speechtotext_from_mic_continuous()
    
    if mic_result == '':
        rprint("[red]Did not receive any input from your microphone!")
        continue

    # Send question to Gemini AI
    response = chat.send_message(mic_result, stream=True)
    
    response.resolve()


    response_history.append(response.text)


    # Save response history to a file
    save_response_history(response_history, RESPONSE_HISTORY_FILE)

    # Write the results to txt file as a backup
    with open(BACKUP_FILE, "w") as file:
        file.write(str(response))
    to_markdown(response.text)
    print(response.text)
    speech_synthesis_result = speechtotext_manager.speech_synthesizer.speak_text_async(response.text)
    

    rprint("[green]\n!!!!!!!\nFINISHED PROCESSING DIALOGUE.\nREADY FOR NEXT INPUT\n!!!!!!!\n")
    