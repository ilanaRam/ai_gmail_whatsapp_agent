# preliminary I installed:
# sounddevice soundfile
# by: pip install sounddevice soundfile
# sounddevice — records audio from your microphone
# soundfile — saves the recorded audio to a file so Whisper can process it
# We will do:
# using Whisper - I will write voice recording and transcription code
# Record your voice from microphone -> Convert it to text using Whisper

# what microphone I use when I wear headphones ?
# ===============================================
# Microphone Array (Realtek(R) Audio) - this is the laptop's built-in microphone driver that listens to input - when we plug in headset the input = headset

import os
import inspect
# for handle voice
import sounddevice as sd
import soundfile as sf
import whisper
import numpy as np
import datetime
from dotenv import load_dotenv
import time as python_time

load_dotenv()

# Whisper model - base is good balance of speed and accuracy
WHISPER_MODEL = "small" # small more accurate model but slower than "base" that is faster but less accurate
SAMPLE_RATE = 16000   # 16000 is optimal for Whisper, while 44100 standard audio sample rate but makes more conversions
SILENCE_THRESHOLD = 0.007  # keep recording till silence (volume level considered as silence)
# Why 0.015:
# Your background noise peaks at 0.0118
# 0.015 is safely above that
# When you speak — volume will be much higher (0.1 - 0.9)
# When silent — volume stays below 0.015 → recording stops

SILENCE_DURATION = 6       # stop after 5 seconds of silence


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
RESULTS_FOLDER_NAME = os.path.join(PROJECT_ROOT, 'Results')
RESULTS_SUBFOLDER_FULL_PATH = None

MY_VOICE_RECORDED_FILE_NAME = "voice_recording.wav"
MY_TEXT_FILE_NAME = "text_from_voice.txt"


def record_voice(results_path: str):
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")

    recorded_chunks = []

    # Track the exact timestamp of when we last heard a sound above the threshold
    last_sound_time = python_time.time()

    print(f"[{func_name}]:[{python_time.time()}] Recording... speak now! (will stop after {SILENCE_DURATION} seconds of silence)")

    def callback(indata, frames, time_info, status):
        nonlocal last_sound_time

        volume = np.max(np.abs(indata))
        # save of the audio chunk
        recorded_chunks.append(indata.copy())

        # If the volume is louder than your threshold, update the timestamp!
        if volume >= SILENCE_THRESHOLD:
            last_sound_time = python_time.time()

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
                        callback=callback):
        # while loop ends when the mic stream ends - the mic stream ends when silence will last more than 2 seconds
        # with block ends when while loop ends
        # The loop checks real elapsed seconds since the last spoken word
        while (python_time.time() - last_sound_time) < SILENCE_DURATION:
            sd.sleep(100)
    print(f"[{func_name}]:[{python_time.time()}] Recording...Finished because —> silence lasted longer than {SILENCE_DURATION} seconds!")

    if not recorded_chunks:
        print(f"[{func_name}]: No audio chunks collected at all.")
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
        print(f"[{"main"}]: Created empty raw audio file ####")
        return None

    # combines all the chunks into a single NumPy array
    # so returned a numpy.ndarray (a NumPy array) of audio samples
    # NumPy array = raw audio data
    print(f"[{"main"}]: Normalize audio before saving ...")
    normalized_raw_audio = normalize_audio(concatenated_audio)
    if len(normalized_raw_audio) == 0:
        print(f"[{"main"}]: Normalization created empty raw audio file ####")
        return None
    print(f"[{"main"}]: Normalizing ... Done")
    print(f"[{"main"}]: Creating wav file (= saving the raw audio data into wav file)")

    # Creation of the wav file - save the NumPy array to a WAV file
    result_wav_file_path = os.path.join(results_path, MY_VOICE_RECORDED_FILE_NAME)
    print(f"[{func_name}]: going to create result wav file: {result_wav_file_path}")

    sf.write(result_wav_file_path,  # full_path  -> full wav file name (path + file name)
             normalized_raw_audio,
             # data       -> raw audio data
             SAMPLE_RATE)

    if not os.path.exists(result_wav_file_path):
        print(f"[{"main"}]: Failed to create wav file: {result_wav_file_path}")
        return None
    print(f"[{"main"}]: Created wav file: {result_wav_file_path}")
    return result_wav_file_path


    # we return raw audio and not the wav file because we wish to translate it into text before we create wav file
    # return normalized_raw_audio

def normalize_audio(audio):
    # normalize volume to maximum level
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val
    return audio

def convert_voice_to_text(audio_file: str,
                          results_path: str):
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")
    print(f"[{func_name}]: Converting wav audio file -> text file by Whisper package ...")

    print(f"[{func_name}]: Loading Whisper package ...")
    model = whisper.load_model(WHISPER_MODEL)
    print(f"[{func_name}]: converting audio -> text ()")

    # whisper need ffmpeg to process audio files.
    # We can install it on windows from cmd:
    # winget install ffmpeg
    # or manually: Go to: https://ffmpeg.org/download.html, Click "Windows", Download the build,Extract the folder,Add the bin folder to your Windows PATH

    # the func works but creates warning: "FP16 is not supported on CPU; using FP32 instead"
    # it means: Whisper prefers FP16 for speed — but your PC is running Whisper on CPU (not on GPU), so it automatically falls back to FP32.

    result = model.transcribe(audio_file,    # raw audio data -> to transcript into the text
                              language='he') # here we say that the data is in hebrew
    text = result["text"]
    print(f"[{func_name}]: Text (from voice): {text}")

    if not text:
        print(f"[{"main"}]: Empty transcript file (text file) XXXXX...")
        return None

    text_file_path = os.path.join(results_path, MY_TEXT_FILE_NAME)

    print(f"[{func_name}]: writing text to text file: {text_file_path}")
    with open(file=text_file_path, mode="w", encoding='utf-8') as my_text_file:
        my_text_file.write(text)
    return text_file_path

def create_results_subfolder():
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")

    print(f"[{func_name}]: we are about calculate, create, and RETURN the path")

    # create results folder 'if not exists'
    os.makedirs(RESULTS_FOLDER_NAME, exist_ok=True)

    # create subfolder name with current date and time
    now = datetime.datetime.now()
    subfolder_name = now.strftime("%Y-%m-%d_%H-%M-%S")
    # full path of new subfolder
    subfolder_path = os.path.join(RESULTS_FOLDER_NAME, subfolder_name)

    # create the unique subfolder
    os.makedirs(subfolder_path, exist_ok=True)
    if not os.path.exists(subfolder_path):
        print(f"[{func_name}]: Failed to find subfolder path: {subfolder_path}")
        return None
    print(f"[{func_name}]: created subfolder path: {subfolder_path}")
    return subfolder_path  # Return the new results path explicitly!




if __name__ == "__main__":
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{"main"}]: called")

    # get results path
    results_path = create_results_subfolder()

    # record voice - api
    result_wav_file_path = record_voice(results_path=results_path) # where to locate text results_path

    if result_wav_file_path is None:
        exit()
    # Pass that exact same path to the transcription engine
    result_text_file_path = convert_voice_to_text(audio_file=result_wav_file_path,   # wav file
                                                  results_path=results_path)         # where to locate text results_path
    if not result_text_file_path:
        exit()
    print(f"[{func_name}]: Both files .wav & .txt are successfully stored in: {results_path}")

