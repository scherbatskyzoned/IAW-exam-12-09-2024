import sqlite3
from datetime import datetime


def create_allenamento(workout, pt_id):
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False
	query = 'INSERT INTO Allenamenti(titolo,descrizione,livello,visibile,pt_id,data_creazione) VALUES (?,?,?,?,?,?)'
	data = str(datetime.now())
	try:
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
	allenamenti = cursor.fetchall()

	cursor.close()
	connection.close()

	return allenamenti


def get_allenamento(id_allenamento):
	query = 'SELECT * FROM Allenamenti WHERE id_allenamento=?'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()

	cursor.execute(query,(id_allenamento,))

	allenamento = cursor.fetchone()

	cursor.close()
	connection.close()

	return allenamento


def modifica_allenamento(workout):
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False

	query1 = 'UPDATE Allenamenti SET titolo=?,descrizione=?,livello=?,visibile=? WHERE id_allenamento = ?'
	query2 = 'SELECT id_scheda FROM Schede S, Allenamenti A WHERE id_allenamento = ? AND visibile = 0 AND S.pt_id != A.pt_id'
	query3 = 'DELETE FROM CompostaDa WHERE id_allenamento = ? AND id_scheda = ?'
	try:
		cursor.execute(query1, (workout['titolo'], workout['description'], workout['livello'], workout['visibile'], workout['id_allenamento']))
		connection.commit()
		# Se reso privato, l'allenamento viene tolto dalle schede fatte dagli altri personal trainer
		if workout['visibile'] == 0:
			cursor.execute(query2, (workout['id_allenamento'],))
			ids_schede_db = cursor.fetchall()
			ids_schede = [id['id_scheda'] for id in ids_schede_db]
			for id in ids_schede:
				cursor.execute(query3, (workout['id_allenamento'], id))
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

	allenamenti = cursor.fetchall()

	cursor.close()
	connection.close()

	return allenamenti


def delete_workout(id_allenamento):
	query1 = 'DELETE FROM CompostaDa WHERE id_allenamento=?'
	query2 = 'DELETE FROM Allenamenti WHERE id_allenamento=?'

	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False

	try:
		cursor.execute(query1, (id_allenamento,)) # Elimino l'allenamento da ogni scheda in cui è presente
		cursor.execute(query2, (id_allenamento,))
		connection.commit()
		success = True
	except Exception as e:
		print('Error', str(e))
		connection.rollback()
	cursor.close()
	connection.close()
	return success