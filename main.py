from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def hello_world():
    return '<h1>Ku</h1>'

@app.route('/bot', methods=['POST'])
def main():
    return 'c4621a4c'

if __name__ == '__main__':
    app.run()