import os
import sys
import time
from contextlib import contextmanager

class HIDOutputDst:
    """Encapsulates the context and writing logic for low-level HID targets."""
    def __init__(self, device_path="/dev/hidg0"):
        self.device_path = device_path
        self._handle = None
        self._null_report_bytes = b'\x00' * 8

    def get_destination_ctx(self):
        return self._hid_report_destination()
        
    @contextmanager
    def _hid_report_destination(self):
        """
        Context manager that provisionally assigns or opens the output target.
        Protects standard system descriptors from accidental lifecycle closure.
        """
        if self.device_path == "-":
            # Direct pass-through to stdout binary interface for workstation testing
            self._handle = sys.stdout.buffer
            try:
                yield self
            finally:
                # CRITICAL: Do NOT close sys.stdout globally
                self._handle.flush()
        else:
            # Physical deployment mode on the Raspberry Pi Gadget architecture
            try:
                self._handle = open(self.device_path, "wb+")
                yield self
            finally:
                if self._handle:
                    self._handle.close()

    def send_report(self, report_bytes, delay=0.01):
        """
        Utility abstraction combining raw writes with the mandatory 
        10ms USB heartbeat delay to prevent host buffer jamming.
        """
        try:
            self._handle.write(report_bytes)
            self._handle.flush()
            # The critical heartbeat delay ensuring host OS registration safety
            time.sleep(delay)
        except Exception as e:
            print(f"Write Failure: {e}", file=sys.stderr)
            
    def send_null_report(self):
        self.send_report(self._null_report_bytes)
