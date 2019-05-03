import database
from os import getenv
import requests
from json import dumps
from random import randint, choice
from datetime import datetime
token = getenv('apitoken')
secret = getenv('secret')
confirm = getenv('confirmation')
DATABASE_URL = getenv('DATABASE_URL')
refer = ('бот', '!бот', 'помощь', 'помочь', 'хелп', 'хелпа', '!помощь', 'команды', '!команды', 'эй', 'начать')
factor = (0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 2.5, 3, 4)
bonus = (250, 500, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 7500, 10000, 15000, 20000, 30000)
bonuswait = 21600  # from 1 to 86400
keyboard = dumps({
	"one_time": False,
	"buttons": [
		[{
				"action": {
					"type": "text",
					"payload": "{\"casino\": \"10000\"}",
					"label": "10к"
				},
				"color": "default"
		},{
				"action": {
					"type": "text",
					"payload": "{\"casino\": \"25000\"}",
					"label": "25к"
				},
				"color": "default"
		},{
				"action": {
					"type": "text",
					"payload": "{\"casino\": \"50000\"}",
					"label": "50к"
				},
				"color": "default"
		},{
				"action": {
					"type": "text",
					"payload": "{\"casino\": \"100000\"}",
					"label": "100к"
				},
				"color": "default"
		}
		],
		[{
			"action": {
				"type": "text",
				"payload": "{\"casino\": \"half\"}",
				"label": "Поставить 1\\2"
			},
			"color": "positive"
		},
			{
				"action": {
					"type": "text",
					"payload": "{\"casino\": \"quarter\"}",
					"label": "Поставить 1\\4"
				},
				"color": "primary"
		}],
		[{
			"action": {
				"type": "text",
				"payload": "{\"casino\": \"all\"}",
				"label": "Поставить всё"
			},
			"color": "negative"
		}]

	]
}, ensure_ascii=False)

db = database.Database(DATABASE_URL)

def get_bonus(vk_id):
	bonus_time = db.select(f"SELECT bonus_time FROM users where vk_id = {vk_id};")[0]['bonus_time'].timestamp()  # 6 hours
	now = datetime.now().timestamp()
	if now < bonus_time:
		return f"""вы можете взять бонус не раньше: {datetime.fromtimestamp(bonus_time).strftime('%H:%M:%S, %Y %B %d')}
		Осталось подождать: {datetime.fromtimestamp(bonus_time - now).strftime('%H:%M:%S')}"""
	win = choice(bonus)
	db.new_action(f"UPDATE users SET balance = balance + {win}, bonus_time = to_timestamp({now + bonuswait}) WHERE vk_id = {vk_id};")
	return f"поздравлем! Вы получили {win} монет.\nСледующий бонус в: {datetime.fromtimestamp(now + bonuswait).strftime('%Y %B %d %H:%M:%S')}"
def casino(bet, vk_id, balance):
	if balance < bet:
		return f"\nВаша ставка - {bet} монет - больше, чем ваш баланс - {balance} монет! Уменьшите ставку!"
	x = choice(factor)
	win = round(bet * x) - bet
	db.new_action(f"UPDATE users SET balance = {balance + win} WHERE vk_id = {vk_id};")
	if x > 1:
		return f"\nПоздравляем!\nВы поставили {bet} монет\nВаш коэффициент: x{x}\nВы получили {win} монет!"
	elif x < 1:
		return f"\nВы поставили {bet} монет\nВаш коэффициент: x{x}\nК сожалению вы потеряли {abs(win)} монет!"
	else:
		return f"\nВы поставили {bet} монет\nВаш коэффициент: x{x}\nВы ничего не выиграли и не потеряли&#128528;"
