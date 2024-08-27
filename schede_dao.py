import sqlite3
# Utilities to work on tables CompostaDa AND Schede

def create_scheda(ids,pt_id,new_scheda):
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False

	query = 'INSERT INTO Schede(client_id,pt_id,rating,titolo,obiettivo) VALUES (?,?,NULL,?,?)'
	
	try:
		cursor.execute(query, (new_scheda["client_id"],pt_id,new_scheda["titolo"],new_scheda["obiettivo"]))
		connection.commit()
		# print("lastrowid",cursor.lastrowid)
		success = True

	except Exception as e:
		print('Error', str(e))
		connection.rollback()
	
	cursor.close()
	connection.close()
	# sistema posizione 
	success = insert_allenamenti(cursor.lastrowid,ids)
	return success

def insert_allenamenti(id_scheda,ids):
	query = 'INSERT INTO CompostaDa(id_scheda,id_allenamento) VALUES (?,?)'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False

	try:
		for id in ids:
			cursor.execute(query, (id_scheda, id))
		connection.commit()
		# print("lastrowid",cursor.lastrowid)
		success = True

	except Exception as e:
		print('Error', str(e))
		connection.rollback()
	cursor.close()
	connection.close()
	
	return success

def get_schede_by_client_id(client_id):
	query = 'SELECT * FROM Schede WHERE client_id = ?'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()

	cursor.execute(query,(client_id,))

	result = cursor.fetchall()
	# print(result)

	cursor.close()
	connection.close()

	return result

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

	workout_ids_montassar = cursor.fetchall()

	cursor.close()
	connection.close()

	return workout_ids_montassar