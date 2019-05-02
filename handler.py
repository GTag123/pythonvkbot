import database
from os import getenv
import requests
from random import randint, choice
from datetime import datetime
token = getenv('apitoken')
secret = getenv('secret')
confirm = getenv('confirmation')
DATABASE_URL = getenv('DATABASE_URL')
factor = (0, 0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 2.5, 3, 4)
bonus = (250, 500, 1000, 1500, 2000, 2500, 3000, 4000, 5000, 7500, 10000, 15000, 20000, 30000)
db = database.Database(DATABASE_URL)

def get_bonus(vk_id):
	bonus_time = db.select(f"SELECT bonus_time FROM users where vk_id = {vk_id};")[0]['bonus_time'].timestamp()  # 6 hours
	now = datetime.now().timestamp()
	if now < bonus_time:
		return f"""вы можете взять бонус не раньше: {datetime.fromtimestamp(bonus_time).strftime('%Y %B %d %H:%M:%S')}
		Осталось подождать: {datetime.fromtimestamp(bonus_time - now).strftime('%H:%M:%S')}"""
	win = choice(bonus)
	db.new_action(f"UPDATE users SET balance = balance + {win}, bonus_time = to_timestamp({now + 21600}) WHERE vk_id = {vk_id};")
	return f"поздравлем! Вы получили {win} монет.\nСледующий бонус в: {datetime.fromtimestamp(now + 21600).strftime('%Y %B %d %H:%M:%S')}"
def casino(bet, vk_id):
	balance = db.select(f"SELECT balance FROM users WHERE vk_id = {vk_id};")[0]['balance']
	if balance < bet:
		return f"Ваша ставка - {bet} монет - больше, чем ваш баланс - {balance} монет! Уменьшите ставку!"
	x = choice(factor)
	win = round(bet * x) - bet
	db.new_action(f"UPDATE users SET balance = {balance + win} WHERE vk_id = {vk_id};")
	if x > 1:
		return f"Поздравляем!\nВы поставили {bet} монет\nВаш коэффициент: x{x}\nВы получили {win} монет!"
	elif x < 1:
		return f"Вы поставили {bet} монет\nВаш коэффициент: x{x}\nК сожалению вы потеряли {abs(win)} монет!"
	else:
		return f"Вы поставили {bet} монет\nВаш коэффициент: x{x}\nВы ничего не выиграли и не потеряли&#128528;"

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

		sending_params = {
			'peer_id': vk_id,
			'message': """Привет! Вот мои команды:
			&#128521;!привет - бот скажет тебе привет&#128521;
			&#128514;!анекдот - бот расскажет анекдот&#128514;
			&#128079;!скажи [фраза]- бот повторит твою фразу&#128079;	
			&#128394;!ник [ваш ник]- установить новый ник&#128394;
			&#128210;!профиль - ваш профиль&#128210;
			&#128177;!казино [ставка] - казино&#128177;""",
			'access_token': token,
			'v': '5.95',
			'random_id': randint(0, 99999)
		}
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
			&#9203;Системное время: {sistime.strftime('%Y %B %d %H:%M:%S')}
			&#8986;Бонус через: {bonusavailable}
			&#128197;Дата регистрации: {profile_info['reg_time']}"""
		elif message[0] == '!казино':
			try:
				sending_params['message'] = f"{nickname},\n{casino(int(message[1]), vk_id)}"
			except (ValueError, IndexError):
				sending_params['message'] = f'{nickname}, ошибка! Ставка должна быть целым числом!'
		elif message[0] == '!бонус':
			sending_params['message'] = f"{nickname}, {get_bonus(vk_id)}"
		requests.post('https://api.vk.com/method/messages.send', data=sending_params)  # sending message
	# --------------------------------------------------------
	elif content['type'] == 'confirmation':
		return confirm
	return 'ok'
