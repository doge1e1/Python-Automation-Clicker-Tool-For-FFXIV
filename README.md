Python Automation Clicker Tool

A small Python automation project for handling repetitive desktop mouse operations.

Features
Record mouse coordinates
Save coordinates to JSON
Run automated clicking workflows
Support simple fixed-point clicking
Support grid-based clicking
GUI version with configurable run count and delay
Manual stop mechanism for safer execution
Tech Stack
Python
PyAutoGUI
Tkinter
JSON
threading
Project Structure
main.py - main GUI automation tool
coord_recorder.py - record key mouse positions
multi_coord_recorder.py - record multiple positions
simple_clicker.py - basic fixed-point auto clicker
grid_clicker.py - grid-based click automation
How to Run

Install dependencies:

pip install -r requirements.txt

Run the GUI tool:

python main.py
What I Learned
Building desktop automation tools with Python
Using Tkinter to create simple GUI applications
Managing automation tasks with threading
Saving and loading configuration through JSON
Improving usability with stop controls and parameter settings
Disclaimer

This project is for learning and automation practice.

![UI Demo](assets/ui.png)
