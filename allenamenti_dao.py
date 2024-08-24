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

def get_allenamento(id_allenamento):
	query = 'SELECT * FROM Allenamenti WHERE id_allenamento=?'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()

	cursor.execute(query,(id_allenamento,))

	result = cursor.fetchone()

	cursor.close()
	connection.close()

	return result

def modifica_allenamento(workout):
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False

	query = 'UPDATE Allenamenti SET titolo=?,descrizione=?,livello=?,visibile=? WHERE id_allenamento = ?'

	try:
		cursor.execute(query, (workout['titolo'], workout['description'], workout['livello'], workout['visibile'], workout['id_allenamento']))
		connection.commit()
		success = True
	except Exception as e:
		print('Error', str(e))
		connection.rollback()
	cursor.close()
	connection.close()
	return success

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

def delete_workout(id_allenamento):
	query = 'DELETE FROM Allenamenti WHERE id_allenamento=?'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False

	try:
		cursor.execute(query, (id_allenamento,))
		connection.commit()
		success = True
	except Exception as e:
		print('Error', str(e))
		connection.rollback()
	cursor.close()
	connection.close()
	return success