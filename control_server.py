from user_data import User_data
from appJar import gui
from video_client import VideoClient

import socket
import sys

class Control_server(object):

    BUSSY_FLAG = 0

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
                    client_data = conn.recv(1024).decode('utf-8')
                    func = self.CONTROL_COMMANDS.get(client_data, lambda: "Invalid command")
                    if func == "Invalid command":
                        break
                    func(self, conn)
            except:
                print("ERROR")
                #break

        s.close()


    def c_calling(self, connection):
        if self.BUSSY_FLAG == 0:
            self.gui.app.infoBox("hola","HEY FUNCIONO")
            connection.sendall(("CALL ACCEPTED " + self.u_data.US_NICK + ' ' + str(self.u_data.UDP_PORT)).encode('utf-8'))

    def c_hold(self,connection):
        connection.sendall(("HOLD").encode('utf-8'))
        return
    def c_resume(self,connection):
        connection.sendall(("RESUME").encode('utf-8'))
        return
    def c_end(self, connection):
        connection.sendall(("END").encode('utf-8'))
        return


    CONTROL_COMMANDS = {'CALLING': c_calling, 'CALL_HOLD': c_hold, 'CALL_RESUME': c_resume, 'CALL_END': c_end}
