#-*- coding: utf-8 -*-
# 
#		Projeto de Conclusão de Curso 
#		
#		Escola e Faculdade SENAI "Anchieta"
#		
#		Curso Técnico em Eletrônica
#
#		Sistema de Qualidade de Peças (SQP)
#		
#		Sistema de Visão Computacional utilizando: ORANGE PI PC (Armbian 5.4.20) + Linguagem Python + Biblioteca OpenCV
#
#		Autor: Rafael Nascimento Silva				Data: Março de 2020
#		
#		

# ------------------------------------------------------------------------------------------------------------------------------------------------------- #
# --- Bibliotecas ---
# ------------------------------------------------------------------------------------------------------------------------------------------------------- #

import OPi.GPIO as GPIO
import time
import cv2
import numpy as np
import imagehash
from PIL import Image

# ------------------------------------------------------------------------------------------------------------------------------------------------------- #
# --- Variaveis Globais ---
# ------------------------------------------------------------------------------------------------------------------------------------------------------- #

captura = 5 																	#pino 29, Botão que captura a imagem original

#iniciar = 6																		#pino 32, Botão que iniciara a esteira.
#resetar = 13																	#pino 33, Botão de reset para a esteira e deleta as imagens
esteira = 26																	#pino 37, Aciona a esteira

sensor = 19																		#pino 35, Sensor que captura as imagens para comparação.
atuador = 16																	#pino 36, Atuador que será acionado para tirar a peça ruim da esteira.

# ------------------------------------------------------------------------------------------------------------------------------------------------------- #
# --- Configuração dos GPIO's ---
# ------------------------------------------------------------------------------------------------------------------------------------------------------- #

GPIO.setwarnings(False)
GPIO.setboard(GPIO.PCPCPLUS)    												# Orange Pi PC board.
GPIO.setmode(GPIO.BOARD)        												# Configura a numeração BMC da placa.
GPIO.setmode(GPIO.BCM)

GPIO.setup(atuador, GPIO.OUT)													# Configura o atuador como saida.
GPIO.setup(esteira, GPIO.OUT)													# Configura a esteira como saida.

#GPIO.setup(iniciar, GPIO.IN, initial=GPIO.HIGH, pull_up_down=GPIO.PUD_UP)		# Configura botão de captura como entrada e valor inicia alto(HIGH)
GPIO.setup(sensor,  GPIO.IN, initial=GPIO.HIGH, pull_up_down=GPIO.PUD_UP)		# Configura sinal do sensor como entrada e valor inicia alto(HIGH)
GPIO.setup(captura, GPIO.IN, initial=GPIO.HIGH, pull_up_down=GPIO.PUD_UP)		# Configura botão de captura como entrada e valor inicia alto(HIGH)
#GPIO.setup(resetar, GPIO.IN, initial=GPIO.HIGH, pull_up_down=GPIO.PUD_UP)		# Configura botão de resetar como entrada e valor inicia alto(HIGH)
data=""

# ------------------------------------------------------------------------------------------------------------------------------------------------------- #
# --- Funções do Programa ---
# ------------------------------------------------------------------------------------------------------------------------------------------------------- #

# Função que capturar a imagem original atravez de um botão.
def capture_image():
	print('Aguarde.....')
	
	camera_port = 1														# Cria um objeto câmera, associado ao identificador dado por camera_port
	nFrame = 30
	camera = cv2.VideoCapture(camera_port)
	file = ("original.jpg")												# Nome do arquivo onde será gravada a imagem
	
	print ("Pressione <ESC> se quiser sair")
	
	emLoop = True
	
	while (emLoop):														# Fica em loop até que seja pressionado a tecla ESC, para sair do programa
		retval, img = camera.read()										# Le um frame da camera
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
		cv2.imshow("Foto", img)											# Mostra o frame na tela
		time.sleep(2)
		
		esc = cv2.waitKey(3000)											# Le o teclado a cada 3000 milissegundos
		
		if esc == 27:													# Se for a tecla ESC sai do loop
			emLoop = False
		else:
			cv2.imwrite(file,img)
			emLoop = False
	
	camera.release()													# Libera objeto da camera.
	time.sleep(2)
	
	print('Imagem capturado com sucesso!')
	print(" ")
	return 0
