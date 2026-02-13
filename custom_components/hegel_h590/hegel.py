import socket

AMP_IP = "192.168.178.59"
AMP_PORT = 50001
TIMEOUT = 3


def send_command(command: str) -> str:
    """
    Send a raw TCP command to the Hegel H590 and return the response.
    """
    if not command.endswith("\r"):
        command += "\r"

    with socket.create_connection((AMP_IP, AMP_PORT), timeout=TIMEOUT) as sock:
        sock.sendall(command.encode("ascii"))

        # Small response, read once
        data = sock.recv(1024)

    return data.decode("ascii", errors="ignore").strip()


if __name__ == "__main__":
    print("Power:", send_command("-p.?"))
    print("Input:", send_command("-i.?"))
    print("Volume:", send_command("-v.?"))
    print("Mute:", send_command("-m.?"))

    # ---- CONTROL TESTS ----
    # print("Power ON:", send_command("-p.1"))
    # print("Set volume 30:", send_command("-v.30"))
    # print("Select Heimkino:", send_command("-i.3"))
    # print("Mute ON:", send_command("-m.1"))
