from flask import Flask, request
app = Flask(__name__)

@app.route('/bot', methods=['POST'])
def hello_world():
    return 'c4621a4c'
if __name__ == '__main__':
    app.run()