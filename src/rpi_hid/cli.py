from rpi_hid.daemon import HIDDaemon

def main():
    # You can later add argparse here to customize socket paths or devices
    daemon = HIDDaemon(socket_path="/tmp/hid_keyboard.sock", device="/dev/hidg0")
    daemon.run()

if __name__ == "__main__":
    main()
    
