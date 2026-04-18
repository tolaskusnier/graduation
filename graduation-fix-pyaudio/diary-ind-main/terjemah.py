from googletrans import Translator

translator = Translator()
recognizer = sr.Recognizer()
with sr.Microphone() as source:
    audio = recognizer.listen(source)
    text = recognizer.recognize_google(audio) # type: ignore
translated = translator.translate(text, dest='en')  # Kode 'en-US' adalah kode untuk bahasa Inggris
print("🌍 Terjemahan ke Bahasa Inggris:", translated.text)