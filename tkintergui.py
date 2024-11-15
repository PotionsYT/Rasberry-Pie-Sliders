import tkinter as tk
import serial
import time
import json
import os

current_values_file = "current_slider_values.json"
previous_values_file = "previous_slider_values.json"

# Function to save values to a specific JSON file
def save_values(values, file_path):
    with open(file_path, 'w') as file:
        json.dump(values, file)

# Function to load values from a specific JSON file
def load_values(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    return None
try:
    ser = serial.Serial('COM7', baudrate=9600, timeout=1)
except serial.SerialException as e:
    print(f"Could not open serial port: {e}")

# Initialize the main window
root = tk.Tk()
root.title("Servo Controller")

# Create 8 sliders
sliders = []
for i in range(2):
    slider = tk.Scale(root, from_=0, to=180, orient='vertical')
    slider.set(50)  # Set default position
    slider.grid(row=i, column=0, padx=10, pady=5)
    sliders.append(slider)

# Create 4 horizontal sliders in the center
for i in range(4):
    slider = tk.Scale(root, from_=0, to=180, orient='horizontal')
    slider.set(50)  # Set default position
    slider.grid(row=0, column=i+1, padx=10, pady=5)
    sliders.append(slider)

# Create 2 vertical sliders on the right side
for i in range(2):
    slider = tk.Scale(root, from_=0, to=180, orient='vertical')
    slider.set(50)  # Set default position
    slider.grid(row=i, column=5, padx=10, pady=5)
    sliders.append(slider)

# Function to get slider values
def send_slider_values():
    if ser.is_open:
        try:
            # Gather slider values
            values = [slider.get() for slider in sliders]
            
            # Save the current values to the previous file before updating
            if os.path.exists(current_values_file):
                previous_values = load_values(current_values_file)
                save_values(previous_values, previous_values_file)
            
            # Save new values as the current state
            save_values(values, current_values_file)

            message = ",".join(map(str, values)) + "\n"

            # Sending the message
            ser.write(message.encode('utf-8'))  # Send the message
            print(f"Sent: {message.strip()}")
            time.sleep(0.1)  # Add a small delay to avoid spamming
        except serial.SerialException as e:
            print(f"Serial error: {e}")

# Function to undo to the last saved values
def undo_slider():
    previous_values = load_values(previous_values_file)
    if previous_values:
        # Set sliders to the previous values
        for slider, value in zip(sliders, previous_values):
            slider.set(value)
        
        # Send the previous values over serial
        message = ",".join(map(str, previous_values)) + "\n"
        if ser.is_open:
            try:
                ser.write(message.encode('utf-8'))
                print(f"Undo Sent: {message.strip()}")
            except serial.SerialException as e:
                print(f"Serial error: {e}")
    else:
        print("No saved values to undo.")
# Button to send slider values
send_button = tk.Button(root, text="Send Slider Values", command=send_slider_values)
send_button.grid(row=3, column=0, columnspan=3, pady=10)

# Button to undo to the last saved values
undo_button = tk.Button(root, text="Undo", command=undo_slider)
undo_button.grid(row=3, column=3, columnspan=3, pady=10)

root.mainloop()

if ser.is_open:
    ser.close()