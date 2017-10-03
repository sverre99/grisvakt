#!/usr/bin/python
import os
import sys
import cherrypy

# hack to make sure we can load wsgi.py as a module in this class
sys.path.insert(0, os.path.dirname(__file__))

# virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
# virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
# 
# try:
#   #execfile(virtualenv, dict(__file__=virtualenv)) # for Python v2.7
#   #exec(compile(open(virtualenv, 'rb').read(), virtualenv, 'exec'), dict(__file__=virtualenv)) # for Python v3.3
#   # Multi-Line for Python v3.3:
#   exec_namespace = dict(__file__=virtualenv)
#   with open(virtualenv, 'rb') as exec_file:
#     file_contents = exec_file.read()
#   compiled_code = compile(file_contents, virtualenv, 'exec')
#   exec(compiled_code, exec_namespace)
# except IOError:
#   pass
# 

# Get the environment information we need to start the server
port = 8080
ip = '0.0.0.0'
environ = os.environ

### My app

from time import gmtime, strftime, localtime

# Import my view & model
from model_helpers import get_images, download_email, images_by_hour
from view_index import HTML_HEADER, HTML_FOOTER, html_navbar

myDir = environ['HOME']

class GrisVakt(object):

    def __init__(self):
        self.view_days = 3
    
    @cherrypy.expose
    def stats(self):
        images_by_hour(self.the_images)
        return str(self.the_images)
        
    @cherrypy.expose
    def days(self, view_days):
        try:
            self.view_days=int(view_days)
        except:
            self.view_days=3
        
        return '<html><head><meta HTTP-EQUIV="REFRESH" content="0; url=/"></head></html>'

    @cherrypy.expose
    def index(self):
        print "(index) Got view_days=%s"% self.view_days
        download_email(environ, '%s/assets/images'% myDir)
        update_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        print "update: %s"% update_time
        
        HTML_LIST=''
        
        self.the_images = get_images("%s/assets/images/"% myDir, self.view_days)
        
        if len(self.the_images) > 0:
            for image in self.the_images:
                HTML_LIST += '\r\
                <div class="container">\r\
                    <img src="/assets/images/%s">\r\
                </div>\r\
                <br>\r\
'% image["name"]
        else:
            HTML_LIST = '\r\
                <div class="container">\r\
                    <p class="lead">Inga bilder!</p>\r\
                </div>\r\
                <br>\r'

        HTML_BODY = '\r\
        \r\
    <div class="container">\r\
\r\
      <div class="starter-template">\r\
        <br>\r\
        <p class="lead">Hittade <strong>%s</strong> bilder, senast uppdaterad <strong>%s</strong></p>\r\
      </div>\r\
      \r\
    <div>\r\
        %s\r\
    </div>\r\
\r\
    </div><!-- /.container -->\r\
'% (len(self.the_images), update_time, HTML_LIST)

        return "%s%s%s%s"%(HTML_HEADER, html_navbar(self.view_days), HTML_BODY, HTML_FOOTER)

conf = {
    '/': {
        'tools.sessions.on': True,
        'tools.staticdir.root': myDir
    },
    '/assets': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': './assets'
    }
}

cherrypy.config.update(
    {
    'server.socket_host': ip,
    'server.socket_port': port
} )

if len(get_images("%s/assets/images/"% myDir)) == 0:
    print "No images...pulling all"
    download_email(environ,"%s/assets/images/"% myDir , 'ALL')
    
cherrypy.quickstart(GrisVakt(), '/', conf)

#server = wsgiserver.CherryPyWSGIServer((ip, port), wsgi.application, server_name=host_name)
#server.start()
