import io
import socket
import ssl
import numpy as np

from PIL import Image


def bytesToRGB(img_bytes):
    image = Image.open(io.BytesIO(img_bytes))
    return np.array(image)

def noise(pixels: np.ndarray, treshold: float):
    result = np.copy(pixels)
    index = np.random.rand(pixels.shape[0], pixels.shape[1])
    result[index < treshold] = np.zeros(3)
    return result

def recvall(sock, count):
    data = bytearray()
    while len(data) < count:
        #need_len = count - len(data)
        need_len = 1024
        pack = sock.recv(need_len)
        print('recieved {0} bytes'.format(len(pack)))
        if not pack:
            return None
        data.extend(pack)
    return data


host_addr = 'localhost'
host_port = 9095
server_sni_hostname = 'example.com'
server_cert = 'server.crt'
client_cert = 'client.crt'
client_key = 'client.key'

listen_addr = 'localhost'
listen_port = 9096
server_cert = 'server.crt'  # публичная часть сертификата
server_key = 'server.key'  # приватная часть сертификата
client_certs = 'client.crt'

context_c = ssl.create_default_context(ssl.Purpose.SERVER_AUTH, cafile=server_cert)
context_c.load_cert_chain(certfile=client_cert, keyfile=client_key)

context_s = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context_s.verify_mode = ssl.CERT_REQUIRED
context_s.load_cert_chain(certfile=server_cert, keyfile=server_key)
context_s.load_verify_locations(cafile=client_certs)

bindsocket = socket.socket()
bindsocket.bind((listen_addr, listen_port))
bindsocket.listen(5)

s = socket.socket()

conn_c = context_c.wrap_socket(s, server_side=False, server_hostname=server_sni_hostname)
conn_c.connect((host_addr, host_port))

print("Waiting for client")
newsocket, fromaddr = bindsocket.accept()  # Поступили данные от клиента
conn_s = context_s.wrap_socket(newsocket, server_side=True)

img_file_len = recvall(conn_s, 8)  # Получаем размер изображения от клиента
a = int.from_bytes(img_file_len, byteorder='big', signed=False)
print("Размер полученного изображения равен:", a)

img_data = recvall(conn_s, a)

image_without_noise = bytesToRGB(img_data)
image_with_noise = noise(image_without_noise, treshold=0.1)  # Делаем зашумление

im = Image.fromarray(image_with_noise)
buf = io.BytesIO()
im.save(buf, format='JPEG')
byte_im = buf.getvalue()

img_file_noise = open('noise_inter_ssl.jpg', 'wb')
img_file_noise.write(byte_im)
img_file_noise.close()

img_file = open('recieved_inter_ssl.jpg', 'wb')
img_file.write(img_data)
img_file.close()

a = len(byte_im)
ba = a.to_bytes(8, byteorder='big')

conn_c.sendall(ba)
conn_c.sendall(byte_im)

conn_s.shutdown(socket.SHUT_RDWR)
conn_s.close()

# conn_c.close()
