"""
PsychoPy Code Component Example

This file contains code snippets to receive live LabChart data in PsychoPy.
Copy and paste these into your PsychoPy Builder Code Component at the 
appropriate tabs (Begin Experiment, Each Frame, End Experiment).

⚠️ NOTE: This is NOT a standalone Python script. These are snippets meant to be
copied into PsychoPy Builder's Code Component. Variables like 'text_display' 
will be defined by your PsychoPy components.

Setup in PsychoPy Builder:
1. Add a Text component (e.g., named 'text_display')
2. Add a Code component to the same routine
3. Copy the code from each section below into the corresponding tabs

Configuration:
- Update LABCHART_SERVER_IP with the IP address of the LabChart computer
- Update the text component name if you named it differently
"""

# ============================================================================
# BEGIN EXPERIMENT TAB
# ============================================================================
# Run ONCE when the experiment starts - establishes connection to LabChart server

import socket
import time

# CONFIGURATION: Update this with your LabChart computer's IP address
# Examples:
#   - Same computer: "127.0.0.1" or "localhost"
#   - Direct ethernet: "169.254.x.x" (check network settings)
#   - Local network: "192.168.x.x" (check network settings)
LABCHART_SERVER_IP = "127.0.0.1"  # Change this!
LABCHART_SERVER_PORT = 5000

print(f"[PsychoPy] Connecting to LabChart server at {LABCHART_SERVER_IP}:{LABCHART_SERVER_PORT}")

labchart_socket = None
connection_attempts = 0
max_attempts = 5

# Attempt connection with retries
while connection_attempts < max_attempts:
    try:
        labchart_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        labchart_socket.connect((LABCHART_SERVER_IP, LABCHART_SERVER_PORT))
        labchart_socket.settimeout(2.0)
        print("[PsychoPy] ✓ Connected to LabChart server")
        break
    except Exception as e:
        connection_attempts += 1
        print(f"[PsychoPy] Connection attempt {connection_attempts}/{max_attempts} failed: {e}")
        if connection_attempts < max_attempts:
            time.sleep(1)
        else:
            print("[PsychoPy] ✗ Could not connect to LabChart server")
            labchart_socket = None

current_value = 0.0
connection_ready = (labchart_socket is not None)


# ============================================================================
# EACH FRAME TAB
# ============================================================================
# Run EVERY FRAME (~60 Hz) - reads and displays the latest data value
# Note: Replace 'text_display' with the name of your Text component

if connection_ready and labchart_socket:
    try:
        data = labchart_socket.recv(1024).decode().strip()
        
        if data:
            current_value = float(data)
            # Update your text component (modify format as needed)
            text_display.text = f"{current_value:.1f}"
            
    except socket.timeout:
        text_display.text = "Waiting..."
    except ValueError:
        text_display.text = "Invalid data"
    except Exception as e:
        text_display.text = f"Error: {str(e)[:20]}"
else:
    text_display.text = "Not connected"


# ============================================================================
# END ROUTINE TAB (Optional)
# ============================================================================
# Run ONCE when a routine/trial ends
# Useful for logging or saving the final value from this trial

print(f"[PsychoPy] Trial ended. Final value: {current_value:.2f}")
# You can also save current_value to your data file here using thisExp.addData()


# ============================================================================
# END EXPERIMENT TAB
# ============================================================================
# Run ONCE when the experiment ends - closes the network connection

print("[PsychoPy] Closing connection to LabChart server...")

if labchart_socket:
    try:
        labchart_socket.close()
        print("[PsychoPy] Connection closed")
    except:
        pass
