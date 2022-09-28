import socket
import threading


IP = 'localhost'
PORT = 9998


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 1-Passando IP e Porta para o server ouvir
    server.bind((IP, PORT))
    # 2-Servidor ouvindo com no maximo 5 conexoes
    server.listen(5)
    print(f'[*] Listening on {IP}:{PORT}')

    while True:
        # 3-Recebemos as variaveis dos clientes na variavel address
        client, address = server.accept()
        print(f'[*] Accepted connection from {address[0]}:{address[1]}')
        client_handler = threading.Thread(target=handle_client, args=(client,))
        # 4-Aqui estamos prontos para receber outra conexao
        client_handler.start()


# 5-Funcao que envia uma mensagem simples ao cliente
def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b'I am the Alpha and the Omega, says the Lord God')


if __name__ == '__main__':
    main()
