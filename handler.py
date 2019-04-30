import database
from os import getenv
import requests
from random import randint

token = getenv('apitoken')
secret = getenv('secret')
confirm = getenv('confirmation')
DATABASE_URL = getenv('DATABASE_URL')

db = database.Database(DATABASE_URL)


# db.select("SELECT EXISTS(select 1 from users where vk_id = 02133);")[0]['exists'] - bool

def main(content):
	if content['secret'] != secret:
		return 'Secret key error! Please, go away!'
	# ---------------------Main handler-----------------------
	elif content['type'] == 'message_new':
		vk_id = content['object']['from_id']
		message = content['object']['text'].split(maxsplit=1)
		message[0] = message[0].lower()

		if not db.select(f"SELECT EXISTS(SELECT 1 FROM users WHERE vk_id = {vk_id});")[0]['exists']:
			vkname = requests.post('https://api.vk.com/method/users.get', data={
				'user_ids': vk_id,
				'access_token': token,
				'v': '5.95'}).json()['response'][0]
			db.new_action(f"INSERT INTO users (vk_id, name, balance, reg_time) VALUES ({vk_id}, '{vkname['first_name']}', 1000, to_timestamp({content['object']['date']}));")
		nickname = db.select(f"SELECT name FROM users WHERE vk_id = {vk_id};")[0]['name']

		sending_params = {
			'peer_id': vk_id,
			'message': 'Мои команды:\n!привет - бот скажет тебе привет\n!анекдот - бот расскажет анекдот\n!скажи - бот повторит твою фразу',
			'access_token': token,
			'v': '5.95',
			'random_id': randint(0, 99999)
		}
		if message[0] == '!привет':
			sending_params['message'] = f"[id{vk_id}|{nickname}], привет!"

		elif message[0] == '!анекдот':
			sending_params['message'] = requests.post('http://rzhunemogu.ru/RandJSON.aspx?CType=1').text[12:-2]
		elif message[0] == '!скажи':
			sending_params['message'] = message
		elif message[0] == '!ник':
			if len(message[1]) <= 30:
				db.new_action(f"UPDATE users SET name = '{message[1]}' WHERE vk_id = {vk_id};")
				sending_params['message'] = f"Ваш новый ник: [id{vk_id}|{message[1]}]!"
			else:
				sending_params['message'] = 'Ошибка! Длина ника не должна превышать 30 символов!'
		requests.post('https://api.vk.com/method/messages.send', data=sending_params)  # sending message
	# --------------------------------------------------------
	elif content['type'] == 'confirmation':
		return confirm
	return 'ok'
