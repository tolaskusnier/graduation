# from speech import speech
import speech_recognition as speech_recog
mic = speech_recog.Microphone()
recog = speech_recog.Recognizer()
# recorded_texts = []
with mic as audio_file:
    print("Silakan bicara in English")

    recog.adjust_for_ambient_noise(audio_file)
    audio = recog.listen(audio_file)
try:
    # text = speech()
    # recorded_texts.append(text)
    # a = 2
    # b = int(input("Masukkan angka: "))
    # print(a/b)


    

    print("Mengkonversikan ucapan menjadi Teks...")
    print("Kamu berkata: " + recog.recognize_google(audio, language="en-GB")) # type: ignore
except:
    # recorded_texts.append("Ada yang salah")
    # print("Pembagian dengan 0 tidak bisa")
    # print("Pembagian yang benar contoh: 4/2, 8/4 denominator tidak bisa 0")
    print("Ada yang salah")
    
# a = 2
# b = int(input("Masukkan angka: "))
# print(a/b)