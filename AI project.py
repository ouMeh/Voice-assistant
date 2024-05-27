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
from tkinter import messagebox

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
        audio = recognizer.listen(source)
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
     
def get_weather(city):
    """Function to fetch weather information for a given city."""
    weather_api_key = '6104bde5d95f43e9e7ec751143be00cc'
    weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}'
    
    try:
        response = requests.get(weather_url)
        response.raise_for_status()
        weather_data = response.json()
        
        if 'weather' in weather_data and len(weather_data['weather']) > 0:
            weather_description = weather_data['weather'][0]['description']
            speak(f"Weather in {city}: {weather_description}")
        else:
            speak("Sorry, I couldn't retrieve the weather information.")
    
    except requests.exceptions.RequestException as e:
        speak(f"Sorry, I couldn't retrieve the weather information due to an error: {e}")

def listen_for_city():
    """Function to listen for a city name."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Please say the name of the city you want the weather information for.")
        print("Listening for city name...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        
        try:
            city = recognizer.recognize_google(audio)
            print(f"You said: {city}")
            return city
        except sr.UnknownValueError:
            speak("Sorry, I did not understand the city name. Please try again.")
            return None
        except sr.RequestError as e:
            speak(f"Could not request results; {e}")
            return None

def translate_sentence():
    """Function to translate a sentence from one language to another."""
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
    """Function to set a timer using a GUI."""
    def start_timer():
        try:
            duration = int(entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of seconds.")
            return
        window.withdraw()
        time.sleep(duration)
        messagebox.showinfo("Timer", "Time's up!")

    window = tk.Tk()
    window.title("Set Timer")
    label = tk.Label(window, text="Enter duration (in seconds):")
    label.pack()
    entry = tk.Entry(window)
    entry.pack()
    button = tk.Button(window, text="Start Timer", command=start_timer)
    button.pack()
    window.mainloop()

def start_stopwatch():
    """Function to start the stopwatch with a GUI display."""
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

    window = tk.Tk()
    window.title("Stopwatch")
    start_time = 0
    running = False

    label = tk.Label(window, text="00:00:00", font=("Helvetica", 48))
    label.pack()

    start_button = tk.Button(window, text="Start", command=on_start)
    start_button.pack(side=tk.LEFT)

    stop_button = tk.Button(window, text="Stop", command=on_stop)
    stop_button.pack(side=tk.RIGHT)

    window.mainloop()

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
    salutations = ['bye bye', 'bye','farewell', 'peace out', 'catch you later']
    
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
    elif 'website' in query:
        speak("Which website do you want me to open?")
        website = listen()
        if website != "None":
            url = f"https://www.{website}.com"
            webbrowser.open(url)
            speak(f"Opening {website}")
            return True  
    elif 'joke' in query:
        speak(pyjokes.get_joke())
    elif 'weather' in query:
        city = listen_for_city()
        if city:
            get_weather(city)
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
