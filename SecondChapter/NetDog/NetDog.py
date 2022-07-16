# NetCat improvisado com python

import sys
import socket
import getopt
import threading
import subprocess

# Definindo algumas variaveis globais
listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0


def to_byte(str_obj):
    return str_obj.encode()


def usage():
    print("NetDog Net Tool")
    print("")
    print("Usage: NetDog.py -t target_host -p port")
    print("-l --listen               - listen on [host]:[port] for incoming connections")
    print("-e --execute=file_to_run  - execute the given file upon receiving a connection")
    print("-c --command              - initialize a command shell")
    print("-u --upload=destination   -upon receiving connection upload a file and write to [destination]")
    print("")
    print("")
    print("Examples: ")
    print("NetDog.py -t 127.0.0.1 -p 5555 -l -c")
    print("NetDog.py -t 127.0.0.1 -p 5555 -l -u=c:\\target.exe")
    print("NetDog.py -t 127.0.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'NetDog' | ./NetDog.py -t 127.0.0.1 -p 135")
    sys.exit(0)


def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        # Conecta-se ao nosso alvo
        client.connect((target, port))
        if len(buffer):
            client.send(to_byte(buffer))

        while True:
            # Agora espera receber dados de volta
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break

            print(response),
            # Espera mais dados de entrada
            buffer = input("")
            buffer += "\n"

            # Envia dados
            client.send(to_byte(buffer))
    except:
        print("[*] Exception! Stopping")
        # Encerra conexao
        client.close()


def client_handler(client_socket):
    global upload
    global execute
    global command

    # Verifica se e upload
    if len(upload_destination):
        # Le todos os bytes e grava em nosso destino
        file_buffer = ""
        # Permanece lendo os dados ate que não haja mais nenhum disponivel
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data

        # Agora tentaremos gravar esses bytes
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(to_byte(file_buffer))
            file_descriptor.close()
            # Confirma que gravamos o arquivo
            client_socket.send(to_byte("Successfully saved file to %s\r\n" % upload_destination))
        except:
            client_socket.send(to_byte("Failed to save file to %s\r\n" % upload_destination))

    # Verifica se e execucao de comando
    if len(execute):
        # Executa o comando
        output = run_command(execute)
        client_socket.send(to_byte(output))

    # Entra em outro laco se um shell de comandos foi solicitado
    if command:
        while True:
            # Mostra um prompt simples
            client_socket.send(to_byte("<BHP:#> "))
            # Agora ficamos recebendo dados ate vermos um linefeed (tecla enter)
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            # Envia de volta a saida do comando
            response = run_command(cmd_buffer)
            # Envia de volta a resposta
            client_socket.send(to_byte(response))


def server_loop():
    global target
    # Se não houver nenhum alvo definido, ouviremos todas as interfaces
    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        # Dispara uma tread para cuidar de nosso novo cliente
        client_thread = threading.Thread(target=client_handler, args=(client_socket,))
        client_thread.start()


def run_command(r_command):
    # Remove a quebra de linha
    r_command = r_command.rstrip()
    # Executa o comando e obtem os dados de saida
    try:
        output = subprocess.check_output(r_command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Failed to execute command.\r\n"
    # Envia dados de saida ao cliente
    return output


def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    argumentsArray = ["help", "listen", "execute", "target", "port", "command", "upload"]

    if not len(sys.argv[1:]):
        usage()

    # Le as opções da linha de comando
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:", argumentsArray)
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    # Iremos ouvir ou enviar dados de stdin?
    if not listen and len(target) and port > 0:
        # Le o buffer da linha de comando
        # Isso causara um bloqueio, portanto envie um CTROL-D se não estiver enviando dados de entrada para o stdin
        buffer = sys.stdin.read()
        # Send data off
        client_sender(buffer)

    # Iremos ouvir a porta e, potencialmente, faremos upload de dados, executaremos comandos e deixaremos um shell
    # de acordo com as opçoes de linha de comando anteriores
    if listen:
        server_loop()


main()
