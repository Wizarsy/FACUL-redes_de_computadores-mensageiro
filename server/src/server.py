from http import client
import json
import os
import pathlib
import queue
import random
import socket
import string
import threading
import sqlite3
import datetime
import time

class server:
  def __init__(self, host: str = "localhost", port: int = 6666) -> None:
    self.__host = host
    self.__port = port
    self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.__clients = {}
    self.__finished_threads = queue.Queue()
    self.__db = "main.db"
    self.__lock = threading.Lock()
    
  def __init_db(self) -> None:
    with sqlite3.connect(f"./{self.__db}") as db_conn:
      with db_conn:
        db_conn.execute("CREATE TABLE IF NOT EXISTS users(uid TEXT PRIMARY KEY NOT NULL)")
        db_conn.execute("CREATE TABLE IF NOT EXISTS groups(gid TEXT PRIMARY KEY NOT NULL)")
        db_conn.execute("""CREATE TABLE IF NOT EXISTS group_members(uid TEXT NOT NULL,
                                                                 gid TEXT NOT NULL,
                                                                 PRIMARY KEY (gid, uid), 
                                                                 FOREIGN KEY (gid) REFERENCES groups(gid) ON DELETE CASCADE, 
                                                                 FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE)""")
    
  def __create_user(self, conn: socket.socket) -> None:
    with sqlite3.connect(f"./{self.__db}") as db_conn:
      try:
        with db_conn:
          uid: str = "".join(random.choices(population = (string.ascii_letters + string.digits), k = 13))
          db_conn.execute("INSERT INTO users(uid) VALUES(?)", (uid,))
          msg: str = "02" + uid
          conn.sendall(msg.encode())
      except ConnectionError:
        pass
    return self.__del_thread(threading.current_thread())
  
  def __create_group(self, conn: socket.socket) -> None:
    pass
  
  def __disconnect_user(self, uid: str):
    return self.__del_thread(threading.current_thread())
  
  def __connect_user(self, conn: socket.socket, data: str) -> None | str:
    with sqlite3.connect(f"./{self.__db}") as db_conn:
      uid: str = db_conn.execute("SELECT * FROM users WHERE uid = ?", (data,)).fetchone()[0]
      if uid is not None:
        user = {"id": uid,
                "conn": conn,
                "queue": queue.Queue()}
        with self.__lock:
          self.__clients[uid] = user["queue"]
        return user
    return None
  
  def __pending_msg(self, user: dict) -> None:
    if os.path.isdir(f"./src/tmp/{user["id"]}"):
      msg_list = []
      for file in os.listdir(f"./src/tmp/{user["id"]}"):
        with open(f"./src/tmp/{user["id"]}/{file}") as json_file:
          msg_list.append(json.load(json_file))
        os.remove(f"./src/tmp/{user["id"]}/{file}")
      os.rmdir(f"./src/tmp/{user["id"]}")
      for msg in msg_list:
        user["queue"].put((msg["from"] + msg["to"] + msg["send_at"] + msg["msg"]))
    return self.__receive_msg(user)
  
  def __receive_msg(self, user: dict) -> None:
    while True:
      while not user["queue"].empty():
        msg = user["queue"].get()
        try:
          user["conn"].sendall(msg.encode())
          self.__new_thread(self.__send_delivered_confirmation, user["id"], msg[2:15])
        except ConnectionError:
          return self.__del_thread(threading.current_thread())
      time.sleep(1)
      
  def __save_msg(self, uid: str, data: str) -> None:
    return self.__del_thread(threading.current_thread())
    
  def __send_msg(self, data: str) -> None:
    cod = "06"
    src = data[2:13]
    dst = data[15:26]
    timestamp = data[26:37]
    msg = data[37:]
    with sqlite3.connect(f"./{self.__db}") as db_conn:
      user = db_conn.execute("SELECT * FROM users WHERE uid = ?", (dst,)).fetchone()[0]
      group_members = db_conn.execute("SELECT * FROM group_members WHERE gid = ?", (dst,)).fetchall()
      if user is not None:
        if self.__clients.get(user) is None:
          return self.__save_msg(user, data)
        self.__clients[user].put((cod + src + dst + timestamp + msg))
      elif group_members is not None:
        for user in group_members:
          if self.__clients.get(user[1]) is None:
            self.__new_thread(self.__save_msg, user[1], data)
          self.__clients[user[1]].put((cod + src + dst + timestamp + msg))        
    return self.__del_thread(threading.current_thread())
  
  def __send_delivered_confirmation(self, src: str, dst: str):
    # src: quem leu a msg
    # dst: originador da msg
    msg = f"07{src}{int(time.time())}"
    with sqlite3.connect(f"./{self.__db}") as db_conn:
      user = db_conn.execute("SELECT * FROM users WHERE uid = ?", (dst,)).fetchone()[0]
      group_members = db_conn.execute("SELECT * FROM group_members WHERE gid = ?", (dst,)).fetchall()
      if user is not None:
        if self.__clients.get(user) is None:
          return self.__save_msg(user, msg)
        self.__clients[user].put(msg)
      elif group_members is not None:
        for user in group_members:
          if self.__clients.get(user[1]) is None:
            self.__new_thread(self.__save_msg, user[1], msg)
          self.__clients[user[1]].put(msg)        
    return self.__del_thread(threading.current_thread())
  
  def __send_readed_confirmation(self, src: str, data: str):
    cod = "09"
    pass
  
  def __connection_loop(self, user):
    self.__new_thread(self.__pending_msg, user)
    with user["conn"]:
      try:
        while (data := user["conn"].recv(256).decode()) != "":
          match data[:2]:
            case "05":
              self.__new_thread(self.__send_msg, data[2:])
            case "08":
              self.__new_thread(self.__send_readed_confirmation, user["id"], data[2:])
            case "10":
              self.__new_thread(self.__create_group, data[2:])
      except ConnectionError:
        pass
    return self.__del_thread(threading.current_thread())
  
  def __handle_connection(self, conn: socket.socket) -> None:
    try:
      while (data := conn.recv(256).decode()) != "":
        match data[:2]:
          case "01":
            self.__create_user(conn)
          case "03":
            user = self.__connect_user(conn, data[2:])
            if user is not None:
              return self.__connection_loop(user)
    except ConnectionError:
      pass
    conn.close()
    return self.__del_thread(threading.current_thread())
  
    while True:
      try:
        data = conn.recv(256).decode()
        match data[:2]:
          case "01":
            self.__new_thread(self.__create_user, conn)
          case "03":
            uid = self.__connect_user(conn, data[2:])
          case "05":
            self.__new_thread(self.__send_msg, conn, data)
          case "08":
            self.__new_thread(self.__send_readed_confirmation, conn, data)
          case "10":
            self.__new_thread(self.__create_group, conn, data[2:])
          case "":
            break
      except TimeoutError:
        continue
      except ConnectionError:
        break
    return self.__del_thread(threading.current_thread())
      
  def __listen(self):
    self.__socket.bind((self.__host, self.__port))
    self.__socket.listen()
    print(f"Running on: {self.__host}:{self.__port}")
    
  def __logging(self):
    while True:
      print(f"Active Threads: {threading.active_count()}\tActive Clients: {len(self.__clients)}", end = "\r")
      time.sleep(1)
      
  def __new_thread(self, func, *args, **kwargs):
    thread = threading.Thread(target = func, args = args, kwargs = kwargs)
    return thread.start()
  
  def __del_thread(self, thread: threading.Thread) -> None:
    return self.__finished_threads.put(thread)
      
  def __thread(self):
    while True:
      while not self.__finished_threads.empty():
        thread = self.__finished_threads.get()
        del thread
      time.sleep(1)
      
  def run(self) -> None:
    self.__init_db()
    self.__listen()
    self.__new_thread(self.__thread)
    self.__new_thread(self.__logging)
    while True:
      conn, _ = self.__socket.accept()
      self.__new_thread(self.__handle_connection, conn)