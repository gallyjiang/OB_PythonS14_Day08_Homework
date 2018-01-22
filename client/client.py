__author__ = 'gally'
import socket,hashlib,os,json,time
class Ftpclient(object):
    def __init__(self):
        self.client = socket.socket()
    def connect(self,ip,port):
        self.client.connect((ip,port))
    def command_list(self):
        cmd =   '''用法:
        get [filename] 下载文件
        put [filename] 上传文件
        cd [path] 切换路劲
        dir 列出文件和目录
        exit 退出
        help 帮助文档
        '''
        print(cmd)
    def login(self,username,password):
        name_password = username + password
        sec_name_password = hashlib.md5(name_password.encode('utf-8')).hexdigest()
        self.client.send(sec_name_password.encode('utf-8'))
        login_code = self.client.recv(1024).decode()
        if  login_code == '1':
            self.client.send(username.encode('utf-8'))
            self.interactive(self)

        else:
            print('账号或密码错误，请重试！')
            self.main_menu(self)



    def main_menu(self,*args):
        # flag = True
        print('''********GALLY'S FTP********
        WELCOME      
        VERSION 0.0.1
        ''')
        username = input('USERNAME:').strip()
        password = input('PASSWORD:').strip()
        self.login(username,password)

    def interactive(self, *args):
        print('********WELCOME********')
        while True:
            msg = input('>>:').strip()
            if len(msg) == 0:continue
            cmd = msg.split()[0]
            if hasattr(self,cmd):
                func = getattr(self,cmd)
                func(msg)
            else:
                self.command_list()

    def put(self,*args):

        user_dict = {

        }
        cmd_split = args[0].split()
        if len(cmd_split) > 1:
            filename = cmd_split[1]
            if os.path.isfile(filename):
                file_size = os.stat(filename).st_size
                self.client.send(str(file_size).encode('utf-8'))

            else:
                print('文件不存在，请重新输入！')

        else:
            print('语法错误！')
            time.sleep(3)
            self.command_list()
    def get(self):
        print('get haha')
    def cd(self):
        pass
    def dir(self,*args):
        pass
    def exit(self,*args):
        # if len(args) == 1:
        #     return 1
        pass
    def help(self,*args):
        # if len(args) == 1:
        self.command_list()
            # pass



client = Ftpclient()
client.connect('localhost',9908)
client.main_menu()