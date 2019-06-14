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
        #return
        sock = socket.socket(socket.AF_INET, # Internet
                            socket.SOCK_DGRAM) # UDP
        sock.bind((self.u_data.US_IP,  int(self.u_data.UDP_PORT)))

        video_rep = threading.Thread(target = self.gui.video_repro , args=())
        video_rep.setDaemon(True)
        video_rep.start()

        while self.u_data.IN_CALL == 1:
            vid = sock.recvmsg(65536) # buffer size is 1024 bytes

            package = vid[0].split(b'#', 4)

            self.gui.vid_buffer.append(self.gui.video_decompression(package))
            # Conversión de formato para su uso en el GUI
        sock.close()

    def udp_video_snd(self):

        sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Conecta el socket en el puerto cuando el servidor esté escuchando
        server_address = (self.u_data.DST_IP, int(self.u_data.DST_TCP))
        sock2.connect(server_address)

        count = 0
        sock = socket.socket(socket.AF_INET, # Internet
                              socket.SOCK_DGRAM) # UDP
        sock.connect((self.u_data.DST_IP, int(self.u_data.DST_UDP)))

        while self.u_data.IN_CALL == 1:
            if self.u_data.HOLD_CALL == 0:
                ret = self.gui.video_compression()
                fps = int((1 / ret[1]))
                resolut = self.gui.resolution
                time_stm = time.time()
                pre = str(count) + '#' + str(time_stm) + '#' + resolut + '#' + str(fps) + '#'
                encimg =  pre.encode('utf-8')+ ret[0]
                sock.send(encimg)
                count += 1
            else:
                sock2.sendall(("CALL_HOLD").encode("utf-8"))
                while 1:
                    if self.u_data.HOLD_CALL == 0:
                        sock2.sendall(("CALL_RESUME").encode("utf-8"))
                        break


        sock.close()
