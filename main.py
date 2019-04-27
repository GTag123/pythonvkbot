from flask import Flask, request
from os import getenv
import requests as send
from random import randint
import psycopg2
import psycopg2.extras

app = Flask(__name__)
token = getenv('apitoken')
secret = getenv('secret')
confirm = getenv('confirmation')
DATABASE_URL = getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
with conn:
	with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
		sql = "SELECT * FROM messages;"
		cursor.execute(sql)
		result = cursor.fetchall()
		print('Data: ' + str(result))

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
			'message': 'Ваше сообщение: ' + content['object']['text'],
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

if __name__ == '__main__':
	app.run()