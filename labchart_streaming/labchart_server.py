"""
LabChart Network Server

Reads live data from a LabChart channel via COM interface and broadcasts 
it over the network for PsychoPy clients to access.

Requirements:
    - Windows OS with LabChart installed
    - pywin32 package (install via: pip install pywin32)
    - LabChart must be running with an active recording

Usage:
    1. Start LabChart and begin recording
    2. Configure SERVER_IP and CHANNEL_INDEX below
    3. Run this script: python labchart_server.py
    4. Keep it running while your PsychoPy experiment is active

Press Ctrl+C to stop the server.
"""

import win32com.client
import pythoncom
import socket
import time
import threading

# ============ CONFIGURATION ============
# Network settings - configure for your setup
SERVER_PORT = 5000
SERVER_IP = "0.0.0.0"  # Listen on all network interfaces (use specific IP if needed)

# LabChart channel to stream (1-based indexing)
CHANNEL_INDEX = 1

# Internal state
_current_value = 0.0
_last_sample_index = 0
_current_block = 0
_last_status_log = 0.0
_last_data_log = 0.0

# ============ LABCHART COM INTERFACE ============

def connect_to_labchart():
    """Connect to LabChart via COM interface.
    
    Returns:
        LabChart document object if successful, None otherwise.
    """
    try:
        print("[INFO] Connecting to LabChart...")
        app = win32com.client.Dispatch("ADIChart.Application")
        doc = app.ActiveDocument
        
        if not doc:
            print("[ERROR] No active document in LabChart!")
            print("[ERROR] Please open a document and start recording")
            return None
        
        print(f"[SUCCESS] Connected to document: {doc.Name}")
        print(f"[INFO] Channels available: {doc.NumberOfChannels}")
        
        for i in range(1, doc.NumberOfChannels + 1):
            print(f"         Channel {i}: {doc.GetChannelName(i)}")
        
        return doc
        
    except Exception as e:
        print(f"[ERROR] Failed to connect to LabChart: {e}")
        print("[TROUBLESHOOTING]")
        print("  1. Is LabChart running?")
        print("  2. Is a document open?")
        print("  3. Have you started recording?")
        return None


def get_latest_value(doc):
    """Fetch the most recent value from the configured LabChart channel.
    
    Args:
        doc: LabChart document object
        
    Returns:
        tuple: (value, status) where status is 'ok', 'not_recording', 'no_data', or 'error: ...'
    """
    global _last_sample_index, _current_block, _current_value
    
    try:
        if not doc.IsSampling:
            return None, "not_recording"
        
        block = doc.SamplingRecord
        if block == -1:
            return None, "not_recording"
        
        # Reset tracking if we switched to a new recording block
        if block != _current_block:
            _current_block = block
            _last_sample_index = 0
        
        total_samples = doc.GetRecordLength(block)
        if total_samples < 1:
            return None, "no_data"
        
        # Average last 5 samples for stability
        start_idx = max(1, total_samples - 5)
        data = doc.GetChannelData(
            1,  # AS_DOUBLE flag (floating point)
            CHANNEL_INDEX,
            block + 1,
            start_idx,
            -1  # Get all remaining samples
        )
        
        if data and len(data) > 0:
            _current_value = sum(data) / len(data)
            _last_sample_index = total_samples
            return _current_value, "ok"
        else:
            return None, "no_data"
            
    except Exception as e:
        return None, f"error: {str(e)}"


# ============ NETWORK SERVER ============

def handle_client(client_socket, client_address):
    """Handle connection from a client (e.g., PsychoPy).
    
    Args:
        client_socket: Connected socket object
        client_address: Client's address tuple
    """
    print(f"[CONNECT] Client connected: {client_address}")
    
    try:
        while True:
            message = f"{_current_value:.2f}\n"
            client_socket.sendall(message.encode())
            time.sleep(0.05)  # ~20 Hz update rate
            
    except (ConnectionResetError, BrokenPipeError, OSError):
        print(f"[DISCONNECT] Client disconnected: {client_address}")
    finally:
        client_socket.close()


def data_reader_thread(doc):
    """Background thread that continuously reads from LabChart.
    
    Args:
        doc: LabChart document object to read from
    """
    global _last_status_log, _last_data_log
    
    print("[THREAD] Data reader started")
    pythoncom.CoInitialize()  # Required for COM in separate thread
    
    while True:
        try:
            value, status = get_latest_value(doc)
            now = time.time()

            if status != "ok":
                if now - _last_status_log >= 1.0:
                    print(f"[WARNING] Status: {status}")
                    _last_status_log = now
            else:
                if now - _last_data_log >= 1.0:
                    print(f"[DATA] Current value: {_current_value:.2f}")
                    _last_data_log = now
                
            time.sleep(0.01)  # Poll at ~100 Hz
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[ERROR] Data reader error: {e}")
            time.sleep(0.1)


def run_server():
    """Run the network server that accepts client connections."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((SERVER_IP, SERVER_PORT))
        server.listen(5)
        
        print(f"[SERVER] Listening on {SERVER_IP}:{SERVER_PORT}")
        print(f"[INFO] Waiting for client connections...")
        
        while True:
            try:
                client_socket, client_address = server.accept()
                client_thread = threading.Thread(
                    target=handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                client_thread.start()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[ERROR] Server error: {e}")
                
    finally:
        server.close()
        print("[SERVER] Server closed")


# ============ MAIN ============

def main():
    """Main entry point."""
    print("=" * 60)
    print("LabChart Network Streaming Server")
    print("=" * 60)
    print()
    
    doc = connect_to_labchart()
    if doc is None:
        print("\n[FATAL] Could not connect to LabChart. Exiting.")
        return
    
    print()
    print(f"[CONFIG] Server listening on: {SERVER_IP}:{SERVER_PORT}")
    print(f"[CONFIG] Streaming channel: {CHANNEL_INDEX}")
    print()
    
    # Start background thread to continuously read from LabChart
    reader = threading.Thread(target=data_reader_thread, args=(doc,), daemon=True)
    reader.start()
    
    # Run server (blocks until Ctrl+C)
    run_server()
    
    print("\n[INFO] Server stopped.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
