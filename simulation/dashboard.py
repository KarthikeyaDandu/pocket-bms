import ctypes
import os
import numpy as np
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation

# ===============================
# Load C SOC Firmware Module
# ===============================

dll_path = os.path.join("build", "soc.dll")
soc_lib = ctypes.CDLL(dll_path)
soc_lib.soc_update.restype = ctypes.c_float

# ===============================
# Simulation Parameters
# ===============================

NUM_CELLS = 4
dt = 1.0
capacities = np.array([2.5, 2.45, 2.55, 2.48]) * 3600

true_soc = np.ones(NUM_CELLS)
estimated_soc = np.ones(NUM_CELLS)

bms_state = "INIT"

def soc_to_voltage(soc):
    return 3.0 + 1.2 * soc


# ===============================
# GUI Setup
# ===============================

root = tk.Tk()
root.title("Pocket BMS - Real-Time Dashboard")
root.geometry("1000x700")

# SOC Label
soc_label = tk.Label(root, text="Pack SOC: 100%", font=("Arial", 18))
soc_label.pack(pady=10)

# State Label
state_label = tk.Label(root, text="State: INIT", font=("Arial", 16))
state_label.pack()

# Fault Indicator
fault_label = tk.Label(root, text="Status: OK", font=("Arial", 16), fg="green")
fault_label.pack(pady=10)

# Voltage Bars
bar_frame = tk.Frame(root)
bar_frame.pack(pady=10)

bars = []
for i in range(NUM_CELLS):
    bar = ttk.Progressbar(bar_frame, orient="vertical", length=200, mode="determinate", maximum=4.2)
    bar.grid(row=0, column=i, padx=20)
    bars.append(bar)

# Matplotlib Figure
fig, ax = plt.subplots(figsize=(6,4))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

time_log = []
soc_log = []

t = 0

# ===============================
# Update Function
# ===============================

def update(frame):
    global true_soc, estimated_soc, bms_state, t

    if bms_state == "INIT":
        bms_state = "RUN"

    if bms_state == "RUN":

        current = 1.0 + 0.05 + np.random.normal(0, 0.02)

        voltages = []

        for i in range(NUM_CELLS):

            true_soc[i] -= (current * dt) / capacities[i]
            true_soc[i] = max(0.0, true_soc[i])

            estimated_soc[i] = soc_lib.soc_update(
                ctypes.c_float(estimated_soc[i]),
                ctypes.c_float(current),
                ctypes.c_float(dt),
                ctypes.c_float(capacities[i])
            )

            voltage = soc_to_voltage(true_soc[i])

            if estimated_soc[i] > 0.8:
                voltage -= 0.01

            voltages.append(voltage)

            if voltage < 3.0 or voltage > 4.2:
                bms_state = "FAULT"

        pack_soc = np.mean(estimated_soc)

        soc_label.config(text=f"Pack SOC: {pack_soc*100:.2f}%")
        state_label.config(text=f"State: {bms_state}")

        if bms_state == "FAULT":
            fault_label.config(text="Status: FAULT", fg="red")
        else:
            fault_label.config(text="Status: OK", fg="green")

        for i in range(NUM_CELLS):
            bars[i]["value"] = voltages[i]

        time_log.append(t)
        soc_log.append(pack_soc)

        ax.clear()
        ax.plot(time_log, soc_log)
        ax.set_title("Pack SOC Over Time")
        ax.set_xlabel("Time")
        ax.set_ylabel("SOC")

        t += 1

ani = FuncAnimation(fig, update, interval=200, cache_frame_data=False)
root.mainloop()