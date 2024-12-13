import os
import google.generativeai as genai
import pyttsx3

class Chatbot:
    def __init__(self, api_key, model_name="gemini-pro", voice_id=None, rate=150, volume=1.0, language=None):
        self.api_key = api_key
        self.model_name = model_name
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)

        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()

        # Configure TTS settings
        voices = self.engine.getProperty('voices')

        if voice_id:
            self.engine.setProperty('voice', voice_id) # Set voice with ID
        #    for voice in voices:
        #        if voice.id == voice_id:
        #            self.engine.setProperty('voice', voice.id)
        #            break
        #        if voice.name == voice_id:
        #            self.engine.setProperty('voice', voice.id)
        #            break

        if language:
            self.engine.setProperty('language', language)

        self.engine.setProperty('rate', rate)  # Set speaking rate
        self.engine.setProperty('volume', volume)  # Set volume

    def get_response(self, text_input):
        """Sends a text input to the Google AI Studio and returns the bot's response."""
        response = self.model.generate_content(text_input)
        return response.text
    
    def speak(self, text):
        """Use Text to Speech to speak the given text"""
        self.engine.say(text)
        self.engine.runAndWait()


if __name__ == '__main__':
    # Example usage (replace with your actual API key and other settings)
    API_KEY = "YOUR_API_KEY_THUC_TE"  # Replace with your Google AI Studio API key
    VOICE_ID = None # Example "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0" # or "com.apple.speech.synthesis.voice.samantha"
    RATE = 150
    VOLUME = 1.0
    LANGUAGE = None # Example "vi-VN"
    chatbot = Chatbot(API_KEY, voice_id=VOICE_ID, rate=RATE, volume=VOLUME, language=LANGUAGE)
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        bot_response = chatbot.get_response(user_input)
        print(f"Bot: {bot_response}")
        chatbot.speak(bot_response)