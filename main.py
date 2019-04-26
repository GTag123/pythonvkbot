from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def hello_world():
	return '<h1>Ku</h1>'

@app.route('/bot', methods=['GET','POST'])
def main():
	print('test\n')
	content = str(request.get_json(force=True))
	return content

if __name__ == '__main__':
	app.run()