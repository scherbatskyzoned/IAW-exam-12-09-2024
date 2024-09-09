from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

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
  id = 0
  numOfSchede = {}
  public_workouts = []
  creators = {}

  email = utenti_dao.get_email(request)
  if email is not None:
    user, tipo = utenti_dao.get_user_by_email(email)
    if tipo == 0: # it's a pt
      id = user['pt_id']
      for workout in allenamenti_db:
        if workout['visibile']:
          public_workouts.append(workout)
          creators[workout['id_allenamento']] = utenti_dao.get_full_name(workout['pt_id'],'pt')
      
      clienti_db = utenti_dao.get_pt_clients(id)
      clienti_ids = [client['client_id'] for client in clienti_db]
      for id in clienti_ids:
        numOfSchede[id] = schede_dao.get_num_schede_by_client(id)[0]
      
  return render_template('index.html', public_workouts=public_workouts, pts=pts_db, clienti=clienti_db, numOfSchede=numOfSchede,creators=creators) 


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
    if new_user['name'].strip() == '':
      app.logger.error('Il campo non può essere vuoto')
      flash("Impossibile creare l'utente.", "danger")
      return redirect(url_for('index'))
    
    if new_user['surname'].strip() == '':
      app.logger.error('Il campo non può essere vuoto')
      flash("Impossibile creare l'utente.", "danger")
      return redirect(url_for('index'))

    if new_user['genere'].strip() == '':
      app.logger.error('Il campo non può essere vuoto')
      flash("Impossibile creare l'utente.", "danger")
      return redirect(url_for('index'))

    if new_user['email'].strip() == '':
      app.logger.error('Il campo non può essere vuoto')
      flash("Impossibile creare l'utente.", "danger")
      return redirect(url_for('index'))
    
    if new_user['tipo'].strip() == '':
      app.logger.error('Il campo non può essere vuoto')
      flash("Impossibile creare l'utente.", "danger")
      return redirect(url_for('index'))
    
    if new_user['password'].strip() == '':
      app.logger.error('Il campo non può essere vuoto')
      flash("Impossibile creare l'utente.", "danger")
      return redirect(url_for('index'))
    
    new_user['password'] = generate_password_hash(new_user['password'])

    new_user['name'] = new_user['name'].capitalize()
    new_user['surname'] = new_user['surname'].capitalize()

    success = False
    if new_user['tipo'] == 'personal_trainer':
      success = utenti_dao.create_pt(new_user)
    elif new_user['tipo'] == 'client':
      success = utenti_dao.create_client(new_user)

    if success:
      user_db = utenti_dao.get_user_by_email(new_user['email'])[0]
      if new_user['tipo'] == 'personal_trainer':
        user = PersonalTrainer(nome=user_db['nome'], cognome=user_db['cognome'], genere=user_db['genere'], pt_id=user_db['pt_id'], rating=user_db['rating'], numOfRatings=user_db['numOfRatings'], email=user_db['email'], password=user_db['password'])
      else:
        user = Client(nome=user_db['nome'], cognome=user_db['cognome'], genere=user_db['genere'], client_id=user_db['client_id'], pt_id=user_db['pt_id'], email=user_db['email'], password=user_db['password'])
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
    user_db, type = utenti_dao.get_user_by_email(form_user['email'])
    
    if not user_db or not check_password_hash(user_db['password'], form_user['password']):
      flash("Email o password errata.","danger")
      return redirect(url_for('login'))
    else:
      if type == 0:
        new_user = PersonalTrainer(nome=user_db['nome'], cognome=user_db['cognome'], genere=user_db['genere'], pt_id=user_db['pt_id'], rating=user_db['rating'], numOfRatings=user_db['numOfRatings'], email=user_db['email'], password=user_db['password'])
      else:
        new_user = Client(nome=user_db['nome'], cognome=user_db['cognome'], genere=user_db['genere'], client_id=user_db['client_id'], pt_id=user_db['pt_id'], email=user_db['email'], password=user_db['password'])
      login_user(new_user, True)

      return redirect(url_for('index'))
  else:
    return render_template('login.html')


