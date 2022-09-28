import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading


def execute(cmd):
    cmd - cmd.strip()
    if not cmd:
        return
    # 1-We’re using its check_output method, which runs a command on the local operating system and then
    # returns the output from that command.
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()


class NetDog:
    # 1-We initialize the NetDog object with the arguments from the command line and the buffer
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        # 2-We create the socket object
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.listen:
            # 3-The run method, which is the entry point for managing the NetCat object,
            # is pretty simple: it delegates execution to two methods. If we’re setting up a
            # listener, we call the listen method
            self.listen()
        else:
            # 4-Otherwise, we call the send method
            self.send()

    def send(self):
        # 1-We connect to the target and port
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)
        # 2-If we have a buffer, we send that to the target first. Then we set up a try/catch block -so we can manually
        # close the connection with CTRL-C
        try:
            # 3-Next, we start a loop to receive data from the target.
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        # 4-If there is no more data, we break out of the loop
                        break
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    # 5-Otherwise, we print the response data and pause to get interactive input,
                    # send that input, and continue the loop.
                    self.socket.send(buffer.encode())
        # 6-The loop will continue until the KeyboardInterrupt (CTRL-C) occurs, which will close the socket
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()

    def listen(self):
        # 1-The listen method binds to the target and port
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        # 2-And starts listening in a loop
        while True:
            client_socket, _ = self.socket.accept()
            # 3-Passing the connected socket to the handle method
            client_thread = threading.Thread(target=self.handle, args=(client_socket,))
            client_thread.start()

    def handle(self, client_socket):
        # 1-The handle method executes the task corresponding to the command
        # line argument it receives: execute a command, upload a file, or start a
        # shell. If a command should be executed, the handle method passes that
        # command to the execute function and sends the output back on the socket
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
        # 2-If a file should be uploaded, we set up a loop to listen for content on the listening socket
        # and receive data until there’s no more data coming in. Then we
        # write that accumulated content to the specified file
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                else:
                    break
            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
            message = f'Saved file {self.args.upload}'
            client_socket.send(message.encode())
        # 3-Finally, if a shell is to be created, we set up a loop,
        # send a prompt to the sender, and wait for a command string to come back.
        elif self.args.command:
            cmd_buffer = b''
            while True:
                try:
                    client_socket.send(b'BHP: #> ')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer = b''
                except Exception as e:
                    print(f'Server killed {e}')
                    self.socket.close()
                    sys.exit()


if __name__ == '__main__':
    # 1-We use the argparse module from the standard library to create a command line interface.
    parser = argparse.ArgumentParser(
        description='NetDog',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        # 2-We provide example usage that the program will display when the user invokes it with --help.
        epilog=textwrap.dedent('''Example:
            netcat.py -t 192.168.1.108 -p 5555 -l -c # command shell
            netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt # upload to file
            netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" # execute command
            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 # echo text to server port 135
            netcat.py -t 192.168.1.108 -p 5555 # connect to server
        '''))
    # 3-Add six arguments that specify how we want the program to behave.
    parser.add_argument('-c', '--command', action='store_true', help='command shell')
    parser.add_argument('-e', '--execute', help='execute specified command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='specified port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='specified IP')
    parser.add_argument('-u', '--upload', help='upload file')
    args = parser.parse_args()
    # 4-If we’re setting it up as a listener, we invoke the NetCat object with an empty buffer string.
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()
    nd = NetDog(args, buffer.encode())
    nd.run()