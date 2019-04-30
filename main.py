from flask import Flask, request
import handler

app = Flask(__name__)


@app.route('/')
def hello_world():
	return 'Дарова'


@app.route('/bot', methods=['POST'])
def main():
	content = request.get_json(force=True)
	print('Json: ', content)
	return handler.main(content)


if __name__ == '__main__':
	app.run()
