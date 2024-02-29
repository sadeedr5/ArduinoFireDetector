## 🤖 Fire Detector (Arduino)

### Overview

This simple yet effective project is a fire detector that uses an Arduino Uno and a simple flame sensor module to detect sudden changes in the thermal environment around it and alert the user via playing an alarm sound and also sending the raw readings to the serial monitor, which also gets used by the backend to send emails to all of the addresses assigned.

### Reason Behind Creation

This project was primarily made for one of the science fests that are arranged in our college every year. It was also a learning attempt for me to try and get used to building various combinations of circuits using Arduino and tinker around with various different sensors and modules.

---

### Used Technologies

- C++ (Arduino, for the main code and TCP server)
- Python (for the mailing and TCP client)
- Hardware:
    - Arduino Uno
    - Flame Sensor Module
    - ESP8266 ESP-01 Module
    - Jumper Wires
    - Breadboard