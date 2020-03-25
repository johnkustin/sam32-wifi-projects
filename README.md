# sam32-wifi-projects
https://lab64.stanford.edu/  

CircuitPython projects for the SAM32 board made by Max Holliday and Steve Clark

**Note:** If you haven't updated the ESP32 WiFi chip (you'll know if you have) then load `NINA_W102-1.3.0_sam32.bin` onto a *micro*SD card, insert that into the SAM32, connect to the SAM32, and run `esp32spi_prog.py`.

## Instructions
Copy and paste `lib/` into the root (base) directory of the CIRCUITPY drive. If your SAM32 will be a server, repeat with `static/`.

Depending on what you want your SAM32 to do, paste either `esp32-http-client.py` or `esp32-http-server.py` into the root directory of the CIRCUITPY drive and **rename** the file to `main.py`.

| Directories & Files   | Description |
| --------------------- | ----------- |
| lib                   | CircuitPython library files |
| static                | STATIC webserver files |
| esp32-http-client.py  | Template for client side interaction with SAM32 webserver |
| esp32-http-server.py  | Template for SAM32 webserver |
| esp32spi_prog.py      | Script to load ESP32 firmware from microSD |

## Project Status
- [x] Initialize a SAM32's firmware and CircuitPython libraries in order to run code.
- [x] Connect a *client* SAM32 to a *server* SAM32 using a WiFi access point (AP).
- [x] Access the AP webserver using a computer.
- [x] Verify HTTP requests between client and server work.
- [x] Create a `.json` document in `/static` so a server can broadcast data to its clients.
- [x] Send and receive *wireless* Digital & Analog pin commands (PWM and Digital I/O).
- [x] Test pin commands on LEDs or servo.
- [ ] Scale the test to *>2* clients. 
- [ ] Control latency between client/server requests.
- [ ] Log data onto the webpage.
- [ ] Add ways to actuate and control SAM32 from browser.

Direct Questions, Concerns, Suggestions to:   kustinj AT stanford DOT edu
