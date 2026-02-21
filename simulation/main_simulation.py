import ctypes
import os
import numpy as np
import matplotlib.pyplot as plt

# ===============================
# Load C SOC Firmware Module
# ===============================

base_dir = os.path.dirname(os.path.dirname(__file__))
dll_path = os.path.join(base_dir, "build", "soc.dll")
soc_lib = ctypes.CDLL(dll_path)
soc_lib.soc_update.restype = ctypes.c_float
soc_lib = ctypes.CDLL(dll_path)
soc_lib.soc_update.restype = ctypes.c_float

# ===============================
# BMS State Definitions
# ===============================

STATE_INIT = 0
STATE_PRECHARGE = 1
STATE_RUN = 2
STATE_FAULT = 3
STATE_SHUTDOWN = 4

# ===============================
# Simulation Parameters
# ===============================

NUM_CELLS = 4
dt = 1.0
capacities = np.array([2.5, 2.45, 2.55, 2.48]) * 3600  # Coulombs

true_soc = np.ones(NUM_CELLS)
estimated_soc = np.ones(NUM_CELLS)

time_log = []
voltage_log = []
soc_error_list = []

# ===============================
# Helper Functions
# ===============================

def soc_to_voltage(soc):
    return 3.0 + 1.2 * soc  # simple OCV model


# ===============================
# BMS Simulation Loop
# ===============================

bms_state = STATE_INIT
precharge_counter = 0

for t in range(2000):

    if bms_state == STATE_INIT:
        print("BMS INIT")
        bms_state = STATE_PRECHARGE

    elif bms_state == STATE_PRECHARGE:
        precharge_counter += 1
        if precharge_counter > 5:
            print("PRECHARGE COMPLETE")
            bms_state = STATE_RUN

    elif bms_state == STATE_RUN:

        # Simulate current with offset + noise
        current = 1.0 + 0.05 + np.random.normal(0, 0.02)

        cell_voltages = []

        for i in range(NUM_CELLS):

            # True SOC update
            true_soc[i] -= (current * dt) / capacities[i]
            true_soc[i] = max(0.0, true_soc[i])

            # Estimated SOC from C firmware
            estimated_soc[i] = soc_lib.soc_update(
                ctypes.c_float(estimated_soc[i]),
                ctypes.c_float(current),
                ctypes.c_float(dt),
                ctypes.c_float(capacities[i])
            )

            voltage = soc_to_voltage(true_soc[i])

            # Passive balancing if SOC > 80%
            if estimated_soc[i] > 0.8:
                voltage -= 0.01

            cell_voltages.append(voltage)

            # Protection logic
            if voltage > 4.2 or voltage < 3.0:
                print("FAULT DETECTED at time:", t)
                bms_state = STATE_FAULT

        # Log data
        time_log.append(t)
        voltage_log.append(cell_voltages)
        soc_error_list.append(np.mean(true_soc - estimated_soc))

    elif bms_state == STATE_FAULT:
        print("CONTACTOR OPEN - PACK ISOLATED")
        bms_state = STATE_SHUTDOWN

    elif bms_state == STATE_SHUTDOWN:
        break


# ===============================
# Post-Simulation Analysis
# ===============================

voltage_log = np.array(voltage_log)

true_pack_soc = np.mean(true_soc)
estimated_pack_soc = np.mean(estimated_soc)
soc_error = true_pack_soc - estimated_pack_soc

rmse = np.sqrt(np.mean(np.square(soc_error_list)))

final_voltages = voltage_log[-1]
weakest_cell = np.argmin(final_voltages)

print("\n===== FINAL RESULTS =====")
print("Final Pack SOC (True):", true_pack_soc)
print("Final Pack SOC (Estimated):", estimated_pack_soc)
print("Final SOC Error:", soc_error)
print("SOC RMSE:", rmse)
print("Weakest Cell Index:", weakest_cell + 1)

# ===============================
# Plot Voltages
# ===============================

for i in range(NUM_CELLS):
    plt.plot(time_log, voltage_log[:, i], label=f"Cell {i+1}")

plt.axhline(4.2, linestyle="--", color="red")
plt.axhline(3.0, linestyle="--", color="black")

plt.title("4-Cell Pack Voltage Simulation with BMS State Machine")
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.legend()
plt.grid()
plt.show()