import socket
import time

HOST = "127.0.0.1"
PORT = 6666




class client:
  def __init__(self, host: str = "localhost", port: int = 6666) -> None:
    self.__host = host
    self.__port = port
    self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  
  def run(self):
    pass











with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  s.connect((HOST, PORT))
  s.settimeout(1)
  s.sendall(b"01")
  while True:
    try:
      print("enviou")
    except TimeoutError:
      print("timeout")
    # try:
    #   s.send(b"05O5tKjJVw9vzN9Ri7j1kRFMXMEa12345678910helloworld")
    # print(s.recv(256).decode())
    #   time.sleep(1)
    # except TimeoutError:
    # except OSError:
    #   break
    # s.send(b"0")
    # print()
    # s.send(b"01")
