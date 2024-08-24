from flask_login import UserMixin

class User(UserMixin): # use uuid6 for id
	def __init__(self, nome, cognome, email, password):
		self.nome = nome
		self.cognome = cognome
		self.email = email
		self.password = password

	def get_id(self):
		return self.email


class PersonalTrainer(User):
	def __init__(self, nome, cognome, pt_id, email, password, rating, numOfRatings):
		super().__init__(nome, cognome, email, password)
		
		# inizializzazione
		self.rating = rating
		self.numOfRatings = numOfRatings
		self.pt_id = pt_id

class Client(User):
	def __init__(self, nome, cognome, client_id, email, password, pt_id):
		super().__init__(nome, cognome, email, password)

		# inizializzazione
		self.pt_id = pt_id
		self.client_id = client_id

