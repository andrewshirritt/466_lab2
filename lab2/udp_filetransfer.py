import os
import random
import socket
import time

from comm_interface import CommInterface

random.seed(1)
DROP_PROBABILITY = 0.1
DUPLICATE_PROBABILITY = 0.1
LAG_PROBABILITY = 0.1

CHUNK_SIZE = 1024


class UDPFileTransfer(CommInterface):
    """Reliable UDP file transfer implementation."""

    CHUNK_SIZE = 1024

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def initialize_as_server(self, host, port):
        self.socket.bind((host, port))

    def initialize_as_client(self):
        pass

    def _send(self, message, dest_addr):
        if random.random() < DROP_PROBABILITY:
            return
        if random.random() < DUPLICATE_PROBABILITY:
            self.socket.sendto(message, dest_addr)
        if random.random() < LAG_PROBABILITY:
            time.sleep(random.uniform(0.1, 0.3))

        self.socket.sendto(message, dest_addr)

    def send_message(self, data, filename="", addr=None):
        message = data + ":" + filename
        self.socket.sendto(message.encode(), addr)



    def send_file(self, filepath, addr):
        snumber = 1
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(self.CHUNK_SIZE-50)

                if not chunk:
                    break
                chunk = f'{snumber}'.encode() + '|||'.encode() + chunk
                #self._send(chunk, addr)
                self._send(chunk, addr)
                #Replace this with
                #Ack#server Ack#client Ack#server#++
                #if Ack# not equal when returned:
                while True:
                    try :
                        self.socket.recvfrom(CHUNK_SIZE)
                        #if client_ack == snumber:
                        break
                    except:

                        self._send(chunk, addr)
                        print("sending again")

                snumber += 1

        chunk = f'{snumber}|||end'.encode()
        self.socket.sendto(chunk, addr)


    def receive_message(self):
        message, addr = self.socket.recvfrom(self.CHUNK_SIZE)

        com, filename = message.decode().split(":")
        return com, filename, addr

    def receive_file(self, filepath):
        snumber = 0
        with open(filepath, "wb") as f:
            while True:
                previous = snumber
                while True:

                    try:
                        chunk, addr = self.socket.recvfrom(self.CHUNK_SIZE)
                        break
                    except:
                        pass


                snumber, message = chunk.split(b'|||')
                if snumber == previous:
                    continue




                if message == b'end':
                    break
                self.socket.sendto(snumber, addr)
                f.write(message)