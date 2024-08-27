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
	query = 'SELECT * FROM PersonalTrainers'

	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()

	cursor.execute(query)

	result = cursor.fetchall()
	
	cursor.close()
	connection.close()

	return result


def get_pt_id_by_email(user_email):
	default = 0
	query = 'SELECT pt_id FROM PersonalTrainers WHERE email = ?'

	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	cursor.execute(query,(user_email,))
	result = cursor.fetchone()
	cursor.close()
	connection.close()
	# print(result['pt_id'])
	if result is None:
		return default
	return result['pt_id']


def get_pt_clients(pt_id):
	query = 'SELECT * FROM Clients WHERE pt_id = ?'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	cursor.execute(query,(pt_id,))
	clients = cursor.fetchall()
	cursor.close()
	connection.close()
	return clients


def get_client_id_by_email(user_email):
	query = 'SELECT client_id FROM Clients WHERE email = ?'

	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	cursor.execute(query,(user_email,))
	result = cursor.fetchone()
	cursor.close()
	connection.close()
	# print(result['client_id'])
	if result is not None:
		return result['client_id']
	return None

# CONTROLLA SUCCESS
def get_user_by_email(user_email):
	type = 0 # 0: personal_trainer, 1: client
	# try using only 1 query, 2 tables in query
	query1 = 'SELECT * FROM PersonalTrainers WHERE email = ?'
	query2 = 'SELECT * FROM Clients WHERE email = ?'

	# query3 = 'SELECT * FROM PersonalTrainers, Clients WHERE PersonalTrainers.email = ? OR Clients.email = ?'

	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	print("utenti_dao email", user_email)

	cursor.execute(query1,(user_email,))
	# cursor.execute(query1,(user_email,)) # Personal Trainers
	result = cursor.fetchone()
	print("query 1:",result)

	if result is None:
		cursor.execute(query2, (user_email,)) # Clients
		result = cursor.fetchone()
		print("query 2:", result)
		type = 1
	
	cursor.close()
	connection.close()
	return result, type


def set_pt_id(pt_id, client_id):
	query = 'UPDATE Clients SET pt_id=? WHERE client_id=?'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False

	try:
		cursor.execute(query,(pt_id,client_id))
		connection.commit()
		success = True
	except Exception as e:
		print('Error', str(e))
		connection.rollback()
	cursor.close()
	connection.close()

	return success


def update_pt_rating(pt_id, rating, votoNuovo, oldRating=0.0):
	# need to get rating & #rating
	query = 'SELECT rating, numOfRatings FROM PersonalTrainers WHERE pt_id=?'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	cursor.execute(query,(pt_id,))
	result = cursor.fetchone()
	cursor.close()
	connection.close()
	print("update pt rating:",result)

	# CONTROLLA SE LA VALUTAZIONE è STATA MODIFICATA O E' UNA VALUTAZIONE NUOVA :C
	old_media_rating=result['rating']
	num=result['numOfRatings']
	tmp = num*old_media_rating
	# print("update pt rating:", tmp)
	
	if votoNuovo:
		num+=1 # solo se nuova
		new_rating=tmp+float(rating)
	else:
		new_rating=tmp+float(rating)-float(oldRating)
		print(f'new_rating = {tmp} - {oldRating} + {float(rating)}')
	
	new_rating=new_rating/num
	query='UPDATE PersonalTrainers SET rating=?, numOfRatings=? WHERE pt_id=?'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	try:
		cursor.execute(query,(new_rating,num,pt_id))
		connection.commit()
	except Exception as e:
		print('Error', str(e))
		connection.rollback()

	cursor.close()
	connection.close()
