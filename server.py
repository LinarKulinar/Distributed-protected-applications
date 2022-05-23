import socket
import ssl
from PIL import Image
import numpy as np
import io
import cv2


# Превращает байтовый массив изображения в np.array
def bytesToRGB(img_bytes):
    image = Image.open(io.BytesIO(img_bytes))
    return np.array(image)

# Функция, которая достаёт из sock 1024*count байт данных
def recvall(sock, count):
    data = bytearray()
    while len(data) < count:
        pack = sock.recv(1024)
        print('recieved {0} bytes'.format(len(pack)))
        if not pack:
            return None
        data.extend(pack)
    return data


listen_addr = 'localhost'
listen_port = 9095
server_cert = 'server.crt'
server_key = 'server.key'
client_certs = 'client.crt'

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.verify_mode = ssl.CERT_REQUIRED
context.load_cert_chain(certfile=server_cert, keyfile=server_key)
context.load_verify_locations(cafile=client_certs)

bindsocket = socket.socket()  # создаём сокет
bindsocket.bind((listen_addr, listen_port))  # связываем сокет с портом и хостом
bindsocket.listen(5)  # включаем режим прослушивания, с возможностью создания 5 подключений

print("Waiting for client")
newsocket, fromaddr = bindsocket.accept()  # принимаем подключение, возвращая кортеж с двумя элементами: новый сокет и адрес клиента
print("Accepted")
conn = context.wrap_socket(newsocket, server_side=True)
# img_file_len = conn.recv(100)

img_file_len = recvall(conn, 8)  # Достаём из сокета 8 КБ данных - размер изображения
a = int.from_bytes(img_file_len, byteorder='big', signed=False)
print("Размер полученного изображения равен:", a)

img_data = recvall(conn, a)
print("Получили изображение")
conn.settimeout(1)

# Фильтруем и сохраняем изображение
img_np = bytesToRGB(img_data)
median_blur = cv2.medianBlur(img_np, 3)
cv2.imwrite("recieved_image_with_filter_ssl.jpg", median_blur)

# Сохраняем изображение исходное полученное изображение без фильтрования
img_file = open('recieved_image_ssl.jpg', 'wb')
img_file.write(img_data)
img_file.close()

conn.shutdown(socket.SHUT_RDWR)
conn.close()

# Показываем изображение после фильтрования
img = Image.open('recieved_image_with_filter_ssl.jpg')
img.show()
