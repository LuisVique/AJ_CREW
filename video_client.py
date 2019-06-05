# import the library
from appJar import gui
from PIL import Image, ImageTk
from ds_users import Ds_users
from control_server import Control_server
import threading
import numpy as np
import cv2


class VideoClient(object):

	ds_server = Ds_users()

	DS_NICK = "rodri"
	DS_PASS = "clave"
	DS_IP = "127.0.0.0"
	DS_PORT = 8080
	DS_VERS = "V0"

	FLAG_LOGIN = 0

	CALL_USER = ''

	def __init__(self, window_size):

		# Creamos una variable que contenga el GUI principal
		self.app = gui("Redes2 - P2P", window_size)
		self.app.setGuiPadding(10,10)

		# Preparación del interfaz
		self.app.addLabel("title", "Cliente Multimedia P2P - Redes2 ")
		self.app.addImage("video", "imgs/webcam.gif")

		# Registramos la función de captura de video
		# Esta misma función también sirve para enviar un vídeo
		self.cap = cv2.VideoCapture(0)
		self.app.setPollTime(20)
		self.app.registerEvent(self.capturaVideo)

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
		self.app.setEntryDefault("Nick", self.DS_NICK)
		self.app.setEntryDefault("Pass", self.DS_PASS)
		self.app.addButton("Sign in", self.buttonsCallback)
		self.app.stopSubWindow()

		self.app.startSubWindow("user_busq", modal = True)
		self.app.addLabel("busqEx", "Búsqueda realizada con éxito ")
		self.app.addHorizontalSeparator(colour="black")
		self.app.stopSubWindow()


	def start(self):
		self.app.go()

	# Función que captura el frame a mostrar en cada momento
	def capturaVideo(self):

		# Capturamos un frame de la cámara o del vídeo
		ret, frame = self.cap.read()
		frame = cv2.resize(frame, (640,480))
		cv2_im = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
		img_tk = ImageTk.PhotoImage(Image.fromarray(cv2_im))

		# Lo mostramos en el GUI
		self.app.setImageData("video", img_tk, fmt = 'PhotoImage')

		# Aquí tendría que el código que envia el frame a la red
		# ...

	# Establece la resolución de la imagen capturada
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
				if self.ds_server.ds_register( self.DS_NICK + ' ' + self.DS_IP + ' ' + str(self.DS_PORT) + ' ' + self.DS_PASS + ' ' + self.DS_VERS ):
					self.app.infoBox("Info", t_aux + " con el usuario: " + self.DS_NICK , parent = "login")
				else:
					self.app.errorBox("Info", "Ha ocurrido un problema durante el registro, por favor, intenteló de nuevo", parent = "login")
			else:

				user = self.app.getEntry("Nick")
				passw = self.app.getEntry("Pass")

				if self.ds_server.ds_register( self.DS_NICK + ' ' + self.DS_IP + ' ' + str(self.DS_PORT) + ' ' + self.DS_PASS + ' ' + self.DS_VERS ):

					self.DS_NICK = user
					self.DS_PASS = passw

					self.app.infoBox("Info", t_aux + " con el usuario: " + self.DS_NICK, parent = "login")
				else:
					self.app.errorBox("Info2", "Ha ocurrido un problema durante el registro, por favor, intenteló de nuevo", parent = "login")

			self.app.setStatusbar("User: " + self.DS_NICK, 0)
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

		#TODO LO DE LLAMADA
		self.app.hideSubWindow("users")

if __name__ == '__main__':

	vc = VideoClient("640x520")

	cServer= threading.Thread(target = Control_server().server_controler , args=())
	cServer.start()
	# Crear aquí los threads de lectura, de recepción y,
	# en general, todo el código de inicialización que sea necesario
	# ...


	# Lanza el bucle principal del GUI
	# El control ya NO vuelve de esta función, por lo que todas las
	# acciones deberán ser gestionadas desde callbacks y threads
	vc.start()
