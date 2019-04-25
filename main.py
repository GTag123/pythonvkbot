from flask import Flask, request
app = Flask(__name__)

@app.route('/bot', methods=['POST'])
def hello_world():
    return request.json
if __name__ == '__main__':
    app.run()