from flask import Flask, request
from os import getenv
import requests as send
from random import randint
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
	print('Json: ', content)
	if content['secret'] != secret:
		return 'Вы дурак, пошёл в жопу!'
	elif content['type'] == 'message_new':
		params = {
			'peer_id': content['object']['peer_id'],
			'message': 'Ваше сообщение: ' + content['object']['text'],
			'access_token': token,
			'v': '5.95',
			'random_id': randint(0, 9999999)
		}
		sending = send.post('https://api.vk.com/method/messages.send', data=params)
		print(send.json())
	elif content['type'] == 'confirmation':
		return confirm

	return 'ok'

if __name__ == '__main__':
	app.run()