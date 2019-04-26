from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def hello_world():
	print('дарова')
    return '<h1>Ku</h1>'

# @app.route('/bot', methods=['POST'])
# def main():
# 	content = request.get_json()
#     return content

if __name__ == '__main__':
    app.run()