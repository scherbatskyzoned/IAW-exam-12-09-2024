from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

import utenti_dao, allenamenti_dao, schede_dao
from models import PersonalTrainer, Client

# Create App
app = Flask(__name__)
app.config['SECRET_KEY'] = 's3cr3t_v41u3'
login_manager = LoginManager()
login_manager.init_app(app)

# Homepage
#
@app.route('/')
def index():
  allenamenti_db = allenamenti_dao.get_allenamenti()
  pts_db = utenti_dao.get_personal_trainers()
  clienti_db = []
  pt_id = 0
  numOfSchede = {}

  email = utenti_dao.get_email(request)
  if email is not None:
    pt_id = utenti_dao.get_user_id_by_email(email)
  if pt_id != 0:
    clienti_db = utenti_dao.get_pt_clients(pt_id)
    clienti_ids = [client['client_id'] for client in clienti_db]
    for id in clienti_ids:
      numOfSchede[id] = schede_dao.get_num_schede_by_client(id)[0]
  return render_template('index.html', datetime=datetime, allenamenti=allenamenti_db, pts=pts_db, clienti=clienti_db, numOfSchede=numOfSchede) 

# Pagina di presentazione del sito
#  
@app.route('/about')
def about():
  return render_template('about.html')


# Pagina di Registrazione
#
@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method == 'POST':
    new_user = request.form.to_dict()
    print("new user:",new_user)

    if new_user['name'] == '':
      app.logger.error('Il campo non può essere vuoto')
      return redirect(url_for('index'))
    
    if new_user['surname'] == '':
      app.logger.error('Il campo non può essere vuoto')
      return redirect(url_for('index'))

    if new_user['email'] == '':
      app.logger.error('Il campo non può essere vuoto')
      return redirect(url_for('index'))
    
    if new_user['tipo'] == '':
      app.logger.error('Il campo non può essere vuoto')
      return redirect(url_for('index'))
    
    if new_user['password'] == '':
      app.logger.error('Il campo non può essere vuoto')
      return redirect(url_for('index'))
    
    new_user['password'] = generate_password_hash(new_user['password'])

    if new_user['tipo'] == 'personal_trainer':
      success = utenti_dao.create_pt(new_user)
    elif new_user['tipo'] == 'client':
      success = utenti_dao.create_client(new_user)

    if success:
      user_db, type = utenti_dao.get_user_by_email(new_user['email'])
      if type == 0:
        user = PersonalTrainer(nome=user_db['nome'], cognome=user_db['cognome'], pt_id=user_db['pt_id'], rating=user_db['rating'], numOfRatings=user_db['numOfRatings'], email=user_db['email'], password=user_db['password'])
      else:
        user = Client(nome=user_db['nome'], cognome=user_db['cognome'], client_id=user_db['client_id'], pt_id=user_db['pt_id'], email=user_db['email'], password=user_db['password'])
      login_user(user, True)
      return redirect(url_for('index'))

    flash("Impossibile creare l'utente.", "danger")
    return redirect(url_for('signup'))
  else:
    return render_template('signup.html')

# Pagina di Login
#
@app.route('/login', methods=['GET','POST'])
def login():
  if request.method == 'POST':
    form_user = request.form.to_dict()
    print("form",form_user)
    user_db, type = utenti_dao.get_user_by_email(form_user['email'])
    
    if not user_db or not check_password_hash(user_db['password'], form_user['password']):
      flash("Email o password errata.","danger")
      return redirect(url_for('login'))
    else:
      if type == 0:
        new_user = PersonalTrainer(nome=user_db['nome'], cognome=user_db['cognome'], pt_id=user_db['pt_id'], rating=user_db['rating'], numOfRatings=user_db['numOfRatings'], email=user_db['email'], password=user_db['password'])
      else:
        new_user = Client(nome=user_db['nome'], cognome=user_db['cognome'], client_id=user_db['client_id'], pt_id=user_db['pt_id'], email=user_db['email'], password=user_db['password'])
      login_user(new_user, True)

      return redirect(url_for('index'))
  else:
    return render_template('login.html')


