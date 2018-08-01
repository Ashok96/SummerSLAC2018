#!/usr/bin/python3
import socket
import telnetlib
import time

DEBUG=1
ESC='\x1b'
CR='\r'
DN="\x1b[B"
UP="\x1b[A"
QUIT='\q'
YES='y'
NO='n'
EXIT='e'
AD='a'
UR='u'
TB='\t'
user1='harry'
user2='moxa1'
pass1 ='moxa'
pass2 ='moxa'
RS ='r'

class TelnetHelper():
     def __init__(self, user='admin', pw='moxa', port=23, cfg_cmd=None, 
moxa_type=None, timeout=5, verbose=False):
         self.user = user
         self.pw = pw
         self.port = port
         self.timeout = timeout
         self.cfg_cmd = cfg_cmd
         self.moxa_type = moxa_type
         self.tn = telnetlib.Telnet()
         self.verbose = verbose
         self.page =''

     def connect(self, host='192.168.127.254'):
         self.host = host
         try:
             if self.verbose: print ('>>>  Connecting to %s' %  host)
             self.tn.open(host, self.port, self.timeout)
         except socket.error as err:
             print ('Failure connecting to %s: %s' % (host, err))
             return 1
         except EOFError as eof_err:
             print ('Connection to %s closed unexpectedly: %s' % (host, 
eof_err))
             return 1
         except IOError as io_err:
             print ('Failure writing %s config to disk: %s' % (host, io_err))
             return 1
         finally:
             if self.verbose: print ('>>>  Successful Telnet connection to %s' %  host)

     def login(self):
         self.cmd_list = [
             ('login: ', self.user + CR),
             ('password: ', self.pw + CR),
         ]

         cmds = [x[1] for x in self.cmd_list]
         for cmd in cmds:
             self.write(cmd)
             self.readpage(showwalkup=True)

     def set_change_pw(self):
         
         self.readpage(showwalkup=True)
         self.write('%s%s' % (ESC, NO))
         self.write(NO)
         self.readpage(showwalkup=True)

        
     def network(self):
         if self.verbose: print (">>>  Entering in Network Menu...")
         self.write('%s%s' % (NO, CR))
         self.readpage(showwalkup=True)
         
         


     def basic(self):
         if self.verbose: print (">>>  Entering in Basic Configuration...")
         self.write('b%s' % CR)
         self.readpage(showwalkup=True)

   
     def dhcp_setup(self):
         
         if self.verbose: print (">>>  Setting up IP source in %s" %  self.host)
         
         # SELECT IP SOURCE LIST
         # Press DOWN Arrow, ENTER to accept
         # ESCAPE to Menu BASIC
         # QUIT Menu BASIC, ENTER to accept,
         # Select 'Y' to SAVE in Flash,
         # Select EXIT From Main Menu, ENTER to accept
         self.write('%s' % CR )
         self.readline()
         if b'Static' in self.page:
             print('\n>>>>>Converting into DHCP<<<<<\n')
             self.write('%s%s%s%s%s%s%s%s' % ( DN, CR, ESC, ESC,YES,CR,CR,CR))
         elif b'DHCP' in self.page:
             print('\n>>>>>Converting into Static<<<<<<<<<\n')
             self.write('%s%s%s%s%s%s%s%s' % (UP, CR, ESC, ESC, YES, CR, CR, CR))
         self.readpage(showwalkup=True)   

     def set_console(self):
         self.write('%s' % CR) # SELECT VT100

     def write(self, msg, showwalkup=True):
         self.tn.write(msg.encode('ascii'))
         time.sleep(0.5)
         


     def close_connection(self):
         self.tn.close()

     def readpage(self, showwalkup=False):
         try:
             self.page = self.tn.read_very_eager()
             if self.verbose:
                 print (80*'=')
                 print (repr(self.page))
                 print (80*'=')
         except EOFError as e:
             print ("Connection closed: %s" % e)
             sys.exit(1)
         if showwalkup:
             if b'user name' in self.page:
                 print ("Login Page")
             elif b'Confirm' in self.page:
                 print ("Change password Page")
             elif b'Overview' in self.page:
                 print ("Network Page")
             elif b'IPv4 configuration' in self.page:
                 print ("Basic Network Configuration Page")
             elif b'gateway' in self.page:
                 print ("IPv4 configuration Page")
        
             elif b'Account' in self.page:
                 print('Account page')
             elif b'Notify' in self.page:
                 print('User Page')
             elif b'Active' in self.page:
                 print('Add account page')
            

     def ip_source_verify(self):
         
         self.write('%s%s%s%s%s' %(ESC, ESC, ESC, QUIT,YES))
         self.readline()
         
         if 'Static' in (repr(self.line)):
             print('\n>>>>>Static confirmed<<<<<<\n')
         elif 'DHCP' in (repr(self.line)):
             print ('\n>>>>>DHCP confirmed<<<<<\n')
         else:
             print('None')
         self.readpage(showwalkup=True)

     def add_users(self):
          print("ENtering into add user page")
          time.sleep(3)
          self.write('%s%s%s%s%s%s%s%s%s%s' %(AD, CR, CR, UR, CR,DN,CR,DN,CR,TB))
          self.write('%s%s%s%s%s%s%s%s' %(user1,TB,pass1,TB,CR,DN,CR,TB))
          self.write('%s%s%s%s%s%s%s%s%s%s%s' %(CR,DN,CR,TB,user2,TB,pass2,TB, CR,UP,CR))
          self.readpage(showwalkup=True)
          print('\n>>>>>>Two users are added>>>>>\n')
                
          
     def save_users(self):
          print(">>>>>>>>>>Saving the user profile after creating")
          self.write(ESC)
          self.write(ESC)
          self.write(YES)
          time.sleep(3)
          self.write(QUIT)
          self.write(CR)
          self.readpage(showwalkup=True)
          print('\n <<<<users added and saved>>>>>\n')
         
                
     def restart(self):
          print(">>>>>>>>>Restarting the server with new config and added user")
          self.write(RS)
          self.write(CR)
          self.write(CR)
          self.write(CR)
          self.readpage(showwalkup=True)
          
     def readline(self):
         try:
             self.line = self.tn.read_eager()
             print (80*'=')
             print (repr(self.line))
             print (80*'=')
         except EOFError as e:
            print ("Connection closed: %s" % e)
            sys.exit(1)
         
def main():
     moxa = TelnetHelper()
     moxa.connect()
     moxa.set_console()
     moxa.login()
     moxa.set_change_pw()
     moxa.network()
     moxa.basic()
     moxa.dhcp_setup()
     moxa.ip_source_verify()
     moxa.add_users()
     moxa.save_users()
     moxa.restart()
     moxa.close_connection()
     


if __name__ == '__main__':
     main()




