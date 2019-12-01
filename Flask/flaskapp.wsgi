#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,'/var/www/356_final_project/Flask')

from Flask import app as application
application.secret_key= "hi_julianne1234"