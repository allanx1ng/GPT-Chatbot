import speech_recognition as sr
from pydub import AudioSegment
from googletrans import Translator

def voice_to_wav(output_file, duration):
    # Initialize the recognizer
    r = sr.Recognizer()

    # Get the list of available microphones
    microphone_list = sr.Microphone.list_microphone_names()

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

    # Use the default microphone as the audio source
    with sr.Microphone(device_index=microphone_index) as source:
        print("Listening...")

        # Wait for a second to let the recognizer adjust the energy threshold based on ambient noise level
        r.adjust_for_ambient_noise(source)

        # Capture the audio
        audio = r.listen(source, timeout=duration)

    try:
        # Convert speech to text
        text = r.recognize_google(audio)

        # Save text as a WAV file
        # audio_data = text.encode("utf-8")
        # audio_segment = AudioSegment(text.encode(), sample_width=2, frame_rate=44100, channels=1)
        # audio_segment.export(output_file, format="wav")
        with open(output_file, "wb") as f:
            f.write(audio.get_wav_data())

        print("Speech saved as WAV file: {}".format(output_file))
    except sr.UnknownValueError:
        print("Speech recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))

# Usage
output_file = "./audio/output.wav"
timeout_duration = 3
voice_to_wav(output_file, timeout_duration)