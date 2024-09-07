import sqlite3

def get_email(request):
	try:
		return request.cookies.get('remember_token').split('|')[0]
	except Exception as e:
		return None

# Creates Personal Trainer
#
def create_pt(user):
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False

	query1 = 'SELECT COUNT(*) FROM Clients WHERE email=?'
	query2 = 'INSERT INTO PersonalTrainers(nome,cognome,genere,email,password,rating,numOfRatings) VALUES (?,?,?,?,?,0.0,0)'
	try:
		cursor.execute(query1, (user['email'],))
		count = cursor.fetchone()[0]
		# Check if email is already used in a client's account
		if count == 0:
			cursor.execute(query2, (user['name'], user['surname'], user['genere'], user['email'], user['password']))
			connection.commit()
			success = True

	except Exception as e:
		print('Error', str(e))
		connection.rollback()

	cursor.close()
	connection.close()
	return success


# Creates Client
#
def create_client(user):
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	success = False
	
	query1 = 'SELECT COUNT(*) FROM PersonalTrainers WHERE email=?'
	query2 = 'INSERT INTO Clients(nome,cognome,genere,email,password,pt_id) VALUES (?,?,?,?,?,NULL)'
	try:
		cursor.execute(query1, (user['email'],))
		count = cursor.fetchone()[0]
		# Check if email is already used in a personal trainer's account
		if count == 0:
			cursor.execute(query2, (user['name'], user['surname'], user['genere'], user['email'],  user['password']))
			connection.commit()
			success = True
	except Exception as e:
		print('Error', str(e))
		connection.rollback()

	cursor.close()
	connection.close()
	return success


def get_client(client_id):
	query = 'SELECT * FROM Clients WHERE client_id=?'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()

	cursor.execute(query,(client_id,))	
	client = cursor.fetchone()
	cursor.close()
	connection.close()
	return client


def get_full_name(id, type='client'):
	query1 = 'SELECT nome, cognome FROM Clients WHERE client_id=?'
	query2 = 'SELECT nome, cognome FROM PersonalTrainers WHERE pt_id=?'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	if type == 'client':
		cursor.execute(query1,(id,))
	else:
		cursor.execute(query2,(id,))
	full_name = cursor.fetchone()
	
	cursor.close()
	connection.close()
	return full_name['nome'] + ' ' + full_name['cognome']


def get_personal_trainers():
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	query = 'SELECT * FROM PersonalTrainers'
	cursor.execute(query)

	pts = cursor.fetchall()
	
	cursor.close()
	connection.close()

	return pts


def get_user_id_by_email(user_email, type='client'):
	query1 = 'SELECT pt_id FROM PersonalTrainers WHERE email = ?'
	query2 = 'SELECT client_id FROM Clients WHERE email = ?'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()

	if type == 'pt':
		cursor.execute(query1,(user_email,))	
	else:
		cursor.execute(query2, (user_email,))

	id = cursor.fetchone()

	cursor.close()
	connection.close()
	return id[0]


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


def get_user_by_email(user_email):
	type = 0 # 0: personal_trainer, 1: client
	query1 = 'SELECT * FROM PersonalTrainers WHERE email = ?'
	query2 = 'SELECT * FROM Clients WHERE email = ?'

	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()

	cursor.execute(query1,(user_email,))
	user = cursor.fetchone()

	if user is None:
		cursor.execute(query2, (user_email,)) # Clients
		user = cursor.fetchone()
		type = 1
	
	cursor.close()
	connection.close()
	return user, type


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
	query = 'SELECT rating, numOfRatings FROM PersonalTrainers WHERE pt_id=?'
	connection = sqlite3.connect('db/personal.db')
	connection.row_factory = sqlite3.Row
	cursor = connection.cursor()
	cursor.execute(query,(pt_id,))
	result = cursor.fetchone()

	old_media_rating=result['rating']
	num=result['numOfRatings']
	tmp = num*old_media_rating
	
	if votoNuovo:
		num+=1 # solo se nuova
		new_rating=tmp+float(rating)
	else:
		new_rating=tmp+float(rating)-float(oldRating)
	new_rating=new_rating/num

	query='UPDATE PersonalTrainers SET rating=?, numOfRatings=? WHERE pt_id=?'
	try:
		cursor.execute(query,(new_rating,num,pt_id))
		connection.commit()
	except Exception as e:
		print('Error', str(e))
		connection.rollback()

	cursor.close()
	connection.close()