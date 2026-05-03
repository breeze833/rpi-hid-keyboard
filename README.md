# rpi-hid-keyboard: Generic USB HID Keyboard Bridge

This project transforms a Raspberry Pi (such as a Pi 4 or Pi Zero 2 W) 
into a programmable **"Hardware Hand"**.
By presenting as a standard USB HID Keyboard, 
it allows any application or agent to "type" on a host computer (Windows, Linux, or macOS) 
with physical-level authority.

The daemon acts as a decoupling layer, 
listening on a Unix domain socket for text strings and converting them 
into precise 8-byte HID reports for the Linux USB gadget driver (`/dev/hidg0`).

## Key Features

* **Universal Compatibility**: Bypasses OS-level software hurdles; works on any system that accepts a standard USB keyboard, including BIOS screens or locked-down corporate environments.
* **Multi-Platform Unicode Support**: Automatically handles complex injection sequences for different operating systems:
    * **Windows**: Alt + '+' + Hex sequences. (Require registry modification)
    * **Linux (Gnome/Wayland)**: Ctrl+Shift+U hex sequences.
    * **macOS**: Option + 4-digit Hex sequences.
* **High-Efficiency Daemon**: Uses a Unix domain socket for near-zero IPC overhead and centralized keyboard state management.
* **Deterministic Reliability**: Implements mandatory 10ms delays between character reports to ensure host input buffers are never overwhelmed.

## Prerequisites

* **Hardware**: Raspberry Pi 4 (2GB) or Pi Zero 2 W.
* **Base OS**: `dietpi_headless` configured for gadget mode.
* **System Package**: `dbus` and `dbus-user-session` are installed.
* **Python**: `python3-pip` and `python3-venv` are installed.

## Installation

### 1. Enable HID Keyboard Support
Enable the hardware-level HID function provided by the [dietpi_headless](https://github.com/breeze833/dietpi_headless) base:

1.  Edit `/usr/local/bin/usb-gadget.sh`.
2.  Locate `ENABLE_HID_KBD` and change its value from `0` to `1`.
3.  Restart the gadget service or reboot the Pi to initialize the `/dev/hidg0` device.

### 2. Install the Package (PEP 668 Compliant)
Since modern Debian/DietPi environments are "externally managed," we use a Virtual Environment to keep the system clean.

```bash
# Create a virtual environment in the project folder
python3 -m venv venv

# Install the package in editable mode within the venv
./venv/bin/pip install -e .
```

### 3. Enable the Systemd Service
Depending on the system defaults, you may need to manually enable the login service:
```bash
sudo systemctl unmask systemd-logind
sudo systemctl restart systemd-logind
sudo loginctl enable-linger dietpi
```
Ensure the `ExecStart` path points to the `hid-keyboard-daemon`.
To run the daemon as a persistent user-level service:
```bash
mkdir -p ~/.config/systemd/user/
cp systemd/hid-keyboard.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now hid-keyboard.service
```

## Usage

Interact with the daemon via the Unix socket using `nc` or any application capable of writing to a socket:

* **Set Target OS Mode**:
    ```bash
    echo "CMD:MODE:WINDOWS" | nc -U /tmp/hid_keyboard.sock
	```
* **Send Text to Type**:
    ```bash
    echo "TEXT:Hello, world!" | nc -U /tmp/hid_keyboard.sock
    ```
## Project Structure

This repository is organized for modularity and professional scalability:

* **`src/rpi_hid/layout.py`**: Encapsulated `USBKeyboardLayout` object for ASCII and Numpad mappings.
* **`src/rpi_hid/daemon.py`**: The core `HIDDaemon` logic managing timing and OS-specific injection.
* **`src/rpi_hid/cli.py`**: A thin wrapper providing the `hid-keyboard-daemon` entry point.

## Host Configuration and Status

I develop this project mainly for my own environments.
Here are my tested configurations.

### Windows (`CMD:MODE:WINDOWS`)

The tested environment is Windows 11. The most stable unicode injection in Windows is to activate the `EnableHexNumpad`.
Using the following PowerShell command to activate it:
```
Set-ItemProperty -Path "HKCU:\Control Panel\Input Method" -Name "EnableHexNumpad" -Value "1" -Type String
```

The injection is good but still under testing.

### Linux (`CMD:MODE:LINUX`)

I have Debian Trixie Wayland Gnome as my working desktop.
So far it works.

### MacOS (`CMD:MODE:MACOS`)

I don't have a Mac. The code is based on some related discussions.
No guarantee for this part.
