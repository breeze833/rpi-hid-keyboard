import os
import signal
from rpi_hid import HIDDaemon, HIDInputSrc, HIDOutputDst, Str2HIDTransformer

def service_shutdown_handler(signum, frame):
    # Raising KeyboardInterrupt forces Python to bubble up cleanly 
    # through all try/finally blocks and Context Managers.
    raise KeyboardInterrupt

# Register the hooks at the very entry point of your main script
signal.signal(signal.SIGTERM, service_shutdown_handler)
signal.signal(signal.SIGINT, service_shutdown_handler) # Handles Ctrl+C too

def main():
    socket_path = os.getenv('HID_SOCKET_PATH', '/tmp/hid_keyboard.sock')
    device_path = os.getenv('HID_DEVICE_PATH', '/dev/hidg0')
    
    input_ctx = HIDInputSrc(socket_path=socket_path).get_source_ctx()
    output_ctx = HIDOutputDst(device_path=device_path).get_destination_ctx()
    transformer = Str2HIDTransformer()
    
    daemon = HIDDaemon(input_ctx, transformer, output_ctx)
    daemon.run()

if __name__ == "__main__":
    main()
    
