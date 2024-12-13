import pickle
import cv2
import mediapipe as mp
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from collections import deque
import time
from chatbot import Chatbot
import os

# Load model
model_dict = pickle.load(open('./model.p', 'rb'))
model = model_dict['model']

# Initialize webcam
cap = cv2.VideoCapture(0)

# Initialize mediapipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

# Labels dictionary
labels_dict = {
    0: 'Miêu tả',
    1: 'con mèo',
    2: 'con chó',
    3: 'Cảm ơn',
    4: 'Tạm biệt',
    5: 'ngắn gọn',
    6: 'cách làm',
    7: 'bánh ngọt',
}

# Initialize label history
label_history = deque(maxlen=5)

# Initialize chatbot with Google AI Studio API key
API_KEY = "AIzaSyCYFgjfukemCJ6zJdnFp51V2Iu-BqqqTd0"  # Replace with your API key
VOICE_ID = "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_viVN_An" # Example "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0" # or "com.apple.speech.synthesis.voice.samantha"
RATE = 150
VOLUME = 1.0
LANGUAGE = "vi-VN"
chatbot = Chatbot(API_KEY, voice_id=VOICE_ID, rate=RATE, volume=VOLUME, language=LANGUAGE)

# Initialize a variable to store the last predicted label (for smoothing and triggering)
last_predicted_label = None
# Initialize variables to store the last predicted label time
last_detected_time = 0
detection_threshold = 3  # 3 seconds

# Initialize variable to store input text
combined_text = ""

# Trạng thái của hệ thống:
# - 'waiting_for_hand': Chờ phát hiện tay
# - 'detecting_sign': Đang chờ 3 giây để nhận diện ký hiệu
system_state = 'waiting_for_hand'
start_detect_time = 0
MAX_LENGTH = 42

# Initialize Tkinter window
window = tk.Tk()
window.title("Sign Language Chatbot")

# Configure the grid layout
window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)

# Load images
logo_dir = 'logo'
delete_icon = Image.open(os.path.join(logo_dir, 'deleteIcon.png'))
chat_icon = Image.open(os.path.join(logo_dir, 'chatIcon.jpg'))
settings_icon = Image.open(os.path.join(logo_dir, 'settingsIcon.png')) # Load settings icon
back_icon = Image.open(os.path.join(logo_dir, 'backIcon.png'))
save_icon = Image.open(os.path.join(logo_dir, 'saveIcon.png'))


# Resize images (optional)
delete_icon = delete_icon.resize((20, 20), Image.LANCZOS)
chat_icon = chat_icon.resize((20, 20), Image.LANCZOS)
settings_icon = settings_icon.resize((20, 20), Image.LANCZOS)
back_icon = back_icon.resize((30, 30), Image.LANCZOS)
save_icon = save_icon.resize((30, 30), Image.LANCZOS)



# Convert to PhotoImage
delete_icon_tk = ImageTk.PhotoImage(delete_icon)
chat_icon_tk = ImageTk.PhotoImage(chat_icon)
settings_icon_tk = ImageTk.PhotoImage(settings_icon)
back_icon_tk = ImageTk.PhotoImage(back_icon)
save_icon_tk = ImageTk.PhotoImage(save_icon)


# Create main frame
main_frame = tk.Frame(window)
main_frame.grid(row=0, column=0, sticky="nsew")
main_frame.grid_columnconfigure(1, weight=1, minsize=400)  # Make the output column stretch

# Create settings frame inside main_frame
settings_frame = tk.Frame(main_frame)
settings_frame.grid(row=0, column=1, sticky="nsew")


# Frame for Camera
camera_frame = tk.Frame(main_frame)
camera_frame.grid(row=0, column=0, sticky="nsew")

# Label for Camera
camera_label = tk.Label(camera_frame)
camera_label.pack()

# Frame for Output and Controls
output_frame = tk.Frame(main_frame)
output_frame.grid(row=0, column=1, sticky="nsew")

# Configure the grid layout for output_frame
output_frame.grid_rowconfigure(0, weight=1)  # Give all extra space to the output text area
output_frame.grid_columnconfigure(0, weight=1)


# Text widget for output with scrollbar
output_text = tk.Text(output_frame, font=("Arial", 14), wrap="word", width=50, height=10)
output_text.grid(row=0, column=0, sticky="nsew", pady=20)


