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
