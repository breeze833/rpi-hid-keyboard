class USBKeyboardLayout:
    # --- HID Modifier Bits --- 
    MOD_NONE  = 0x00
    MOD_CTRL  = 0x01
    MOD_SHIFT = 0x02
    MOD_ALT   = 0x04  # Option on macOS
    MOD_GUI   = 0x08  # Windows / Command Key

    def __init__(self):
        self._null_report = b'\x00' * 8

        # --- Standard US ASCII to (Modifier, ScanCode) --- 
        self.ASCII_MAP = {
            # Lowercase a-z (0x04 - 0x1d)
            'a': (0, 0x04), 'b': (0, 0x05), 'c': (0, 0x06), 'd': (0, 0x07),
            'e': (0, 0x08), 'f': (0, 0x09), 'g': (0, 0x0a), 'h': (0, 0x0b),
            'i': (0, 0x0c), 'j': (0, 0x0d), 'k': (0, 0x0e), 'l': (0, 0x0f),
            'm': (0, 0x10), 'n': (0, 0x11), 'o': (0, 0x12), 'p': (0, 0x13),
            'q': (0, 0x14), 'r': (0, 0x15), 's': (0, 0x16), 't': (0, 0x17),
            'u': (0, 0x18), 'v': (0, 0x19), 'w': (0, 0x1a), 'x': (0, 0x1b),
            'y': (0, 0x1c), 'z': (0, 0x1d),

            # Uppercase A-Z (Shift + ScanCode) [cite: 131, 133]
            'A': (self.MOD_SHIFT, 0x04), 'B': (self.MOD_SHIFT, 0x05), 
            'C': (self.MOD_SHIFT, 0x06), 'D': (self.MOD_SHIFT, 0x07),
            'E': (self.MOD_SHIFT, 0x08), 'F': (self.MOD_SHIFT, 0x09), 
            'G': (self.MOD_SHIFT, 0x0a), 'H': (self.MOD_SHIFT, 0x0b),
            'I': (self.MOD_SHIFT, 0x0c), 'J': (self.MOD_SHIFT, 0x0d), 
            'K': (self.MOD_SHIFT, 0x0e), 'L': (self.MOD_SHIFT, 0x0f),
            'M': (self.MOD_SHIFT, 0x10), 'N': (self.MOD_SHIFT, 0x11), 
            'O': (self.MOD_SHIFT, 0x12), 'P': (self.MOD_SHIFT, 0x13),
            'Q': (self.MOD_SHIFT, 0x14), 'R': (self.MOD_SHIFT, 0x15), 
            'S': (self.MOD_SHIFT, 0x16), 'T': (self.MOD_SHIFT, 0x17),
            'U': (self.MOD_SHIFT, 0x18), 'V': (self.MOD_SHIFT, 0x19), 
            'W': (self.MOD_SHIFT, 0x1a), 'X': (self.MOD_SHIFT, 0x1b),
            'Y': (self.MOD_SHIFT, 0x1c), 'Z': (self.MOD_SHIFT, 0x1d),

            # Numbers 1-9, 0
            '1': (0, 0x1e), '2': (0, 0x1f), '3': (0, 0x20), '4': (0, 0x21),
            '5': (0, 0x22), '6': (0, 0x23), '7': (0, 0x24), '8': (0, 0x25),
            '9': (0, 0x26), '0': (0, 0x27),

            # Punctuation & Structural [cite: 64, 138]
            ' ':  (0, 0x2c), '\n': (0, 0x28), '\t': (0, 0x2b),
            '!': (self.MOD_SHIFT, 0x1e), '@': (self.MOD_SHIFT, 0x1f),
            '#': (self.MOD_SHIFT, 0x20), '$': (self.MOD_SHIFT, 0x21),
            '.': (0, 0x37), ',': (0, 0x36), '?': (self.MOD_SHIFT, 0x38),
        }

        # --- Numpad Scan Codes for Windows Strategy B --- 
        self.NUMPAD_MAP = {
            '0': 0x62, '1': 0x59, '2': 0x5a, '3': 0x5b, '4': 0x5c,
            '5': 0x5d, '6': 0x5e, '7': 0x5f, '8': 0x60, '9': 0x61,
            '+': 0x57
        }

    def get_report(self, char):
        """Returns the 8-byte HID report for a standard ASCII character."""
        if char in self.ASCII_MAP:
            mod, code = self.ASCII_MAP[char]
            return self._build_report(mod, code)
        return None

    def get_numpad_report(self, digit, modifier=0x00):
        """Returns the 8-byte HID report for a Numpad digit."""
        if digit in self.NUMPAD_MAP:
            code = self.NUMPAD_MAP[digit]
            return self._build_report(modifier, code)
        return None

    def get_null_report(self):
        """Returns the 8-byte null report (all release)."""
        return self._null_report

    def _build_report(self, modifier, scancode):
        """Internal helper to construct the 8-byte buffer."""
        report = bytearray(8)
        report[0] = modifier   # Byte 0: Modifiers
        report[1] = 0x00       # Byte 1: Reserved
        report[2] = scancode   # Byte 2: Scan code
        # Bytes 3-7 remain 0x00 (Padding)
        return bytes(report)

