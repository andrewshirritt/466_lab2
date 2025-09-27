import os
import random
import socket
import time

from comm_interface import CommInterface

random.seed(1)
DROP_PROBABILITY = 0.1
DUPLICATE_PROBABILITY = 0.1
LAG_PROBABILITY = 0.5

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
        message = f"{data}:{filename}:{self.sendsnumber}"
        encoded_msg = message.encode()
        print(f"Sending {self.sendsnumber}")
        self._send(encoded_msg, addr)
        if data != 'QUT':
            while True:
                try:
                    ack, _ = self.socket.recvfrom(self.CHUNK_SIZE)
                    if ack.startswith(b'ack:'):
                        ack_num = int(ack.decode().split(":")[1])
                        if ack_num == self.sendsnumber:
                            print(f"Received ack for {ack_num}")
                            self.sendsnumber += 1
                            break
                except:
                    print(f"Timeout or error, resending {self.sendsnumber}")
                    self._send(encoded_msg, addr)
        else:
            for i in range(10):
                self._send(encoded_msg, addr)



        # message = data + ":" + filename + ":" + str(self.sendsnumber)
        # print(self.sendsnumber)
        # self._send(message.encode(), addr)
        #
        #
        # while True:
        #     try:
        #         message, addr = self.socket.recvfrom(self.CHUNK_SIZE)
        #         if message == b'ack':
        #             self._send(b'ack', addr)
        #             self.sendsnumber += 1
        #             break
        #
        #     except:
        #         self._send(message.encode(), addr)
        #         print(f"sending again {self.sendsnumber}")







    def send_file(self, filepath, addr):
        pass
        # snumber = 1
        # with open(filepath, "rb") as f:
        #     while True:
        #         chunk = f.read(self.CHUNK_SIZE-50)
        #
        #         if not chunk:
        #             break
        #         chunk = f'{snumber}'.encode() + '|||'.encode() + chunk
        #         #self._send(chunk, addr)
        #         self._send(chunk, addr)
        #         #Replace this with
        #         #Ack#server Ack#client Ack#server#++
        #         #if Ack# not equal when returned:
        #         while True:
        #             try :
        #                 self.socket.recvfrom(CHUNK_SIZE)
        #                 #if client_ack == snumber:
        #                 break
        #             except:
        #
        #                 self._send(chunk, addr)
        #                 print("sending again")
        #
        #         snumber += 1
        #
        # chunk = f'{snumber}|||end'.encode()
        # self._send(chunk, addr)
        # while True:
        #     try:
        #         self.socket.recvfrom(CHUNK_SIZE)
        #         # if client_ack == snumber:
        #         break
        #     except:
        #
        #         self._send(chunk, addr)
        #         print("sending again")

    def receive_message(self):
        while True:
            try:
                message, addr = self.socket.recvfrom(self.CHUNK_SIZE)
                if message.startswith(b'ack:'):
                    continue  # ignore ack packets

                com, filename, snumber = message.decode().split(":")
                snumber = int(snumber)

                if snumber == self.recvsnumber:
                    print(f"Received new message {snumber}")
                    ack_msg = f"ack:{snumber}".encode()
                    self._send(ack_msg, addr)
                    self.recvsnumber += 1
                    return com, filename, addr
                else:
                    # Duplicate or out-of-order — re-ack
                    print(f"Duplicate or old message {snumber}, expected {self.recvsnumber}")
                    ack_msg = f"ack:{snumber}".encode()
                    self._send(ack_msg, addr)
            except:
                continue




        self._send(b'ack', addr)
        self.recvsnumber += 1
        print(self.recvsnumber)
        return com, filename, addr
        # while True:
        #     try:
        #         message, addr = self.socket.recvfrom(self.CHUNK_SIZE)
        #         if message == b'ack':
        #             continue
        #         com, filename, snumber = message.decode().split(":")
        #         #print(snumber)
        #         #print(self.recvsnumber)
        #
        #         snumber = int(snumber)
        #         if snumber == self.recvsnumber:
        #             self._send(b'ack', addr)
        #             continue
        #         break
        #     except:
        #         continue
        #
        # self._send(b'ack', addr)
        # while True:
        #     try:
        #         message, addr = self.socket.recvfrom(self.CHUNK_SIZE)
        #         print('hi')
        #         if message != b'ack':
        #             self._send(b'ack', addr)
        #         else:
        #             break
        #     except:
        #         continue
        #
        # self.recvsnumber +=1
        # print(self.recvsnumber)
        #
        #
        # return com, filename, addr

    def receive_file(self, filepath):
        pass
        # snumber = 0
        # with open(filepath, "wb") as f:
        #     while True:
        #         previous = snumber
        #         while True:
        #
        #             try:
        #                 chunk, addr = self.socket.recvfrom(self.CHUNK_SIZE)
        #                 if chunk == b'ack':
        #                     continue
        #                 break
        #             except:
        #                 pass
        #
        #         try:
        #             snumber, message = chunk.split(b'|||')
        #         except:
        #             self._send(b'ack', addr)
        #             continue
        #
        #         if snumber == previous:
        #             continue
        #
        #
        #
        #
        #         if message == b'end':
        #             self.socket.sendto(b'ack', addr)
        #             break
        #         self.socket.sendto(snumber, addr)
        #         f.write(message)