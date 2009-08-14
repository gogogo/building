#!/usr/bin/python

# Remote console

import code
import getpass
import sys
import os
from optparse import make_option, OptionParser

sys.path.append(os.path.abspath(os.path.dirname(__file__) + "./gogogo-hk"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "./gogogo-hk/common/.google_appengine/"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "./gogogo-hk/common/google_appengine/")) # For win32
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "./gogogo-hk/common/appenginepatch"))
sys.path.append(os.path.abspath(os.path.dirname(__file__) + "./gogogo-hk/common"))
print sys.path

from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.ext import db
debug = False

option_list = [
	make_option("-d", "--debug",
				action="store_true",  dest="debug",default=False),
	make_option("-u", "--url",
				action="store", type="string", dest="url",default="localhost:8000"),					
]

parser = OptionParser(option_list = option_list,usage="usage: console.py app_id")
(options , args ) = parser.parse_args()

def auth_func():
	if options.debug == False:
		return raw_input('Username:'), getpass.getpass('Password:')
	return "test@example.com",""

if len(args) != 1:
  parser.print_help()
  sys.exit(0)
  
app_id = args[0]
if options.debug:
  host = options.url
else:
  host = '%s.appspot.com' % app_id

remote_api_stub.ConfigureRemoteDatastore(app_id, '/remote_api', auth_func, host)

code.interact('App Engine interactive console for %s at %s' % (app_id,host), None, locals())

### Example code 

# import main # Ignore the error

# from django.conf import settings
# from gogogo.models import Agency
# q = Agency.all()
# [a for a in q]


