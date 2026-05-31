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
from dotenv import load_dotenv

load_dotenv()

# Whisper model - base is good balance of speed and accuracy
WHISPER_MODEL = "base"
SAMPLE_RATE = 44100        # standard audio sample rate
SILENCE_THRESHOLD = 0.01   # keep recording till silence (volume level considered as silence)
SILENCE_DURATION = 3       # stop after 5 seconds of silence
MY_VOICE_RECORDED_FILE = "voice_recording.wav"
MY_TEXT_FILE = "text_from_voice.txt"

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

    print(f"[{func_name}]: Recording stopped — silence detected!")

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

    result = model.transcribe(audio_file)
    text = result["text"]
    print(f"[{func_name}]: Transcription: {text}")
    return text

def log_textual_output(my_text):
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{func_name}]: called")

    print(f"[{func_name}]: writing text to text file: {MY_TEXT_FILE}")
    with open(file=MY_TEXT_FILE, mode="w") as my_text_file:
        my_text_file.write(my_text)




if __name__ == "__main__":
    func_name = inspect.currentframe().f_code.co_name
    print(f"[{"main"}]: called")

    raw_audio_data = record_voice() # returned NumPy array (not wav file)
    if len(raw_audio_data) == 0:
        print(f"[{"main"}]: Empty raw audio file, NO file can be created XXXXX...")
    else:
        print(f"[{"main"}]: Raw audio file created, now will be created wav file VVVV ...")
        # Save the NumPy array to a WAV file: MY_RECORD
        sf.write(MY_VOICE_RECORDED_FILE, raw_audio_data, SAMPLE_RATE)

        print(f"[{"main"}]: Will be created text file, using Whisper package ...")
        text = transcribe_voice(MY_VOICE_RECORDED_FILE)
        print(f"[{"main"}]: You said: {text}")

        log_textual_output(text)

        # add AI to understand what was actually said
