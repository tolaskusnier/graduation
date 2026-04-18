import speech_recognition as speech_recog#+

# language="id" for Indonesian
#### V1 - function
def speech():
    mic = speech_recog.Microphone()
    recog = speech_recog.Recognizer()

    with mic as audio_file:
        recog.adjust_for_ambient_noise(audio_file)
        audio = recog.listen(audio_file)
        return recog.recognize_google(audio, language="id") # type: ignore

### V2 - script special for local testing
# mic = speech_recog.Microphone()
# recog = speech_recog.Recognizer()

# with mic as audio_file:
#     print("Silakan bicara in English")

#     recog.adjust_for_ambient_noise(audio_file)
#     audio = recog.listen(audio_file)

#     print("Mengkonversikan ucapan menjadi Teks...")
#     print("Kamu berkata: " + recog.recognize_google(audio, language="id-ID")) # type: ignore