@login_manager.user_loader
def load_user(user_email):
  user_db, type = utenti_dao.get_user_by_email(user_email)
  if type == 0:
    user = PersonalTrainer(nome=user_db['nome'], cognome=user_db['cognome'], genere=user_db['genere'], pt_id=user_db['pt_id'], rating=user_db['rating'], numOfRatings=user_db['numOfRatings'], email=user_db['email'], password=user_db['password'])
  else:
    user = Client(nome=user_db['nome'], cognome=user_db['cognome'], genere=user_db['genere'], client_id=user_db['client_id'], pt_id=user_db['pt_id'], email=user_db['email'], password=user_db['password'])
  return user


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# Pagina Profilo di un Personal Trainer
#
@app.route("/profile")
def pt_profile():
  email = utenti_dao.get_email(request)
  pt_id = utenti_dao.get_user_id_by_email(email,'pt')
  public_workouts = []
  private_workouts = []
  allenamenti_pt_db = allenamenti_dao.get_allenamenti_by_pt(pt_id)
  for workout in allenamenti_pt_db:
    if workout['visibile'] == 0:
      private_workouts.append(workout)
    else:
      public_workouts.append(workout)

  return render_template('profile.html', public_workouts=public_workouts, private_workouts=private_workouts)


# Assunzione di un Personal Trainer
#
@app.route("/assumi_pt/<int:pt_id>", methods=['POST'])
def assumi_pt(pt_id):
  email = utenti_dao.get_email(request)
  client_id = utenti_dao.get_user_id_by_email(email,'client')
  success = False

  # Check client has not already a personal trainer
  pt_id_client = utenti_dao.get_user_by_email(email)[0]['pt_id']
  if pt_id_client is None:
    success = utenti_dao.set_pt_id(pt_id, client_id)
  if not success:
    flash("Impossibile assumere il personal trainer.", "danger")
  
  flash("Personal trainer assunto con successo.", "success")
  return redirect(url_for("index"))


# Pagina per la Creazione di un Allenamento
#
@app.route("/create_workout",methods=['GET','POST'])
def create_workout():
  if request.method == 'POST':
    new_workout = request.form.to_dict()
    
    email = utenti_dao.get_email(request)
    pt_id = utenti_dao.get_user_id_by_email(email, 'pt')

    visibilita = new_workout.get("pubblico", "privato")
    if visibilita == "pubblico":
      new_workout['visibile'] = 1
    else:
      new_workout['visibile'] = 0

    if new_workout['titolo'].strip() == '':
      app.logger.error('Il campo non può essere vuoto')
      flash("Impossibile creare l'allenamento.", "danger")
      return redirect(url_for('index'))
    
    if new_workout['description'].strip() == '':
      app.logger.error('Il campo non può essere vuoto')
      flash("Impossibile creare l'allenamento.", "danger")
      return redirect(url_for('index'))  

    if new_workout['livello'].strip() == '':
      app.logger.error('Il campo non può essere vuoto')
      flash("Impossibile creare l'allenamento.", "danger")
      return redirect(url_for('index'))  

    new_workout['livello'] = new_workout['livello'].capitalize()
    
    success = allenamenti_dao.create_allenamento(new_workout,pt_id)

    if success:
      flash("Allenamento creato con successo.", "success")
      return redirect(url_for('index'))
    flash("Impossibile creare l'allenamento.", "danger")
    return redirect(url_for('create_workout'))
  
  else:
    return render_template('create_workout.html')


