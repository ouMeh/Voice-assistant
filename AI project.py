import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import wikipedia
import requests
import json
import random
import time
import keyboard
import pyjokes
from googletrans import Translator
import os
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import math 

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

def speak(text):
    print(text)
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source, timeout=10)
    try:
        print("Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")
    except sr.UnknownValueError:
        speak("Sorry, I couldn't understand. Can you please repeat?")
        return "None"
    except sr.RequestError:
        speak("Sorry, my speech service is down. Please try again later.")
        return "None"
    return query.lower()

def translate_sentence():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Please say the sentence you want to translate.")
        print("Listening for sentence...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            sentence = recognizer.recognize_google(audio)
            print(f"You said: {sentence}")
        except sr.UnknownValueError:
            speak("Sorry, I did not understand the sentence. Please try again.")
            return
        except sr.RequestError as e:
            speak(f"Could not request results; {e}")
            return
    
    speak("Please say the target language.")
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            target_language = recognizer.recognize_google(audio)
            print(f"Target language: {target_language}")
        except sr.UnknownValueError:
            speak("Sorry, I did not understand the target language. Please try again.")
            return
        except sr.RequestError as e:
            speak(f"Could not request results; {e}")
            return
    
    translator = Translator()
    translation = translator.translate(sentence, dest=target_language)
    speak(f"The translation in {target_language} is: {translation.text}")

def set_timer_gui():
    def start_timer():
        try:
            duration = int(entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of seconds.")
            return
        window.withdraw()
        threading.Thread(target=run_timer, args=(duration,)).start()

    def run_timer(duration):
        time.sleep(duration)
        messagebox.showinfo("Timer", "Time's up!")

    window = tk.Tk()
    window.title("Set Timer")
    label = ttk.Label(window, text="Enter duration (in seconds):")
    label.pack(pady=10)
    entry = ttk.Entry(window)
    entry.pack(pady=10)
    button = ttk.Button(window, text="Start Timer", command=start_timer)
    button.pack(pady=10)
    window.mainloop()

def start_stopwatch():
    def update_stopwatch():
        if running:
            elapsed_time = time.time() - start_time
            time_str = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
            label.config(text=time_str)
            window.after(1000, update_stopwatch)

    def on_start():
        nonlocal start_time, running
        start_time = time.time()
        running = True
        update_stopwatch()

    def on_stop():
        nonlocal running
        running = False

    def on_reset():
        nonlocal running, start_time
        running = False
        start_time = 0
        label.config(text="00:00:00")

    window = tk.Tk()
    window.title("Stopwatch")
    start_time = 0
    running = False

    label = ttk.Label(window, text="00:00:00", font=("Helvetica", 48))
    label.pack(pady=20)

    start_button = ttk.Button(window, text="Start", command=on_start)
    start_button.pack(side=tk.LEFT, padx=10)

    stop_button = ttk.Button(window, text="Stop", command=on_stop)
    stop_button.pack(side=tk.LEFT, padx=10)

    reset_button = ttk.Button(window, text="Reset", command=on_reset)
    reset_button.pack(side=tk.LEFT, padx=10)

    window.mainloop()

def open_website():
    try:
        speak("Which website do you want me to open?")
        website = listen()
        if website != "None":
            if not website.startswith("www."):
                website = "www." + website
            url = f"https://{website}.com"
            webbrowser.open(url)
            speak(f"Opening {website}")
    except Exception as e:
        speak(f"Sorry, I couldn't open the website. Error: {str(e)}")

def create_note():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("What do you want to note down?")
        print("Listening for note...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        try:
            note = recognizer.recognize_google(audio)
            print(f"You said: {note}")
            with open("notes.txt", "a") as file:
                file.write(f"{datetime.datetime.now()}: {note}\n")
            speak("Note added.")
        except sr.UnknownValueError:
            speak("Sorry, I did not understand. Please try again.")
        except sr.RequestError:
            speak("Sorry, there was an error with the speech recognition service.")
    
    subprocess.Popen(["notepad.exe", "notes.txt"])

def assistant(query):
    greetings = ['hi', 'hello', 'hey']
    salutations = ['bye bye', 'bye', 'farewell', 'peace out', 'catch you later']

    if any(greeting in query for greeting in greetings):
        greet_response = random.choice(["Hi there!", "Hello!", "Hey!"])
        speak(greet_response)
    elif 'a timer' in query:
        set_timer_gui()
    elif 'stopwatch' in query:
        start_stopwatch()
    elif 'time' in query:
        current_time = datetime.datetime.now().strftime("%H:%M")
        speak(f"The current time is {current_time}")
    elif 'date' in query:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {current_date}")
    elif 'wikipedia' in query:
        try:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=3)
            speak("According to Wikipedia")
            speak(results)
        except wikipedia.exceptions.DisambiguationError as e:
            speak("The query is too ambiguous. Please be more specific.")
            print(e.options)
        except wikipedia.exceptions.PageError:
            speak("Sorry, I couldn't find any relevant information.")
        except requests.exceptions.RequestException:
            speak("Sorry, I couldn't connect to Wikipedia. Please check your internet connection.")
    elif 'website' in query:
        open_website()
    elif 'joke' in query:
        speak(pyjokes.get_joke())
    elif 'translate' in query:
        translate_sentence()
    elif 'note' in query:
        create_note()
    elif any(salutation in query for salutation in salutations):
        bye_response = random.choice(['bye-bye', 'farewell', 'peace out', 'catch you later', 'bye'])
        speak(bye_response)
        return True
    else:
        speak("I'm sorry, I can't help with that.")
    return False

if __name__ == "__main__":
    speak("Hi! I am Lumo, your desktop assistant. How can I help you?")
    while True:
        query = listen()
        if query == "None":
            continue
        if assistant(query):
            break

