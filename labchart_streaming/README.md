# LabChart to PsychoPy Live Streaming

This folder contains a minimal working example for streaming live data from LabChart to PsychoPy over a network connection.

## Overview

The system consists of two parts:
1. **LabChart Server** (`labchart_server.py`) - Runs on the computer with LabChart, reads data via COM interface, and broadcasts it over the network
2. **PsychoPy Client** (`psychopy_receiver.py`) - Code snippets to add to your PsychoPy experiment to receive the data

## Requirements

### LabChart Computer (Server)
- **Operating System**: Windows (required for LabChart COM interface)
- **Software**: 
  - LabChart installed and running
  - Python 3.7+
  - `pywin32` package: `pip install pywin32`
- **Network**: Network connection to PsychoPy computer

### PsychoPy Computer (Client)
- **Software**: PsychoPy (any recent version)
- **Network**: Network connection to LabChart computer
- No additional Python packages required (uses built-in `socket` module)

## Setup Instructions

### 1. Configure Network Connection

You need network connectivity between the two computers. Choose one option:

#### Option A: Same Computer (Easiest for Testing)
- Run both LabChart and PsychoPy on the same computer
- Use IP address: `127.0.0.1` or `localhost`

#### Option B: Direct Ethernet Connection
1. Connect both computers with an ethernet cable
2. Configure static IP addresses on both computers:
   - LabChart computer: e.g., `169.254.1.10`
   - PsychoPy computer: e.g., `169.254.1.11`
   - Subnet mask: `255.255.0.0`
3. Use the LabChart computer's IP in PsychoPy code

#### Option C: Local Network (WiFi/LAN)
1. Connect both computers to the same network
2. Find the LabChart computer's IP address:
   - Open Command Prompt and run: `ipconfig`
   - Look for "IPv4 Address" (e.g., `192.168.1.100`)
3. Use this IP address in PsychoPy code

### 2. Configure LabChart Server

Edit `labchart_server.py` and configure these settings:

```python
# Network settings
SERVER_PORT = 5000                  # Port number (keep default unless conflicts)
SERVER_IP = "0.0.0.0"              # Listen on all interfaces (recommended)

# LabChart channel to stream (1-based indexing)
CHANNEL_INDEX = 1                   # Change to your desired channel
```

**Notes:**
- `SERVER_IP = "0.0.0.0"` allows connections from any network interface (recommended)
- To restrict to specific interface, use that interface's IP address
- `CHANNEL_INDEX` uses 1-based numbering (Channel 1 = index 1)

### 3. Configure PsychoPy Client

In `psychopy_receiver.py`, update the IP address to match your LabChart computer:

```python
LABCHART_SERVER_IP = "127.0.0.1"    # Change to your LabChart computer's IP
LABCHART_SERVER_PORT = 5000         # Must match server port
```

## Usage

### Step 1: Start LabChart Recording
1. Open LabChart
2. Open or create a document with your channels configured
3. **Start recording** (the server requires active recording)
4. Leave LabChart running

### Step 2: Start LabChart Server
Choose one method:

**Method A: Double-click the batch file** (Windows only)
- Double-click `labchart_starter.bat`

**Method B: Command line**
```bash
cd labchart_streaming
python labchart_server.py
```

You should see:
```
============================================================
LabChart Network Streaming Server
============================================================

[INFO] Connecting to LabChart...
[SUCCESS] Connected to document: YourDocument.adicht
[INFO] Channels available: 4
         Channel 1: Force
         Channel 2: EMG
         Channel 3: Temperature
         Channel 4: ECG

[CONFIG] Server listening on: 0.0.0.0:5000
[CONFIG] Streaming channel: 1

[SERVER] Listening on 0.0.0.0:5000
[INFO] Waiting for client connections...
[THREAD] Data reader started
[DATA] Current value: 123.45
```

