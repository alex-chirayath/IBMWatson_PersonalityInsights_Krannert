import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
import requests
import json
import csv
from docx import *
import enchant
import re
import unicodedata
import glob
import PyPDF2
import time

app = Flask(__name__)

app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'docx','doc'])

url = "https://gateway.watsonplatform.net/personality-insights/api"
username = "0481e8d1-66f4-4fa1-b24a-0d56a3250e44"
password = "1glewAbnWn3L"
csvfilename = "values.csv"
folder = "files"

def getdatafromfile(dataFile):
    w=nw=0.0
    en = enchant.Dict("en_US")
    f = 1
        
    if (dataFile.endswith('.docx') or dataFile.endswith('.doc')):
        f=0
        #print "File "+dataFile +"   is a Word doc"
    if (dataFile.endswith('.txt')):
        f=1
        #print "File "+dataFile +"     is a .txt file"   
    if (dataFile.endswith('.pdf')):
        f=2
        #print "pdf"
    #else if dataFile.endswith('.odt'): any other formats?
    
    
    if(f==1):               #make data from txt file
        with open(dataFile, 'r') as myfile:
            data=myfile.read().replace('\n', '')

    if(f==0):               #make data from docx file
        doc= opendocx(dataFile)
        docText=getdocumenttext(doc)
        data="" 
        for paragraphs in docText:  # remove encoding by MS Word
            data+=" "+(paragraphs.encode('utf8'))   

    if(f==2):
        pdfFileObj = open(dataFile, 'r')
        pdfReader = PyPDF2.PdfFileReader(dataFile)
        pageObj = pdfReader.getPage(0)
        data =  pageObj.extractText()

    words= re.findall(r"[\w']+", data)  #check for special characters and regular expressions

    #print " For " +dataFile +"possible wrong words are- \n"
    wordstorem = []
    for word in words:
        if  (en.check(word.lower()) or word.lower()=="purdue" or word.lower()=="edu"):          #since purdue and edu are not words but are acceptable. Maybe we need our own dictionary?
            w=w+1
        else :
            nw=nw+1                     
            wordstorem.append(word)
            #print "\n"
    if ( nw/(nw+w) >0.4):
        print "Too many spelling errors in the file. Check manually."
  #  print words
    text = ' '.join(words)
    pattern = re.compile(r"\b(" + "|".join(wordstorem) + ")\\W", re.I)
    return pattern.sub("", text)

def headeradder():
    return ["id","Adventurousness","Artistic interests","Emotionality","Imagination","Intellect","Authority-challenging","Achievement striving",
            "Cautiousness","Dutifulness","Orderliness","Self-discipline","Self-efficacy","Activity level","Assertiveness","Cheerfulness",
            "Excitement-seeking","Outgoing","Gregariousness","Altruism","Cooperation","Modesty","Uncompromising","Sympathy","Trust","Fiery",
            "Prone to worry","Melancholy","Immoderation","Self-consciousness","Susceptible to stress","Challenge","Closeness","Curiosity",
            "Excitement","Harmony","Ideal","Liberty","Love","Practicality","Self-expression","Stability","Structure","Conservation",
            "Openness to change","Hedonism","Self-enhancement","Self-transcendence"]

def jsontocsvwriter(csvwriter,filename,data):
    csvdata = []
    csvdata.append(filename)
    v1 =  data['tree']
    headers = []
    for i in v1:
        if i == 'children':
            for j in v1[i]:
                for k in j:
                    if k == 'children':
                        vals = []
                        for l in j[k]:
                            for m in l['children']:
                                if 'children' in m:
                                    for n in m['children']:
                                        #csvwriter.writerow([n['name'],n['percentage']])
                                        csvdata.append(n['percentage'])
                                else:
                                    #csvwriter.writerow([m['name'],m['percentage']])
                                    csvdata.append(m['percentage'])                                
    csvwriter.writerow(csvdata)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index(name="Upload SOP in pdf/txt/doc format"):
    return render_template('index.html',name=name)


@app.route('/upload', methods=['POST'])
def upload():
    fileslist = request.files.getlist("file[]")
    if(os.path.isfile(csvfilename)):
        open(csvfilename,'w').close()
    csvf = open(csvfilename,'ab')
    csvwriter = csv.writer(csvf, delimiter=',')
    csvwriter.writerow(headeradder()) 
    #print fileslist
    for f in fileslist:
        #print f.filename
        if f and allowed_file(f.filename):
            s = requests.Session()
            filename = secure_filename(f.filename)
            filepath = os.path.join(folder,filename)
             #print filename
            text = getdatafromfile(filepath)
           
            response = requests.post(url + "/v2/profile",
                              auth=(username, password),
                              headers = {"content-type": "text/plain"},
                              data=text
                              )
            jsontocsvwriter(csvwriter,filename,json.loads(response.text))
    return index("Finished Uploading. Check values.csv for insights")

if __name__ == '__main__':
    app.run(
        host="127.0.0.1",
        port=int("3000"),
        debug=True
    )
