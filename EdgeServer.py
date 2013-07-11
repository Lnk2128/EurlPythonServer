#!/usr/bin/env python

# Copyright Jon Berg , turtlemeat.com
# Modified by nikomu @ code.google.com
# Modified by Jon Schull
# EdgeServer.py Jon.Schull@RIT.edu
#https://code.google.com/p/python-simple-fileserver/#Code_Snippet

import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse, parse_qsl

MYIP = '129.21.142.144' 
MYPORT = '8080' 
MSG="""<h1>USAGE:</h1>
<ul>
    <li>To view this page, visit http://""" + str(MYIP) + ':' + str(MYPORT) +""" or send an erroneous url.</li>
    <li>If you send a partially qualified url, this server will attempt to fill in the missing information. </li>
    <li>If it cannot guess the needed fields, a form will be sent back to help you build a full url.</li>
</ul>"""


def allTrue(list):
    for elem in list:
        if list[elem] is False:
            return False
    return True
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
def guessSourceByURL(url):
    pos = 0
    for part in reversed(url.split("/")):
        if pos is 0 and len(part.split("-")) >= 2:
            if not is_number(part.split("-")[1]):
                break
        if pos is 1 and str(part) == "browse":
                return "jira"
        if pos is 2:
            break
        pos += 1
    return "handshake"
def getInformalName(name):
    if name == 'verNum':    return 'Version Number'
    if name == 'jID':       return 'JIRA issue ID'
    if name == 'jDomain':   return 'Source Domain'
    if name == 'edgeIp':    return 'EdgeTable Server URL'
    if name == 'cName':     return 'Canvas Name'
    if name == 'source':    return 'Source'
def guessverNum(self):
    return 0.2
def guessjID(self):
    referer = self.headers.getheader('referer')
    if referer:
        if guessSourceByURL(referer) == "handshake":
            idIsNext = False
            for elem in referer.split("/"):
                if idIsNext: return elem
                if elem == 'view': idIsNext = True
        if guessSourceByURL(referer) == "jira": 
            return referer.split("/")[-1]
        return False
    else:
        return False
def guessjDomain(self):
    if self.headers.getheader('referer'):
        return urlparse(self.headers.getheader('referer')).netloc
    else:
        return False
def guessedgeIp(self):
    return "129.21.142.218"
def guesscName(self):
    return False
def guesssource(self):
    if self.headers.getheader('referer'):
        return guessSourceByURL(self.headers.getheader('referer'))
    else:
        return "handshake"

def make_eURLfile(self):
    self.send_response(200)
    parsedPath = urlparse(self.path)
    query = dict(  parse_qsl(parsedPath.query) )
    #assume everything is ready to go
    readyToSend = {}
    readyToSend['jID'] = True
    readyToSend['jDomain'] = True
    readyToSend['edgeIp'] = True
    readyToSend['cName'] = True
    readyToSend['source'] = True
    
    #guess the value if it is not being told
    for elem in readyToSend:
        if elem not in query:
            readyToSend[elem] = query[elem] = globals()["guess" + elem](self)
    
    
    if allTrue(readyToSend):    #we're all good to go...
        self.send_header('Content-type', 'application/octet-stream')
        cleanName = query['cName'].replace(" ", "_")
        self.send_header('Content-Disposition', 'attachment; filename=' + cleanName + '.eurl')
        self.end_headers()
        self.wfile.write(query) #write to the .eurl file in a JSON format
        return #Triggers the download
    else:   #ask the user for a few more values
        #attach headers
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        #directions for the user
        self.wfile.write("""
                            <style>
                                p label 
                                {
                                    display: inline-block;
                                    width: 150px;
                                }
                                p input 
                                {
                                    width: 200px;
                                }
                                span
                                {
                                    text-decoration:underline;
                                }
                            </style>
                         """)
        self.wfile.write("<h1>Please add the following information:</h1>")
        
        #create form
        self.wfile.write("<FORM action='/eurl?' enctype='multipart/form-data' method='get'><P>")
       
        
        #add the elements that don't have values yet
        for elem in readyToSend:
            if not readyToSend[elem]:
                self.wfile.write('<label for="'+elem+'">'+getInformalName(elem)+'</label>' + ' <INPUT type="text" name="'+elem+'" id="'+elem+'" value=''><br/>' )
        
        self.wfile.write("<span style='color:grey;'>Guessed Fields</span><br/>")
        
        #add hidden fields the user has already provided
        for elem in query:
            print elem + ":" + str(getInformalName(elem))
            if query[elem] is not False:
                self.wfile.write('<label for="'+str(elem)+'">'+str(getInformalName(elem))+'</label>' + ' <INPUT type="text" name="'+str(elem)+'" id="'+str(elem)+'"   value="'+query[elem]+' " ><br/>' )#disabled="disabled"
        
        self.wfile.write("<INPUT type='submit' value='Attempt Download'/>")
        #self.wfile.write("""
         #                   <INPUT type='button' value='Unlock Guessed Fields' onclick='
        #                    
         #                   var e = document.querySelectorAll("input");
        #                    for(var i = 0; i < e.length; i++)
         #                   {
        #                        if(e[i].disabled)
         #                       {
        #                            console.log("hey");
         #                           e[i].removeAttribute("disabled");
        #                        }
         #                   };
        #                    ' /><br/>
         #               """)
        self.wfile.write("</P></FORM>")
        
        

class MyHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.startswith("/eurl"): # handle valid EURL requests
                make_eURLfile(self)
            else:                             # provide directions after invalid requests
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(linkify(MSG))
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
    import webbrowser 
    webbrowser.open('http://localhost:8080/eurl')
    main()
