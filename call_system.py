import sys
import socket

class Call_system(object):
    #cerrar ventana de calling

    def __init__(self, u_data, gui):
        self.u_data = u_data
        self.gui = gui

    def start_video_call(self):

        while 1:
            if self.u_data.IN_CALL == 1:
                break
        #self.gui.app.hideSubWindow("calling")

        #hilo de video entrante
        #hilo de video saliente
