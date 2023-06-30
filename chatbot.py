import speech_recognition as sr
from pydub import AudioSegment
from googletrans import Translator
import openai
import dotenv
import os
import urllib
import urllib.parse
import urllib.request
import requests
from pydub.playback import play
import wave
import googletrans
import keyboard

#INIT

dotenv.load_dotenv()
api = os.environ.get('API_KEY')
openai.api_key = api

lore = os.environ.get('LORE')
bot_name = os.environ.get('NAME')

model_engine = "text-davinci-003"

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
    print(f"{i}: {microphone}")

# Validate the microphone index
while True:
    try:
        microphone_index = int(input("Enter the microphone index: "))
        if 0 <= microphone_index < len(microphone_list):
            break
        else:
            print("Invalid microphone index. Please try again.")
    except ValueError:
        print("Invalid input. Please enter a valid microphone index.")



#def voice_to_wav(output_file, duration):

    
    # # Use the default microphone as the audio source
    # with sr.Microphone(device_index=microphone_index) as source:
    #     print("Listening...")

    #     # Wait for a second to let the recognizer adjust the energy threshold based on ambient noise level
    #     r.adjust_for_ambient_noise(source)

    #     # Capture the audio
    #     audio = r.listen(source, timeout=duration)

    # try:
    #     # Convert speech to text
    #     text = r.recognize_google(audio)

    #     # Save text as a WAV file
    #     # audio_data = text.encode("utf-8")
    #     # audio_segment = AudioSegment(text.encode(), sample_width=2, frame_rate=44100, channels=1)
    #     # audio_segment.export(output_file, format="wav")
    #     with open(output_file, "wb") as f:
    #         f.write(audio.get_wav_data())

    #     print("Speech saved as WAV file: {}".format(output_file))
    # except sr.UnknownValueError:
    #     print("Speech recognition could not understand audio")
    # except sr.RequestError as e:
    #     print("Could not request results from Google Speech Recognition service; {0}".format(e))

# def on_press(event):
#     global audio
#     global recording
#     if event.name == 'shift' and audio is None and not recording:
#         with sr.Microphone(device_index=microphone_index) as source:
#             audio = r.listen(source, timeout = None)

# # Stop recording and save to WAV file when Shift key is released
# def on_release(event):
#     global audio
#     global recording
#     if event.name == 'shift' and audio is not None and recording:
#         print("Recording stopped.")
#         audio.stop()
        


while True:
    # print("Hold shift to speak...")
    # global recording
    # recording = False

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
        with sr.Microphone(device_index=microphone_index) as source:
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

        # Save text as a WAV file
        # audio_data = text.encode("utf-8")
        # audio_segment = AudioSegment(text.encode(), sample_width=2, frame_rate=44100, channels=1)
        # audio_segment.export(output_file, format="wav")
        # with open(output_file, "wb") as f:
        #     f.write(audio.get_wav_data())
        with open(input_file, "wb") as f:
            f.write(audio.get_wav_data())

        print("Speech saved as WAV file: {}".format(input_file))
        isValidSpeech = True
    except sr.UnknownValueError:
        print("Speech recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

    audio = None

    # with open(input_file, "wb") as f:
    #     f.write(audio.get_wav_data())

    if isValidSpeech == True:

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
        with open(chat_log, "a") as c:
            c.write("\nUser:" + words)
        words = words.replace(".", "")
        words = words.lower()
        words = words.split()


        c = open(chat_log, "r")

        start_sequence = "\nAI:"
        restart_sequence = "\nHuman:"

        response = openai.Completion.create(
            engine=model_engine,
            prompt=lore + "\n" + c.read(),
            max_tokens=150,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            temperature=0.9,
        ).choices[0].text.strip()
    else:
        c = open(chat_log, "r")
        start_sequence = "\nAI:"
        restart_sequence = "\nHuman:"

        response = bot_name + " : Sorry I couldnt understand, could you please repeat that?"



    print(response)

    with open(chat_log, "a") as c:
        c.write("\n" + response)

    # Translate English text to Japanese
    translator = googletrans.Translator()
    response_jp = translator.translate(response, src='en', dest='ja')
    print(response_jp.text)

    # Call Voicevox to generate audio
    params_encoded = urllib.parse.urlencode({'text': response_jp.text[5:], 'speaker': 20})
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