# Pagina di Modifica di un Allenamento
#
@app.route("/modify_workout/<int:id_allenamento>", methods=['POST','GET'])
def modify_workout(id_allenamento):
  if request.method == 'POST':
    workout = request.form.to_dict()

    pt_id_workout = allenamenti_dao.get_allenamento(id_allenamento)['pt_id']
    workout['pt_id'] = pt_id_workout
    email = utenti_dao.get_email(request)
    pt_id = utenti_dao.get_user_id_by_email(email,'pt')

    # Check that the pt is the creator of the workout
    if (pt_id_workout != pt_id):
      flash("Non hai i permessi per modificare l'allenamento.", "danger")
      return redirect(url_for('pt_profile'))

    visibilita = workout.get("pubblico", "privato")
    if visibilita == "pubblico":
      workout['visibile'] = 1
    else:
      workout['visibile'] = 0

    if workout['titolo'].strip() == '':
      app.logger.error('Il campo non può essere vuoto')
      flash("Impossibile modificare l'allenamento.", "danger")
      return redirect(url_for('index'))
    
    if workout['description'].strip() == '':
      app.logger.error('Il campo non può essere vuoto')
      flash("Impossibile modificare l'allenamento.", "danger")
      return redirect(url_for('index'))  

    if workout['livello'].strip() == '':
      app.logger.error('Il campo non può essere vuoto')
      flash("Impossibile modificare l'allenamento.", "danger")
      return redirect(url_for('index'))  

    workout['livello'] = workout['livello'].capitalize()
    workout['id_allenamento'] = id_allenamento
    success = allenamenti_dao.modifica_allenamento(workout)

    if not success:
      flash("Impossibile modificare l'allenamento.", "danger")
      return redirect(url_for('pt_profile'))

    flash("Allenamento modificato con successo.", "success")
    return redirect(url_for('pt_profile'))
  
  else:
    allenamento_db = allenamenti_dao.get_allenamento(id_allenamento)
    return render_template("modify_workout.html", allenamento=allenamento_db)


# Eliminazione di un Allenamento
#
@app.route("/delete_workout", methods=['POST'])
def delete_workout():
  workout_id = request.form.get("workout_id")
  if workout_id is None:
    app.logger.error('Il campo non può essere vuoto')
    return redirect(url_for('pt_profile'))
  
  pt_id_workout = allenamenti_dao.get_allenamento(workout_id)['pt_id']
  email = utenti_dao.get_email(request)
  pt_id = utenti_dao.get_user_id_by_email(email,'pt')

  # Check that the pt is the creator of the workout
  if (pt_id_workout != pt_id):
    flash("Non hai i permessi per eliminare l'allenamento.", "danger")
    return redirect(url_for('pt_profile'))
  
  success = allenamenti_dao.delete_workout(workout_id)
  if not success:
    flash("Impossibile eliminare l'allenamento.", "danger")

  flash("Allenamento eliminato con successo.", "success")
  return redirect(url_for("pt_profile"))


# Pagina per le Schede
#
@app.route("/schede")
def schede():
  email = utenti_dao.get_email(request)
  user, type = utenti_dao.get_user_by_email(email)
  
  if type == 0: # A pt is logged
    client_id = request.args.get("client_id")
    # retrieve name of client 
    name = utenti_dao.get_full_name(client_id, 'client')
  else: # A client is logged
    client_id = user['client_id']
    # retrieve name of pt
    name = utenti_dao.get_full_name(user['pt_id'],'pt')
  
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
    pt_id = utenti_dao.get_user_id_by_email(email,'pt')
    client_id = request.form.get('client_id')
    new_scheda = request.form.to_dict()
    pt_id_client = utenti_dao.get_client(client_id)['pt_id']
    success = False

    # Check that the pt is the one hired by the client
    if (pt_id_client != pt_id):
      flash("Non hai i permessi per creare la scheda.", "danger")
      return redirect(url_for('index'))
    # Check that the plan has more than 2 exercises
    if len(ids) >= 2:
      success = schede_dao.create_scheda(ids,pt_id,new_scheda)
    if success:
      flash("Scheda creata con successo.", "success")
      return redirect(url_for("schede", client_id=client_id))
    flash("Impossibile creare la scheda.", "danger")
    return redirect(url_for("create_scheda",client_id=client_id))

  else:
    allenamenti_db = allenamenti_dao.get_allenamenti()
    allenamenti = []
    email = utenti_dao.get_email(request)
    pt_id = utenti_dao.get_user_id_by_email(email,'pt')
    client_id = request.args.get("client_id")

    for allenamento in allenamenti_db:
      if allenamento['visibile'] == 1 or allenamento['pt_id'] == pt_id:
        allenamenti.append(allenamento)
    return render_template("create_scheda.html",allenamenti=allenamenti, client_id=client_id)


