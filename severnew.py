from machine import Pin, PWM, UART
import sys
import time
from random import randint

def degrees_to_duty(degrees):
    min_pulse_width = 1000  # Minimum pulse width in microseconds
    max_pulse_width = 2000  # Maximum pulse width in microseconds
    pulse_width = min_pulse_width + (degrees / 180.0) * (max_pulse_width - min_pulse_width)
    return int((pulse_width / 20000.0) * 65535)

uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

# Initialize servos on pins
servo1 = PWM(0, freq=50)
servo2 = PWM(3, freq=50)
servo3 = PWM(4, freq=50)
servo4 = PWM(7, freq=50)
servo5 = PWM(8, freq=50)
servo6 = PWM(11, freq=50)
servo7 = PWM(12, freq=50)
servo8 = PWM(15, freq=50)

def listen_serial():
    while True:  # Infinite loop
        if uart.any():  # Check if there's any data available
            message = uart.read().decode('utf-8').strip()  # Read and decode the data
            if message.isdigit():  # Check if the message is a digit
                print('Position acquired:', message)
                position = int(message)  # Convert to integer
                # Further processing of 'position' can go here
            else:
                print('Invalid input, not a digit:', message)
        time.sleep(0.1)  # Small delay to avoid busy waiting

def move_servos(servo, pos):# + servo1  
    movement = degrees_to_duty(pos)
    
    servo.duty_u16(movement)
    time.sleep(0.01)  # Wait for 1 second
    print(f"Servo moved")
        
    # Stop all servos
    servo.duty_u16(0)  # Set duty cycle to 0 to stop the servo

servos = [servo1, servo2, servo3, servo4, servo5, servo6, servo7, servo8]

# # Run the servo movement
# while True:
# #     positions = listen_serial() # "30, 35, 120, .... *8"
# #     move_servos(pos) # +servo you ant to move)
#     try:
#         servo_index = int(input("pick which servo to move: ")) -1
#         pos = int(input("enter a number for pos: "))
#         if 0 <= servo_index < len(servos):
#             move_servos(servos[servo_index], pos)

#     except ValueError:
#         print("Input error, Try a different number")



try:
    listen_serial()
except KeyboardInterrupt:
    print("Exiting...")


# for i in range(7):
#     for values in pos:
    
#         move_servos(servos[i], pos[i])
#         print(f'servo {i} is moving to {pos[i]}')



