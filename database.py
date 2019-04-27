import psycopg2
import psycopg2.extras

class Database:
	def __init__(self, DATABASE_URL):
		try:
			self.conn = psycopg2.connect(DATABASE_URL, sslmode='require')
			self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
			print('Connection opened!')
		except:
			print("Cannot connect to datase")
	def new_action(self, query):
		self.cursor.execute(query)
		self.conn.commit()
	def select(self, table, column='*', limit='ALL'):
		self.cursor.execute("SELECT %s FROM %s LIMIT %s", (column, table, limit))
		return self.cursor.fetchall()
	def __del__(self):
		self.cursor.close()
		self.conn.close()
		print('Connection closed successfully!')