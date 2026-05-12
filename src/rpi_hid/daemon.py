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

    def _write_null_report(self):
        self._write_report(self.layout.get_null_report())
        
    def _write_report(self, report_bytes, delay=0.01):
        """Writes the 8-byte report and handles the critical 10ms delay."""
        try:
            self.hid_handle.write(report_bytes)
            self.hid_handle.flush()
            # delay to prevent overwhelming host buffer
            time.sleep(delay)
        except Exception as e:
            print(f"HID Write Error: {e}")

    def inject_unicode(self, codepoint):
        """Implements injection sequences for different OS flavors."""
        
        if self.os_mode == "windows":
            # Strategy: Universal Hex Numpad (Requires EnableHexNumpad Registry Key)
            # This bypasses Codepage 950 / Big5 issues by using raw Unicode.
            
            # Trick: All the key presses/releases should keep Alt down
            
            # 1. Trigger: Press Alt + Numpad '+' (Scan code 0x57)
            self._write_report(self.layout._build_report(self.layout.MOD_ALT, self.layout.NUMPAD_MAP['+']))
            self._write_report(self.layout._build_report(self.layout.MOD_ALT, 0x00))
            
            # 2. Sequence: Type Hex digits while continuing to hold Alt
            for h in f"{codepoint:04x}":
                # Retrieve the standard scan code for the hex digit (0-9, a-f)
                # and wrap it in a report where MOD_ALT is still active.
                if h.isdigit():
                    code = self.layout.NUMPAD_MAP[h]
                else:
                    _, code = self.layout.ASCII_MAP[h]
                self._write_report(self.layout._build_report(self.layout.MOD_ALT, code))
                self._write_report(self.layout._build_report(self.layout.MOD_ALT, 0x00))
                
            # Release of Alt via the NULL_REPORT 
            self._write_null_report()
                
        elif self.os_mode == "linux":
            # Linux: Ctrl+Shift+U, hex code, then Enter
            # 1. Trigger sequence (Ctrl+Shift+U)
            trigger_mod = self.layout.MOD_CTRL | self.layout.MOD_SHIFT
            _, u_code = self.layout.ASCII_MAP['u']
            self._write_report(self.layout._build_report(trigger_mod, u_code))
            self._write_null_report()
            
            # 2. Send Hex digits (no modifiers)
            for h in f"{codepoint:x}":
                self._write_report(self.layout.get_report(h))
                self._write_null_report()
                
            # 3. Finalize with Enter
            self._write_report(self.layout.get_report('\n'))
            self._write_null_report();
            
        elif self.os_mode == "macos":
            # macOS: Hold Option (Alt) and type 4-digit hex
            # Requires "Unicode Hex Input" to be active on the host
            for h in f"{codepoint:04x}":
                report = self.layout.get_report(h)
                # Apply Option (MOD_ALT) to the hex digit report
                mod, code = self.layout.ASCII_MAP[h]
                self._write_report(self.layout._build_report(self.layout.MOD_ALT, code))
                self._write_report(self.layout._build_report(self.layout.MOD_ALT, 0x00))
            # release Alt key after the input sequence
            self._write_null_report()

    def type_string(self, text):
        """Iterates through text and chooses the correct input path."""
        for char in text:
            cp = ord(char)
            # Path 1: Standard ASCII
            if cp < 128 and char in self.layout.ASCII_MAP:
                report = self.layout.get_report(char)
                self._write_report(report)
                self._write_null_report()
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
        os.chmod(self.socket_path, 0o666) # Allow access from user-land services
        server.listen(1)
        
        print(f"HID Daemon started. Mode: {self.os_mode}")

        while True:
            conn, _ = server.accept()
            buffer = ""
            try:
                while True:
                    chunk = conn.recv(1024).decode('utf-8')
                    if not chunk:
                        break
                    
                    buffer += chunk
                    
                    while "\n" in buffer:
                        line, buffer = buffer.split("\n", 1)
                        # We don't strip() here because we want to preserve 
                        # leading/trailing spaces for a "Generic" bridge.
                        
                        if not line and not buffer: # Handle empty lines
                            self.type_string("\n")
                            continue
                        
                        # Route: Explicit Commands
                        if line.startswith("CMD:MODE:"):
                            new_mode = line.split(':')[-1].lower()
                            if new_mode in ['windows', 'linux', 'macos']:
                                self.os_mode = new_mode
                                print(f"Switched mode to: {self.os_mode}")
                        
                        # Route: Implicit Text (the string PLUS the newline)
                        else:
                            self.type_string(line+"\n")

            except Exception as e:
                print(f"Communication error: {e}")
            finally:
                conn.close()

if __name__ == "__main__":
    daemon = HIDDaemon()
    daemon.run()
