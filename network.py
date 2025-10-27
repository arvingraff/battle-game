import socket
import threading
import json

# Simple network module for 2-player LAN connection

class NetworkHost:
    def __init__(self, port=50007):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", port))
        self.sock.listen(1)
        self.conn = None
        self.addr = None
        self.running = True
        self.thread = threading.Thread(target=self.accept)
        self.thread.start()

    def accept(self):
        self.conn, self.addr = self.sock.accept()
        if self.conn:
            self.conn.setblocking(False)  # Make non-blocking

    def send(self, data):
        if self.conn:
            try:
                if isinstance(data, dict):
                    data = json.dumps(data)
                self.conn.sendall((data + '\n').encode())
            except:
                pass

    def recv(self):
        if self.conn:
            try:
                data = self.conn.recv(4096).decode().strip()  # Larger buffer
                if data:
                    return json.loads(data)
            except BlockingIOError:
                pass  # No data available yet
            except:
                pass
        return None

    def close(self):
        self.running = False
        if self.conn:
            self.conn.close()
        self.sock.close()

class NetworkClient:
    def __init__(self, host_ip, port=50007):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host_ip, port))
        self.sock.setblocking(False)  # Make non-blocking
        self.running = True

    def send(self, data):
        try:
            if isinstance(data, dict):
                data = json.dumps(data)
            self.sock.sendall((data + '\n').encode())
        except:
            pass

    def recv(self):
        try:
            data = self.sock.recv(4096).decode().strip()  # Larger buffer
            if data:
                return json.loads(data)
        except BlockingIOError:
            pass  # No data available yet
        except:
            pass
        return None

    def close(self):
        self.running = False
        self.sock.close()
