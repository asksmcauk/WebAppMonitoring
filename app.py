import json
from flask import Flask, request, render_template

import requests
import validators
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/websitestatus', methods=['POST'])
def check_websitestatus():
    file = request.files['inputFile']

    if file.filename == '':
        return 'No selected file'

    file_content = file.read()
    data = json.loads(file_content)

    if data['url'] is None:
        return 'URL is Empty'
    
    validation = validators.url(data['url'])
    if validation != True:
        return 'Invalid URL value'

    uResponse = requests.get(data['url'])

    if uResponse.status_code == 200:
        return str(uResponse.status_code)
    else:
        return "HTTP request is unsuccessful,Please check"

if __name__ == '__main__':
    app.run(debug=True)