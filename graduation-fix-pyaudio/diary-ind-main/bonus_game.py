from speech import speech
from random import choice
import time

# Difficulty levels
levels = {"mudah": ["diario", "amigo", "ratón"],
		"sedang": ["computadora", "algoritmo", "Desarrollador"],
		"sulit": ["red neuronal", "aprendizaje automático", "inteligencia artificial","aprendizaje profundo"]}


def play_game(level):
    words = levels.get(level, [])  # Pemilihan kata berdasarkan tingkatan
    if not words:
        print("Salah ketik.")
        return

    score = 0
    num_attempts = len(words)  # Jumlah percobaan
    attempts_left = num_attempts
    for _ in range(len(words)):
        random_word = choice(words)
        print(f"Silakan ucapkan {random_word}")
        recog_word = speech()
        print(recog_word)
        
        if random_word == recog_word:
            print("Itu Benar!")
            score += 1
            attempts_left -= 1
        else:
            attempts_left -= 1
            print(f"Attempts left: {attempts_left}")
            print(f"Ada sesuatu yang salah. Kata itu adalah: {random_word}")

        time.sleep(1)  # Tunda beberapa detik
        
    print(f"Game berakhir! Skor kamu adalah: {score}/{len(words)}")

# Select the difficulty level
selected_level = input("Ketik tingkatan game (mudah/sedang/sulit): ").lower()
play_game(selected_level)