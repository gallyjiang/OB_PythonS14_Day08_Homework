__author__ = 'gally'
import socketserver,hashlib,os,json,sys
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
from conf.setting import *
class Mytcpserver(socketserver.BaseRequestHandler):
    def handle(self):
        try:
            while True:
                self.sec_name_password = self.request.recv(1024).decode()
                with open(DB,'r') as f:
                    sec_list = []
                    user_conf = []
                    for line in f.readlines():
                        name_password = (line.split(',')[0]) + (line.split(',')[1])
                        md5_name_password = hashlib.md5(name_password.encode('utf-8')).hexdigest()
                        sec_list.append(md5_name_password)

                    if self.sec_name_password in sec_list:
                        self.request.send('1'.encode('utf-8'))
                    else:
                        self.request.send('0'.encode('utf-8'))
                    self.auth_user = self.request.recv(1024).decode()


                self.file_size = self.request.recv(1024).decode()



        except ConnectionResetError as e:
            print('error:',e)


if __name__ == '__main__':
    HOST,PORT = 'localhost',9908
    server = socketserver.ThreadingTCPServer((HOST,PORT),Mytcpserver)
    server.serve_forever()


