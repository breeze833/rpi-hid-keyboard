
class HIDDaemon:
    def __init__(self, hid_src_ctx, transform, hid_dst_ctx):
        self.hid_src_ctx = hid_src_ctx
        self.transform = transform
        self.hid_dst_ctx = hid_dst_ctx

    def run(self):
        with self.hid_src_ctx as src, self.hid_dst_ctx as dst:
            for text in src:
                if text.startswith("CMD:MODE:"):
                    new_mode = line.split(':')[-1].lower()
                    if new_mode in ['windows', 'linux', 'macos']:
                        self.transform.os_mode = new_mode
                        print(f"Switched mode to: {transform.os_mode}", file=sys.stderr)
                            
                # Route: Implicit Text
                else:
                    for report in self.transform.generate_hid_reports(text):
                        dst.send_report(report)
