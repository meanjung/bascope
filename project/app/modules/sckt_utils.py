import bson
import socket
import time
import struct

p32 = lambda x: struct.pack("<I", x)
u32 = lambda x: struct.unpack("<I", x)[0]

from private.ports import SOCKET_PORT, TCP_SERVER_IP

BUFSIZE = 0x1000
def send_with_size(sock: socket.socket, msg):
    payload = p32(len(msg)) + msg
    sock.sendall(payload)


def create_socket():
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            sckt.connect((TCP_SERVER_IP, SOCKET_PORT))
            break
        except ConnectionRefusedError as e:
            time.sleep(1)
            continue
    
    # 본인이 웹임을 알리기 위해서
    introduce = {
        "type": "introduce",
        "detail": "web",
    }
    send_with_size(sckt, bson.dumps(introduce))
    time.sleep(1)
    
    return sckt

# 앞의 4바이트는 데이터 사이즈를 뜻함
def recv_data(sckt):
    result = b''

    total_length = u32(sckt.recv(4))
    BUF_SIZE = 4096
    while True:
        tmp = sckt.recv(BUF_SIZE)
        if not tmp:
            break
        result += tmp
        if total_length == len(result):
            break

    assert total_length == len(result)
    return result

# # Not Working :(
# def recv_data(sckt):
#     result = sckt.recv(1)
#     sckt.setblocking(False)
#     try:
#         while True:
#             tmp = sckt.recv(BUFSIZE)
#             if not tmp:
#                 break
#             result += tmp
#     except BlockingIOError as e:
#         # EAGAIN
#         pass
#     finally:
#         sckt.setblocking(True)
#     result = bson.loads(result)
#     return result

def get_local_ip(server_ip="8.8.8.8"):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect((server_ip, 0))
    ip = s.getsockname()[0]
    s.close()
    return ip
