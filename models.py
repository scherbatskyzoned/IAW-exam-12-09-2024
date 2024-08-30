from flask_login import UserMixin

class User(UserMixin):
	def __init__(self, nome, cognome, genere, email, password):
		self.nome = nome
		self.cognome = cognome
		self.genere = genere
		self.email = email
		self.password = password

	def get_id(self):
		return self.email


class PersonalTrainer(User):
	def __init__(self, nome, cognome, genere, pt_id, email, password, rating, numOfRatings):
		super().__init__(nome, cognome, genere, email, password)
		
		# inizializzazione
		self.rating = rating
		self.numOfRatings = numOfRatings
		self.pt_id = pt_id

class Client(User):
	def __init__(self, nome, cognome, genere, client_id, email, password, pt_id):
		super().__init__(nome, cognome, genere, email, password)

		# inizializzazione
		self.pt_id = pt_id
		self.client_id = client_id