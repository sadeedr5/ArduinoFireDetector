# Import libraries
import email.message
import smtplib
import socket
import ssl
from datetime import datetime
from os import system
from threading import Thread
from typing import Any, List, Optional

import serial.tools.list_ports
import simpleaudio as sa
from decouple import config

# Configurations.
# Define the email credentials
MAIN_EMAIL = config('MAIN_EMAIL')
MAIN_EMAIL_PASSWORD = config('MAIN_EMAIL_PASSWORD')
SKIP_SERIAL_CONN = config('SKIP_SERIAL_CONN', cast=bool, default=False)
SKIP_ALARM = config('SKIP_ALARM', cast=bool, default=False)
SKIP_EMAIL = config('SKIP_EMAIL', cast=bool, default=False)

# Define a variable to store the number of signal passes.
signal_passes: int = 0


# Functions.
def register(signal: str) -> None:
    """
    Prints the signal and increments the signal_passes variable.
    """

    global signal_passes
    signal_passes += 1
    print(f'#{signal_passes}: {signal}')


def get_arduino_serial() -> Optional[serial.Serial]:
    """
    Returns a Serial object if the Arduino is connected to the computer.
    """

    # Define a port variable
    ports: List[Any] = []

    # Searching for ports
    for port in serial.tools.list_ports.comports():
        print('Discovered port:', port)

        try:
            if 'Arduino' in port.manufacturer:
                print('Attempting to use port:', port.device)
                ports.append(port)

        except TypeError:
            pass

    # Form a Serial object with the same port
    try:
        return serial.Serial(port=ports[0].device, baudrate=115200, timeout=20)
    except serial.serialutil.SerialException:
        print('Port busy!')
    except IndexError:
        return
    except serial.serialutil.PortNotOpenError:
        return


def create_tcp_client(host: str, port: int) -> socket.socket:
    """
    Raw function for connecting to a TCP server (in this case the one hosted on the ESP8266 board).
    """

    # Create a TCP client and connect to the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    return client


def play_alert() -> None:
    """
    Plays the alert sound if a fire is detected.
    """

    # Load the sound file and play
    play_obj = sa.WaveObject.from_wave_file('assets/chipi.wav')
    play_obj.play()


def send_smtp_mail(reading: str) -> None:
    """
    Sends an email to the user if a fire is detected.
    """

    # Define the SMTP port and context
    context = ssl.create_default_context()

    # Establish an SSL-based connection with the SMTP server
    with smtplib.SMTP_SSL('smtp.gmail.com', port=465, context=context) as server:
        sender_emails = [MAIN_EMAIL]
        sender_messages = []

        # Form a message object for each mailing address
        for mail in sender_emails:
            message = email.message.Message()
            message['Subject'] = 'Fire detected!'
            message['From'] = MAIN_EMAIL
            message['To'] = mail
            message.add_header('Content-Type', 'text/html')
            message.set_payload(
                f"""\
                <html>
                <head></head>
                <body>
                    <h1>Fire detected!</h1>

                    <h3>There is a fire in your house. Please take necessary precautions.</h3>
                    <p>Detected on: {datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
                    <br>Raw Reading >> {reading}
                    </p>
                </body>
                </html>
            """
            )
            sender_messages.append(message)

        # Log into the server and send the mails
        server.login(MAIN_EMAIL, MAIN_EMAIL_PASSWORD)

        for message in sender_messages:
            register(f"Sending mail to: {message['To']}")
            server.sendmail(
                MAIN_EMAIL,
                message['To'],
                message.as_string().encode('utf-8'),
            )


def main() -> None:
    """
    Main function for running the entire fire detection system.
    """

    # Clear terminal window
    system('clear')

    # Define a variable to store the Arduino object
    if not SKIP_SERIAL_CONN:
        arduino = get_arduino_serial()
        print('Connected via serial port.')
    else:
        client = create_tcp_client('192.168.6.100', 333)
        print('Connected via TCP.')

    # Start the main loop
    while True:
        signal = (client.recv(1024) if SKIP_SERIAL_CONN else arduino.readline()).decode().strip()

        if signal:
            register(signal)

        if 'detected' in signal:
            if not SKIP_ALARM:
                x = Thread(target=play_alert)
                x.start()
                x.join()

            if not SKIP_EMAIL:
                y = Thread(target=send_smtp_mail, args=(signal,))
                y.start()
                y.join()


# Run the main function
if __name__ == '__main__':
    main()