# Scrollbar
scrollbar = tk.Scrollbar(output_frame, command=output_text.yview)
scrollbar.grid(row=0, column=1, sticky="ns", pady=20)
output_text.configure(yscrollcommand=scrollbar.set)


# Entry for text input
input_text = tk.StringVar()
input_entry = tk.Entry(output_frame, textvariable=input_text, font=("Arial", 12), width=40)
input_entry.grid(row=1, column=0, pady=10, sticky="ew", columnspan=1)

# Function for clear text box
def clear_text_box():
    global combined_text
    combined_text = ""
    input_text.set("")

# Button to clear text box
clear_text_button = tk.Button(output_frame, image=delete_icon_tk, command=clear_text_box)
clear_text_button.grid(row=1, column=1, sticky="ew", pady=10)

# Button to trigger the chatbot
chatbot_button = tk.Button(output_frame, text="Ask Chatbot", image=chat_icon_tk, compound="left", command=lambda: trigger_chatbot(input_text.get()))
chatbot_button.grid(row=2, column=0, sticky="ew", columnspan=2)

# --------- Settings Page --------------
# Function for switching between main_frame and setting_frame
def show_settings():
    output_frame.grid_forget()
    settings_frame.grid(row=0, column=1, sticky="nsew")

def show_main():
    settings_frame.grid_forget()
    output_frame.grid(row=0, column=1, sticky="nsew")

# Settings Button on the main screen
settings_button = tk.Button(output_frame, image=settings_icon_tk, command=show_settings)
settings_button.grid(row=2, column=1, sticky="ew")

# Back button
back_button = tk.Button(settings_frame, image=back_icon_tk, command=show_main)
back_button.pack(pady=20)

voice_id_to_country = {
    "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\MSTTS_V110_viVN_An": "Việt Nam",
    "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0": "Mỹ",
    "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0": "Anh Mỹ",
}

# Voice ID combobox
voice_label = ttk.Label(settings_frame, text="Voice ID:")
voice_label.pack()
voice_ids = [voice.id for voice in chatbot.engine.getProperty('voices')]
voice_names = [voice_id_to_country.get(voice_id,voice_id) for voice_id in voice_ids ] # Lấy tên quốc gia tương ứng
voice_combo = ttk.Combobox(settings_frame, values=voice_names)
voice_combo.insert(0, voice_id_to_country.get(chatbot.engine.getProperty('voice'),chatbot.engine.getProperty('voice'))) # Set default values
voice_combo.pack()


# Language Combobox
language_label = ttk.Label(settings_frame, text="Language:")
language_label.pack()
language_combo = ttk.Combobox(settings_frame, values=['en-US','vi-VN'])
language_combo.insert(0, 'vi-VN') # Set default values
language_combo.pack()


# Rate slider
rate_label = ttk.Label(settings_frame, text="Rate:")
rate_label.pack()
rate_slider = tk.Scale(settings_frame, from_=50, to=300, orient=tk.HORIZONTAL, label=f"Current Rate: {RATE}")
rate_slider.set(RATE)
rate_slider.pack()

# Volume slider
volume_label = ttk.Label(settings_frame, text="Volume:")
volume_label.pack()
volume_slider = tk.Scale(settings_frame, from_=0, to=1.0, resolution = 0.1, orient=tk.HORIZONTAL, label=f"Current Volume: {VOLUME}")
volume_slider.set(VOLUME)
volume_slider.pack()


# Save Settings button
def save_settings():
    global chatbot
    #Update Chatbot
    new_voice_name = voice_combo.get()
    new_voice_id = next((key for key, value in voice_id_to_country.items() if value == new_voice_name), new_voice_name)  # Lấy voice ID tương ứng từ dict, nếu không có thì giữ lại tên
    new_language = language_combo.get()
    new_rate = int(rate_slider.get())
    new_volume = volume_slider.get()
    chatbot = Chatbot(API_KEY, voice_id=new_voice_id, rate=new_rate, volume=new_volume, language=new_language)
    show_main()  # Return to the main screen
    

save_button = tk.Button(settings_frame, image=save_icon_tk, command=save_settings)
save_button.pack(pady=20)

# --------- End Settings Page --------------