# Fim da Função

# Função que capturar a imagem do sensor que sera comparada com a original. 	
def capture_image_sensor():
	print('Aguarde.....')
	print(" ")
	
	camera_port = 1														
	nFrame = 30
	camera = cv2.VideoCapture(camera_port)
	file = ("image_sensor/sensor.jpg")												
	
	print ("Pressione <ESC> se quiser sair")
	print (" ")
	
	emLoop = True
	
	while (emLoop):														
		retval, img = camera.read()
		img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)										
		cv2.imshow("Foto", img)											
		time.sleep(2)
		
		esc = cv2.waitKey(3000)											
		
		if esc == 27:													
			emLoop = False
		else:
			cv2.imwrite(file,img)
			emLoop = False
	
	camera.release()													
	time.sleep(2)
	
	print('Imagem capturado com sucesso!')
	print(" ")
	return 0
# Fim da Função

# Função que vai compara as duas imagens e retornar a semelhança entre elas
def compare_image():
							
	hash = imagehash.average_hash(Image.open('original.jpg'))
	otherhash = imagehash.average_hash(Image.open('image_sensor/sensor.jpg'))

	time.sleep(3)
	
	comparado = hash - otherhash
	
	print(comparado)
	print(" ")
	
	if (comparado <= 7):
		print ("PEÇA BOA...")
		print (" ")
		time.sleep(5)
		GPIO.output(esteira,1)					 						            # Se a peça for igual a original, liga a esteira.	
		time.sleep(2)
		GPIO.output(esteira,0)
	else:
		print ("PEÇA COM DEFEITO...")
		print (" ")
		time.sleep(5)
		GPIO.output(atuador,1)                     						            #Se a peça for não for igual a original, liga atuador e liga esteira.
		GPIO.output(esteira, 1)	
		time.sleep(2)						 							            # Apaga a imagem do sensor.
		GPIO.output(atuador,0)                     						            # Se a peça for não for igual a original, liga atuador e liga esteira.
		GPIO.output(esteira, 0)
	
# Fim da Função


	
# ------------------------------------------------------------------------------------------------------------------------------------------------------- #
# --- Inicio do Programa ---
# ------------------------------------------------------------------------------------------------------------------------------------------------------- #

print('Bem vindo ao Sistema de Visão')
print(" ")
time.sleep(1)
Loop = False

while True:
	print('Por favor aperte o botão "capture" para salvar a peça boa')
	print(" ")
	time.sleep(1)

	if GPIO.input(captura) == False:											# Botão Captura: Quando pressionado captura a imagem da peça boa.
		time.sleep(1)
		capture_image()
		time.sleep(1)
		
		Loop = True
		break
	
# --- LOOP INFINITO --- 

try:
	while (Loop):
		print ("Aguardando Sinal... ")
		print (" ")
		
#		if GPIO.input(iniciar) == False:										# Botão Iniciar: Quando for pressionado inicia o processo, faz a esteira andar.
#			GPIO.output(esteira, 1) 
#	
#		if GPIO.input(resetar) == False:										# Botão Reset: Quando for pressionado reseta o processo, e apaga a imagem original. 
#			GPIO.output(esteira, 0)
#			print ("Reiniciando Programa... ")
#			print(" ")
#			time.sleep(2)
#			break
#				
		if GPIO.input(sensor) == False:											# Quando o sensor detectar a peça a esteira para e a camera captura a imagem.
			capture_image_sensor()
			time.sleep(2)
			compare_image()
			
			

# -- FIM DO LOOP --					

# ------------------------------------------------------------------------------------------------------------------------------------------------------- #
		
#Se qualquer tecla do teclado foi apertada o programa sai do loop e encerra.
except KeyboardInterrupt:			 
	print("Programa interrompido.......")
	GPIO.cleanup()
	cv2.destroyAllWindows()												# Fecha as janelas
	time.sleep(3)

# -- FIM DO PROGRAMA --	
# ------------------------------------------------------------------------------------------------------------------------------------------------------- #
