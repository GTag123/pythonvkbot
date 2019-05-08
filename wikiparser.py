from bs4 import BeautifulSoup as bs
from requests import session

headers = {'accept': '*/*', 'user-agent': 'user-agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}

def article(query):
	connection = session()
	link = 'https://ru.wikipedia.org/wiki/' + query
	site = connection.get(link)
	if site.status_code == 200:
		soup = bs(site.text, 'lxml')
		try:
			title = soup.find('h1', id='firstHeading').get_text()
		except:
			title = 'Title error'
		try:
			body = soup.find('div', class_='mw-parser-output').find('p')
			try:
				body.style.decompose()
			except:
				pass
			body = body.get_text()
		except:
			body = 'Body error'
		return f"\n{title}:\n&#12288;{body}\nПодробнее: {link}"
	else:
		return 'Запрошенная статья не найдена!'
