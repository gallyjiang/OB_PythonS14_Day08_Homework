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
                sec_list = []
                user_conf = []
                # with open(DB,'r') as f:
                f = open(DB,'r')
                for line in f.readlines():
                    name_password = (line.split(',')[0]) + (line.split(',')[1]) #用户账户密码
                    user = line.split(',')[0]#账户
                    quota = line.split(',')[2]#磁盘配额
                    profile = line.split(',')[3]#个人文件夹
                    # user_quota_profile = line.split(',')[0] + ','+line.split(',')[2] + ',' + line.split(',')[3] #用户配置文件，磁盘配置，个人家目录
                    md5_name_password = hashlib.md5(name_password.encode('utf-8')).hexdigest()
                    sec_list.append(md5_name_password)
                    user_quota_profile = {'user':user,'quota':quota,'profile':profile}
                    user_conf.append(user_quota_profile)
                f.close()
                if self.sec_name_password in sec_list:
                    self.request.send('1'.encode('utf-8'))
                    self.auth_user = self.request.recv(1024).decode()
                    for user_dict in user_conf:
                        if self.auth_user == user_dict['user']:
                            self.quota = user_dict['quota'] #获取登录名的磁盘配额
                            self.profile = user_dict['profile'] #获取登录名的个人文件夹


                    relative_path = r'\users\%s' % (self.profile)
                    profile_path = relative_path.strip('\n') #个人相对文件夹
                    full_path = r'%s\users\%s' % (DIR,self.profile)
                    full_profile_path = full_path.strip('\n') #个人绝对文件夹

                    relative_dir = [profile_path]
                    full_dir = [full_profile_path]

                     # 发送当前目录
                    # profile_path_dict = {'profile_path': profile_path}
                    # self.request.send(chr_dir[-1].encode('utf-8'))
                    while True:
                        self.request.send(relative_dir[-1].encode('utf-8'))
                        self.request.recv(1024) # 防止粘包
                        self.request.send(full_dir[-1].encode('utf-8'))
                        break_code = self.request.recv(1024).decode()
                        if break_code == '1':
                            continue
                        else:
                            self.file_dict = json.loads(self.request.recv(1024).decode())
                            self.action = self.file_dict['action']
                            if self.action == 'put':
                                self.file_size = self.file_dict['file_size']
                                self.put_filename = self.file_dict['filename']

                                size = 0
                                os.chdir(full_profile_path)
                                f = open(self.put_filename, 'wb')
                                int_file_size = self.file_size
                                int_quota = int(self.quota)
                                if int_file_size - int_quota <= 0:  # 文件大小小于磁盘配置
                                    int_quota -= int_file_size
                                    self.request.send('0'.encode('utf-8'))
                                    m1 = hashlib.md5()
                                    while size < int_file_size:
                                        if int_file_size - size > 1024:
                                            data_size = 1024
                                        else:
                                            data_size = (int_file_size - size)
                                        data = self.request.recv(data_size)
                                        m1.update(data) #md5加密
                                        f.write(data)
                                        size += len(data)
                                        # i = int((size / int_file_size)*100)
                                        # self.request.send(str(i).encode('utf-8'))

                                    else:
                                        md5_recv = self.request.recv(1024).decode()
                                        if md5_recv == m1.hexdigest(): #判断是否被修改
                                            self.request.send('file putting has done'.encode('utf-8'))
                                        else:
                                            os.remove(self.put_filename)
                                            self.request.send('file has changed and deleted'.encode('utf-8'))
                                        f.close()
                                else:
                                    self.request.send('1'.encode('utf-8'))
                                    continue
                            elif self.action == 'get':
                                self.get_filename = self.file_dict['filename']
                                if os.path.isfile(self.get_filename):
                                    self.request.send('0'.encode('utf-8'))
                                    file_size = os.stat(self.get_filename).st_size
                                    self.request.send(str(file_size).encode('utf-8'))  # 发送文件大小
                                    self.request.recv(1024)  # 接受应答,防止粘包
                                    m2 = hashlib.md5()
                                    f = open(self.get_filename, 'rb')
                                    for line in f:
                                        m2.update(line)
                                        self.request.send(line)
                                    self.request.send(m2.hexdigest().encode())
                                    f.close()
                                else:
                                    self.request.send('1'.encode('utf-8'))
                            elif self.action == 'cd':
                                a_path = self.request.recv(1024).decode()
                                path_list = os.listdir(full_dir[-1])
                                if a_path in path_list:
                                    if not os.path.isfile(a_path):
                                        a = '\\' + a_path
                                        profile_path += a
                                        full_profile_path += a
                                        full_dir.append(full_profile_path)
                                        relative_dir.append(profile_path)
                                        self.request.send(' '.encode('utf-8'))
                                    else:
                                        self.request.send(('%s不是文件路径'%a_path).encode('utf-8'))

                                else:
                                    self.request.send('拒绝访问'.encode('utf-8'))
                            elif self.action == 'dir':
                                dir_list = os.listdir(full_dir[-1])
                                self.request.send(json.dumps(dir_list).encode('utf-8'))
                            elif self.action == 'pwd':
                                self.request.send(relative_dir[-1].encode('utf-8'))
                            elif self.action == 'exit':
                                exit(0)

                else:
                    self.request.send('0'.encode('utf-8'))
                    continue

        except ConnectionResetError as e:
            print('error:',e)






if __name__ == '__main__':
    HOST,PORT = 'localhost',9903
    server = socketserver.ThreadingTCPServer((HOST,PORT),Mytcpserver)
    server.serve_forever()


