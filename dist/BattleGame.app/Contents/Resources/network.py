import socket
import threading
import json
import struct
import time
import zlib

# Simple network module for 2-player LAN connection with UDP support
# Ultra-low latency optimizations

class NetworkHost:
    def __init__(self, port=50007, use_udp=True):
        self.use_udp = use_udp
        self.port = port
        self.client_addr = None
        self.buffer = b""  # For TCP message buffering
        self.last_recv_time = time.time()
        self.compress = True  # Enable compression for larger payloads
        self.send_queue = []  # Batch small messages
        self.last_send_time = time.time()
        
        if use_udp:
            # UDP socket - faster, no connection overhead
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Ultra-low latency UDP settings
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)  # Larger send buffer
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)  # Larger receive buffer
            try:
                # Set IP_TOS for low latency (best effort)
                self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, 0x10)  # IPTOS_LOWDELAY
            except:
                pass
            self.sock.bind(("", port))
            self.sock.setblocking(False)
            self.conn = None
            self.running = True
        else:
            # TCP socket with optimizations
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Disable Nagle's algorithm
            self.sock.bind(("", port))
            self.sock.listen(1)
            self.conn = None
            self.addr = None
            self.running = True
            self.thread = threading.Thread(target=self.accept)
            self.thread.start()

    def accept(self):
        if not self.use_udp:
            self.conn, self.addr = self.sock.accept()
            if self.conn:
                self.conn.setblocking(False)  # Make non-blocking
                self.conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

    def send(self, data, priority='normal'):
        try:
            if isinstance(data, dict):
                data = json.dumps(data, separators=(',', ':'))  # Compact JSON
            msg = data.encode()
            
            # Compress if message is large enough (>100 bytes saves bandwidth)
            if self.compress and len(msg) > 100:
                compressed = zlib.compress(msg, level=1)  # Fast compression
                if len(compressed) < len(msg) * 0.9:  # Only if we save 10%+
                    msg = b'\x01' + compressed  # Flag as compressed
                else:
                    msg = b'\x00' + msg  # Flag as uncompressed
            else:
                msg = b'\x00' + msg  # Flag as uncompressed
            
            if self.use_udp:
                if self.client_addr:
                    # Send immediately for UDP (no batching needed, already fast)
                    self.sock.sendto(msg, self.client_addr)
            else:
                if self.conn:
                    # Add length prefix for TCP
                    self.conn.sendall(struct.pack('!I', len(msg)) + msg)
        except:
            pass

    def recv(self):
        try:
            if self.use_udp:
                data, addr = self.sock.recvfrom(65536)  # Larger buffer for less fragmentation
                if data:
                    # Remember client address for sending
                    if not self.client_addr:
                        self.client_addr = addr
                    self.last_recv_time = time.time()
                    
                    # Check compression flag
                    if data[0:1] == b'\x01':
                        data = zlib.decompress(data[1:])
                    else:
                        data = data[1:]
                    
                    return json.loads(data.decode())
            else:
                if self.conn:
                    # Read length prefix
                    while len(self.buffer) < 4:
                        chunk = self.conn.recv(4 - len(self.buffer))
                        if not chunk:
                            return None
                        self.buffer += chunk
                    
                    msg_len = struct.unpack('!I', self.buffer[:4])[0]
                    self.buffer = self.buffer[4:]
                    
                    # Read message
                    while len(self.buffer) < msg_len:
                        chunk = self.conn.recv(msg_len - len(self.buffer))
                        if not chunk:
                            return None
                        self.buffer += chunk
                    
                    msg = self.buffer[:msg_len]
                    self.buffer = self.buffer[msg_len:]
                    self.last_recv_time = time.time()
                    return json.loads(msg.decode())
        except BlockingIOError:
            pass  # No data available yet
        except:
            pass
        return None

    def close(self):
        self.running = False
        if not self.use_udp and self.conn:
            self.conn.close()
        self.sock.close()

class NetworkClient:
    def __init__(self, host_ip, port=50007, use_udp=True):
        self.use_udp = use_udp
        self.host_addr = (host_ip, port)
        self.buffer = b""  # For TCP message buffering
        self.last_recv_time = time.time()
        self.compress = True  # Enable compression
        self.send_queue = []  # Batch small messages
        self.last_send_time = time.time()
        
        if use_udp:
            # UDP socket - faster, no handshake
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Ultra-low latency UDP settings
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
            try:
                # Set IP_TOS for low latency
                self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, 0x10)  # IPTOS_LOWDELAY
            except:
                pass
            self.sock.setblocking(False)
            # Send initial packet to establish connection
            self.sock.sendto(b'\x00{"type":"connect"}', self.host_addr)
        else:
            # TCP socket with optimizations
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)  # Disable Nagle's algorithm
            self.sock.connect((host_ip, port))
            self.sock.setblocking(False)
        
        self.running = True

    def send(self, data, priority='normal'):
        try:
            if isinstance(data, dict):
                data = json.dumps(data, separators=(',', ':'))  # Compact JSON
            msg = data.encode()
            
            # Compress if message is large enough
            if self.compress and len(msg) > 100:
                compressed = zlib.compress(msg, level=1)  # Fast compression
                if len(compressed) < len(msg) * 0.9:  # Only if we save 10%+
                    msg = b'\x01' + compressed
                else:
                    msg = b'\x00' + msg
            else:
                msg = b'\x00' + msg
            
            if self.use_udp:
                self.sock.sendto(msg, self.host_addr)
            else:
                # Add length prefix for TCP
                self.sock.sendall(struct.pack('!I', len(msg)) + msg)
        except:
            pass

    def recv(self):
        try:
            if self.use_udp:
                data, _ = self.sock.recvfrom(8192)
                if data:
                    self.last_recv_time = time.time()
                    return json.loads(data.decode())
            else:
                # Read length prefix
                while len(self.buffer) < 4:
                    chunk = self.sock.recv(4 - len(self.buffer))
                    if not chunk:
                        return None
                    self.buffer += chunk
                
                msg_len = struct.unpack('!I', self.buffer[:4])[0]
                self.buffer = self.buffer[4:]
                
                # Read message
                while len(self.buffer) < msg_len:
                    chunk = self.sock.recv(msg_len - len(self.buffer))
                    if not chunk:
                        return None
                    self.buffer += chunk
                
                msg = self.buffer[:msg_len]
                self.buffer = self.buffer[msg_len:]
                self.last_recv_time = time.time()
                return json.loads(msg.decode())
        except BlockingIOError:
            pass  # No data available yet
        except:
            pass
        return None

    def close(self):
        self.running = False
        self.sock.close()
