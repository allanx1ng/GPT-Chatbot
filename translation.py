import googletrans
import subprocess
import io
import os
from pydub import AudioSegment
from pydub.playback import play
import wave

import urllib
import urllib.parse
import urllib.request
import requests



def translate_and_play(text):
    # Translate English text to Japanese
    translator = googletrans.Translator()
    response_jp = translator.translate(text, src='en', dest='ja')
    print(response_jp.text)

    # Call Voicevox to generate audio
    params_encoded = urllib.parse.urlencode({'text': response_jp.text[0:], 'speaker': 20})
    request = requests.post(f'http://127.0.0.1:50021/audio_query?{params_encoded}')
    print(request.content)
    params_encoded = urllib.parse.urlencode({'speaker': 20, 'enable_interrogative_upspeak': True})
    request = requests.post(f'http://127.0.0.1:50021/synthesis?{params_encoded}', json=request.json())

    print('hello world')
    
    with wave.open("output.wav", "wb") as outfile:
        outfile.setnchannels(1)
        outfile.setsampwidth(2)
        outfile.setframerate(24000)
        outfile.writeframes(request.content)

    song = AudioSegment.from_wav("output.wav")
    play(song)
    

# Usage
english_text = input("Enter the English text: ")
translate_and_play(english_text)
