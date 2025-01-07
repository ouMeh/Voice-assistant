import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import wikipedia
import requests
import random
import time
import pyjokes
from googletrans import Translator, LANGUAGES
import os
import urllib.parse
import subprocess
import tkinter as tk
from tkinter import messagebox, ttk
import threading

LANGUAGES = { "english": "en", "spanish": "es", "french": "fr", "german": "de", "italian": "it", "portuguese": "pt",
              "chinese": "zh-CN", "japanese": "ja",  "korean": "ko", "russian": "ru"}

API_KEY = 'e015ab0fb254f4d75410b1583728173a'
BASE_URL = 'http://api.openweathermap.org/data/2.5/weather'

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
        audio = recognizer.listen(source, timeout=20)
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
        if sentence:
            print(f"You said: {sentence}")
        else:
            speak("Sorry, I did not hear anything. Please try again.")
            return
    except sr.UnknownValueError:
        speak("Sorry, I did not understand the sentence. Please try again.")
        return
    except sr.RequestError as e:
        speak(f"Could not request results; {e}")
        return

    with sr.Microphone() as source:
        speak("Please say the target language.")
        print("Listening for target language...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        target_language = recognizer.recognize_google(audio).lower()
        if target_language:
            print(f"Target language: {target_language}")
        else:
            speak("Sorry, I did not hear anything. Please try again.")
            return
    except sr.UnknownValueError:
        speak("Sorry, I did not understand the target language. Please try again.")
        return
    except sr.RequestError as e:
        speak(f"Could not request results; {e}")
        return

    language_codes = {key.lower(): value for key, value in LANGUAGES.items()}
    if target_language not in language_codes:
        speak("Sorry, I don't support that language. Please try again.")
        return

    try:
        translator = Translator()
        translation = translator.translate(sentence, dest=language_codes[target_language])
        if translation and translation.text:
            speak(f"The translation in {target_language} is: {translation.text}")
        else:
            speak("Sorry, I couldn't get the translation. Please try again.")
    except AttributeError as e:
        speak(f"An error occurred: {str(e)}. It seems the translation service returned an unexpected result.")
        print(f"AttributeError: {str(e)}")
    except Exception as e:
        speak(f"An unexpected error occurred during translation: {str(e)}")
        print(f"Error: {str(e)}")
  
def set_timer_gui():
    window = tk.Tk()
    window.title("Timer")
    
    def start_timer():
        try:
            duration = int(entry.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number of seconds.")
            return
        window.withdraw()
        threading.Thread(target=run_timer, args=(duration, window)).start()

    def run_timer(duration, window):
        time.sleep(duration)
        window.after(0, lambda: messagebox.showinfo("Timer", "Time's up!"))
        window.deiconify()

    label = ttk.Label(window, text="Enter duration (in seconds):")
    label.pack(pady=10)
    entry = ttk.Entry(window)
    entry.pack(pady=10)
    button = ttk.Button(window, text="Start Timer", command=start_timer)
    button.pack(pady=10)
    window.mainloop()

def start_stopwatch():
    window = tk.Tk()
    window.title("Stopwatch")
    
    start_time = 0
    running = False

    label = tk.Label(window, text="00:00:00", font=("Helvetica", 48))
    label.pack()

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

    start_button = tk.Button(window, text="Start", command=on_start)
    start_button.pack(side=tk.LEFT)

    stop_button = tk.Button(window, text="Stop", command=on_stop)
    stop_button.pack(side=tk.RIGHT)

    window.mainloop()
    
def get_weather(city):
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        data = response.json()
        main = data['main']
        wind = data['wind']
        weather_description = data['weather'][0]['description']
        temperature = main['temp']
        humidity = main['humidity']
        wind_speed = wind['speed']
        return (temperature, humidity, wind_speed, weather_description)
    else:
        return None

def open_website():
    speak("Which website do you want me to open?")
    website = listen()
    if website != "None":
        url = f"https://www.{website}.com"
        webbrowser.open(url)
        speak(f"Opening {website}")
        return True

def create_note():
    try:
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
    except Exception as e:
        speak(f"An error occurred while creating the note: {str(e)}")

def get_wikipedia_summary():
    speak("What topic would you like to know about?")
    topic = listen()
    
    if topic:
        try:
            summary = wikipedia.summary(topic, sentences=3)
            speak(f"Here's a brief summary of {topic}:")
            print(f"Summary: {summary}")
            speak(summary)
        except wikipedia.exceptions.DisambiguationError as e:
            speak("There are multiple results for this topic. Please be more specific.")
            print(f"Disambiguation Error: {e.options}")
        except wikipedia.exceptions.PageError:
            speak("Sorry, I couldn't find any information on that topic.")
    else:
        speak("I couldn't hear the topic name.")
        
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
    elif 'day' in query:
        current_day = datetime.datetime.now().strftime("%A")
        speak(f"Today is {current_day}")
    elif 'wikipedia' in query:
        get_wikipedia_summary()
    elif 'website' in query:
        open_website()
    elif 'joke' in query:
        speak(pyjokes.get_joke())
    elif 'translate' in query:
        translate_sentence()
    elif 'weather' in query:
        speak('Please tell me the city name.')
        city = listen()
        if city == "None":
            return
        weather = get_weather(city)
        if weather:
            temperature, humidity, wind_speed, weather_description = weather
            weather_report = (
                f'The current temperature in {city} is {temperature}°C with {weather_description}. '
                f'The humidity level is {humidity}% and the wind speed is {wind_speed} meters per second.'
            )
            speak(weather_report)
        else:
            speak('Sorry, I could not retrieve the weather information.')
    elif 'note' in query:
        create_note()
    elif any(salutation in query for salutation in salutations):
        speak("Goodbye!")
        exit(0)
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
