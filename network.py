import socket
import threading

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

    def send(self, data):
        if self.conn:
            self.conn.sendall(data.encode())

    def recv(self):
        if self.conn:
            return self.conn.recv(1024).decode()
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
        self.running = True

    def send(self, data):
        self.sock.sendall(data.encode())

    def recv(self):
        return self.sock.recv(1024).decode()

    def close(self):
        self.running = False
        self.sock.close()
