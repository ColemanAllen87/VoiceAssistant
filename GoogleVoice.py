import google.generativeai as genai
from gtts import gTTS
import os
import pygame
import tkinter as tk
from tkinter import messagebox

GOOGLE_API_KEY = ""
genai.configure(api_key=GOOGLE_API_KEY)

generation_config = {
    "temperature": 0.7,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 500,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_NONE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_NONE"
  },
]
model = genai.GenerativeModel("gemini-1.0-pro-latest",
                               generation_config=generation_config,
                               safety_settings=safety_settings)
convo = model.start_chat()

pygame.mixer.init()

# Function to handle sending the user's input to the virtual assistant
def send_message(event=None):
    user_input = text_input.get("1.0", tk.END).strip()
    if not user_input:  # Check if the input is empty
        return

    if user_input.lower() == "end":
        print("Conversation ended.")
        # Play goodbye audio
        goodbye_sound = pygame.mixer.Sound("goodbye.mp3")
        goodbye_sound.play()
        pygame.time.wait(int(goodbye_sound.get_length() * 1000))  # Wait for goodbye to finish
        root.destroy()
    else:
        conversation_history.config(state=tk.NORMAL)
        conversation_history.insert(tk.END, f"You: {user_input}\n", "user")
        conversation_history.config(state=tk.DISABLED)
        conversation_history.see(tk.END)  # Scroll to the bottom
        
        # Disable text input
        text_input.config(state=tk.DISABLED)
        
        response = convo.send_message(user_input)
        
        # Check if the response was blocked due to safety settings
        if response.safety_rating == 'BLOCKED':
            response_text = "Sorry, I can't respond to that due to safety concerns."
        else:
            response_text = response.result.text
        
        conversation_history.config(state=tk.NORMAL)
        conversation_history.insert(tk.END, f"Gwen: {response_text}\n\n", "gwen")
        conversation_history.config(state=tk.DISABLED)
        conversation_history.see(tk.END)  # Scroll to the bottom
        
        if not muted:
            # Use gTTS to generate speech from text with Irish accent
            tts = gTTS(text=response_text, lang='en-ie', slow=False)
            tts.save("response.mp3")
            
            # Play the generated speech using pygame
            sound = pygame.mixer.Sound("response.mp3")
            sound.play()
            
            # Wait for the sound to finish playing
            pygame.time.wait(int(sound.get_length() * 1000))
        
        # Enable text input
        text_input.config(state=tk.NORMAL)
        text_input.delete("1.0", tk.END)
# Function to handle enter key press
def on_enter(event):
    if event.state & 0x1:  # Check if Shift key is pressed
        text_input.insert(tk.INSERT, "\n")  # Insert new line
    else:
        send_message()  # Send the message

# Function to toggle mute
def toggle_mute():
    global muted
    muted = not muted
    mute_button.config(text="Unmute" if muted else "Mute")

# Greeting text (replace with your desired message)
greeting_text = "Hello! I'm Gwendoline your virtual assistant. How can I help you today?"

# Text-to-speech for greeting
greeting_tts = gTTS(text=greeting_text, lang='en-ie', slow=False)  # Adjust language code if needed
greeting_tts.save("greeting.mp3")

# Create the main window
root = tk.Tk()
root.title("Virtual Assistant")
root.configure(bg="dark blue")
root.geometry("700x500")
root.resizable(True, True)  # Make the window resizable
root.option_add("*Font", "Arial 10")

# Play greeting audio
greeting_sound = pygame.mixer.Sound("greeting.mp3")
greeting_sound.play()

# Open the application after a short delay
root.after(500, root.deiconify)

# Create a frame for conversation history
history_frame = tk.Frame(root, bg="dark blue", bd=0, relief="flat")
history_frame.pack(pady=10, padx=10, fill="both", expand=True)

# Create a label for conversation history
history_label = tk.Label(history_frame, text="Conversation History:", fg="white", bg="dark blue")
history_label.pack(pady=(0, 5))

# Create a conversation history display
conversation_history = tk.Text(history_frame, width=40, height=15, wrap=tk.WORD, bg="light gray", fg="dark blue")
conversation_history.pack(pady=10, padx=5, fill="both", expand=True)
conversation_history.tag_configure("user", foreground="black")
conversation_history.tag_configure("gwen", foreground="blue")
conversation_history.config(state=tk.DISABLED)

# Create a frame for text input and buttons
input_frame = tk.Frame(root, bg="black", bd=1, relief="solid", highlightbackground="black", highlightcolor="dark blue", highlightthickness=2)
input_frame.pack(pady=(0, 10), padx=10, fill="x")

# Create a label for text input
input_label = tk.Label(input_frame, text="Enter your message:", fg="white", bg="black")
input_label.pack(side="left", padx=(5, 0))

# Create a text input box
text_input = tk.Text(input_frame, width=30, height=3, wrap=tk.WORD, bg="light gray", fg="black")
text_input.pack(side="left", padx=(5, 0), pady=5, fill="x", expand=True)
text_input.bind("<Return>", on_enter)  # Bind the Enter key to the on_enter function

# Create a frame for the buttons
button_frame = tk.Frame(input_frame, bg="black")
button_frame.pack(side="left", padx=(5, 0), pady=5)

# Create a button to send the message
send_button = tk.Button(button_frame, text="Send", command=send_message, bg="white", fg="black", relief="solid", borderwidth=1)
send_button.pack(pady=(0, 5))

# Create a mute button
muted = False
mute_button = tk.Button(button_frame, text="Mute", command=toggle_mute, bg="white", fg="black", relief="solid", borderwidth=1)
mute_button.pack(pady=(5, 0))

# Hide the main window initially
root.withdraw()

# Start the GUI event loop
root.mainloop()
