__author__ = 'gally'
import socket,hashlib,os,json,time,sys,progressbar
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
        pwd 显示当前目录
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
            current_directory = self.client.recv(1024).decode().strip()
            self.client.send(b'asdf') #防止粘包
            full_directory = self.client.recv(1024).decode().strip()
            msg = input('%s:'%current_directory).strip()
            if len(msg) == 0:
                continue
            cmd = msg.split()[0]
            if hasattr(self,cmd):
                func = getattr(self,cmd)
                func(msg)
            else:
                self.command_list()
                self.client.send('1'.encode('utf-8')) #结束循环

    def put(self,*args):
        cmd_split = args[0].split()
        if len(cmd_split) > 1:
            filename = cmd_split[1]
            if os.path.isfile(filename):
                self.client.send('0'.encode('utf-8'))
                file_size = os.stat(filename).st_size
                file_dict = json.dumps({'action': 'put', 'filename': filename, 'file_size': file_size})
                self.client.send(file_dict.encode('utf-8'))
                return_code = self.client.recv(1024).decode()
                if return_code == '0':
                    f = open(filename,'rb')
                    i = 0
                    for line in f:
                        self.client.send(line) #按行发送文件内容
                        # a = len(line)/file_size
                        # i += a
                        # rate = int(i*100)
                        # s1 = '\r[%s%s]%d%%'%('*'*rate,' '*(100-rate),rate)
                        # sys.stdout.write(s1)
                        # sys.stdout.flush()
                    f.close()
                    print('\n' + self.client.recv(1024).decode()) #接受完成信号
                elif return_code == '1':
                    print('超出文件大小')

            else:
                print('文件不存在，请重新输入！')
                self.client.send('1'.encode('utf-8'))

        else:
            print('语法错误！')
            time.sleep(0.5)
            self.command_list()
            self.client.send('1'.encode('utf-8'))

    def get(self,*args):
        cmd_split = args[0].split()
        if len(cmd_split) > 1:
            self.client.send('0'.encode('utf-8'))
            filename = cmd_split[1]
            file_dict = json.dumps({'action':'get','filename':filename})
            self.client.send(file_dict.encode('utf-8'))
            return_code = self.client.recv(1024).decode()
            if return_code == '1':
                print('文件不存在！')

            else:
                file_size = self.client.recv(1024).decode()
                totel_file_size = int(file_size)
                size = 0
                self.client.send(b'1234')

                f = open(filename,'wb')
                while size < totel_file_size:
                    if totel_file_size - size > 1024:
                        data_size = 1024
                    else:
                        data_size = (totel_file_size - size)
                    data = self.client.recv(data_size)
                    f.write(data)
                    size += len(data)
                else:
                    print('file getting done')
                    f.close()

        else:
            print('语法错误！')
            time.sleep(0.5)
            self.command_list()
            self.client.send('1'.encode('utf-8'))

    def cd(self,*args):
        cmd_split = args[0].split()
        if len(cmd_split) > 1:
            self.client.send('0'.encode('utf-8'))
            file_dict = json.dumps({'action': 'cd'})
            self.client.send(file_dict.encode('utf-8'))
            path = cmd_split[1]
            self.client.send(path.encode('utf-8'))
            print(self.client.recv(1024).decode())
            # error_code = self.client.recv(1024)
            # if error_code == '2':
            #     print('拒绝访问')
            # else:
            #     pass
        else:
            print('语法错误！')
            time.sleep(0.5)
            self.command_list()

    def dir(self,*args):
        cmd_split = args[0].split()
        if len(cmd_split) == 1:
            file_dict = json.dumps({'action': 'cd'})
            self.client.send(file_dict.encode('utf-8'))

        else:
            print('语法错误')
            time.sleep(0.5)
            self.command_list()


    def pwd(self,*args):
        cmd_split = args[0].split()
        if len(cmd_split) == 1:
            self.client.send('0'.encode('utf-8'))
            file_dict = json.dumps({'action':'pwd'})
            self.client.send(file_dict.encode('utf-8'))
            pwd_dir = self.client.recv(1024).decode()
            print(pwd_dir)
        else:
            print('语法错误')
            time.sleep(0.5)
            self.command_list()
            self.client.send('1'.encode('utf-8'))

    def exit(self,*args):
        # if len(args) == 1:
        #     return 1
        pass
    def help(self,*args):
        # if len(args) == 1:
        self.command_list()
            # pass



client = Ftpclient()
client.connect('localhost',9905)
client.main_menu()