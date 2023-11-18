import socket
import threading
import json
class Servidor:
    peersINFO = [] #Armazenamento de informações dos peers conectados
    serverLigado = True
    sockIn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def __init__(self):
        ipServer = input("Digite o ip do servidor: ")
        portaServer = input("Digite a porta do servidor: ")
        self.sockIn.bind((ipServer, int(portaServer)))          #Definindo endereço do socket
        self.sockIn.listen(5)                                   #Socket pronto para receber conexões
        while self.serverLigado:
            c, _ = self.sockIn.accept()                                     #Socket aguarda conexão
            threading.Thread(target=self.serverConectionThread(c)).start()  #Cada conexão entra em uma thread de tratamento
    def serverConectionThread(self, c):                                     #Tratamento de pacotes recebidos
        sockOut = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         #define um socket para a resposta
        msg = json.loads(c.recv(1024).decode())                 #Recebe o pacote e transforma ele em um dicionario com as informações do pacote
        c.close()
        match msg["CMD"]:                       #Todos os dicionarios tem a chave "CMD" que define qual a solicitação dada ao servidor
            case "JOIN":
                self.peersINFO.append([msg["IP"], msg["PORTA"], json.dumps(msg["ARQUIVOS"])]) #Armazena informações do Peer adicionado
                msg["CMD"] = "JOIN_OK"          # Muda o CMD do pacote para envia-lo de volta ao Peer
                sockOut.connect((msg["IP"], msg["PORTA"]))  #Conecta ao peer que enviou a mensagem
                sockOut.send(json.dumps(msg).encode())      #Envia JOIN_OK
                sockOut.close()
                print(f'Peer {msg["IP"]}:{msg["PORTA"]} adicionado com arquivos {msg["ARQUIVOS"]}.')
            case "SEARCH":
                resultado = []                          #Armazena lista de peers que contem o arquivo
                print(f'Peer {msg["IP"]}:{msg["PORTA"]} solicitou arquivo {msg["BUSCA"]}.')
                for listaInfo in self.peersINFO:        #Pega cada lista armazenada na lista peersINFO
                    for arquivo in json.loads(listaInfo[2]):    #transforma listaInfo[2] que é uma lista armazenada em uma string para uma lista de verdade
                        if msg["BUSCA"] == arquivo:     #Compara cada arquivo que contem na listaInfo[2] com a busca
                            resultado.append([listaInfo[0], listaInfo[1]]) #adiciona informação dos peers que contém a busca
                msg["RESULTADO"] = json.dumps(resultado)#Insere o resultado da busca na mensagem, que também pode ser uma lista vazia
                msg["CMD"] = "SEARCH_OK"
                sockOut.connect((msg["IP"], msg["PORTA"]))
                sockOut.send(json.dumps(msg).encode())  #Envia a mensagem com o resultado do SEARCH
                sockOut.close()
            case "UPDATE":
                msg["CMD"] = "UPDATE_OK"
                for peer in self.peersINFO: #entra em cada lista contida na lista PeersINFO
                    if peer[0] == msg["IP"] and peer[1] == msg["PORTA"]: #Compara IP e Porta que deve ser atualizado com as informações salvas em PeersINFO
                        arquivos_peer = json.loads(peer[2])
                        arquivos_peer.append(msg["ARQUIVO"])
                        peer[2] = json.dumps(arquivos_peer)     #Salva o conjunto de arquivos que o servidor sabe do Peer
                        sockOut.connect((msg["IP"], msg["PORTA"]))
                        sockOut.send(json.dumps(msg).encode())  #Envia Update_OK
                        print(f'Peer {peer[0]}:{peer[1]} atualizado com arquivos {peer[2]}.')
                sockOut.close()
            case _:
                print("Mensagem não identificada")  #Caso entre algum pacote não identificado
Servidor()

