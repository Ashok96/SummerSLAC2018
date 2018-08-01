#!/usr/bin/python3
import socket
import requests
import os
import sys
import subprocess
import time

def backup_moxa(moxa, moxapass = 'moxa'):
     ''' Gets moxa configuration and returns config binary file: moxacfg'''
     try:
         print('Retrieving configuration from %s', moxa)
         script_dir = os.path.dirname(__file__)
         s          = requests.Session()
         login_page = s.get("http://%s/" % moxa)
         ltext      = login_page.text
         chpattern  = "name=FakeChallenge value="
         chstart    = ltext.index(chpattern) + len(chpattern)
         chend      = ltext.index(">", chstart)
         challenge  = ltext[chstart:chend]
         #md5pwd     = subprocess.check_output(["node", "moxapwd.js", moxapass, challenge])
         md5pwd     = subprocess.check_output(["node", "%s/moxapwd.js" % script_dir, moxapass, challenge])
         post_data = {
         'Username'      : 'admin',
         'Password'      : '',
         'MD5Password'   : md5pwd,
         'FakeChallenge' : challenge,
         'Submit.x'      : '51',
         'Submit.y'      : '17',
         'Submit'        : 'Login'}
         m= s.post("http://%s/" % moxa, post_data)
         #print(m.text)

         # Find the correct MOXA model:
         main = s.get("http://%s/main.htm" % moxa)
        #print('main')
        #print(main.text)
         model = main.text.split('Model name</TD><TD')[1].split('column_text_no_bg>')[1].split('</TD>')[0].replace(" ", " ")
         print('---- %-20s Model %s' % (moxa, model))
         serial = main.text.split('Serial No.</TD><TD')[1].split('column_text_no_bg>')[1].split('</TD>')[0].replace(" ", " ")
         print('/nThe serial number is \n' + serial)
         config_resp = s.get("http://%s/ConfExp.htm" % moxa)
         #print("\nThe text is\n" + config_resp.text)
         cfg_text    = config_resp.text

         if 'NP6610' in model:
             moxacfg = s.post("http://%s/Config.txt" % moxa, data = { "Submit": "Download"  })
         elif 'NP6650' in model:
             cfg_pattern = "name=csrf_token value="
             crb_start   = cfg_text.index(cfg_pattern) + len(cfg_pattern)
             crb_end     = cfg_text.index(">", crb_start)
             crb         = cfg_text[crb_start:crb_end]
             moxacfg = s.post("http://%s/Config.txt" % moxa, data = {"Submit": "Download", "csrf_token" : crb  })
             print("/nDownloaded/n")
	     
         else:
             print ('MOXA model to be implemented..')
             return False

     except socket.error as err:
         print('Failure connecting to %s: %s' % (moxa, err))
         print('Skipping file transfer for %s' % moxa)
         return False

     except EOFError as eof_err:
         print('Connection to %s closed unexpectedly: %s'% (moxa, eof_err))
         print('Skipping file tra  /\nsfer for %s'% moxa)
         return False

     print("/nNow it is")
    # return  moxacfg.content

     filename= time.strftime("%Y%m%d-%H%M%S")
     f = open('moxa-%s-%s'% (serial,filename), 'wb+')
     f.write(moxacfg.content)
#backup_moxa('192.168.127.254', moxapass ='moxa')
