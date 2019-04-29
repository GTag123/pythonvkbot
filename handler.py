import database
from os import getenv
import requests
from random import randint

token = getenv('apitoken')
secret = getenv('secret')
confirm = getenv('confirmation')
DATABASE_URL = getenv('DATABASE_URL')

db = database.Database(DATABASE_URL)

def main(content):
	if content['secret'] != secret:
		return 'Secret key error! Please, go away!'
# ---------------------Main handler-----------------------
	elif content['type'] == 'message_new':
		vk_id = content['object']['from_id']
		message = content['object']['text'].split(maxsplit=1)
		getname = requests.post('https://api.vk.com/method/users.get', data={
    		'user_ids': vk_id,
    		'access_token': token,
    		'v': '5.95'}).json()['response'][0]
		sending_params = {
			'peer_id': vk_id,
			'message': 'Мои команды:\n!привет - бот скажет тебе привет',
			'access_token': token,
			'v': '5.95',
			'random_id': randint(0, 99999)
			}
		if message[0].lower() == '!привет':
			sending_params['message'] = f'[id{vk_id}|{getname['first_name']}], привет!'
		requests.post('https://api.vk.com/method/messages.send', data=sending_params) # sending message
# --------------------------------------------------------
	elif content['type'] == 'confirmation':
		return confirm
	return 'ok'