### Step 3: Set Up PsychoPy Experiment
1. Open your PsychoPy experiment in Builder view
2. Create a **Text component** (e.g., name it `text_display`)
3. Add a **Code component** to the same routine
4. Copy code from `psychopy_receiver.py` into the appropriate tabs:
   - Copy "BEGIN EXPERIMENT" section → Code component's "Begin Experiment" tab
   - Copy "EACH FRAME" section → Code component's "Each Frame" tab
   - Copy "END EXPERIMENT" section → Code component's "End Experiment" tab
5. Update the IP address in "BEGIN EXPERIMENT" section
6. Make sure variable names match (e.g., `text_display`)

### Step 4: Run PsychoPy Experiment
1. Run your PsychoPy experiment
2. You should see connection messages in the Runner output
3. The text component should display the live data from LabChart
4. The LabChart server will show `[CONNECT] Client connected: ...`

### Step 5: Stop When Finished
- PsychoPy will disconnect automatically when experiment ends
- Stop LabChart server with **Ctrl+C**
- Stop LabChart recording

## Troubleshooting

### "Could not connect to LabChart server"
- Verify LabChart server is running
- Check IP address is correct in PsychoPy code
- Test network connectivity: `ping <labchart-ip>` from PsychoPy computer
- Check firewall settings allow connections on port 5000
- Verify both computers are on same network (or properly configured for direct connection)

### "No active document in LabChart"
- Make sure LabChart has a document open
- Start recording in LabChart
- Restart the server script

### "Status: not_recording"
- Start or resume recording in LabChart
- The server requires active sampling to read data

### "Invalid data" or "Waiting..." in PsychoPy
- Check that LabChart server is sending data (look for `[DATA] Current value: ...` messages)
- Verify CHANNEL_INDEX in server matches an active channel
- Check network connection stability

### Firewall Issues
If connection fails, temporarily disable firewall or add exception:
- Windows Firewall: Allow Python/port 5000
- Third-party firewalls: Add exception for Python or port 5000

## Customization

### Change Data Format
Modify the format string in `labchart_server.py`:
```python
message = f"{_current_value:.2f}\n"  # 2 decimal places
```

Or in PsychoPy `psychopy_receiver.py`:
```python
text_display.text = f"{current_value:.1f}"      # 1 decimal place
text_display.text = f"{current_value:.1f} N"    # Add units
text_display.text = f"Force: {current_value:6.2f}"  # With label
```

### Change Update Rate
In `labchart_server.py`, modify sleep duration:
```python
time.sleep(0.05)  # 20 Hz (50ms between updates)
time.sleep(0.033) # 30 Hz
time.sleep(0.016) # 60 Hz
```

### Stream Multiple Channels
Current example streams one channel. To stream multiple channels:
1. Modify `labchart_server.py` to read multiple channels and format as comma-separated values
2. Modify PsychoPy code to parse the values: `values = data.split(',')`

### Save Data in PsychoPy
Add to the "End Routine" tab in PsychoPy:
```python
thisExp.addData('labchart_value', current_value)
```

## Files

- **`labchart_server.py`** - Server that reads from LabChart and broadcasts data
- **`psychopy_receiver.py`** - Example code snippets for PsychoPy Builder
- **`labchart_starter.bat`** - Optional Windows launcher for the server
- **`README.md`** - This file

## Technical Details

### Communication Protocol
- **Protocol**: TCP socket connection
- **Format**: Plain text, one floating-point value per line
- **Encoding**: UTF-8
- **Rate**: ~20 Hz by default (configurable)

### Data Flow
1. Server polls LabChart COM interface at ~100 Hz
2. Server averages last 5 samples for stability
3. Server broadcasts current value to all connected clients at ~20 Hz
4. PsychoPy reads value each frame (~60 Hz) and displays latest received value

### Threading
- Server uses two threads:
  - Data reader thread: Continuously polls LabChart
  - Main thread: Handles network connections
- Each client connection runs in its own thread

## License

See repository root for license information.

## Support

For issues or questions, please open an issue on the GitHub repository.
