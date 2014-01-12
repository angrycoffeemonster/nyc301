import sys, os

log = file('/home/jproberts00/311asp.com/passengerwsgi.log', 'a')
print >>log, "Running %s" % (sys.executable)

DEBUG   = True
ROOT    = os.path.dirname(os.path.abspath(__file__))
INTERP  = '/home/jproberts00/311asp.com/venv/bin/python'

sys.path.insert(1,ROOT)
if sys.executable != INTERP:
	print >>log, "Detected wrong interpreter location, swapping to %s" % (INTERP)
	#swapping interpreters will not flush any files
	log.flush()
	log.close()
	
	os.execl(INTERP, INTERP, *sys.argv)

from app import app as application
from app.config import AppConfig
from app.controllers import * # register the controllers with Flask

config = AppConfig() # get access to configuration information
