from flask import Flask, request
from os import getenv
import requests as send
from random import randint
import database

app = Flask(__name__)
token = getenv('apitoken')
secret = getenv('secret')
confirm = getenv('confirmation')
DATABASE_URL = getenv('DATABASE_URL')

db = database.Database(DATABASE_URL)
db.new_action("INSERT INTO messages(text) VALUES('ураа');")

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

# ---------------------Main handler-----------------------
	elif content['type'] == 'message_new':
		params = {
			'peer_id': content['object']['peer_id'],
			'message': 'Ваше сообщение: %s' % content['object']['text'],
			'access_token': token,
			'v': '5.95',
			'random_id': randint(0, 9999999)
		}
		sending = send.post('https://api.vk.com/method/messages.send', data=params)
		print(sending.json())

# --------------------------------------------------------
	elif content['type'] == 'confirmation':
		return confirm
	return 'ok'

print('SELECT: ' + str(db.select('messages')))

if __name__ == '__main__':
	app.run()