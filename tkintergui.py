import tkinter as tk
import serial
import time
import json
import os

current_values_file = "current_slider_values.json"
previous_values_file = "previous_slider_values.json"
button_states_file = "button_states.json"

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
    ser = None

# Initialize the main window
root = tk.Tk()
root.title("Servo Controller")

# Create 8 sliders
sliders = []
for i in range(2):
    slider = tk.Scale(root, from_=0, to=180, orient='vertical')
    slider.set(90)  # Set default position
    slider.grid(row=i, column=0, padx=10, pady=5)
    sliders.append(slider)

# Create 4 horizontal sliders in the center
for i in range(4):
    slider = tk.Scale(root, from_=0, to=180, orient='horizontal')
    slider.set(90)  # Set default position
    slider.grid(row=0, column=i+1, padx=10, pady=5)
    sliders.append(slider)

# Create 2 vertical sliders on the right side
for i in range(2):
    slider = tk.Scale(root, from_=0, to=180, orient='vertical')
    slider.set(90)  # Set default position
    slider.grid(row=i, column=5, padx=10, pady=5)
    sliders.append(slider)

last_sent_values = None

# Function to get slider values
def send_slider_values():
    global last_sent_values

    if ser and ser.is_open:
        try:
            # Gather slider values
            values = [slider.get() for slider in sliders]
            print(f"Slider values: {values}")  # Debug print
            
            # Only send values if they are different from the last sent ones
            if values != last_sent_values:
                message = ",".join(map(str, values)) + "\n"
                ser.write(message.encode('utf-8'))  # Send the message
                last_sent_values = values  # Update the last sent values
                print(f"Sent: {message.strip()}")  # Debug print
                time.sleep(0.1)  # Add a small delay to avoid spamming
            else:
                print("No change in slider values, not sending.")
        
        except serial.SerialException as e:
            print(f"Serial error: {e}")
    else:
        print("Serial port not open or not available.")
# Function to undo to the last saved values
def undo_slider():
    previous_values = load_values(previous_values_file)
    if previous_values:
            # Set sliders to the previous values
        for slider, value in zip(sliders, previous_values):
            slider.set(value)
        
        #    Send the previous values over serial
        message = ",".join(map(str, previous_values)) + "\n"
        if ser and ser.is_open:
            try:
                ser.write(message.encode('utf-8'))
                print(f"Undo Sent: {message.strip()}")
            except serial.SerialException as e:
                print(f"Serial error: {e}")
    else:
        print("No saved values to undo.")

# Function to save the current slider values
def save_current_values():
    # Gather slider values
    values = [slider.get() for slider in sliders]
    
    # First, save the current values as the previous values
    previous_values = load_values(current_values_file)
    if previous_values:
        save_values(previous_values, previous_values_file)
        print(f"Saved previous values: {previous_values}")
    
    # Save the current values as the new state
    save_values(values, current_values_file)
    print(f"Saved Current Values: {values}")

def stand_position():
    return [0, 180, 0, 180, 0, 0, 180, 0]

def sit_position():
    return [90, 90, 90, 90, 90, 90, 90, 90]

def waving_sequence_1():
    return [0, 180, 0, 140, 0, 0, 180, 0]

def waving_sequence_2():
    return [0, 180, 0, 0, 0, 0, 180, 0]

button_states = load_values(button_states_file) or {}
sit_stand_state = button_states.get("sit_stand", False)
waving_state = button_states.get("waving", False)

def toggle_sit_stand():
    global sit_stand_state
    if sit_stand_state:
        # Move to stand position
        values = stand_position()
        sit_stand_state = False
    else:
        # Move to sit position
        values = sit_position()
        sit_stand_state = True
    save_values({"sit_stand": sit_stand_state}, button_states_file)  # Save button state
    update_servos(values)

def toggle_waving():
    #step 1:
    stand_values = stand_position()
    update_servos(stand_values)

    # step 2:
    print("Preforming wave set")
    waving_sequences = [
        [0, 180, 0, 0, 0, 0, 180, 0],
        [0, 180, 0, 140, 0, 0, 180, 0]
    ]

    for cycle in range(4):
        print(f"Cycle {cycle + 1}:")
        for sequence in waving_sequences:
            update_servos(sequence)
            time.sleep(0.05)
        print(f"Completed cycle {cycle + 1}")
    stand_position()
    print("Wave sequence completed.")

def update_servos(values):
    # Set the sliders and send the values
    for slider, value in zip(sliders, values):
        slider.set(value)
    send_slider_values()

def set_default_position():
    default_position = [90] * len(sliders)  # Set all sliders to 90 (default position)
    update_servos(default_position)  # Send the default position to the servos
    print("All servos set to default position (90 degrees).")

# Create a frame for the buttons
button_frame = tk.Frame(root)
button_frame.grid(row=3, column=0, columnspan=6, pady=10)

# Button to save slider values
save_button = tk.Button(button_frame, text="Save Slider Values", command=save_current_values)
save_button.pack(side="left", padx=10)

# Button to send slider values
send_button = tk.Button(button_frame, text="Send Slider Values", command=send_slider_values)
send_button.pack(side="left", padx=10)

# Button to undo to the last saved values
undo_button = tk.Button(button_frame, text="Undo", command=undo_slider)
undo_button.pack(side="left", padx=10)

# Button for Sit/Stand functionality
sit_stand_button = tk.Button(button_frame, text="Sit/Stand",  command=toggle_sit_stand)
sit_stand_button.pack(side="left", padx=10)

wave_button = tk.Button(button_frame, text="Wave", command=toggle_waving)
wave_button.pack(side="left", padx=10)

set_default_position()
root.mainloop()

if ser and ser.is_open:
    ser.close()
