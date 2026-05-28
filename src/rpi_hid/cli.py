from rpi_hid.daemon import HIDDaemon

def main():
    # You can later add argparse here to customize socket paths or devices
    daemon = HIDDaemon()
    daemon.run()

if __name__ == "__main__":
    main()
    
