import socket
import ssl


def recvall(sock, count):
    data = bytearray()
    while len(data) < count:
        pack = sock.recv(count - len(data))
        print('recieved {0} bytes'.format(len(pack)))
        if not pack:
            return None
        data.extend(pack)
    return data


host_addr = 'localhost'
host_port = 9096
server_sni_hostname = 'example.com'
server_cert = 'server.crt'
client_cert = 'client.crt'
client_key = 'client.key'

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
context.load_cert_chain(certfile=client_cert, keyfile=client_key)

s = socket.socket()

conn = context.wrap_socket(s, server_side=False, server_hostname=server_sni_hostname)
conn.connect((host_addr, host_port))

img = open('A320neo.jpg', 'rb')
byte_array = img.read()

a = len(byte_array)

ba = a.to_bytes(8, byteorder='big')

int.from_bytes(ba, byteorder='big', signed=False)

conn.sendall(ba)  # Отправляем в сокет размер изображения
print("Отправили размер байтового массива в сокет")
conn.sendall(byte_array)  # Отправляем в сокет изображение
print("Отправили картинку в сокет")

# conn.shutdown(socket.SHUT_RDWR)
# conn.close()
