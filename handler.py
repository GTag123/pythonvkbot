import database
from os import getenv
import requests
from json import dumps, loads
from random import randint, choice
from datetime import datetime
token = getenv('apitoken')
secret = getenv('secret')
confirm = getenv('confirmation')
DATABASE_URL = getenv('DATABASE_URL')
refer = ('бот', '!бот', 'помощь', 'help', 'хелп', '!помощь', 'команды', '!команды', 'начать')
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

def sell(id, message):
	message = message.split()[0].lower()
	try:
		type = {'телефон': ('phone', 'phones'), 'дом': ('home', 'homes'), 'авто': ('car', 'cars'), 'бизнес': ('business', 'business')}[message]
		thinginfo = db.select("SELECT name, price FROM %s WHERE id = %d") % (type[1], db.select(f"SELECT {type[0]} FROM own WHERE id = {id};")[0][0])
		if thinginfo['name'] == 'NULL':
			return "ошибка, у вас нет такого вида имущества, для просмотра имущества - !профиль"
		db.new_action(f"UPDATE users SET balance = balance + ({thinginfo['price'] * 0.6}); UPDATE own SET {type[0]} = DEFAULT WHERE id = {id};""")
		return f"вы успешно продали {thinginfo['name']} за {thinginfo['price'] * 0.6} монет (60% стоимости)\nДля покупки нового имущества - !магазин"
	except KeyError:
		print(message)
		return "1"

def shoplist():
	string = '\nМагазин:\n&#9742;1. Телефоны:'
	for i in db.select("SELECT * FROM phones WHERE id >= 1 ORDER BY id ASC;"):
		string += f"\n&#12288;&#12288;{i['id']}. {i['name']}. Цена: {i['price']} монет"
	string += '\n\n&#128665;2. Автомобили:'
	for i in db.select("SELECT * FROM cars WHERE id >= 1 ORDER BY id ASC;"):
		string += f"\n&#12288;&#12288;{i['id']}. {i['name']}. Цена: {i['price']} монет"
	string += '\n\n&#127968;3. Недвижемость:'
	for i in db.select("SELECT * FROM homes WHERE id >= 1 ORDER BY id ASC;"):
		string += f"\n&#12288;&#12288;{i['id']}. {i['name']}. Цена: {i['price']} монет"
	string += '\n\n&#127978;4. Бизнесы:'
	for i in db.select("SELECT * FROM business WHERE id >= 1 ORDER BY id ASC;"):
		string += f"\n&#12288;&#12288;{i['id']}. {i['name']}. Цена: {i['price']} монет.\nПрибыль: {i['profit']} монет в час"
	string += '\n\nДля покупки введите !магазин [вид товара] [id товара]\nНапример: !магазин 2 6 - чтобы купить BMW x7'
	return string

def shop(params, id):
	params = params.split()
	if len(params) < 2:
		return shoplist()
	kind = {'1': ('phone', 'phones'), '2': ('car', 'cars'), '3': ('home', 'homes'), '4': ('business', 'business')}
	try:
		product = db.select(f"SELECT * FROM {kind[params[0]][1]} WHERE id = {params[1]} AND id >= 1;")[0]
		print(product)
	except (KeyError, IndexError):
		return "такой категории/товара не существует!\nСписок товаров - !магазин"
	db.new_action(f"UPDATE users SET balance = balance - {product['price']} WHERE id = {id}")
	db.new_action(f"UPDATE own SET {kind[params[0]][0]} = {product['id']} WHERE id = {id};")
	return f"вы успешно купили {product['name']} за {product['price']} монет"

def own(id):
	string = '&#128273;Ваше имущество:'
	flag = False
	things = db.select(f"""SELECT p.name as phone, c.name as car, h.name as home, b.name as business 
	FROM own o, phones p, cars c, homes h, business b 
	WHERE o.id = {id} AND o.phone =  p.id AND o.car = c.id AND o.home = h.id AND o.business = b.id;""")[0]
	if things['phone'] != 'NULL':
		string += f"\n&#128241;Телефон - {things['phone']}"
		flag = True
	if things['car'] != 'NULL':
		string += f"\n&#128663;Автомобиль - {things['car']}"
		flag = True
	if things['home'] != 'NULL':
		string += f"\n&#127969;Жильё - {things['home']}"
		flag = True
	if things['business'] != 'NULL':
		string += f"\n&#128200;Предприятие - {things['business']}"
		flag = True
	if flag:
		return string
	return 'На данный момент у вас нет имущества!\nЧтобы купить - !магазин'

def get_bonus(id):
	bonus_time = db.select(f"SELECT bonus_time FROM users where id = {id};")[0]['bonus_time'].timestamp()  # 6 hours
	now = datetime.now().timestamp()
	if now < bonus_time:
		return f"""вы можете взять бонус не раньше: {datetime.fromtimestamp(bonus_time).strftime('%H:%M:%S, %Y %B %d')}
		Осталось подождать: {datetime.fromtimestamp(bonus_time - now).strftime('%H:%M:%S')}"""
	win = choice(bonus)
	db.new_action(f"UPDATE users SET balance = balance + {win}, bonus_time = to_timestamp({now + bonuswait}) WHERE id = {id};")
	return f"поздравлем! Вы получили {win} монет.\nСледующий бонус в: {datetime.fromtimestamp(now + bonuswait).strftime('%Y %B %d %H:%M:%S')}"

