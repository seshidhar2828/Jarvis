import cv2
import pyttsx3
import speech_recognition as sr
from datetime import datetime, timedelta
import pywhatkit
import webbrowser
import os
import time

# Initialize Text-to-Speech
engine = pyttsx3.init()

def speak(text):
    print(f"Jarvis: {text}")
    engine.say(text)
    engine.runAndWait()

def listen_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source, phrase_time_limit=5)
    try:
        command = recognizer.recognize_google(audio).lower()
        print(f"You said: {command}")
        return command
    except sr.UnknownValueError:
        speak("Sorry, I didn't catch that.")
        return ""
    except sr.RequestError:
        speak("Sorry, there was an internet issue.")
        return ""

def detect_motion_and_face():
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)
    time.sleep(2)  # Warm-up camera

    # Initialize for motion detection
    _, frame1 = cap.read()
    frame1_gray = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    frame1_gray = cv2.GaussianBlur(frame1_gray, (21, 21), 0)

    speak("Motion and face detection started. Press Q to stop.")

    while True:
        ret, frame2 = cap.read()
        if not ret:
            speak("Camera not accessible.")
            break

        gray = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # Detect motion
        frame_diff = cv2.absdiff(frame1_gray, gray)
        thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = False
        for contour in contours:
            if cv2.contourArea(contour) < 1000:
                continue
            motion_detected = True
            break

        if motion_detected:
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in faces:
                cv2.rectangle(frame2, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame2, "Face Detected", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame2, "Motion Detected", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

        cv2.imshow("Jarvis Motion + Face Detection - Press Q to exit", frame2)

        frame1_gray = gray  # Update reference frame

        if cv2.waitKey(1) & 0xFF == ord('q'):
            speak("Motion and face detection stopped.")
            break

    cap.release()
    cv2.destroyAllWindows()

def get_greeting():
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "Good morning"
    elif 12 <= current_hour < 17:
        return "Good afternoon"
    elif 17 <= current_hour < 21:
        return "Good evening"
    else:
        return "Hello"

def jarvis():
    greeting = get_greeting()
    speak(f"{greeting}, I am Jarvis. How can I help you today?")

    while True:
        command = listen_command()

        if "detect face" in command or "motion" in command:
            detect_motion_and_face()

        elif "time" in command:
            now = datetime.now().strftime("%H:%M")
            speak(f"The current time is {now}")

        elif "open youtube" in command or "play video" in command:
            speak("What should I search on YouTube?")
            query = listen_command()
            if query:
                speak(f"Playing {query} on YouTube")
                pywhatkit.playonyt(query)

        elif "search google" in command or "google" in command:
            speak("What should I search on Google?")
            query = listen_command()
            if query:
                speak(f"Searching Google for {query}")
                pywhatkit.search(query)

        elif "send whatsapp" in command or "whatsapp" in command:
            speak("Please say the phone number with country code.")
            phone = listen_command().replace(" ", "")
            speak("What is the message?")
            message = listen_command()
            if phone and message:
                speak("Sending message in about 2 minutes. Please keep WhatsApp Web open.")
                try:
                    now = datetime.now() + timedelta(minutes=2)
                    hour = now.hour
                    minute = now.minute
                    pywhatkit.sendwhatmsg("+" + phone, message, hour, minute, wait_time=20)
                    speak("Message scheduled successfully.")
                except Exception as e:
                    speak("Something went wrong while sending the message.")
                    print("Error:", e)

        elif "play music" in command and "jio saavn" not in command:
            speak("What song should I play?")
            song = listen_command()
            if song:
                speak(f"Playing {song} on YouTube.")
                pywhatkit.playonyt(song)

        elif "play music on jio saavn" in command or "jio saavn" in command:
            speak("What song should I search on JioSaavn?")
            song = listen_command()
            if song:
                speak(f"Searching for {song} on JioSaavn")
                search_url = f"https://www.jiosaavn.com/search/{song.replace(' ', '%20')}"
                webbrowser.open(search_url)

        elif "introduce yourself" in command or "who developed you" in command:
            speak("I am Jarvis, a voice assistant developed by Seshidhar. I can help you with various tasks like face detection, playing music, searching online, and more.")

        elif "exit" in command or "bye" in command:
            speak("Bye! Have a great day.")
            break

        elif command:
            speak("Sorry, I did not understand that. Please try again.")

if __name__ == "__main__":
    jarvis()