@login_manager.user_loader
def load_user(user_email):
  print("load user:", user_email)
  user_db, type = utenti_dao.get_user_by_email(user_email)
  if type == 0:
    user = PersonalTrainer(nome=user_db['nome'], cognome=user_db['cognome'], pt_id=user_db['pt_id'], rating=user_db['rating'], numOfRatings=user_db['numOfRatings'], email=user_db['email'], password=user_db['password'])
  else:
    user = Client(nome=user_db['nome'], cognome=user_db['cognome'], client_id=user_db['client_id'], pt_id=user_db['pt_id'], email=user_db['email'], password=user_db['password'])
  return user


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Pagina per la Creazione di un Allenamento
#
@app.route("/create_workout",methods=['GET','POST'])
def create_workout():
  if request.method == 'POST':
    new_workout = request.form.to_dict()
    print("workout:",new_workout)
    
    email = utenti_dao.get_email(request)
    pt_id = utenti_dao.get_user_id_by_email(email)

    visibilita = new_workout.get("pubblico", "privato")
    if visibilita == "pubblico":
      new_workout['visibile'] = 1
    else:
      new_workout['visibile'] = 0

    if new_workout['titolo'] == '':
      app.logger.error('Il campo non può essere vuoto')
      return redirect(url_for('index'))
    
    if new_workout['description'] == '':
      app.logger.error('Il campo non può essere vuoto')
      return redirect(url_for('index'))  

    if new_workout['livello'] == '':
      app.logger.error('Il campo non può essere vuoto')
      return redirect(url_for('index'))  

    success = allenamenti_dao.create_allenamento(new_workout,pt_id)

    if success:
      return redirect(url_for('index'))
    flash("Impossibile creare l'allenamento.", "danger")
    return redirect(url_for('create_workout'))
  
  else:
    return render_template('create_workout.html')


# Pagina Profilo di un Personal Trainer
#
@app.route("/profile")
def pt_profile():
  email = utenti_dao.get_email(request)
  pt_id = utenti_dao.get_user_id_by_email(email)
  public_workouts = []
  private_workouts = []
  allenamenti_pt_db = allenamenti_dao.get_allenamenti_by_pt(pt_id)
  for workout in allenamenti_pt_db:
    if workout['visibile'] == 0:
      private_workouts.append(workout)
    else:
      public_workouts.append(workout)

  return render_template('profile.html', public_workouts=public_workouts, private_workouts=private_workouts)


# Pagina di Modifica di un Allenamento
#
@app.route("/modify_workout/<int:id_allenamento>", methods=['POST','GET'])
def modify_workout(id_allenamento):
  if request.method == 'POST':
    workout = request.form.to_dict()
    print("workout to modify:",workout)

    visibilita = workout.get("pubblico", "privato")
    if visibilita == "pubblico":
      workout['visibile'] = 1
    else:
      workout['visibile'] = 0

    # print(form.get("pubblico", "privato"))
    if workout['titolo'] == '':
      app.logger.error('Il campo non può essere vuoto')
      return redirect(url_for('index'))
    
    if workout['description'] == '':
      app.logger.error('Il campo non può essere vuoto')
      return redirect(url_for('index'))  

    if workout['livello'] == '':
      app.logger.error('Il campo non può essere vuoto')
      return redirect(url_for('index'))  

    workout['id_allenamento'] = id_allenamento
    success = allenamenti_dao.modifica_allenamento(workout)

    if not success:
      flash("Impossibile modificare l'allenamento.", "danger")
    return redirect(url_for('pt_profile'))
  
  else:
    allenamento_db = allenamenti_dao.get_allenamento(id_allenamento)
    return render_template("modify_workout.html", allenamento=allenamento_db)


# Eliminazione di un Allenamento
#
@app.route("/delete_workout/<int:id_allenamento>", methods=['POST'])
def delete_workout(id_allenamento):
  success = allenamenti_dao.delete_workout(id_allenamento)
  if not success:
    flash("Impossibile eliminare l'allenamento.", "danger")
  return redirect(url_for("pt_profile"))

# Assunzione di un Personal Trainer
#
@app.route("/assumi_pt/<int:pt_id>", methods=['POST'])
def assumi_pt(pt_id):
  email = utenti_dao.get_email(request)
  client_id = utenti_dao.get_user_id_by_email(email)
  print("assumi_pt:", email, client_id, pt_id)
  success = utenti_dao.set_pt_id(pt_id, client_id)
  if not success:
    flash("Impossibile assumere il personal trainer.", "danger")
  return redirect(url_for("index"))

# Pagina per le Schede
#
@app.route("/schede")
def schede():
  email = utenti_dao.get_email(request)
  user, type = utenti_dao.get_user_by_email(email)
  
  if type == 0: # A pt is logged
    client_id = request.args.get("client_id")
    # retrieve name of client 
    name = utenti_dao.get_full_name_client(client_id)
  else: # A client is logged
    client_id = user['client_id']
    # retrieve name of pt
    name = utenti_dao.get_full_name_pt(user['pt_id'])
  
  schede = schede_dao.get_schede_by_client_id(client_id)

  # crea dizionario con chiavi==id_scheda e values==lista di allenamenti della scheda
  schede_ids = [scheda['id_scheda'] for scheda in schede]
  allenamenti_by_id_scheda = {}
  for id_scheda in schede_ids:
    # id dei workout presenti nella scheda: lista di oggetti
    workout_ids = schede_dao.get_allenamenti_ids_by_id_scheda(id_scheda)
    # id dei workout presenti nella scheda: lista di interi
    ids = [obj['id_allenamento'] for obj in workout_ids]
    # info dei workout presenti nella scheda
    allenamenti_obj_by_id_scheda=[allenamenti_dao.get_allenamento(id) for id in ids]
    # dizionario con chiavi: id_scheda e valori: lista allenamenti presenti 
    allenamenti_by_id_scheda[id_scheda] = allenamenti_obj_by_id_scheda

  return render_template("schede.html",client_id=client_id,schede=schede,allenamenti=allenamenti_by_id_scheda,name=name)