def casino(bet, id, balance):
	if balance < bet:
		return f"\nВаша ставка - {bet} монет - больше, чем ваш баланс - {balance} монет! Уменьшите ставку!"
	x = choice(factor)
	win = round(bet * x) - bet
	db.new_action(f"UPDATE users SET balance = {balance + win} WHERE id = {id};")
	if x > 1:
		return f"\nПоздравляем!\nВы поставили {bet} монет\nВаш коэффициент: x{x}\nВы получили {win} монет!"
	elif x < 1:
		return f"\nВы поставили {bet} монет\nВаш коэффициент: x{x}\nК сожалению вы потеряли {abs(win)} монет!"
	else:
		return f"\nВы поставили {bet} монет\nВаш коэффициент: x{x}\nВы ничего не выиграли и не потеряли&#128528;"

def getbet(message, balance, id, payload=False):
	if not payload:
		try:
			return casino(abs(int(message)), id, balance)
		except ValueError:
			if message.lower() in ('*', 'всё', 'все', 'all'):
				return casino(balance, id, balance)
			elif message.lower() in ('1/2', 'половина'):
				return casino(balance // 2, id, balance)
			else:
				return 'ошибка! Ставка должна быть целым числом!'
	if payload == 'all':
		return casino(balance, id, balance)
	elif payload == 'half':
		return casino(balance // 2, id, balance)
	elif payload == 'quarter':
		return casino(balance // 4, id, balance)
	else:
		return casino(int(payload), id, balance)

def main(content):
	if content['secret'] != secret:
		return 'Secret key error! Please, go away!'
	# ---------------------Main handler-----------------------
	elif content['type'] == 'message_new':
		vk_id = content['object']['from_id']
		message = content['object']['text'].split(maxsplit=1) + ['N/A']
		message[0] = message[0].lower()

		if not db.select(f"SELECT EXISTS(SELECT 1 FROM users WHERE vk_id = {vk_id});")[0]['exists']:
			vkname = requests.post('https://api.vk.com/method/users.get', data={
				'user_ids': vk_id,
				'access_token': token,
				'v': '5.95'}).json()['response'][0]
			db.new_action(f"INSERT INTO users (vk_id, name, balance, reg_time) VALUES ({vk_id}, '{vkname['first_name']}', 1000, to_timestamp({content['object']['date']}));")
			db.new_action("INSERT INTO own DEFAULT VALUES;")
		profile_info = db.select(f"SELECT * FROM users WHERE vk_id = {vk_id};")[0]
		nickname = '[id%s|%s]' % (vk_id, profile_info['name'])
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
			'keyboard': '{"buttons":[],"one_time":true}',
			'access_token': token,
			'v': '5.95',
			'random_id': randint(0, 99999)
		}
		if 'payload' in content['object']:
			payload_value = loads(content['object']['payload'])['casino']
			sending_params['message'] = f"{nickname}, {getbet(message[1], profile_info['balance'], profile_info['id'], payload=payload_value)}"
			sending_params['keyboard'] = keyboard
		elif message[0] == '!профиль':
			sistime = datetime.now()
			if sistime.timestamp() >= profile_info['bonus_time'].timestamp():
				bonusavailable = 'уже доступен!'
			else:
				bonusavailable = f"{datetime.fromtimestamp(profile_info['bonus_time'].timestamp() - sistime.timestamp()).strftime('%H:%M:%S')} часов"
			sending_params['message'] = f"""
			&#8265;{nickname}, Ваш профиль:
			&#127380;ID: {profile_info['id']}
			&#10004;Вконтакте ID: {profile_info['vk_id']}
			&#128310;Ник: {nickname}
			&#128176;Баланс: {profile_info['balance']} монет
			&#9203;Системное время: {sistime.strftime('%H:%M:%S, %Y %B %d')}
			&#8986;Бонус через: {bonusavailable}
			\n{own(profile_info['id'])}\n
			&#128197;Дата регистрации: {profile_info['reg_time']}"""
		elif message[0] == '!казино':
			sending_params['message'] = f"{nickname}, {getbet(message[1], profile_info['balance'], profile_info['id'])}"
			sending_params['keyboard'] = keyboard
		elif message[0] == '!ник':
			if len(message[1]) <= 30:
				db.new_action(f"UPDATE users SET name = '{message[1]}' WHERE id = {profile_info['id']};")
				sending_params['message'] = f"{nickname}, ваш новый ник: [id{vk_id}|{message[1]}]!"
			else:
				sending_params['message'] = f'{nickname}, ошибка! Длина ника не должна превышать 30 символов!'
		elif message[0] == '!бонус':
			sending_params['message'] = f"{nickname}, {get_bonus(profile_info['id'])}"
		elif message[0] == '!магазин':
			sending_params['message'] = f"{nickname}, {shop(message[1], profile_info['id'])}"
		elif message[0] == '!продать':
			sending_params = f"{nickname}, {sell(profile_info['id'], message[1])}"
		elif message[0] == '!репорт':
			requests.post('https://api.vk.com/method/messages.send', data={'peer_id': 239188570, 'message': f"Новое сообщение от полозователя {nickname}:\n{message[1]}", 'access_token': token, 'v': '5.95', 'random_id': randint(0, 99999)})
			sending_params['message'] = f"Сообщение:\n{message[1]}\nбыло успешно отправлено админу!"
		elif message[0] == '!анекдот':
			sending_params['message'] = requests.post('http://rzhunemogu.ru/RandJSON.aspx?CType=1').text[12:-2]
		elif message[0] == '!скажи':
			sending_params['message'] = message[1]
		elif message[0] == '!привет':
			sending_params['message'] = f"{nickname}, привет!"
		elif (not message[0] in refer) and (vk_id != content['object']['peer_id']):
			return 'ok'
		requests.post('https://api.vk.com/method/messages.send', data=sending_params)  # sending message
	# --------------------------------------------------------
	elif content['type'] == 'confirmation':
		return confirm
	return 'ok'
