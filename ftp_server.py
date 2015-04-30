#
#		writed by caramel 
#

import SocketServer
import os
import sys
import stat
import time
import MySQLdb

#-- send error --

def send_err(sock_handler,err_info):
#{
	try:
	#{
		sock_handler.request.sendall(err_info)
	#}
	except Exception,e:
	#{
		print e
	#}
#}


#-- login module --

def login(username,password):
#{

	try:
	#{
		login_str = '''select password from user where username = "%s" and password = "%s"''' % (username,password)
		mycursor.execute(login_str)
		mydata = mycursor.fetchall()
		
		if(mydata):
			print username,'has logined'
			return(1)
		else:
			print username,'logined error'
			return(0)
	#}	
	except Exception,e:
	#{
		print e
		return(0)
	#}
		
#}


#-- user register --

def register(username,password):
#{
	
	try:
	#{
		select_str = '''select username from user where username = "%s"''' %(username)
		mycursor.execute(select_str)
		sel_data = mycursor.fetchall()
		if(sel_data):
			return(0)
			
		reg_str = '''insert into user(username,password)values("%s","%s")''' %(username,password)
		n = mycursor.execute(reg_str)
		mysqlconn.commit()
		print n
		if(n):
		#{
			print username,'has registed'
			return(1)
		#}
		else:
		#{
			print username,'registed failure'
		#}
	#}	
	except Exception,e:
	#{
		print e
		return(0)
	#}

#}


#-- list process --

# data struct
# __________________________
# | R |    request data     |
# ==========================
# | D |    transport data   |
# ==========================
# | A |    acking data      |
# --------------------------
#  ______ request data struct _______
# |                                  |
# |   option   |        R or L       |
# |----------------------------------|
# |  username  |        value        |
# |----------------------------------|
# |  password  |        value        |
# |__________________________________|
#  ______ request data struct _______
# |                                  |
# |   option   |         ls          |
# |----------------------------------|
# |    cmd     |        value        |
# |__________________________________|
#  ______ request data struct _______
# |                                  |
# |   option   |          S          |
# |----------------------------------|
# |  filename  |        value        |
# |__________________________________|
#  ______ request data struct _______
# |                                  |
# |   option   |        begin        |
# |----------------------------------|
# |  filename  |        value        |
# |__________________________________|
#  _____ transport data struct ______
# |                                  |
# |   option   |        value        |
# |----------------------------------|
# |   filename |        value        |
# |----------------------------------|
# |   path     |        value        |
# |__________________________________|
#  _______ acking data struct _______
# |                                  |
# |   option   |        value        |
# |----------------------------------|
# |   result   |        value        |
# |__________________________________|

def list_process(data_list):
#{

	ret_data = {}
	print data_list
	for i in range(1,len(data_list),2):
	#{
		ret_data[data_list[i]] = data_list[i + 1]
	#}

	return(ret_data)

#}


#-- ret_value --

def ret_value(sock_handler,r_value):
#{
	value_for_return = "A,option,A,result,"+str(r_value)
	sock_handler.request.sendall(value_for_return)
#}


#-- is exists file --

def is_exist_file(filename):
#{
	if(filename):
	#{
		isExists = os.path.exists(filename)
		return(1)
	#}
	else:
	#{
		return(0)
	#}
#}


#-- cmd list --

def cmd_list(sock_handler,cmd_string):
#{
	list_string = os.popen(cmd_string)
	if(list_string):
	#{
		send_string = list_string.read()
	#}
	else:
	#{
		send_string = 'no items'
	#}
	print send_string
	sock_handler.request.sendall(send_string)
#}


#-- get file from client --

def get_file_from_client(sock_handler,filename):
#{
	if(filename):
	#{
		sock_handler.request.sendall('begin')
		with open(filename,'wb') as t_file_fd:
		#{	
			while True:
			#
				rcv_buff = sock_handler.request.recv(65535)
				if(rcv_buff == 'EOF'):
				#{
					print 'put < %s > success' %(filename)
					break;
				#}
				t_file_fd.write(rcv_buff)
			#}
		#}
	#}
	else:
	#{
		sock_handler.request.sendall('null')
	#}
