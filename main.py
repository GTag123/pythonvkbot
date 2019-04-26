from flask import Flask, request
from os import getenv
app = Flask(__name__)
token = getenv('apitoken')
secret = getenv('secret')
confirm = getenv('confirmation')
@app.route('/')
def hello_world():
	print(token)
	print(secret)
	print(confirm)
	return 'Дарова'

@app.route('/bot', methods=['POST'])
def main():
	content = request.get_json(force=True)
	if content['secret'] != secret:
		return 'Вы дурак, пошёл в жопу!'
	print('Json: ', content)
	return content

if __name__ == '__main__':
	app.run()