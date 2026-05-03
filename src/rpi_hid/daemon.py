import socket
import os
import time
from .layout import USBKeyboardLayout

class HIDDaemon:
    def __init__(self, socket_path="/tmp/hid_keyboard.sock", device="/dev/hidg0"):
        self.socket_path = socket_path
        self.device_path = device
        self.os_mode = "linux"  # Default mode
        self.layout = USBKeyboardLayout()
        self.hid_handle = None

    def _write_report(self, report_bytes):
        """Writes the 8-byte report and handles the critical 10ms delay."""
        try:
            self.hid_handle.write(report_bytes)
            self.hid_handle.flush()
            # 10ms delay to prevent overwhelming host buffer
            time.sleep(0.01)
            
            # Immediately send null report to prevent auto-repeat
            self.hid_handle.write(self.layout.get_null_report())
            self.hid_handle.flush()
            time.sleep(0.01)
        except Exception as e:
            print(f"HID Write Error: {e}")

    def inject_unicode(self, codepoint):
        """Implements injection sequences for different OS flavors."""
        
        if self.os_mode == "windows":
            # Windows: Hold Alt and type decimal digits on Numpad
            decimal_str = str(codepoint)
            for digit in decimal_str:
                # Every digit report must keep Alt (0x04) active [cite: 81, 82]
                report = self.layout.get_numpad_report(digit, self.layout.MOD_ALT)
                self._write_report(report)
                
        elif self.os_mode == "linux":
            # Linux: Ctrl+Shift+U, hex code, then Enter
            # 1. Trigger sequence (Ctrl+Shift+U)
            trigger_mod = self.layout.MOD_CTRL | self.layout.MOD_SHIFT
            _, u_code = self.layout.ASCII_MAP['u']
            self._write_report(self.layout._build_report(trigger_mod, u_code))
            
            # 2. Send Hex digits (no modifiers)
            for h in f"{codepoint:x}":
                self._write_report(self.layout.get_report(h))
                
            # 3. Finalize with Enter
            self._write_report(self.layout.get_report('\n'))
            
        elif self.os_mode == "macos":
            # macOS: Hold Option (Alt) and type 4-digit hex
            # Requires "Unicode Hex Input" to be active on the host
            for h in f"{codepoint:04x}":
                report = self.layout.get_report(h)
                # Apply Option (MOD_ALT) to the hex digit report
                mod, code = self.layout.ASCII_MAP[h]
                self._write_report(self.layout._build_report(self.layout.MOD_ALT, code))

    def type_string(self, text):
        """Iterates through text and chooses the correct input path."""
        for char in text:
            cp = ord(char)
            # Path 1: Standard ASCII
            if cp < 128 and char in self.layout.ASCII_MAP:
                report = self.layout.get_report(char)
                self._write_report(report)
            # Path 2: Strategy B (Multilingual Injection)
            else:
                self.inject_unicode(cp)

    def run(self):
        """Sets up the Unix socket listener and manages permissions."""
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

        # Open the HID device; requires correct permissions (group 'input')
        self.hid_handle = open(self.device_path, "wb+")
        
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(self.socket_path)
        os.chmod(self.socket_path, 0o666) # Allow access from user-land services [cite: 57, 137]
        server.listen(1)
        
        print(f"HID Daemon started. Mode: {self.os_mode}")

        while True:
            conn, _ = server.accept()
            try:
                data = conn.recv(1024).decode('utf-8').strip()
                if data.startswith("CMD:MODE:"):
                    self.os_mode = data.split(":")[-1].lower()
                    print(f"Switched mode to: {self.os_mode}")
                elif data.startswith("TEXT:"):
                    self.type_string(data[5:])
            except Exception as e:
                print(f"Communication error: {e}")
            finally:
                conn.close()

if __name__ == "__main__":
    daemon = HIDDaemon()
    daemon.run()
