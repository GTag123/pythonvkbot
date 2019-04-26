from flask import Flask, request
import os
app = Flask(__name__)

@app.route('/')
def hello_world():
	print(os.getenv("test123"))
	return os.getenv("test123")

@app.route('/bot', methods=['POST'])
def main():
	content = str(request.get_json(force=True))
	print('Json: ', content)
	return content

if __name__ == '__main__':
	app.run()