# Valutazione di una Scheda
#
@app.route("/update_rating", methods=['POST'])
def update_rating():
  form_data = request.form.to_dict()
  email = utenti_dao.get_email(request)
  client = utenti_dao.get_user_by_email(email)[0]
  pt_id = client["pt_id"]

  if form_data['id_scheda'].strip() == '':
    app.logger.error('Il campo non può essere vuoto')
    return redirect(url_for('index'))
    
  if form_data['rating'].strip() == '':
    app.logger.error('Il campo non può essere vuoto')
    return redirect(url_for('index'))
  
  success = schede_dao.set_rating(form_data['id_scheda'], form_data['rating'])

  if form_data['oldRating'] == 'None': # Primo voto inserito
    utenti_dao.update_pt_rating(pt_id, form_data['rating'], votoNuovo=True)
  else: # Voto modificato
    utenti_dao.update_pt_rating(pt_id, form_data['rating'], votoNuovo=False, oldRating=form_data['oldRating'])
  
  if success:
    flash("Valutazione inserita con successo.", "success")
    return redirect(url_for("schede",client_id=client['client_id'])) 
  flash("Impossibile aggiornare il rating.", "danger")
  return redirect(url_for("index"))


# Pagina di Modifica di una Scheda
#
@app.route("/modify_scheda/<int:id_scheda>", methods=['POST','GET'])
def modify_scheda(id_scheda):
  if request.method == 'POST':
    client_id = schede_dao.get_client_id_by_id_scheda(id_scheda)
    scheda = request.form.to_dict()

    pt_id_scheda = schede_dao.get_scheda_by_id(id_scheda)['pt_id']
    email = utenti_dao.get_email(request)
    pt_id = utenti_dao.get_user_id_by_email(email,'pt')

    # Check that the pt is the creator of the workout plan
    if (pt_id_scheda != pt_id):
      flash("Non hai i permessi per modificare la scheda.", "danger")
      return redirect(url_for('index'))
  
    if scheda['titolo'].strip() == '':
        app.logger.error('Il campo non può essere vuoto')
        flash("Impossibile modificare la scheda.", "danger")
        return redirect(url_for('index'))
      
    if scheda['obiettivo'].strip() == '':
      app.logger.error('Il campo non può essere vuoto')
      flash("Impossibile modificare la scheda.", "danger")
      return redirect(url_for('index'))  

    scheda['id_scheda'] = id_scheda
    ids = request.form.getlist("ids")

    success = False
    if len(ids) >= 2:
      success = schede_dao.update_scheda(scheda, ids)

    if success:
      flash("Scheda modificata con successo.", "success")
      return redirect(url_for("schede", client_id=client_id))
    flash("Impossibile modificare la scheda.", "danger")
    return redirect(url_for("schede", client_id=client_id))
  
  else:
    email = utenti_dao.get_email(request)
    pt_id = utenti_dao.get_user_id_by_email(email,'pt')

    # Get the already selected workouts
    scheda = schede_dao.get_scheda_by_id(id_scheda)
    allenamenti_ids = schede_dao.get_allenamenti_ids_by_id_scheda(id_scheda)
    ids = [id['id_allenamento'] for id in allenamenti_ids]
    selected = [allenamenti_dao.get_allenamento(id) for id in ids]

    # Get all the possible workouts to put in the plan
    allenamenti_db = allenamenti_dao.get_allenamenti()
    allenamenti=[]
    for allenamento in allenamenti_db:
      if allenamento['visibile'] == 1 or allenamento['pt_id'] == pt_id:
        allenamenti.append(allenamento)
    return render_template("modify_scheda.html", scheda=scheda,allenamenti=allenamenti,selected=selected)
  

# Eliminazione di una Scheda
#
@app.route("/delete_scheda", methods=['POST'])
def delete_scheda():
  id_scheda = request.form.get("id_scheda")
  if id_scheda is None:
    app.logger.error('Il campo non può essere vuoto')
    return redirect(url_for('index'))
  
  client_id = schede_dao.get_client_id_by_id_scheda(id_scheda)

  pt_id_scheda = schede_dao.get_scheda_by_id(id_scheda)['pt_id']
  email = utenti_dao.get_email(request)
  pt_id = utenti_dao.get_user_id_by_email(email,'pt')

  # Check that the pt is the creator of the workout plan
  if (pt_id_scheda != pt_id):
    flash("Non hai i permessi per eliminare la scheda.", "danger")
    return redirect(url_for('index'))

  success = schede_dao.delete_scheda(id_scheda)
  if not success:
    flash("Impossibile eliminare la scheda.", "danger")
  flash("Scheda eliminata con successo.", "success")
  return redirect (url_for("schede",client_id=client_id)) 