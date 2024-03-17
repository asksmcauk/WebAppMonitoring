import json
from flask import Flask, request, render_template

import requests
import validators

from flask_swagger_ui import get_swaggerui_blueprint

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


@app.route('/')
def index():
    return render_template('index.html')

#API to check the website health status
@app.route('/websitestatus', methods=['POST','GET'])
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
        return 'Invalid URL.'
    try:
        uResponse = requests.get(data['url'])
    except Exception:
        return "Web Application is Not Found or not Working."
    if uResponse.status_code == 200:
        return "HTTP request is successful."
    else:
        return "HTTP request is unsuccessful,Please check"

if __name__ == '__main__':
    app.run(debug=True)