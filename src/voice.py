# preliminary I installed:
# sounddevice soundfile
# by: pip install sounddevice soundfile
# sounddevice — records audio from your microphone
# soundfile — saves the recorded audio to a file so Whisper can process it
# We will do:
# using Whisper - I will write voice recording and transcription code
# Record your voice from microphone -> Convert it to text using Whisper

import os
import inspect
# for handle voice
import sounddevice as sd
import soundfile as sf
import whisper
import numpy as np
import datetime
from dotenv import load_dotenv

load_dotenv()

# Whisper model - base is good balance of speed and accuracy
WHISPER_MODEL = "small" # small more accurate model but slower than "base" that is faster but less accurate
SAMPLE_RATE = 16000   # 16000 is optimal for Whisper, while 44100 standard audio sample rate but makes more conversions
SILENCE_THRESHOLD = 0.015  # keep recording till silence (volume level considered as silence)
# Why 0.015:
# Your background noise peaks at 0.0118
# 0.015 is safely above that
# When you speak — volume will be much higher (0.1 - 0.9)
# When silent — volume stays below 0.015 → recording stops

SILENCE_DURATION = 4       # stop after 5 seconds of silence


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # => here we will have a root of the project
# explanation:
# __file__ returns special Python variable that contains the path of the current file, sometime ir can be relative path and sometimes it can be full path
# it depends on how did we run it:
# python -m src.voice => returns full path
# python src/voice => returns relative path

# os.path.abspath(__file__)
# creates a full complete path from any path (relative / full) no shortcuts, no relative paths

# os.path.dirname(path) returns me 1 level up. gives me the parent folder" of whatever path I give
# C:\Users\PRIVATE_ILANA\ai_gmail_whatsapp_agent\src\voice.py => dirname removes this part => we get:
# C:\Users\PRIVATE_ILANA\ai_gmail_whatsapp_agent\src  => dirname removes this part => we get:
# C:\Users\PRIVATE_ILANA\ai_gmail_whatsapp_agent  ← project root
RESULTS_FOLDER = os.path.join(PROJECT_ROOT, 'Results')

MY_VOICE_RECORDED_FILE_NAME = "voice_recording.wav"
MY_TEXT_FILE_NAME = "text_from_voice.txt"


def record_voice():
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")

    recorded_chunks = []
    silence_counter = 0

    print(f"[{func_name}]: Recording... speak now! (will stop automatically when you stop speaking)")

    def callback(indata, frames, time, status):
        """
        :param indata: is the actual audio data chunk just captured by mic
        :return:
        """
        # callback is a function that you don't call yourself
        # instead you give it to sounddevice and sounddevice calls it automatically.

        # You hire a secretary and tell her: "Every time the phone rings — write down what was said"
        # callback = secretary
        # operation = write down what was said

        # sounddevice calls it automatically every few milliseconds when a new chunk of audio arrives from your microphone

        # what keyword 'nonlocal' means in python? It is used in inner function - to modify a variable defined in outer function, without this keyword python
        # will create new local variable
        nonlocal silence_counter
        # measure volume of this chunk
        volume = np.max(np.abs(indata))
        # save of the audio chunk
        recorded_chunks.append(indata.copy())

        # counts how many 'consecutive' silent chunks we got
        if volume < SILENCE_THRESHOLD:
            silence_counter += 1
        else:
            # reset if silence detected
            silence_counter = 0

    # context manager - manages the microphone stream (the recording) - recording is done by:
    # capturing of the sound by mic -> calling the callback to safe the audio chunk
    # with means:
    #              Opens the microphone stream when entering
    #              Dont worry about closing - closing the microphone stream will be done automatically when done
    # with = security guard at the door
    # while = party inside
    # Party keeps going → guard stays at door
    # Party ends (silence) → guard closes the door automatically
    # The guard (with) never decides when to close — he just waits for the party (while) to end, then closes automatically.

    # sd.InputStream is a function that calls my callback. It is a part of package: sounddevice, it listens to my mic in background.
    # Every time a new chunk of audio is recorded (every 10-50 msec) the sounddevice automatically calls the callback with indata (new audio chunk = my voice)
    # as long as i talk, my voice is voice stream, recorded chunk by chunk and saved by a callback which is called by sd.InputStream.
    # sd.InputStream will be called as long as while loop leaves = as long as I dont make silence.
    with sd.InputStream(samplerate=SAMPLE_RATE,
                        channels=1,
                        device=2, # Device 2: Microphone Array (Realtek(R) Au
                        callback=callback):
        # while loop ends when the mic stream ends - the mic stream ends when silence will last more than 2 seconds
        # with block ends when while loop ends
        while silence_counter < (SAMPLE_RATE / 1024 * SILENCE_DURATION):
            sd.sleep(100)

    print(f"[{func_name}]: Recording finished because —> silence detected!")

    if not recorded_chunks:
        return None

    concatenated_audio = np.concatenate(recorded_chunks)
    # is numpy array - it is an object, it is not simply type as list or str, so it is not correct to ask about it: if not
    # if not concatenated_audio
    #    return None

    # what we can ask:
    # array.any() = is any element non-zero?
    # array.all() = are all elements non-zero?
    # len(array) == 0 = is array empty?
    if len(concatenated_audio) == 0:
        return None

    # combines all the chunks into a single NumPy array
    # so returned a numpy.ndarray (a NumPy array) of audio samples
    # NumPy array = raw audio data

    # ve return raw audio and not the wav file because we wish to translate it into text before we create wav file
    return concatenated_audio

