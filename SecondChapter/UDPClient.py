import socket

target_host = "192.168.18.12"
target_port = 80

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
byte_obj = "I am the Alpha and the Omega,” says the Lord God".encode()
client.sendto(byte_obj, (target_host, target_port))

data, addr = client.recvfrom(4096)

print(data)
