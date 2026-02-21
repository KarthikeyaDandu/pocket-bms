# Pocket BMS – Embedded + Simulation Architecture

A hybrid Battery Management System architecture combining:

• C-based SOC firmware logic  
• Python simulation layer  
• Real-time GUI dashboard  
• Firmware–Software integration via ctypes  

## Architecture

Firmware (C)
    ↓
Compiled to DLL
    ↓
Python Simulation Layer
    ↓
Real-time Dashboard

## Features

- Coulomb counting SOC update (C)
- Multi-cell pack simulation
- Pack voltage tracking
- Fault state handling
- Real-time SOC plotting
- Live dashboard with cell monitoring

## Tech Stack

- C (Embedded-style firmware logic)
- Python
- NumPy
- Matplotlib
- ctypes interface

## How to Run

1. Compile firmware:
   gcc -shared -o soc.dll -fPIC firmware/soc.c

2. Run simulation:
   python simulation/main_simulation.py

3. Launch dashboard:
   python simulation/dashboard.py

## Why This Project Matters

This project demonstrates:
- Embedded firmware + high-level simulation integration
- Cross-language interface design
- Real-time system visualization
- EV battery system architecture fundamentals