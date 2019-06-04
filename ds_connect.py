import socket
import sys

class Ds_connect(object):


    DS_IP = 'vega.ii.uam.es'
    DS_PORT = 8000

    def ds_connect(self, message):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.DS_IP, self.DS_PORT))

        try:
            s.send(message.encode('utf-8'))
            ret = s.recv(1024).decode('utf-8')
            #FALTA IMPLEMENTAR LECTURA DE TODA LA LISTA
        except:
            s.close()
            return None

        s.close()
        return ret
