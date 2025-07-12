# port_finder.py
import socket
import os

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

port = find_free_port()

# Write to .env
with open('.env', 'w') as f:
    f.write(f"PORT={port}\n")

print(f"[✔] Port {port} selected and written to .env")
