from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash

import utenti_dao, allenamenti_dao, schede_dao
from models import PersonalTrainer, Client

# create app
app = Flask(__name__)
app.config['SECRET_KEY'] = 's3cr3t_v41u3'

login_manager = LoginManager()
login_manager.init_app(app)


# Homepage
@app.route('/')
def index():
  allenamenti_db = allenamenti_dao.get_allenamenti()
  pts_db = utenti_dao.get_personal_trainers()
  clienti_db = []
  pt_id = 0

  email = request.cookies.get('remember_token')
  if email is not None:
    email = email.split('|')[0]
    pt_id = utenti_dao.get_pt_id_by_email(email)
  if pt_id != 0:
    clienti_db = utenti_dao.get_pt_clients(pt_id)
  return render_template('index.html', allenamenti=allenamenti_db, pts=pts_db, clienti=clienti_db) 

# define the about page
@app.route('/about')
def about():
  return render_template('about.html')

# define the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
  if request.method == 'POST':
    new_user = request.form.to_dict()
    print(new_user)

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
      return redirect(url_for('index'))
    return redirect(url_for('signup'))
  else:
    return render_template('signup.html')


@app.route('/login', methods=['GET','POST'])
def login():
  if request.method == 'POST':
    form_user = request.form.to_dict()
    # @type: 0 if personal_trainer, 1 if client
    print("app.py email", form_user['email'])
    user_db, type = utenti_dao.get_user_by_email(form_user['email'])
    print("post chiamata:", user_db['email'])
    
    if not user_db or not check_password_hash(user_db['password'], form_user['password']):
      flash("L'utente non esiste.")
      return redirect(url_for('index'))
    else:
      if type == 0:
        new_user = PersonalTrainer(nome=user_db['nome'], cognome=user_db['cognome'], pt_id=user_db['pt_id'], rating=user_db['rating'], numOfRatings=user_db['numOfRatings'], email=user_db['email'], password=user_db['password'])
      else:
        new_user = Client(nome=user_db['nome'], cognome=user_db['cognome'], client_id=user_db['client_id'], pt_id=user_db['pt_id'], email=user_db['email'], password=user_db['password'])
      login_user(new_user, True)
      flash('Success!')
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

# define create_allenamento page
@app.route("/create_workout",methods=['GET','POST'])
def create_workout():
  if request.method == 'POST':
    new_workout = request.form.to_dict()
    print("workout",new_workout)
    
    email = request.cookies.get('remember_token').split('|')[0]
    pt_id = utenti_dao.get_pt_id_by_email(email)

    visibilita = new_workout.get("pubblico", "privato")
    if visibilita == "pubblico":
      new_workout['visibile'] = 1
    else:
      new_workout['visibile'] = 0

    # print(form.get("pubblico", "privato"))
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
    return redirect(url_for('create_workout'))
  
  else:
    return render_template('create_workout.html')


# define pt profile page
@app.route("/profile")
def pt_profile():
  email = request.cookies.get('remember_token').split('|')[0]
  pt_id = utenti_dao.get_pt_id_by_email(email)
  allenamenti_pt_db = allenamenti_dao.get_allenamenti_by_pt(pt_id)
  return render_template('profile.html',allenamenti=allenamenti_pt_db)


# define modify page for workouts
@app.route("/modify_workout/<int:id_allenamento>", methods=['POST','GET'])
def modify_workout(id_allenamento):
  if request.method == 'POST':
    workout = request.form.to_dict()
    print("workout to modify",workout)

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

    if success:
      return redirect(url_for('pt_profile'))
    return redirect(url_for('index'))
  
  else:
    allenamento_db = allenamenti_dao.get_allenamento(id_allenamento)
    return render_template("modify_workout.html", allenamento=allenamento_db)


# define delete page for workouts
@app.route("/delete_workout/<int:id_allenamento>", methods=['POST'])
def delete_workout(id_allenamento):
  allenamenti_dao.delete_workout(id_allenamento)
  return redirect(url_for("pt_profile"))

# define page for assuming a personal trainer
@app.route("/assumi_pt/<int:pt_id>", methods=['POST'])
def assumi_pt(pt_id):
  email = request.cookies.get('remember_token').split('|')[0]
  client_id = utenti_dao.get_client_id_by_email(email)
  print("assumi_pt", email, client_id, pt_id)
  utenti_dao.set_pt_id(pt_id, client_id)
  return redirect(url_for("index"))

# define page for schede
@app.route("/schede")
def schede():
  client_id = request.args.get("client_id")
  print("schede",client_id)
  # vedi tutte le schede relative al client
  schede = schede_dao.get_schede_by_client_id(client_id)
  return render_template("schede.html",client_id=client_id,schede=schede)

# define page to create schede
@app.route("/create_scheda",methods=['GET','POST'])
def create_scheda():
  if request.method == 'POST':
    ids = request.form.getlist("ids")
    print(ids)
    email = request.cookies.get('remember_token').split('|')[0]
    pt_id = utenti_dao.get_pt_id_by_email(email)
    client_id = request.form.get("client_id")

    print("POST create_scheda client_id",client_id)
    success = schede_dao.create_scheda(ids,pt_id,client_id)
    if success:
      return redirect(url_for("index"))
    return redirect(url_for("create_scheda"))

  else:
    allenamenti_db = allenamenti_dao.get_allenamenti()
    allenamenti = []
    email = request.cookies.get('remember_token').split('|')[0]
    pt_id = utenti_dao.get_pt_id_by_email(email)
    client_id = request.args.get("client_id")
    print("create_scheda",client_id)
    # need to know client

    for allenamento in allenamenti_db:
      if allenamento['visibile'] == 1 or allenamento['pt_id'] == pt_id:
        allenamenti.append(allenamento)
    return render_template("create_scheda.html",allenamenti=allenamenti_db, client_id=client_id)

# if __name__ == "__main__":
#  app.run(host='0.0.0.0', port=3000, debug= True)