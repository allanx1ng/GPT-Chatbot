import speech_recognition as sr
from pydub import AudioSegment
import openai
from openai import OpenAI
import dotenv
import os
import urllib
import urllib.parse
import urllib.request
import requests
from pydub.playback import play
import wave
# import googletrans
import keyboard

#INIT

dotenv.load_dotenv()
api = os.environ.get('OPENAI_API_KEY')
openai.api_key = api

lore = os.environ.get('LORE')
bot_name = os.environ.get('NAME')

model_engine = "gpt-4-turbo-preview"
client = OpenAI()

chat_log = "./logs/chatlogs.txt"
with open(chat_log, "r") as c:
    conversation = c.read

input_file = "./audio/input.wav"
timeout_duration = 3

# Initialize the recognizer
r = sr.Recognizer()
r.energy_threshold = 1500

# Get the list of available microphones
microphone_list = sr.Microphone.list_microphone_names()

audio = None

# Prompt the user for the microphone index
print("Available microphones:")
for i, microphone in enumerate(microphone_list):
    print(f"{i + 1}: {microphone}")

# Validate the microphone index
while True:
    try:
        microphone_index = int(input("Enter the microphone index, or enter 0 to type: "))
        if 0 <= microphone_index <= len(microphone_list):
            break
        else:
            print("Invalid microphone index. Please try again.")
    except ValueError:
        print("Invalid input. Please enter a valid microphone index.")
        


while True:
    # print("Hold shift to speak...")
    # global recording
    # recording = False

    if microphone_index != 0:

        while True:
            try:
                button = input("Enter C to speak: ")
                if button != "C":
                    break
                else:
                    print("Invalid Letter.")
            except ValueError:
                print("Invalid input. Please enter a valid microphone index.")

        try:
            with sr.Microphone(device_index=(microphone_index-1)) as source:
                audio = r.listen(source, timeout = 5)
        except sr.WaitTimeoutError:
            print("Timeout occurred. Continuing...")

        # Wait for Shift key to be pressed and released
        # text = r.recognize_google(audio)
        # if len(text) == 0:
        #     continue
        # else:
        #     pass
        isValidSpeech = False

        try:
            # Convert speech to text
            text = r.recognize_google(audio)

            with open(input_file, "wb") as f:
                f.write(audio.get_wav_data())

            print("Speech saved as WAV file: {}".format(input_file))
            isValidSpeech = True
        except sr.UnknownValueError:
            print("Speech recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

        audio = None
    else:
        text = input("Please type your message: ")
        isValidSpeech = True
                

    if isValidSpeech == True:

        if microphone_index != 0:
            audio_file= open(input_file, "rb")
            trans = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file,
                temperature=0.1,
                language="en"
            )

            if len(trans['text']) == 0:
                continue
            else:
                pass

            print("You: " + trans['text'])
            words = str(trans['text'])
        else:
            words = text

        c = open(chat_log, "r")

        start_sequence = "\nAI:"
        restart_sequence = "\nHuman:"

        result = client.chat.completions.create(
            model=model_engine,
            messages=[
                {"role": "system", "content": f"You are: {lore}, here is the previous conversation we had: {c.read()}."},
                {"role": "user", "content": f"{words}"}
            ]
        )
        print(result)
        response = result.choices[0].message.content

        
        with open(chat_log, "a") as c:
            c.write("\nUser:" + words)
        words = words.replace(".", "")
        words = words.lower()
        words = words.split()


        

    else:
        c = open(chat_log, "r")
        start_sequence = "\nAI:"
        restart_sequence = "\nHuman:"

        response = bot_name + " : Sorry I couldnt understand, could you please repeat that?"



    print(response)

    with open(chat_log, "a") as c:
        c.write("\n" + response)

    # Translate English text to Japanese
    # translator = googletrans.Translator()
    # response_jp = translator.translate(response, src='en', dest='ja')
    # print(response_jp.text)

    # Call Voicevox to generate audio
    params_encoded = urllib.parse.urlencode({'text': response, 'speaker': 20})
    request = requests.post(f'http://127.0.0.1:50021/audio_query?{params_encoded}')
    # print(request.content)
    params_encoded = urllib.parse.urlencode({'speaker': 20, 'enable_interrogative_upspeak': True})
    request = requests.post(f'http://127.0.0.1:50021/synthesis?{params_encoded}', json=request.json())
    
    with wave.open("output.wav", "wb") as outfile:
        outfile.setnchannels(1)
        outfile.setsampwidth(2)
        outfile.setframerate(24000)
        outfile.writeframes(request.content)

    song = AudioSegment.from_wav("output.wav")
    play(song)

# # Register the event handlers for key presses and releases
# keyboard.on_press(on_press)
# keyboard.on_release(on_release)