def getbet(message, balance, vk_id, payload = False):
	if not payload:
		try:
			return casino(abs(int(message)), balance, vk_id)
		except ValueError:
			if message.lower() in ('*', 'всё', 'все', 'all'):
				return casino(balance, balance, vk_id)
			elif message.lower() in ('1/2', 'половина'):
				return casino(balance // 2, balance, vk_id)
			else:
				return 'ошибка! Ставка должна быть целым числом!'
	if payload == 'all':
		return casino(balance, balance, vk_id)
	elif payload == 'half':
		return casino(balance // 2, balance, vk_id)
	elif payload == 'quarter':
		return casino(balance // 4, balance, vk_id)
	else:
		return casino(int(payload), balance, vk_id)


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
		nickname = '[id%s|%s]' % (vk_id, db.select(f"SELECT name FROM users WHERE vk_id = {vk_id};")[0]['name'])
		balance = db.select(f"SELECT balance FROM users WHERE vk_id = {vk_id};")[0]['balance']
		sending_params = {
			'peer_id': content['object']['peer_id'],
			'message': """Привет! Вот мои команды:
			&#128521;!привет - бот скажет тебе привет&#128521;
			&#128514;!анекдот - бот расскажет анекдот&#128514;
			&#128079;!скажи [фраза]- бот повторит твою фразу&#128079;	
			&#128394;!ник [ваш ник]- установить новый ник&#128394;
			&#128210;!профиль - ваш профиль&#128210;
			&#11088;!бонус - взять бонус(раз в 6 часов)&#11088;
			&#128177;!казино [ставка] - казино&#128177;
			&#8252;!репорт [текст] - откправить сообщение админу&#8252;""",
			'access_token': token,
			'v': '5.95',
			'random_id': randint(0, 99999)
		}
		if 'payload' in content['object']:
			print(content['object']['payload'])
		if message[0] == '!привет':
			sending_params['message'] = f"{nickname}, привет!"
		elif message[0] == '!анекдот':
			sending_params['message'] = requests.post('http://rzhunemogu.ru/RandJSON.aspx?CType=1').text[12:-2]
		elif message[0] == '!скажи':
			if len(message) > 1:
				sending_params['message'] = message[1]
			else:
				sending_params['message'] = 'А что сказать-то?)'
		elif message[0] == '!ник':
			if len(message) > 1:
				if len(message[1]) <= 30:
					db.new_action(f"UPDATE users SET name = '{message[1]}' WHERE vk_id = {vk_id};")
					sending_params['message'] = f"{nickname}, Ваш новый ник: [id{vk_id}|{message[1]}]!"
				else:
					sending_params['message'] = f'{nickname}, Ошибка! Длина ника не должна превышать 30 символов!'
			else:
				sending_params['message'] = f'{nickname}, Вы не указали ник!'
		elif message[0] == '!профиль':
			profile_info = db.select(f"SELECT * FROM users WHERE vk_id = {vk_id};")[0]
			sistime = datetime.now()
			if sistime.timestamp() >= profile_info['bonus_time'].timestamp():
				bonusavailable = 'уже доступен!'
			else:
				bonusavailable = f"{datetime.fromtimestamp(profile_info['bonus_time'].timestamp() - sistime.timestamp()).strftime('%H:%M:%S')} часов"
			sending_params['message'] = f"""
			&#8265;{nickname}, Ваш профиль:
			&#127380;ID: {profile_info['id']}
			&#10004;Вконтакте ID: {profile_info['vk_id']}
			&#128310;Ник: [id{vk_id}|{profile_info['name']}]
			&#128176;Баланс: {profile_info['balance']} монет
			&#9203;Системное время: {sistime.strftime('%H:%M:%S, %Y %B %d')}
			&#8986;Бонус через: {bonusavailable}
			&#128197;Дата регистрации: {profile_info['reg_time']}"""
		elif message[0] == '!казино':
			sending_params['message'] = f"{nickname}, {casino(message[1], vk_id, balance)}"
			sending_params['keyboard'] = keyboard
		elif message[0] == '!бонус':
			sending_params['message'] = f"{nickname}, {get_bonus(vk_id)}"
		elif message[0] == '!репорт':
			if len(message) > 1:
				requests.post('https://api.vk.com/method/messages.send', data={'peer_id': 239188570, 'message': f"Новое сообщение от полозователя {nickname}:\n{message[1]}", 'access_token': token, 'v': '5.95', 'random_id': randint(0, 99999)})
				sending_params['message'] = f"Сообщение:\n{message[1]}\nбыло успешно отправлено админу!"
			else:
				sending_params['message'] = 'Пустое сообщение!'
		elif not message[0] in refer:
			return 'ok'
		requests.post('https://api.vk.com/method/messages.send', data=sending_params)  # sending message
	# --------------------------------------------------------
	elif content['type'] == 'confirmation':
		return confirm
	return 'ok'
