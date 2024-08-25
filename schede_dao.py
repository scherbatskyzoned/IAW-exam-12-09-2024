import sqlite3
# Utilities to work on tables CompostaDa AND Schede

def create_scheda(id_allenamenti, pt_id, client_id):
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False

	query = 'INSERT INTO Schede(client_id,pt_id,rating) VALUES (?,?,NULL)'
	
	try:
		cursor.execute(query, (client_id,pt_id))
		connection.commit()
		# print("lastrowid",cursor.lastrowid)
		success = True

	except Exception as e:
		print('Error', str(e))
		connection.rollback()
	
	cursor.close()
	connection.close()
	# sistema posizione 
	success = insert_allenamenti(cursor.lastrowid,id_allenamenti)
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