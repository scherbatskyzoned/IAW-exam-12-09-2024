import sqlite3

# used when signing up a personal trainer
#
def create_pt(user):
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False
	# TO CHECK EMAIL IN CLIENTS
	query = "INSERT INTO PersonalTrainers(nome,cognome,email,password,rating,numOfRatings) VALUES (?,?,?,?,0.0,0)"
	try:
		cursor.execute(query, (user['name'], user['surname'], user['email'], user['password']))
		connection.commit()
		success = True
	except Exception as e:
		print('Error', str(e))
		connection.rollback()
	cursor.close()
	connection.close()
	return success

# Used when signign up a client
#
def create_client(user):
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False
	# TO CHECK EMAIL IN PTS
	query = "INSERT INTO Clients(nome,cognome,email,password,pt_id) VALUES (?,?,?,?,NULL)"
	try:
		cursor.execute(query, (user['name'], user['surname'], user['email'],  user['password']))
		connection.commit()
		success = True
	except Exception as e:
		print('Error', str(e))
		connection.rollback()
	cursor.close()
	connection.close()
	return success


def get_personal_trainers():
	query = 'SELECT * FROM Utenti WHERE tipo = ?'

	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()

	cursor.execute(query, ("personal_trainer",))

	result = cursor.fetchall()
	
	cursor.close()
	connection.close()

	return result


# def get_user_by_id(id_utente):
# 	query = 'SELECT * FROM Utenti WHERE id = ?'

# 	connection = sqlite3.connect('db/personal.db')
# 	connection.row_factory = sqlite3.Row
# 	cursor = connection.cursor()

# 	cursor.execute(query, (id_utente,))

# 	result = cursor.fetchone()
	
# 	cursor.close()
# 	connection.close()

# 	return result

def get_pt_id_by_email(user_email):
	query = 'SELECT pt_id FROM PersonalTrainers WHERE email = ?'

	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	cursor.execute(query,(user_email,))
	result = cursor.fetchone()
	cursor.close()
	connection.close()
	print(result['pt_id'])
	return result['pt_id']

def get_user_by_email(user_email):
	type = 0 # 0: personal_trainer, 1: client

	query1 = 'SELECT * FROM PersonalTrainers WHERE email = ?'
	query2 = 'SELECT * FROM Clients WHERE email = ?'

	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	print("utenti_dao email", user_email)
	cursor.execute(query1,(user_email,)) # Personal Trainers
	result = cursor.fetchone()
	# cursor.close()
	# connection.close()
	print("query 1:",result)

	if result is None:
		# connection = sqlite3.connect('db/personal.db')
		# connection.row_factory = sqlite3.Row
		# cursor = connection.cursor()
		cursor.execute(query2, (user_email,)) # Clients
		result = cursor.fetchone()
		print("query 2:", result)
		type = 1
	
	cursor.close()
	connection.close()
	return result, type