# Pagina per la creazione di una Scheda
#
@app.route("/create_scheda",methods=['GET','POST'])
def create_scheda():
  if request.method == 'POST':
    ids = request.form.getlist("ids")
    email = utenti_dao.get_email(request)
    pt_id = utenti_dao.get_user_id_by_email(email)
    client_id = request.form.get('client_id')
    new_scheda = request.form.to_dict()
    success = schede_dao.create_scheda(ids,pt_id,new_scheda)
    if success:
      return redirect(url_for("schede", client_id=client_id))
    flash("Impossibile creare la scheda.", "danger")
    return redirect(url_for("create_scheda"))

  else:
    allenamenti_db = allenamenti_dao.get_allenamenti()
    allenamenti = []
    email = utenti_dao.get_email(request)
    pt_id = utenti_dao.get_user_id_by_email(email)
    client_id = request.args.get("client_id")
    print("create_scheda:",client_id)

    for allenamento in allenamenti_db:
      if allenamento['visibile'] == 1 or allenamento['pt_id'] == pt_id:
        allenamenti.append(allenamento)
    return render_template("create_scheda.html",allenamenti=allenamenti, client_id=client_id)

# Valutazione di una Scheda
#
@app.route("/update_rating", methods=['POST'])
def update_rating():
  form_data = request.form.to_dict()
  print("update_rating",form_data)
  email = utenti_dao.get_email(request)
  client = utenti_dao.get_user_by_email(email)[0]
  pt_id = client["pt_id"]

  if form_data['id_scheda'] == '':
    app.logger.error('Il campo non può essere vuoto')
    return redirect(url_for('index'))
    
  if form_data['rating'] == '':
    app.logger.error('Il campo non può essere vuoto')
    return redirect(url_for('index'))
  
  success = schede_dao.set_rating(form_data['id_scheda'], form_data['rating'])

  if form_data['oldRating'] == 'None':
    print("votoNuovo: si")
    utenti_dao.update_pt_rating(pt_id, form_data['rating'], votoNuovo=True)
  else:
    print("votoNuovo: no")
    utenti_dao.update_pt_rating(pt_id, form_data['rating'], votoNuovo=False, oldRating=form_data['oldRating'])
  
  if success:
    return redirect(url_for("schede",client_id=client['client_id'])) 
  flash("Impossibile aggiornare il rating.", "danger")
  return redirect(url_for("index"))

# Eliminazione di una Scheda
#
@app.route("/delete_scheda", methods=['POST'])
def delete_scheda():
  id_scheda = request.form.get("id_scheda")
  if id_scheda is None:
    app.logger.error('Il campo non può essere vuoto')
    return redirect(url_for('index'))
  
  client_id = schede_dao.get_client_id_by_id_scheda(id_scheda)
  success = schede_dao.delete_scheda(id_scheda)
  if not success:
    flash("Impossibile eliminare la scheda.", "danger")
  return redirect (url_for("schede",client_id=client_id)) 

# Pagina di Modifica di una Scheda
#
@app.route("/modify_scheda/<int:id_scheda>", methods=['POST','GET'])
def modify_scheda(id_scheda):
  if request.method == 'POST':
    client_id = schede_dao.get_client_id_by_id_scheda(id_scheda)
    scheda = request.form.to_dict()
    print(scheda)
  
    if scheda['titolo'] == '':
        app.logger.error('Il campo non può essere vuoto')
        return redirect(url_for('index'))
      
    if scheda['obiettivo'] == '':
      app.logger.error('Il campo non può essere vuoto')
      return redirect(url_for('index'))  

    scheda['id_scheda'] = id_scheda
    ids = request.form.getlist("ids")

    print("modify scheda:", ids)

    success = schede_dao.update_scheda(scheda, ids)

    if success:
      return redirect(url_for("schede", client_id=client_id))
    flash("Impossibile modificare la scheda.", "danger")
    return redirect(url_for("index"))
  
  else:
    email = utenti_dao.get_email(request)
    pt_id = utenti_dao.get_user_id_by_email(email)

    scheda = schede_dao.get_scheda_by_id(id_scheda)
    allenamenti_ids = schede_dao.get_allenamenti_ids_by_id_scheda(id_scheda)
    ids = [id['id_allenamento'] for id in allenamenti_ids]
    selected = [allenamenti_dao.get_allenamento(id) for id in ids]

    allenamenti_db = allenamenti_dao.get_allenamenti()
    allenamenti=[]
    for allenamento in allenamenti_db:
      if allenamento['visibile'] == 1 or allenamento['pt_id'] == pt_id:
        allenamenti.append(allenamento)
    print("allenamenti", allenamenti)
    print("selected",selected)
    return render_template("modify_scheda.html", scheda=scheda,allenamenti=allenamenti,selected=selected)