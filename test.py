import tkinter as tk
import serial
import json
import os
import time

# Constants for file paths
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

class SerialCommunicator:
    """Handles serial communication with the Pico."""
    
    def __init__(self, port='COM7', baud_rate=9600):
        """Initialize the serial connection."""
        try:
            self.ser = serial.Serial(port, baudrate=baud_rate, timeout=1)
        except serial.SerialException as e:
            print(f"Could not open serial port: {e}")
            self.ser = None

    def send_command(self, values):
        """Send the command (slider values) to the Pico."""
        if self.ser and self.ser.is_open:
            try:
                message = ",".join(map(str, values)) + "\n"
                self.ser.write(message.encode('utf-8'))
                print(f"Sent: {message.strip()}")
            except serial.SerialException as e:
                print(f"Serial error: {e}")

    def close(self):
        """Close the serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()

class Servo:
    """Represents a servo motor in the GUI."""
    
    def __init__(self, parent, name, x, y, min_val=0, max_val=180, orientation='vertical'):
        """Initialize a servo control in the GUI at specific pixel coordinates."""
        self.name = name
        if orientation == 'vertical':
            self.slider = tk.Scale(parent, from_=min_val, to=max_val, orient='vertical', label=name)
            self.slider.set(90)  # Set default position
            self.slider.place(x=x, y=y)
        else:
            self.slider = tk.Scale(parent, from_=min_val, to=max_val, orient='horizontal', label=name)
            self.slider.set(90)  # Set default position
            self.slider.place(x=x, y=y)
    
    def get_value(self):
        """Get the current value of the servo."""
        return self.slider.get()

    def set_value(self, value):
        """Set the value of the servo."""
        self.slider.set(value)

class Quadruped:
    """Represents the entire quadruped robot."""
    
    def __init__(self, parent, serial_communicator):
        """Initialize the quadruped with four legs and their corresponding servos."""
        self.servos = []
        self.serial_communicator = serial_communicator
        self.servos.append(Servo(parent, 'Servo 1', 50, 100, orientation='vertical'))
        self.servos.append(Servo(parent, 'Servo 2', 50, 200, orientation='vertical'))
        self.servos.append(Servo(parent, 'Servo 3', 500, 100, orientation='vertical'))
        self.servos.append(Servo(parent, 'Servo 4', 500, 200, orientation='vertical'))

        # Horizontal sliders on the left and right columns (positions 0, 1, 6, 7)
        self.servos.append(Servo(parent, 'Servo 5', 100, 150, orientation='horizontal'))
        self.servos.append(Servo(parent, 'Servo 6', 200, 150, orientation='horizontal'))
        self.servos.append(Servo(parent, 'Servo 7', 300, 150, orientation='horizontal'))
        self.servos.append(Servo(parent, 'Servo 8', 400, 150, orientation='horizontal'))

        self.set_default_positions()

    def get_all_positions(self):
        """Get positions of all servos in the quadruped."""
        return [servo.get_value() for servo in self.servos]

    def set_all_positions(self, positions):
        """Set positions of all servos in the quadruped."""
        for servo, position in zip(self.servos, positions):
            servo.set_value(position)

    def set_default_positions(self):
        """Set all servos to a default position (e.g., 90)."""
        default_position = [90] * len(self.servos)  # Set all servos to 90 degrees
        self.set_all_positions(default_position)
        self.serial_communicator.send_command(default_position)  # Send to Pico        

class StateManager:
    """Manages saving and loading of robot states."""
    
    def __init__(self):
        """Initialize the state manager."""
        pass

    def load_states(self, filename):
        """Load states from a file."""
        return load_values(filename)

    def save_states(self, filename, states):
        """Save states to a file."""
        save_values(states, filename)

class QuadrupedGUI:
    """Main GUI class for controlling the quadruped robot."""
    
    def __init__(self, root):
        """Initialize the GUI."""
        self.root = root
        self.root.title("Servo Controller")
        
        self.root.geometry("800x600")  # Set the window size to 800x600 pixels

         # Initialize serial communicator
        self.serial_communicator = SerialCommunicator()

        # Initialize quadruped and pass the serial communicator
        self.quadruped = Quadruped(root, self.serial_communicator)

        self.create_gui()
        self.quadruped.set_default_positions()

    def create_gui(self):
        """Create the GUI elements."""
        # Button frame for actions
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Buttons
        self.save_button = tk.Button(button_frame, text="Save Slider Values", command=self.save_current_values)
        self.save_button.pack(side="left", padx=10)
        
        self.send_button = tk.Button(button_frame, text="Send Slider Values", command=self.send_slider_values)
        self.send_button.pack(side="left", padx=10)
        
        self.undo_button = tk.Button(button_frame, text="Undo", command=self.undo_slider)
        self.undo_button.pack(side="left", padx=10)
        
        self.sit_stand_button = tk.Button(button_frame, text="Sit/Stand", command=self.toggle_sit_stand)
        self.sit_stand_button.pack(side="left", padx=10)

        self.wave_button = tk.Button(button_frame, text="Wave", command=self.toggle_waving)
        self.wave_button.pack(side="left", padx=10)

    def save_current_values(self):
        """Save the current state of the servos."""
        values = self.quadruped.get_all_positions()
        save_values(values, current_values_file)

    def send_slider_values(self):
        """Send the current slider values to the Pico."""
        values = self.quadruped.get_all_positions()
        self.serial_communicator.send_command(values)

    def undo_slider(self):
        """Undo to the previous state."""
        previous_values = load_values(previous_values_file)
        if previous_values:
            self.quadruped.set_all_positions(previous_values)
            self.serial_communicator.send_command(previous_values)

    def toggle_sit_stand(self):
        """Toggle between sit and stand positions."""
        sit_position = [90, 90, 90, 90, 90, 90, 90, 90]  # Example sit position
        stand_position = [0, 180, 0, 180, 0, 0, 180, 0]  # Example stand position
        
        current_values = self.quadruped.get_all_positions()
        if current_values == sit_position:
            self.quadruped.set_all_positions(stand_position)
        else:
            self.quadruped.set_all_positions(sit_position)
        
        self.serial_communicator.send_command(self.quadruped.get_all_positions())


    def toggle_waving(self):
        """Toggle waving sequence."""
        wave_sequence_1 = [0, 180, 0, 140, 0, 0, 180, 0]
        wave_sequence_2 = [0, 180, 0, 40, 0, 0, 180, 0]
        self.serial_communicator.send_command(wave_sequence_1)
        time.sleep(0.1)
        self.serial_communicator.send_command(wave_sequence_2)
        time.sleep(0.1)
        self.serial_communicator.send_command(wave_sequence_1)
        self.serial_communicator.send_command(wave_sequence_2)
        time.sleep(0.5)
        self.serial_communicator.send_command(wave_sequence_1)
        self.serial_communicator.send_command(wave_sequence_2)
        time.sleep(0.1)
        self.serial_communicator.send_command(wave_sequence_1)
        self.serial_communicator.send_command(wave_sequence_2)
        time.sleep(0.1)
        self.serial_communicator.send_command(wave_sequence_1)

    def close(self):
        """Close the serial connection when done."""
        self.serial_communicator.close()

# Main loop
if __name__ == "__main__":
    root = tk.Tk()
    app = QuadrupedGUI(root)
    root.mainloop()
    app.close()
