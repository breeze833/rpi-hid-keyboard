from .layout import USBKeyboardLayout

class Str2HIDTransformer:
    def __init__(self, os_mode='linux'):
        self.os_mode = os_mode
        self.layout = USBKeyboardLayout()
    
    def inject_unicode(self, codepoint):
        """Implements injection sequences for different OS flavors."""
        
        if self.os_mode == "windows":
            # Strategy: Universal Hex Numpad (Requires EnableHexNumpad Registry Key)
            # This bypasses Codepage 950 / Big5 issues by using raw Unicode.
            
            # Trick: All the key presses/releases should keep Alt down
            
            # 1. Trigger: Press Alt + Numpad '+' (Scan code 0x57)
            yield self.layout._build_report(self.layout.MOD_ALT, self.layout.NUMPAD_MAP['+'])
            yield self.layout._build_report(self.layout.MOD_ALT, 0x00)
            
            # 2. Sequence: Type Hex digits while continuing to hold Alt
            for h in f"{codepoint:04x}":
                # Retrieve the standard scan code for the hex digit (0-9, a-f)
                # and wrap it in a report where MOD_ALT is still active.
                if h.isdigit():
                    code = self.layout.NUMPAD_MAP[h]
                else:
                    _, code = self.layout.ASCII_MAP[h]
                yield self.layout._build_report(self.layout.MOD_ALT, code)
                yield self.layout._build_report(self.layout.MOD_ALT, 0x00)
                
            # Release of Alt via the NULL_REPORT 
            yield self.layout.get_null_report()
                
        elif self.os_mode == "linux":
            # Linux: Ctrl+Shift+U, hex code, then Enter
            # 1. Trigger sequence (Ctrl+Shift+U)
            trigger_mod = self.layout.MOD_CTRL | self.layout.MOD_SHIFT
            _, u_code = self.layout.ASCII_MAP['u']
            yield self.layout._build_report(trigger_mod, u_code)
            yield self.layout.get_null_report()
            
            # 2. Send Hex digits (no modifiers)
            for h in f"{codepoint:x}":
                yield self.layout.get_report(h)
                yield self.layout.get_null_report()
                
            # 3. Finalize with Enter
            yield self.layout.get_report('\n')
            yield self.layout.get_null_report()
            
        elif self.os_mode == "macos":
            # macOS: Hold Option (Alt) and type 4-digit hex
            # Requires "Unicode Hex Input" to be active on the host
            for h in f"{codepoint:04x}":
                report = self.layout.get_report(h)
                # Apply Option (MOD_ALT) to the hex digit report
                mod, code = self.layout.ASCII_MAP[h]
                yield self.layout._build_report(self.layout.MOD_ALT, code)
                yield self.layout._build_report(self.layout.MOD_ALT, 0x00)
            # release Alt key after the input sequence
            yield self.layout.get_null_report()
            
    def generate_hid_reports(self, text):
        """Iterates through text and chooses the correct input path."""
        for char in text:
            cp = ord(char)
            # Path 1: Standard ASCII
            if cp < 128 and char in self.layout.ASCII_MAP:
                yield self.layout.get_report(char)
                yield self.layout.get_null_report()
            # Path 2: Strategy B (Multilingual Injection)
            else:
                for r in self.inject_unicode(cp):
                    yield r
