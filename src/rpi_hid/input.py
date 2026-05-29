import os
import sys
import socket
import select
from contextlib import contextmanager

class HIDInputSrc:
    """Encapsulates the context and streaming logic for data sources."""
    def __init__(self, socket_path="/tmp/hid_keyboard.sock"):
        self.socket_path = socket_path
        self.server = None

    def get_source_ctx(self):
        if self.socket_path == '-':
            return self._stdin_source()
        else:
            return self._unix_socket_source()
            
    @contextmanager
    def _unix_socket_source(self):
        """Persistent UNIX socket server wrapper."""
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.server.bind(self.socket_path)
        os.chmod(self.socket_path, 0o666)  # Give user-land services access
        self.server.listen(1)
        print(f"HID Daemon: unix socket {self.socket_path}", file=sys.stderr)

        try:
            yield self._stream_sockets()
        except KeyboardInterrupt:
            print("Terminated.", file=sys.stderr)
        finally:
            if self.server:
                self.server.close()
                print('service on socket stopped.', file=sys.stderr)
            if os.path.exists(self.socket_path):
                os.remove(self.socket_path)

    def _stream_sockets(self):
        """Internal generator reading raw text sequences."""
        while True:
            conn, _ = self.server.accept()
            buffer = ""
            try:
                while True:
                    data = conn.recv(1024)
                    if not data:  # Client disconnected safely
                        raise EOFError("socket EOF")
                    
                    buffer += data.decode('utf-8', errors='ignore')
                    while "\0" in buffer:
                        message, buffer = buffer.split("\0", 1)
                        yield message
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)
            finally:
                conn.close()

    @contextmanager
    def _stdin_source(self):
        """Standard Input wrapper protecting global sys.stdin handles."""
        print("HID Daemon: Reading from STDIN (Press Ctrl+D to exit)", file=sys.stderr)
        try:
            yield self._stream_stdin()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
        finally:
            # Defensive sandbox block: Do NOT close sys.stdin directly!
            print('service on stdin stopped.', file=sys.stderr)

    def _stream_stdin(self):
        buffer = ""
        while True:
            ready_to_read, _, _ = select.select([sys.stdin], [], [])
            data = sys.stdin.buffer.read()
            if not data:
                raise EOFError("stdin EOF")
            
            buffer += data.decode('utf-8', errors='ignore')
            while "\0" in buffer:
                message, buffer = buffer.split("\0", 1)
                yield message
