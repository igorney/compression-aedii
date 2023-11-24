import socket
import threading
import json
import os
import time
import Node
from RunLengthEncodingCompressor import RunLengthEncodingCompressor
import base64

class Peer:
    sockIn= socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Socket de entrada de pacotes
    rle = RunLengthEncodingCompressor()
    peerLigado = True
    ipPeer = 0
    portaPeer = 0
    pastaPeer = ""
    arquivos = []
    def __init__(self):
        #self.ipPeer = input("Digite o ip do Peer: ")
        self.ipPeer = "127.0.0.1"
        self.portaPeer = int(input("Digite a porta do Peer: "))
        self.pastaPeer = input("Digite o caminho da pasta: ")   # Digitar com ./ no inicio para entrar em pastas dentro da mesma pasta do arquivo .py
        for _, _, filename in os.walk(self.pastaPeer):          #Aqui usei parte do codigo da referencia 3 para acessar os arquivos dentro das pastas
            for uniquefile in filename:
                self.arquivos.append(uniquefile)
        self.sockIn.bind((self.ipPeer, self.portaPeer))
        self.sockIn.listen(5)
        threading.Thread(target=self.peerMenuThread).start()    #Inicia a thread de menu
        while self.peerLigado:
            c, _ = self.sockIn.accept()
            threading.Thread(target=self.peerConectionThread(c)).start()    #Inicia thread de tratamento de recebimento de pacotes
    def peerConectionThread(self, c):               #thread de tratamento de recebimento de pacotes
        msg = json.loads(c.recv(1024).decode())     #abre o pacote recebido e armazena em um dicionario
        match msg["CMD"]:   #Classifica o comando da solicitação recebida
            case "JOIN_OK":
                print(f'Sou peer {msg["IP"]}:{msg["PORTA"]} com arquivos {msg["ARQUIVOS"]}')
            case "SEARCH_OK":
                print(f'Peers com arquivo solicitado: {msg["RESULTADO"]}')
            case "UPDATE_OK":
                print(f'Servidor atualizou minha informação sobre o arquivo: {msg["ARQUIVO"]}')
            case "DOWNLOAD": #Recebe um pedido de download de arquivo que esse Peer contém
                arquivoEncontrado = False
                for arq in self.arquivos:
                    if msg["DOWNLOAD"] == arq: #Procura arquivo dentro desse Peer
                        msg["CMD"] = "DOWNLOAD_OK"
                        c.send(json.dumps(msg).encode()) #envia um "DOWLOAD_OK" permitindo o envio do arquivo para o peer
                        time.sleep(0.5)     #time para que o peer requisitante esteja pronto para receber o arquivo
                        arquivoEncontrado = True
                        file = open(self.pastaPeer +"/" + msg["DOWNLOAD"], "rb") #abre o arquivo que pertence a esse Peer
                        data = file.read()  #armazena todos os bytes do arquivo em data
                        #INICIO RELOGIO
                        data = (self.rle.compress(data))
                        #FIM relogio
                        c.sendall(data)     #envia todos os dados
                        c.send(b"<END>")    #Tag que informa fim do envio
                        file.close()
                if not arquivoEncontrado:   #Tratamento para quando não existe o arquivo pedido
                    msg = {"CMD" : "DOWNLOAD_NOT_OK", "IP" : self.ipPeer, "PORTA" : self.portaPeer, "DOWNLOAD": msg["DOWNLOAD"]}
                    c.send(json.dumps(msg).encode())    #Envia DOWLOAD_NOT_OK
                    print(f'Arquivo {msg["DOWNLOAD"]} inexistente nesse Peer')
            case _:                         #Tratamento para recebimento de pacotes "msg" não identificados
                print("Erro comando recebido não identificado")
        c.close()
    def peerMenuThread(self):
        ultimaBusca = ""
        ipServer = ""
        portaServer = ""
        while self.peerLigado:
            sockOut = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            time.sleep(0.5)
            comand = input("Digite JOIN, SEARCH, DOWNLOAD ou EXIT para executar um comando: ")
            match comand:
                case "JOIN":    #Armazena as informações desse Peer a um servidor
                    ipServer = input("Digite o ip do servidor: ")
                    portaServer = input("Digite a porta do servidor: ")
                    sockOut.connect((ipServer, int(portaServer)))
                    msg = {"CMD" : "JOIN", "IP" : self.ipPeer, "PORTA" : self.portaPeer, "ARQUIVOS" : self.arquivos} #Envia mensagem com informações sobre esse peer 
                    sockOut.send(json.dumps(msg).encode())                                                           # para que seja armazenadas pelo servidor
                    sockOut.close()
                case "SEARCH":
                    if ipServer == "" or portaServer == "": # Tratamento para casos onde o Peer ainda não deu JOIN em nenhum servidor
                        print("É necessário se conectar a um servidor para usar esse comando, use JOIN ")
                        continue    #Quebra o case SEARCH
                    ultimaBusca = input("Digite o arquivo com extensão que deseja encontrar: ") #Armazena arquivo para que o download seja feito no futuro
                    sockOut.connect((ipServer, int(portaServer)))
                    msg = {"CMD" : "SEARCH", "IP" : self.ipPeer, "PORTA" : self.portaPeer, "BUSCA" : ultimaBusca} #Envia o SEARCH para o servidor
                    sockOut.send(json.dumps(msg).encode())
                    sockOut.close()
                case "DOWNLOAD":
                    if ipServer == "" or portaServer == "":     #Tratamento para casos onde o Peer ainda não deu JOIN em nenhum servidor
                        print("É necessário se conectar a um servidor para usar esse comando, use JOIN ")
                        continue    #Quebra o case DOWNLOAD
                    elif ultimaBusca == "":                     #Tratamento para requisicao de DOWNLOAD sem ter feito SEARCH antes
                        print("É necessário fazer um SEARCH antes de fazer um DOWNLOAD")
                        continue
                    ipConnect = input("Digite o ip do Peer: ")  #Envia dados do peer que deseja copiar o arquivo
                    portaConnect = input("Digite a porta do Peer: ")
                    sockOut.connect((ipConnect, int(portaConnect)))
                    msg = {"CMD" : "DOWNLOAD", "IP" : self.ipPeer, "PORTA" : self.portaPeer, "DOWNLOAD" : ultimaBusca}
                    sockOut.send(json.dumps(msg).encode())              #Envia pedido de download
                    resposta = json.loads(sockOut.recv(1024).decode())  #Recebe "DOWNLOAD_OK" ou "DOWNLOAD_NOT_OK"
                    if(resposta["CMD"] == "DOWNLOAD_NOT_OK"):           #Trata o caso de o Peer solicitado não conter o arquivo
                        print(f'Arquivo {resposta["DOWNLOAD"]} não existe no Peer {resposta["IP"]}:{resposta["PORTA"]}')
                        continue    #Quebra o case DOWNLOAD
                    file = open(self.pastaPeer +"/" + ultimaBusca, "wb")#Cria o arquivo na pasta do Peer solicitante com o mesmo nome do pedido
                    file_bytes = b""
                    done = False
                    while not done:
                        data = sockOut.recv(8388608)    #recebe dados enviados pelo outro peer, buffer tem tamanho 2**23
                        if file_bytes[-5:] == b"<END>": #Verifica se tem a tag que indica final do arquivo
                            done = True                 #Caso tenha sai do laço
                        else:
                            file_bytes += data          #Caso não continua recebendo arquivo
                    # TODO: Decode do arquivo recebido comprimido
                    file.write(self.rle.decompress(file_bytes))        #Quando recebe o arquivo inteiro (todos os bytes), insere no arquivo criado
                    #RELOGIOrle_decode
                    file.close()                        #Fecha arquivo
                    sockOut.close()
                    print(f'Arquivo {ultimaBusca} baixado com sucesso na pasta {self.pastaPeer}')
                    sockUPDT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    #Cria socket para envio do UPDATE
                    sockUPDT.connect((ipServer, int(portaServer)))
                    msg = {"CMD" : "UPDATE", "IP" : self.ipPeer, "PORTA" : self.portaPeer, "ARQUIVO" : ultimaBusca} 
                    sockUPDT.send(json.dumps(msg).encode())                         #Cria e envia pacote UPDATE para o servidor
                    sockUPDT.close()
                case "EXIT":    #trata quando queremos desligar o PEER
                    self.peerLigado = False
                    self.sockIn.close()
                case _:         #trata erros de digitação
                    print("\n Erro de digitação, insira os comandos com letras maiusculas")
        
p = Peer()
