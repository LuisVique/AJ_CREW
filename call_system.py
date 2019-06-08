import sys
import socket
import threading

class Call_system(object):
    #cerrar ventana de calling

    def __init__(self, u_data, gui):
        self.u_data = u_data
        self.gui = gui

    def start_video_call(self):

        while 1:
            if self.u_data.IN_CALL == 1:
                break

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Conecta el socket en el puerto cuando el servidor esté escuchando
        server_address = (self.u_data.DST_IP, int(self.u_data.DST_TCP))
        sock.connect(server_address)

        #self.gui.app.hideSubWindow("calling")

        #hilo de video entrante
        #hilo de video saliente

        video_rcv = threading.Thread(target = self.udp_video_rcv , args=())
        video_rcv.setDaemon(True)
        video_rcv.start()

        video_snd = threading.Thread(target = self.udp_video_snd , args=())
        video_snd.setDaemon(True)
        video_snd.start()


    def udp_video_rcv(self):

        sock = socket.socket(socket.AF_INET, # Internet
                            socket.SOCK_DGRAM) # UDP
        sock.bind((self.u_data.DST_IP,  int(self.u_data.DST_UDP)))

        while True:
            data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
            # Conversión de formato para su uso en el GUI
            self.gui.video_decompression(data)

    def udp_video_snd(self):

        sock = socket.socket(socket.AF_INET, # Internet
                              socket.SOCK_DGRAM) # UDP

        encimg = self.gui.video_compression()

        sock.sendto(encimg, (self.u_data.DST_IP, int(self.u_data.DST_UDP)))
        # Los datos "encimg" ya están listos para su envío por la red
        #enviar(encimg)