def normalize_audio(audio):
    # normalize volume to maximum level
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val
    return audio

def transcribe_voice(audio_file: str):
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")
    print(f"[{func_name}]: Loading Whisper model...")

    model = whisper.load_model(WHISPER_MODEL)
    print(f"[{func_name}]: Transcribing audio...")

    # whisper need ffmpeg to process audio files.
    # We can install it on windows from cmd:
    # winget install ffmpeg
    # or manually: Go to: https://ffmpeg.org/download.html, Click "Windows", Download the build,Extract the folder,Add the bin folder to your Windows PATH

    # the func works but creates warning: "FP16 is not supported on CPU; using FP32 instead"
    # it means: Whisper prefers FP16 for speed — but your PC is running Whisper on CPU (not on GPU), so it automatically falls back to FP32.

    result = model.transcribe(audio_file,    # raw audio data -> to transcript into the text
                              language='he') # here we say that the data is in hebrew
    text = result["text"]
    print(f"[{func_name}]: Transcription: {text}")
    return text

def create_results_subfolder():
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")

    print(f"[{"main"}]: Will be checked if folder Results exists in the project under the root, if not Results will be added else,\n"
          f" under Results will be added new sub folder with Data and time in it's name,\n"
          f"under it will be located 2 results: wav and txt files")

    # create results folder 'if not exists'
    os.makedirs(RESULTS_FOLDER, exist_ok=True)

    # create subfolder name with current date and time
    now = datetime.datetime.now()
    subfolder_name = now.strftime("%Y-%m-%d_%H-%M-%S")

    # full path of new subfolder
    subfolder_path = os.path.join(RESULTS_FOLDER, subfolder_name)

    # create the subfolder
    os.makedirs(subfolder_path, exist_ok=True)

    print(f"[{func_name}]: created subfolder: {subfolder_path}")
    return subfolder_path




if __name__ == "__main__":
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{"main"}]: called")

    results_subfolder_path = create_results_subfolder()
    wav_file_path = os.path.join(results_subfolder_path, MY_VOICE_RECORDED_FILE_NAME)

    raw_audio_data = record_voice() # returned NumPy array (not wav file)
    if len(raw_audio_data) == 0:
        print(f"[{"main"}]: Empty raw audio file, NO file can be created XXXXX...")
    else:
        print(f"[{"main"}]: Raw audio data created")

        print(f"[{"main"}]: Normalize audio before saving ...")
        raw_audio_data = normalize_audio(raw_audio_data)

        print(f"[{"main"}]: Creating wav file ...saving the raw audio data into wav file")
        # Creation of the wav file - save the NumPy array to a WAV file
        sf.write(wav_file_path,  # full_path  -> full wav file name (path + file name)
                 raw_audio_data, # data       -> raw audio data
                 SAMPLE_RATE)

        print(f"[{"main"}]: Creating transcript (text file from audio), using Whisper package ...")
        text = transcribe_voice(wav_file_path)
        if not text:
            print(f"[{"main"}]: Empty transcript file (text file) XXXXX...")
        else:
            text_file_path = os.path.join(results_subfolder_path, MY_TEXT_FILE_NAME)

            print(f"[{func_name}]: writing text to text file: {text_file_path}")
            with open(file=text_file_path, mode="w", encoding='utf-8') as my_text_file:
                my_text_file.write(text)
