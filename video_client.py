# import the library
from appJar import gui
from PIL import Image, ImageTk
from ds_users import Ds_users
from user_data import User_data
import threading
import numpy as np
import cv2
import socket
import sys
import time
import collections

class VideoClient(object):

	# DS_NICK = "rodri"
	# DS_PASS = "clave"
	# DS_VERS = "V0"

	FLAG_LOGIN = 0

	def __init__(self, window_size, u_data):


		self.ds_server = Ds_users(u_data)
		self.u_data = u_data

		self.vid_buffer = collections.deque(maxlen = None)
		# Creamos una variable que contenga el GUI principal
		self.app = gui("Redes2 - P2P", window_size)
		self.app.setGuiPadding(10,10)

		# Preparación del interfaz
		self.app.addLabel("title", "Cliente Multimedia P2P - Redes2 ")
		self.app.addImage("video", "imgs/webcam.gif")

		# Registramos la función de captura de video
		# Esta misma función también sirve para enviar un vídeo
		# self.cap = cv2.VideoCapture(0)
		# self.app.setPollTime(20)
		# self.app.registerEvent(self.capturaVideo)

		# Añadir los botones
		self.app.addButtons(["Conectar", "Login", "Salir"], self.buttonsCallback)

		# Barra de estado
		# Debe actualizarse con información útil sobre la llamada (duración, FPS, etc...)
		self.app.addStatusbar(fields=2)

		self.app.startSubWindow("users", modal= True)
		self.app.startScrollPane("PANE")
		self.app.addLabel("1", "Selecciona al usuario que desea llamar:")
		list_users = self.ds_server.ds_listUsers()[1:]
		for user in list_users:
			self.app.addButton(user.split()[0], self.callButtons)
		self.app.stopScrollPane()
		self.app.addButton("Introducir usuario", self.callButtons)
		self.app.stopSubWindow()


		self.app.startSubWindow("login", modal = True)
		self.app.addLabel("labelNick", "Nick :")
		self.app.addEntry("Nick")
		self.app.addLabel("labelPass","Password :")
		self.app.addSecretEntry("Pass")
		self.app.setEntryDefault("Nick", self.u_data.US_NICK)
		self.app.setEntryDefault("Pass", self.u_data.US_PASS)
		self.app.addButton("Sign in", self.buttonsCallback)
		self.app.stopSubWindow()

		self.app.startSubWindow("user_busq", modal = True)
		self.app.addLabel("busqEx", "Búsqueda realizada con éxito ")
		self.app.addHorizontalSeparator(colour="black")
		self.app.stopSubWindow()

		# self.app.startSubWindow("calling", modal = True)
		# self.app.addLabel("info3", "Conexión exitosa: \n")
		# self.app.stopSubWindow()

	def start(self):
		self.app.go()


	def incoming_call(self, user):
		ret = self.app.questionBox("Llamada", user + ' ' + 'te está llamando' + '\n' + '¿ Quieres aceptar la llamada ?')

		return ret

	def end_call(self):
		self.app.infoBox("end", "El usuario ha colgado la llamada ")

	def hold_call(self):
		self.app.infoBox("hold", "El usuario ha pausado la llamada")

	def c_user_available(self, user):
		self.u_data.DST_UDP = user.split()[2]
		# self.app.openSubWindow("calling")
		# self.app.addLabel("callingT", "Llamando a:" + user.split()[1])
		# self.app.stopSubWindow()
		# self.app.showSubWindow("calling")
		# time.sleep(5)
		self.u_data.IN_CALL = 1
		#ACTIVANDO EL FLAG COMIENZA LA LLAMADA

	def c_user_cancel(self, user):
		self.app.errorBox("err1","El usuario " + user.split()[1] + " ha rechazado la llamada")

	def c_user_busy(self, user):
		self.app.errorBox("err2", "El usuario " + user.split()[1] + " está ocupado")

	def start_call(self, user):

		C_USER_STATUS = {"CALL_ACCEPTED": self.c_user_available, "CALL_DENIED": self.c_user_cancel, "CALL_BUSY": self.c_user_busy}
		msg, msg2, nick, ip, port, proto = self.ds_server.ds_query(user).split()

		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Conecta el socket en el puerto cuando el servidor esté escuchando
		server_address = (ip, int(port))
		sock.connect(server_address)

		try:
			sock.sendall(("CALLING " + self.u_data.US_NICK + ' ' + str(self.u_data.UDP_PORT)).encode('utf-8'))
			ret = sock.recv(1024).decode('utf-8')
			self.u_data.DST_IP = ip
			self.u_data.DST_TCP = port
			status = ret.split()[0]

			func = C_USER_STATUS.get(status, lambda: "Invalid status")
			if func != "Invalid status":
				func(ret)

		finally:
		    sock.close()


	# Función que captura el frame a mostrar en cada momento
	def capturaVideo(self):

		# Capturamos un frame de la cámara o del vídeo
		ret, frame = self.cap.read()
		frame = cv2.resize(frame, (640,480))

		return frame

	def video_compression(self):

		ret, img = self.cap.read() # lectura de un frame de vídeo

		# Compresión JPG al 50% de resolución (se puede variar)
		encode_param = [cv2.IMWRITE_JPEG_QUALITY,50]
		result,encimg = cv2.imencode('.jpg',img,encode_param)
		if result == False: print('Error al codificar imagen')
		encimg = encimg.tobytes()

		return encimg

	def video_decompression(self, c_video):

		decimg = cv2.imdecode(np.frombuffer(c_video[4], np.uint8), 1)

		self.app.setStatusbar("FPS: " + c_video[3].decode('utf-8'), 1)

		return decimg

	# Establece la resolución de la imagen capturada


	def video_repro(self):

		while self.u_data.IN_CALL == 1:
			if len(self.vid_buffer) > 20:
					if len(self.vid_buffer) > 1:
						try:#frame_gran = self.capturaVideo()
							rcv_video = self.vid_buffer.popleft()

							frame_peque = cv2.resize(rcv_video, (320,240)) # ajustar tamaño de la imagen pequeña

							#frame_compuesto = frame_gran

							#frame_compuesto[0:frame_peque.shape[0], 0:frame_peque.shape[1]] = frame_peque

							cv2_im = cv2.cvtColor(frame_peque,cv2.COLOR_BGR2RGB)
							img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))

							self.app.setImageData("video", img_tk, fmt = 'PhotoImage')
						except:
							print("ERROR IN VIDEO BUFFER")

	def setImageResolution(self, resolution):
		# Se establece la resolución de captura de la webcam
		# Puede añadirse algún valor superior si la cámara lo permite
		# pero no modificar estos
		if resolution == "LOW":
			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)
		elif resolution == "MEDIUM":
			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
		elif resolution == "HIGH":
			self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
			self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

	# Función que gestiona los callbacks de los botones
	def buttonsCallback(self, button):

		if button == "Salir":
			# Salimos de la aplicación
			self.app.stop()
		elif button == "Conectar":
			self.app.showSubWindow("users")
		elif button == "Login":
			self.app.showSubWindow("login")
		elif button == "Sign in":
			t_aux = "Actualizado"
			if self.FLAG_LOGIN == 0:
				t_aux = "Registrado"
				self.app.setButton("Login", "Cambiar de usuario")

			if self.app.getEntry("Nick") == '' and self.app.getEntry("Pass") == '':
				if self.ds_server.ds_register( self.u_data.US_NICK + ' ' + self.u_data.US_IP + ' ' + str(self.u_data.TCP_CONTROL_PORT) + ' ' + self.u_data.US_PASS + ' ' + self.u_data.US_PROTO ):
					self.app.infoBox("Info", t_aux + " con el usuario: " + self.u_data.US_NICK , parent = "login")
				else:
					self.app.errorBox("Info", "Ha ocurrido un problema durante el registro, por favor, intenteló de nuevo", parent = "login")
			else:

				user = self.app.getEntry("Nick")
				passw = self.app.getEntry("Pass")

				if self.ds_server.ds_register( self.u_data.US_NICK + ' ' + self.u_data.US_IP + ' ' + str(self.u_data.TCP_CONTROL_PORT) + ' ' + self.u_data.US_PASS + ' ' + self.u_data.US_PROTO ):

					self.u_data.US_NICK = user
					self.u_data.US_PASS = passw

					self.app.infoBox("Info", t_aux + " con el usuario: " + self.u_data.US_NICK, parent = "login")
				else:
					self.app.errorBox("Info2", "Ha ocurrido un problema durante el registro, por favor, intenteló de nuevo", parent = "login")

			self.app.setStatusbar("User: " + self.u_data.US_NICK, 0)
			self.app.hideSubWindow("login")
			self.FLAG_LOGIN = 1


	def callButtons(self, button):
		self.USER_CALL = button
		if button == "Introducir usuario":
			self.USER_CALL = self.app.textBox("Conexión",
			"Introduce el nick del usuario a buscar")
			if self.USER_CALL:
				ret = self.ds_server.ds_query(self.USER_CALL)
				if ret:
					self.app.openSubWindow("user_busq")
					self.app.addLabel("user", "Usuario: " + self.USER_CALL)
					self.app.addButtons(["Llamar", "Cancelar"], self.callButtons)
					self.app.stopSubWindow()
					self.app.showSubWindow("user_busq")
					return
				else:
					self.app.errorBox("no_user", "El usuario introducido no se encuentra en el servidor")
		elif button == "Cancelar":
			self.app.hideSubWindow("user_busq")
			return

		self.start_call(button)
		self.app.hideSubWindow("users")

if __name__ == '__main__':

	u_data = User_data()
	vc = VideoClient("640x520", u_data)

	from call_system import Call_system;

	cSystem= threading.Thread(target = Call_system(u_data, vc).start_video_call , args=())
	cSystem.setDaemon(True)
	cSystem.start()

	from control_server import Control_server;

	cServer= threading.Thread(target = Control_server(u_data, vc).server_controler , args=())
	cServer.setDaemon(True)
	cServer.start()
	# Crear aquí los threads de lectura, de recepción y,
	# en general, todo el código de inicialización que sea necesario
	# ...


	# Lanza el bucle principal del GUI
	# El control ya NO vuelve de esta función, por lo que todas las
	# acciones deberán ser gestionadas desde callbacks y threads
	vc.start()
