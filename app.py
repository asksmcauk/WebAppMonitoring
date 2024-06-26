import json
from flask import Flask, request, render_template
import requests
import validators
from googlesearch import search
from bs4 import BeautifulSoup

from flask_swagger_ui import get_swaggerui_blueprint
from flask import jsonify
SWAGGER_URL="/swagger"
API_URL="/static/swagger.json"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Access API'
    }
)
app = Flask(__name__)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/', defaults={'page':None})
@app.route('/<page>')
def index(page):
    if page == None:
        return render_template('index.html')
    else:
        return render_template('search.html')

#API to check the website health status
@app.route('/websitestatus', methods=['POST','GET'])
def check_websitestatus():
  
    file = request.files['inputFile']
    if file.filename == '':
        return 'No selected file'

    file_content = file.read()
    #   print (file_content)
    data = json.loads(file_content)

    outmessage = {}
    for rootKey,rootVal in data.items():
        lstRoot = []
        for childVal in rootVal:
            for k,v in childVal.items():
                if validators.url(v):
                    lstRoot.append(getStatus(k,v))
        outmessage[rootKey] = lstRoot
    #print (outmessage)
    return jsonify(outmessage)

@app.route('/getstatus', methods=['POST','GET'])
def getStatus(): 
    data = request.get_json(silent=True)
    #print(data)
    outmessage = {}
    for rootKey,rootVal in data.items():
        lstRoot = []
        for childVal in rootVal:
            for k,v in childVal.items():
                if validators.url(v):
                    lstRoot.append(getStatus(k,v))
        outmessage[rootKey] = lstRoot

    return jsonify(outmessage)

def getStatus(k,v):
    urloutput = {}
    urloutput.update({k: v})
    try:
        uresponse = requests.get(v)
    except Exception:
        urloutput.update({"status_code": "000"})
        urloutput.update({"status": "Failed"})
        return urloutput

    urloutput.update({"status_code": uresponse.status_code})
    if uresponse.status_code == 200:
        urloutput.update({"status": "Success"})
    else:
        urloutput.update({"status": "Failed"})
    return urloutput

@app.route('/google_search', methods=['GET'])
def google_search():
    my_list =[]
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    try:
        links = list(search(query, num=5, stop=5))
        #links = list(search(query, tld='com', lang='en', num=5, start=0, stop=5, pause=2))
        for item in links:
            my_list.append(read_website(item))
        return json.dumps(my_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

 
def read_website(k):
    try:
        response = requests.get(k)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            return  replace_special_characters(text.strip())
        else:
            return  'Failed to fetch content from the provided URL'

    except Exception as e:
        return jsonify({'error': str(e)}), 500   

def replace_special_characters(text, replacement=' '):
    special_characters = "!@#$%^&*()-_=+[]{};:'\",.<>/?\\|`~"
    for char in special_characters:
        text = text.replace(char, replacement)
        text = text.replace('\n', '')
    return text

if __name__ == '__main__':
    app.run(debug=True)