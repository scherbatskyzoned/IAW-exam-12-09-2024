# Utilities to work on tables CompostaDa AND Schede
#
import sqlite3


def create_scheda(ids,pt_id,new_scheda):
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False
	query = 'INSERT INTO Schede(client_id,pt_id,rating,titolo,obiettivo) VALUES (?,?,NULL,?,?)'
	
	try:
		cursor.execute(query, (new_scheda["client_id"],pt_id,new_scheda["titolo"],new_scheda["obiettivo"]))
		success = insert_allenamenti(cursor.lastrowid,ids,cursor,connection)
		if success:
			connection.commit()

	except Exception as e:
		print('Error', str(e))
		connection.rollback()
	
	cursor.close()
	connection.close()
	return success


def insert_allenamenti(id_scheda,ids,cursor,connection):
	query = 'INSERT INTO CompostaDa(id_scheda,id_allenamento) VALUES (?,?)'
	success = False

	try:
		for id in ids:
			cursor.execute(query, (id_scheda, id))
		connection.commit()
		success = True
	except Exception as e:
		print('Error', str(e))
		connection.rollback()
	
	return success


def get_schede_by_client_id(client_id):
	query = 'SELECT * FROM Schede WHERE client_id = ?'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()

	cursor.execute(query,(client_id,))
	schede = cursor.fetchall()
	cursor.close()
	connection.close()

	return schede


def set_rating(id_scheda, rating):
	query = "UPDATE Schede SET rating=? WHERE id_scheda=?"
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False
	try:
		cursor.execute(query, (rating, id_scheda))
		connection.commit()
		success = True
	except Exception as e:
		print('Error', str(e))
		connection.rollback()
	cursor.close()
	connection.close()
	return success


def get_allenamenti_ids_by_id_scheda(id_scheda):
	query = 'SELECT id_allenamento FROM CompostaDa WHERE id_scheda=?'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()

	cursor.execute(query,(id_scheda,))
	workout_ids = cursor.fetchall()

	cursor.close()
	connection.close()

	return workout_ids


def delete_scheda(id_scheda):
	query = 'DELETE FROM CompostaDa WHERE id_scheda=?' 
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False

	try:
		cursor.execute(query, (id_scheda,))
		connection.commit()
		success = True
	except Exception as e:
		print('Error', str(e))
		connection.rollback()

	query = 'DELETE FROM Schede WHERE id_scheda=?'
	success = False

	try:
		cursor.execute(query, (id_scheda,))
		connection.commit()
		success = True
	except Exception as e:
		print('Error', str(e))
		connection.rollback()

	cursor.close()
	connection.close()

	return success


def get_client_id_by_id_scheda(id_scheda):
	query = 'SELECT client_id FROM Schede WHERE id_scheda = ?'

	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	cursor.execute(query,(id_scheda,))
	result = cursor.fetchone()
	cursor.close()
	connection.close()
	if result is not None:
		return result['client_id']
	return None


def get_scheda_by_id(id_scheda):
	query = 'SELECT * FROM Schede WHERE id_scheda = ?'

	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	cursor.execute(query,(id_scheda,))
	result = cursor.fetchone()
	cursor.close()
	connection.close()
	if result is not None:
		return result
	return None


def update_scheda(scheda, ids):
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False
	query = 'UPDATE Schede SET titolo=?, obiettivo=? WHERE id_scheda=?'
	query2 = 'DELETE FROM CompostaDa WHERE id_scheda=?'
	
	try:
		cursor.execute(query, (scheda['titolo'], scheda['obiettivo'], scheda['id_scheda']))
		cursor.execute(query2, (scheda['id_scheda'],))
		
		success = insert_allenamenti(scheda['id_scheda'],ids,cursor,connection)
		if success:
			connection.commit()

	except Exception as e:
		print('Error', str(e))
		connection.rollback()

	cursor.close()
	connection.close()
	return success


def get_num_schede_by_client(client_id):
	query = 'SELECT COUNT(*) FROM Schede WHERE client_id=?'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	cursor.execute(query,(client_id,))
	result = cursor.fetchone()
	cursor.close()
	connection.close()
	
	return result