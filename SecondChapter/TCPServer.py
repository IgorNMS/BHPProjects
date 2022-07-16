import socket
import threading

bind_ip = "127.0.0.1"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((bind_ip, bind_port))  # 1
server.listen(5)  # 2

print("[*] Listening on %s:%d" % (bind_ip, bind_port))


# Esta e nossa thread para o tratamento de clientes

def handle_client(client_socket):  # 3
    # Exibe o que o cliente enviar
    request = client_socket.recv(1024)
    print("[*] Received: %s" % request)
    # Converte em byte para envio
    byte_obj = "ACK!".encode()
    # Envia um pacote de volta
    client_socket.send(byte_obj)
    client_socket.close()


while True:
    client, addr = server.accept()  # 4
    print("[*] Accepted connection from: %s:%d" % (addr[0], addr[1]))
    # Coloca nossa thread de cliente em ação para tratar dados de enntrada
    client_handler = threading.Thread(target=handle_client, args=(client,))
    client_handler.start()  # 5
