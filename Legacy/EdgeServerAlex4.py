#!/usr/bin/env python

# Copyright Jon Berg , turtlemeat.com
# Modified by nikomu @ code.google.com     
#https://code.google.com/p/python-simple-fileserver/#Code_Snippet
#EdgeServer.py Jon.Schull@RIT.edu

MSG="""EDGESERVER
If the URL starts with /eurl, and the canvas name has been supplied, we'll deliver an eUrl file.
If the canvas name is missing, we'll ask you to supply it.
<hr>
Deliver the File:
    http://localhost:8080/eurl?edgeIp=129.21.142.218&jDomain=http://129.21.142.226:8080&cName=ATable222

Ask for canvasName
    http://localhost:8080/eurl?edgeIp=129.21.142.218&jDomain=http://129.21.142.226:8080&

useCases:

* If you go to... http://localhost:8080 you get this information.

* If you go to a fully qualified URL like... 
... http://localhost:8080/eurl?edgeIp=129.21.142.218&jDomain=http://129.21.142.226:8080&cName=ATable222 
... you get an EURL file.

* If you need a canvasName, as with... 
... http://localhost:8080/eurl?edgeIp=129.21.142.218&jDomain=http://129.21.142.226:8080& 
... you get a form that asks for a canvasname.

* If you click the form's Submit without giving the canvas Name, you return to the form.

* If you do provide the canvas name to the form, you  get a CLICK to Download screen.

* If you go to http://localhost:8080/a_file_that_we_are_prepared_to_serve.html you'll get it.

* If you go to http://localhost:8080/eurl/any_inadequate_URL you'll get a cryptic warning 

"""

import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from pprint import pprint 
from urlparse import urlparse, parse_qsl

MYIP = '129.21.142.144' 
MYPORT = '8080' 

# PORT = 8080     
UPLOAD_PAGE = 'upload.html' # must contain a valid link with address and port of the server     s

def whiteList(REFERER):
    legits = ['http://129.21.142.226:8080',  'https://jira.acme-edge.com'   ]
    for legit in legits:
        if REFERER.startswith(legit):
            return True
    return False


def make_eURLfile(self):
    self.send_response(200)

    parsedPath = urlparse(self.path)
    parsedQSLdict = dict(  parse_qsl(parsedPath.query) )
    if 'verNum' not in parsedQSLdict:
        parsedQSLdict['verNum'] = 0.2 #When this is updated be sure to change it here and in the edgeTable code
    #parsedQSLdict['help'] = Some url that leads to something that explains what this file is (Maybe "Click this link to learn more about the .eurl file type: " + link

    if 'jDomain' in parsedQSLdict and 'jID' not in parsedQSLdict:
        """ Munge the REFERER as needed to get jID if appropriate
        """
        REFERER = self.headers.getheader('referer')
        if REFERER:
            if whiteList(REFERER):
                REFERER = REFERER.split('?')[0]  #when coming from JIRA comments, we have extra garbage
                if REFERER.endswith('/'):
                    REFERER=REFERER[:-1]
                issue = REFERER.split('/')[-1]
                parsedQSLdict['jID'] = issue  
    
    """We need to deal with 2 cases
        1) we're all set, so offer a button for downloading
        2) we need a canvas name, go ask for it, and then go to 1
    """
    
    def writeHiddenFields():
        for key,value in parsedQSLdict.items():
            self.wfile.write('<INPUT type="hidden" name="' + key + '" value="' + str(value) + '">\n')
            if key<>'DOWNLOAD' or key == 'CHANGEME':
                self.wfile.write(key + ': ' + str(value) + '<BR>\n')

    def writeURLstring(parsedQSLdict):
            urlString='<i> This URL can be shared to access the Canvas</i><br/>http://'  + MYIP  + ':' + MYPORT + '/eurl?'
            for key,value in parsedQSLdict.items():
                if key<>'DOWNLOAD':
                    urlString += key + '=' + str(value) + '&'
            urlString = urlString[:-1]
            self.wfile.write('<hr>' + urlString + '<hr>')
    
    
    #DELIVER
    if ('cName' in parsedQSLdict) and ('DOWNLOAD' not in parsedQSLdict) : #deliver the eURL file.
        self.send_header('Content-type', 'application/octet-stream')
        self.send_header('Content-Disposition', 'attachment; filename='+ parsedQSLdict['cName'] + '.eUrl')
        self.end_headers()

        self.wfile.write(parsedQSLdict) #write to the .eurl file in a JSON format
        return #  We just downloaded the file.  We wont' do anything below. 
    else:  # NOT READY TO DELIVER...
    
        # First, send the web page header
        self.send_header('Content-type',    'text/html')
        self.end_headers()
        self.wfile.write("""
         <FORM action="/eurl?" 
               enctype="multipart/form-data"
               method="get">
            <P>""")

        # Do we need to get a a canvas name, or are we ready to deliver?
        ReadyToDeliver = ('DOWNLOAD' in parsedQSLdict) and ('cName' in parsedQSLdict) and ('edgeIp' in parsedQSLdict)
        if ReadyToDeliver:
            self.wfile.write("<i>We're good to go!</i><hr>")
            parsedQSLdict.pop('DOWNLOAD') #remove the DOWNLOAD attribute so it doesn't clutter the eURL
            writeURLstring( parsedQSLdict )
            writeHiddenFields()             
            self.wfile.write("""<hr/> <INPUT type="submit" value="CLICK TO DOWNLOAD">""")
        else:
            self.wfile.write('If you are reading this in the browser, you need to supply more information.<hr/>')
            #insert a hidden download file so that next time we are ReadyToDownload
            self.wfile.write('<INPUT type="hidden" name="DOWNLOAD" value="True">\n')  
            writeHiddenFields()
            if 'cName'  not in parsedQSLdict: parsedQSLdict['cName'] = 'CHANGEME'        
            if 'edgeIP' not in parsedQSLdict: parsedQSLdict['edgeIP']= 'CHANGEME'        
            self.wfile.write('Canvas Name : <INPUT type="text" name="cName"  value=' + parsedQSLdict['cName' ] + '><br/>' )
            self.wfile.write('EdgeTable IP: <INPUT type="text" name="edgeIp"  value=' + parsedQSLdict['edgeIP'] + '><br/>' )
            self.wfile.write("""
                <INPUT type="submit" value="Update Parameters"> <INPUT type="reset">""")
            
 
       # Finally, deliver close up the Form
        self.wfile.write("""
               </P>
             </FORM>
             """)

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        #print self.path
        try:

            if self.path == '/' :     
                self.send_response(200)
                self.send_header('Content-type',    'text/html')
                self.end_headers()
                self.wfile.write(linkify(MSG))
                return     


            if ( self.path.endswith(".html") or self.path.endswith(".txt") ) :
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
            print e
            self.send_error(404,'File Not Found: %s' % self.path)

def linkify(MSG):
    """ Turn URLs into clickable links"""
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
        print MSG
        print 'Starting Server...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

if __name__ == '__main__':
    #khanChecker.setup()  #We don't need no stinking Khan now but if we want oauth, we might use this
    MSG +=  'BEWARE: MYIP IS SET TO ' + str(MYIP) + ':' + str(MYPORT) 
    import webbrowser 
    webbrowser.open('http://localhost:8080')
    main()
