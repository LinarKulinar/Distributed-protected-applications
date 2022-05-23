import os
from OpenSSL import crypto

"""
генерация сертификатов
"""

def create_self_signed_cert(cert_dir, key_file, cert_file):
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 1024)  # размер может быть 2048, 4196

    #  Создание сертификата
    cert = crypto.X509()
    cert.get_subject().C = "RU"  # указываем свои данные
    cert.get_subject().ST = "Tatarstan"  # указываем свои данные
    cert.get_subject().L = "Naberezhnye Chelny"  # указываем свои данные
    cert.get_subject().O = "xazrad"  # указываем свои данные
    cert.get_subject().OU = "xazrad"  # указываем свои данные
    cert.get_subject().CN = "example.com"  # указываем свои данные
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10 * 365 * 24 * 60 * 60)  # срок "жизни" сертификата
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')

    with open(os.path.join(cert_dir, cert_file), "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

    with open(os.path.join(cert_dir, key_file), "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))


create_self_signed_cert(cert_dir='.', key_file='client.key', cert_file='client.crt')
create_self_signed_cert(cert_dir='.', key_file='server.key', cert_file='server.crt')