#}


#-- begin transport file --

def send_file_to_client(sock_handler,filename):
#{
	if(filename):
	#{
		with open(filename,'rb') as t_file_fd:
		#{
			read_buff = t_file_fd.read()
			sock_handler.request.sendall(read_buff)
		#}
		time.sleep(1)
		sock_handler.request.sendall('EOF')
		print 'send ' + filename 
	#}
	else:
	#{
		sock_handler.request.sendall('null')
	#}
#}


#-- request_func --

def request_func(sock_handler,dict_data):
#{

	if(dict_data['option'] == 'R'):
	#{
		ret_value(sock_handler,register(dict_data['username'],dict_data['password']))
	#}	
	elif(dict_data['option'] == 'L'):
	#{	
		ret_value(sock_handler,login(dict_data['username'],dict_data['password']))
	#}	
	elif(dict_data['option'] == 'ls'):
	#{
		cmd_list(sock_handler,dict_data['cmd'])
	#}
	elif(dict_data['option'] == 'S'):
	#{
		ret_value(sock_handler,is_exist_file(dict_data['filename']))
	#}
	elif(dict_data['option'] == 'begin'):
	#{
		send_file_to_client(sock_handler,dict_data['filename'])
	#}
	elif(dict_data['option'] == 'put'):
	#{
		get_file_from_client(sock_handler,dict_data['filename'])
	#}
	else:
	#
		send_err(sock_handler,'error option')
		return(0)
	#}

#}


#-- SocketServer class --

class MyTCPHandler(SocketServer.BaseRequestHandler):
#{

	def handle(self):
	#{	
		while True:
		#{
			self.data = self.request.recv(65535).strip()
			if not self.data:
				break

			print self.client_address			
			
			data_list = self.data.split(',')
			dict_data = list_process(data_list)
			if(data_list[0] == 'R'):
				request_func(self,dict_data)
			elif(data_list[0] == 'D'):
				transport_func(self,dict_data)
			elif(data_list[0] == 'A'):
				break
			else:
				return(0)
		#}
	#}	

#}


#-- listening_func --

def listening_func():
#{
	
	print 'waiting a connecting'
	ADDR,PORT = '',50001
	sockfd = SocketServer.ThreadingTCPServer((ADDR,PORT),MyTCPHandler)
	sockfd.serve_forever()

#}



#-- main function --
# begin main()

if __name__ == '__main__':
#{
	#judge ftp path
	isExists = os.path.exists('/tmp/ftp')
	if(not isExists):
	#{
		os.makedirs('/tmp/ftp')
		os.chmod('/tmp/ftp',stat.S_IRWXU + stat.S_IRWXG + stat.S_IRWXO)
	#}
	os.chdir('/tmp/ftp')
	
	#create welcome file if not exists
	isExists = os.path.exists('/tmp/ftp/Welcome')
	if(not isExists):
	#{
		with open('/tmp/ftp/Welcome','wa'):
			os.utime('/tmp/ftp/Welcome',None)	
	#}

	#A global varible for database cursor
	#-- connect mysql --
	try:
	#{
		mysqlconn = MySQLdb.connect(host='localhost',user='root',passwd='root')
			
		mycursor = mysqlconn.cursor()
		# create database
		mycursor.execute('create database if not exists moya')
		# select database moya
		mysqlconn.select_db('moya')
		# create table
		mycursor.execute('create table if not exists user(id int not null primary key auto_increment,username varchar(20),password varchar(30))')
		
		print 'mysql starting'
	#}	
	except Exception,e:
	#{
		print e
		sys.exit(0)
	#}

	#listening
	listening_func()
	
#}
# end main()
