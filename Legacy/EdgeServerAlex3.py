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
    """print('\Here is query information')
    print 'self.path', self.path
    print 'parsedPath=', parsedPath
    print
    print "Here is the query parsed from the path as a dict (object).  This is what we want!"
    print
    """
    parsedPath = urlparse(self.path)
    parsedQSLdict = dict(  parse_qsl(parsedPath.query) )

    parsedQSLdict['verNum'] = 0.2 #When this is updated be sure to change it here and in the edgeTable code
    #parsedQSLdict['help'] = Some url that leads to something that explains what this file is (Maybe "Click this link to learn more about the .erul file type: " + link

    #print 'parsedQSLdict----------------'
    #pprint( parsedQSLdict )
    
    if 'jDomain' in parsedQSLdict and 'jID' not in parsedQSLdict:
        REFERER = self.headers.getheader('referer')
        REFERER
        if REFERER.endswith('/'):
            REFERER=REFERER[:-1]
        issue = REFERER.split('/')[-1]
        parsedQSLdict['jID'] = issue  
             
        
    
    if ('cName' in parsedQSLdict) and ('DOWNLOAD' not in parsedQSLdict) : #deliver the file
        self.send_header('Content-type', 'application/octet-stream')
        self.send_header('Content-Disposition', 'attachment; filename='+ parsedQSLdict['cName'] + '.eUrl')
        self.end_headers()

        self.wfile.write(parsedQSLdict) #write to the .eurl file in a JSON format
        print 'parsedQSLdict =', parsedQSLdict
        print
        print 'you can manipulate it before returning it if you want'
        #parsedQSLdict['GUID'] = 'vvvvvvvvvv'
        print 'parsedQSL =', parsedQSLdict
        return
        
    else: #missing cName.  
        DOWNLOAD = ('DOWNLOAD' in parsedQSLdict) and ('cName' in parsedQSLdict)
        
        self.send_header('Content-type',    'text/html')
        self.end_headers()
        #self.wfile.write('parsedQSL =' + repr(parsedQSLdict))
        if not DOWNLOAD:
            self.wfile.write('If you are reading this in the browser, you need to supply a canvas name.')
            if not 'edgeIp' in parsedQSLdict:
                self.wfile.write("<h2>Because you haven't supplied a server name, this will only work locally (if that).</h2>")
                
        else:
            self.wfile.write("<i>We're good to go!</i>")
        
        self.wfile.write("""
         <FORM action="/eurl?" 
               enctype="multipart/form-data"
               method="get">
            <P>""")
        
        if not DOWNLOAD: #we're missing cname; put it in
            self.wfile.write('<INPUT type="hidden" name="DOWNLOAD" value="True">\n')               
        else: #take out the need-to-DOWNLOAD flag
            parsedQSLdict.pop('DOWNLOAD')
            
            
        for key,value in parsedQSLdict.items():
            self.wfile.write('<INPUT type="hidden" name="' + key + '"  value="' + str(value) + '">\n')
            if key<>'DOWNLOAD': 
                self.wfile.write(key + ': ' + str(value) + '<BR>\n')

        if not DOWNLOAD: 
            self.wfile.write("""                
                Canvas Name?: <INPUT type="text" name="cName"  value=""><BR>""")
            self.wfile.write("""
                <INPUT type="submit" value="Send"> <INPUT type="reset">""")
        else:
            self.wfile.write("""<hr>
                <INPUT type="submit" value="CLICK TO DOWNLOAD">""")
        self.wfile.write("""
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
                #self.wfile.write('<p/><hr>Here is a directory:<p>')
                #self.wfile.write(page)
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
TRY: http://localhost:8080/eurl?edgeIp=129.21.142.21&jDomain=http://129.21.142.226:8080&cName=ATable222
vs : http://localhost:8080/eurl?edgeIp=129.21.142.21&jDomain=http://129.21.142.226:8080&


useCases:

If you go to... http://localhost:8080 you get this information.

If you go to a fully qualified URL like http://localhost:8080/eurl?edgeIp=129.21.142.21&jDomain=http://129.21.142.226:8080&cName=ATable222 you get an EURL file.

If you need a canvasName, as with http://localhost:8080/eurl?edgeIp=129.21.142.21&jDomain=http://129.21.142.226:8080& you get a form that asks for a canvasname.

If you click the form's Submit without giving the canvas Name, you return to the form.

If you do provide the canvas name to the form, you are get a CLICK to Download screen.

If you go to http://localhost:8080/a_file_that_we_are_prepared_to_serve.html you'll get it.

If you go to http://localhost:8080/eurl/any_inadequate_URL you'll get a cryptic warning 



"""

def linkify(MSG):
    MSG =MSG.replace('\n',' <br/>\n')
    fixedWords=[]
    for word in MSG.split():
        if 'http:' in word:
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
