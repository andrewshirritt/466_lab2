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
        self.recvsnumber = 0
        self.sendsnumber = 0

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
        message = data + ":" + filename + ":" + str(self.sendsnumber)
        encodedmsg = message.encode()
        self._send(encodedmsg, addr)


        if data != 'QUT':
            while True:

                try:
                    ack, addr = self.socket.recvfrom(self.CHUNK_SIZE)
                    if ack.startswith(b'ACK:'):
                        snumber = ack.decode().split(":")[1]
                        snumber = int(snumber)

                        if snumber == self.sendsnumber:

                            self.sendsnumber += 1
                            break
                except:
                    print(f"sending again packet {self.sendsnumber}")
                    self._send(encodedmsg, addr)
        else:
            for i in range(10):
                self._send(encodedmsg, addr)


    def send_file(self, filepath, addr):


        snumber = 0
        with open(filepath, "rb") as f:
            while True:
                chunk = f.read(self.CHUNK_SIZE-50)

                if not chunk:
                    break
                chunk = f'{snumber}'.encode() + '|||'.encode() + chunk

                self._send(chunk, addr)


                while True:
                    try :
                        ack, addr = self.socket.recvfrom(self.CHUNK_SIZE)

                        if ack.startswith(b'ack:'):
                            acknumber = ack.decode().split(":")[1]
                            acknumber = int(acknumber)

                            if snumber == acknumber:
                                snumber += 1
                                break
                    except:

                        self._send(chunk, addr)
                        print("sending again")



        chunk = f'{snumber}|||end'.encode()
        self._send(chunk, addr)
        while True:
            try:
                ack , addr = self.socket.recvfrom(CHUNK_SIZE)
                if ack.startswith(b'ack:'):
                    acknumber = ack.decode().split(":")[1]
                    acknumber = int(acknumber)
                    if snumber == acknumber:
                        pass

                    break

            except:

                self._send(chunk, addr)
                print("sending again")

    def receive_message(self):
        while True:
            try:
                message, addr = self.socket.recvfrom(self.CHUNK_SIZE)
                if message.startswith(b'ack:') or message.startswith(b'ACK'):

                    continue

                com, filename, snumber = message.decode().split(":")
                snumber = int(snumber)


                if snumber == self.recvsnumber:



                    ackmsg = f"ACK:{snumber}".encode()
                    self._send(ackmsg, addr)
                    self.recvsnumber += 1
                    return com, filename, addr
                else:

                    ackmsg = f"ACK:{snumber}".encode()
                    self._send(ackmsg, addr)
            except:
                continue






    def receive_file(self, filepath):


        recvnumber = 0
        with open(filepath, "wb") as f:
            while True:

                while True:

                    try:
                        chunk, addr = self.socket.recvfrom(self.CHUNK_SIZE)
                        if chunk.startswith(b'ack:') or chunk.startswith(b'GET:') or chunk.startswith(b'PUT:') or chunk.startswith(b'QUT'):

                            continue
                        break
                    except:
                        pass


                snumber, message = chunk.split(b'|||')
                #
                # ackmsg = f'ack:{snumber}'.encode()
                #
                # self.socket.sendto(ackmsg, addr)

                snumber = int(snumber)

                if snumber == recvnumber:
                    ackmsg = f'ack:{snumber}'.encode()
                    self._send(ackmsg, addr)
                    recvnumber += 1

                    if message == b'end':
                        ackmsg = f'ack:{recvnumber}'.encode()
                        self._send(ackmsg, addr)
                        break
                    f.write(message)
                else:
                    ackmsg = f'ack:{snumber}'.encode()
                    self._send(ackmsg, addr)







