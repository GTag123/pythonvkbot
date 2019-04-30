import database
from os import getenv
import requests
from random import randint

token = getenv('apitoken')
secret = getenv('secret')
confirm = getenv('confirmation')
DATABASE_URL = getenv('DATABASE_URL')

db = database.Database(DATABASE_URL)
check = db.select("SELECT EXISTS(select 1 from users where vk_id = 2133);")
print(check)
print(type(check))

def main(content):
	if content['secret'] != secret:
		return 'Secret key error! Please, go away!'
# ---------------------Main handler-----------------------
	elif content['type'] == 'message_new':
		vk_id = content['object']['from_id']
		message = content['object']['text'].split(maxsplit=1)
		message[0] = message[0].lower()
		sending_params = {
			'peer_id': vk_id,
			'message': 'Мои команды:\n!привет - бот скажет тебе привет\n!анекдот - бот расскажет анекдот\n!скажи - бот повторит твою фразу',
			'access_token': token,
			'v': '5.95',
			'random_id': randint(0, 99999)
			}
		if message[0] == '!привет':
			getname = requests.post('https://api.vk.com/method/users.get', data={
    		'user_ids': vk_id,
    		'access_token': token,
    		'v': '5.95'}).json()['response'][0]
			sending_params['message'] = f"[id{vk_id}|{getname['first_name']}], привет!"

		elif message[0] == '!анекдот':
			sending_params['message'] = requests.post('http://rzhunemogu.ru/RandJSON.aspx?CType=1').text[12:-2]
		elif message[0] == '!скажи':
			sending_params['message'] = message
		requests.post('https://api.vk.com/method/messages.send', data=sending_params) # sending message
# --------------------------------------------------------
	elif content['type'] == 'confirmation':
		return confirm
	return 'ok'