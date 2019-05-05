from bs4 import BeautifulSoup as bs
from requests import session

headers = {'accept': '*/*', 'user-agent': 'user-agent: Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'}

def getlinks(query):
	connection = session()
	site = connection.get('https://ru.wikipedia.org/w/index.php?', params={'search': query, 'fulltext': 1})
	if site.status_code == 200:
		soup = bs(site.text, 'lxml')
		try:
			results = soup.find('ul', class_='mw-search-results').find_all('li', class_='mw-search-result')
		except:
			return 'произошла ошибка при парсинге ссылок(('
		returnstring = 'первые 5 результатов поиска по твоему запросу:'
		for i in range(5):
			text = results[i].find('div', class_='mw-search-result-heading').find('a').get_text()
			returnstring += f"\n{i+1}. {text}"
		return returnstring
	else:
		return 'произошла ошибка при подключении(('
