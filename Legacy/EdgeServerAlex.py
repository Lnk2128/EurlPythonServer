#!/usr/bin/env python

# Copyright Jon Berg , turtlemeat.com
# Modified by nikomu @ code.google.com     
#https://code.google.com/p/python-simple-fileserver/#Code_Snippet
import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

from pprint import pprint 
from urlparse import urlparse, parse_qsl

import os # os. path

CWD = os.path.abspath('.')
## print CWD

# PORT = 8080     
UPLOAD_PAGE = 'upload.html' # must contain a valid link with address and port of the server     s


def make_index( relpath ):     

    abspath = os.path.abspath(relpath) # ; print abspath
    flist = os.listdir( abspath ) # ; print flist
    
    rellist = []
    for fname in flist :     
        relname = os.path.join(relpath, fname)
        rellist.append(relname)
    
    # print rellist
    inslist = []
    for r in rellist :     
        inslist.append( '<a href="%s">%s</a><br>' % (r,r) )
    
    # print inslist
    
    page_tpl = "<html><head></head><body>%s</body></html>"     
    
    ret = page_tpl % ( '\n'.join(inslist) , )
    
    return ret


# -----------------------------------------------------------------------
import khanChecker # THIS IS RESPONSIBLE FOR THE FIRST STEP (KHAN AUTHENICATION)


def make_eURLfile(self):
    self.send_response(200)
    #self.send_header('Content-type',    'text/html')
    #self.wfile.write('Your path is ' + self.path ) #We will need to send the user to a page with the URL rather then make them download something if they are using/coming from JIRA
    #self.wfile.write(self.path)#Simple situation first is they manually input everything
    print '========'
    print 'in make_eURLfile'
    print 'self.path', self.path
    
    print('Here is parsed information from self.path')
    
    print
    print('\nAnd here is query information')
    parsedPath = urlparse(self.path)
    print 'parsedPath=', parsedPath
    print
    print "Here is the query parsed from the path as a dict (object).  This is what we want!"
    print
    parsedQSLdict = dict(  parse_qsl(parsedPath.query) )
    print 'you can manipulate it before returning it if you want'
    parsedQSLdict['verNum'] = 0.2 #When this is updated be sure to change it here and in the edgeTable code
    #parsedQSLdict['help'] = Some url that leads to something that explains what this file is (Maybe "Click this link to learn more about the .erul file type: " + link
    print 'parsedQSLdict----------------'
    pprint( parsedQSLdict )
    if 'cName' in parsedQSLdict:
        self.send_header('Content-type', 'application/octet-stream')
        self.send_header('Content-Disposition', 'attachment; filename="myfile.eUrl')
        self.end_headers()

        self.wfile.write(parsedQSLdict) #write to the .eurl file in a JSON format
        print 'parsedQSLdict =', parsedQSLdict
        print
        print 'you can manipulate it before returning it if you want'
        #parsedQSLdict['GUID'] = 'vvvvvvvvvv'
        print 'parsedQSL =', parsedQSLdict
        print
        print 20 * '='
        print('Here is more information available from self, nicely formatted.' )
        pprint(self.__dict__) 
        print
        print("Trying to get the referer url")
        #print self.request.referer
        #print dir(self.request)
        #print os.environ['HTTP_REFERER']
        #print(self.request.info())
        #print(self.request.META.get('HTTP_REFERER'))
        #print self.getheaders
        #print dir(self)
        #pprint(self.responses)
        print self.headers.getheader('referer')
        print
        print "self['client_address'] above should reveal the Jira server, maybe the page..."
        
        return
    else: #missing cName
        self.send_header('Content-type',    'text/html')
        self.end_headers()
        #self.wfile.write('parsedQSL =' + repr(parsedQSLdict))

        self.wfile.write('If you are reading this in the browser, you need to supply a canvas name.')
        
        self.wfile.write("""
         <FORM action="http://localhost:8080/eurl?" 
               enctype="multipart/form-data"
               method="get">
            <P>""")
            
        for key,value in parsedQSLdict.items():
            self.wfile.write('<INPUT type="hidden" name="' + key + '"  value="' + str(value) + '">\n')
            self.wfile.write(key + ': ' + str(value) + '<BR>\n')

        self.wfile.write("""                
            Canvas Name?: <INPUT type="text" name="cName"  value=""><BR>
        """)
        self.wfile.write("""
            <INPUT type="submit" value="Send"> <INPUT type="reset">
           </P>
         </FORM>
         """)



class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        #print self.path
        try:

            if self.path == '/' :     
                page = make_index( '.' )
                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.end_headers()
                self.wfile.write(linkify(MSG))
                self.wfile.write('<p/><hr>Here is a directory:<p>')
                self.wfile.write(page)
                return     


            if ( self.path.endswith(".html") or self.path.endswith(".txt") ) :
                ## print curdir + sep + self.path
                f = open(curdir + sep + self.path)
                #note that this potentially makes every file on your computer readable by the internet
                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
                return
                
            if self.path.endswith(".esp"):   #our dynamic content
                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.end_headers()
                self.wfile.write("hey, today is the" + str(time.localtime()[7]))
                self.wfile.write(" day in the year " + str(time.localtime()[0]))
                return
                
            if self.path.startswith("/eurl"):   #ALEX our dynamic content
                make_eURLfile(self)

            else:
                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.end_headers()
                self.wfile.write("SORRY:  I can't handle  " + self.path )
                return

            return # be sure not to fall into "except:" clause ?       
        except IOError as e :  
            # debug     
            print e
            self.send_error(404,'File Not Found: %s' % self.path)


MSG="""EDGESERVER
If the URL starts with /eurl, and the canvas name has been supplied, we'll deliver an eUrl file.
If the canvas name is missing, we'll ask you to supply it.
<hr>
TRY: http://localhost:8080/eurl?edgeIp=129.21.142.218&jDomain=http://129.21.142.226:8080&cName=ATable222
vs : http://localhost:8080/eurl?edgeIp=129.21.142.218&jDomain=http://129.21.142.226:8080&

"""

def linkify(MSG):
    MSG =MSG.replace('\n',' <br/>\n')
    fixedWords=[]
    for word in MSG.split():
        if 'http:' in word:
            print 'WORD', word
            fixedWord = '<a href="' + word + '">\n' + word + '</a>\n'
        else:
            fixedWord = word
        fixedWords.append(fixedWord)
    return ' '.join(fixedWords).replace('<br/>','<br/>\n')
    

def main():
    try:
        server = HTTPServer(('', 8080), MyHandler)
        print 40*'\n'
        print 'STARTED SERVER\n\n\n'
        print MSG
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    #khanChecker.setup()  #We don't need no stinking Khan now but if we want oauth, we might use this
    main()