# Function for chatbot trigger
def trigger_chatbot(text_input=None):
    global last_predicted_label, combined_text
    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    if text_input:
        bot_response = chatbot.get_response(text_input)
        output_text.insert(tk.END, f"Chatbot: {bot_response}")
        chatbot.speak(bot_response)
    elif combined_text:
        bot_response = chatbot.get_response(combined_text)
        output_text.insert(tk.END, f"Chatbot: {bot_response}")
        chatbot.speak(bot_response)
        combined_text = ""
        input_text.set("")  # clear text input after ask
    else:
        output_text.insert(tk.END, "No sign detected or text entered.")
    output_text.config(state=tk.DISABLED)

def update_frame():
    global last_predicted_label, last_detected_time, combined_text, system_state, start_detect_time
    ret, frame = cap.read()
    current_time = time.time()

    if ret:
        H, W, _ = frame.shape

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        results = hands.process(frame_rgb)
        
        if results.multi_hand_landmarks:
             for hand_landmarks in results.multi_hand_landmarks:
                 mp_drawing.draw_landmarks(
                    frame,  # image to draw
                    hand_landmarks,  # model output
                    mp_hands.HAND_CONNECTIONS,  # hand connections
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
        
        if system_state == 'waiting_for_hand':
            if results.multi_hand_landmarks:
                # Nếu phát hiện tay, chuyển sang trạng thái detecting_sign và lưu lại thời điểm bắt đầu
                system_state = 'detecting_sign'
                start_detect_time = current_time
                label_history.clear() # clear history
                last_predicted_label = None # reset label
            
        elif system_state == 'detecting_sign':
             if results.multi_hand_landmarks:
                 if current_time - start_detect_time >= detection_threshold: # Đã qua 3 giây
                    
                    all_data_aux = []
                    for hand_landmarks in results.multi_hand_landmarks:
                        data_aux = []
                        x_ = []
                        y_ = []
                        
                        for i in range(len(hand_landmarks.landmark)):
                            x = hand_landmarks.landmark[i].x
                            y = hand_landmarks.landmark[i].y
                            x_.append(x)
                            y_.append(y)
                        
                        for i in range(len(hand_landmarks.landmark)):
                            x = hand_landmarks.landmark[i].x
                            y = hand_landmarks.landmark[i].y
                            data_aux.append(x - min(x_))
                            data_aux.append(y - min(y_))
                        
                        # Padding or Truncate the data_aux
                        if len(data_aux) < MAX_LENGTH:
                            data_aux.extend([0] * (MAX_LENGTH - len(data_aux)))
                        elif len(data_aux) > MAX_LENGTH:
                            data_aux = data_aux[:MAX_LENGTH]
                        all_data_aux.append(data_aux)

                    if all_data_aux:
                        predicted_labels = []
                        for data_aux in all_data_aux:
                            prediction = model.predict([np.asarray(data_aux)])
                            predicted_labels.append(labels_dict[int(prediction[0])])

                        combined_prediction = " ".join(predicted_labels)

                        # Thêm từ vào combined_text
                        combined_text += " " + combined_prediction if combined_text else combined_prediction
                        input_text.set(combined_text)
                    
                    # Chuyển về trạng thái chờ tay và reset
                    system_state = 'waiting_for_hand'
                    
                    
                 else: # Chưa đủ 3 giây , vẫn detect và vẽ khung
                      for hand_landmarks in results.multi_hand_landmarks:
                          x_ = []
                          y_ = []
                          for i in range(len(hand_landmarks.landmark)):
                                x = hand_landmarks.landmark[i].x
                                y = hand_landmarks.landmark[i].y
                                x_.append(x)
                                y_.append(y)
                          x1 = int(min(x_) * W) - 10
                          y1 = int(min(y_) * H) - 10
                          x2 = int(max(x_) * W) - 10
                          y2 = int(max(y_) * H) - 10
                          cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)    

             else: # Nếu không còn phát hiện tay, trở về waiting_for_hand
                 system_state = 'waiting_for_hand'


        # Convert cv2 image to PIL image
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image)

        camera_label.config(image=photo)
        camera_label.image = photo
    window.after(10, update_frame)

update_frame()
main_frame.grid(row=0, column=0, sticky="nsew")
window.mainloop()
cap.release()