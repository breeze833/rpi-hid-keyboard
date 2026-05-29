import os
from rpi_hid import HIDDaemon, HIDInputSrc, HIDOutputDst, Str2HIDTransformer

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
    
