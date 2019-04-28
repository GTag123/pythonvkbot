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
		vk_id = content['object']['from_id']
		message = content['object']['text']
		getname = send.post('https://api.vk.com/method/users.get', data={
    		'user_ids': vk_id,
    		'access_token': token,
    		'v': '5.95'}).json()['response'][0]

		db.new_action("INSERT INTO messages(vk_id, name, message) VALUES('{}', '{} {}', '{}');".format(vk_id, getname['first_name'], getname['last_name'], message))
		sending_params = {
			'peer_id': vk_id,
			'message': 'Ваше сообщение: %s\n%s' % (message, 'Последняя запись: ' + str(db.select('messages')[-1])),
			'access_token': token,
			'v': '5.95',
			'random_id': randint(0, 9999999)
			}
		print(str(db.select('messages')[-1]))
		send.post('https://api.vk.com/method/messages.send', data=sending_params) # sending message
# --------------------------------------------------------
	elif content['type'] == 'confirmation':
		return confirm
	return 'ok'
if __name__ == '__main__':
	app.run()