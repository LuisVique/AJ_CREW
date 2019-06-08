import socket
import sys

class Ds_connect(object):

    def __init__(self, u_data):
        self.u_data = u_data

    def ds_connect(self, message):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.u_data.DS_IP, self.u_data.DS_PORT))

        try:
            s.send(message.encode('utf-8'))
            ret = s.recv(1024).decode('utf-8')
            #FALTA IMPLEMENTAR LECTURA DE TODA LA LISTA
        except:
            s.close()
            return None

        s.close()
        return ret
