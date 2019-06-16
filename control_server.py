from user_data import User_data
from appJar import gui
from video_client import VideoClient

import socket
import sys

class Control_server(object):

    BUSSY_FLAG = 0

    CALL_USER = ''

    def __init__(self, u_data, gui):
        self.u_data = u_data
        self.gui = gui

    def server_controler(self):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            s.bind((self.u_data.US_IP, self.u_data.TCP_CONTROL_PORT))
        except socket.error as msg:
            sys.exit()

        s.listen(1)

        while 1:
            conn, addr = s.accept()
            ip_c, res = addr

            try:
                while 1:
                    client_data = conn.recv(1024).decode('utf-8').split()
                    command, self.CALL_USER, self.u_data.DST_UDP = client_data
                    print(command)
                    self.u_data.DST_IP = ip_c
                    self.u_data.DST_TCP = self.u_data.DST_UDP
                    func = self.CONTROL_COMMANDS.get(command, lambda: "Invalid command")

                    if func == "Invalid command":
                        break
                    func(self, conn)
            except:
                continue

        s.close()


    def c_calling(self, connection):
        if self.u_data.BUSSY_FLAG == 0:
            if self.gui.incoming_call(self.CALL_USER) == 'yes' :
                connection.sendall(("CALL_ACCEPTED " + self.u_data.US_NICK + ' ' + str(self.u_data.UDP_PORT)).encode('utf-8'))
                self.u_data.BUSSY_FLAG = 1
                self.u_data.IN_CALL = 1
                #ACTIVANDO EL FLAG COMIENZA LA LLAMADA
            else:
                connection.sendall(("CALL_DENIED " + self.u_data.US_NICK ).encode('utf-8'))
        else:
            connection.sendall(("CALL_BUSY").encode('utf-8'))

    def c_hold(self,connection):
        self.u_data.HOLD_CALL = 1
        self.gui.hold_call()

    def c_resume(self,connection):
        self.u_data.HOLD_CALL = 0

    def c_end(self, connection):
        self.u_data.IN_CALL = 0
        self.u_data.BUSSY_FLAG = 0
        self.gui.end_call()


    CONTROL_COMMANDS = {'CALLING': c_calling, 'CALL_HOLD': c_hold, 'CALL_RESUME': c_resume, 'CALL_END': c_end}
