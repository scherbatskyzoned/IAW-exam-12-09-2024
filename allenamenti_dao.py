import sqlite3
from datetime import date

def create_allenamento(workout, pt_id):
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False
	query = 'INSERT INTO Allenamenti(titolo,descrizione,livello,visibile,pt_id,data_creazione) VALUES (?,?,?,?,?,?)'
	data = str(date.today())
	try:
		# print("pt id", type(pt_id), "data", type(data))
		cursor.execute(query, (workout['titolo'], workout['description'], workout['livello'], workout['visibile'], pt_id, data))
		connection.commit()
		success = True
	except Exception as e:
		print('Error', str(e))
		connection.rollback()
	cursor.close()
	connection.close()
	return success


def get_allenamenti():
	query = 'SELECT * FROM Allenamenti ORDER BY data_creazione DESC'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()

	cursor.execute(query)

	result = cursor.fetchall()
	print(result)

	cursor.close()
	connection.close()

	return result

def get_allenamenti_by_pt(pt_id):
	query = 'SELECT * FROM Allenamenti WHERE pt_id=? ORDER BY data_creazione DESC'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()

	cursor.execute(query, (pt_id,))

	result = cursor.fetchall()
	print(result)

	cursor.close()
	connection.close()

	return result
