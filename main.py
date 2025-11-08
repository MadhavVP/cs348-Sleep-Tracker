from flask import Flask, redirect, url_for, render_template, request, session
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "askdjndjksanlcdklasnjcaslkndjc"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

class users(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100))
	email = db.Column(db.String(100))
	passw = db.Column(db.String)

	def __init__(self, email, name, passw):
		self.passw = passw
		self.name = name
		self.email = email

class sleepT(db.Model):
	sid = db.Column(db.Integer, primary_key=True)
	day = db.Column(db.Date)
	duration = db.Column(db.Float)
	start = db.Column(db.Time)
	end = db.Column(db.Time)
	user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

	def __init__(self, day, sleep_start, sleep_end, sleep_duration, user_id):
		self.day = day
		self.duration = sleep_duration
		self.start = sleep_start
		self.end = sleep_end
		self.user_id = user_id

@app.route("/")
def home():
	return redirect(url_for("profile"))

@app.route("/filter/", methods=["POST"])
def filter():
	sday = request.form["sday"]
	eday = request.form["eday"]
	stime = request.form["start"]
	etime = request.form["end"]
	mindur = request.form["mindur"]
	maxdur = request.form["maxdur"]

	query = sleepT.query.filter_by(user_id=session["id"])

	if sday:
		query = query.filter(sleepT.day >= datetime.strptime(sday, "%Y-%m-%d").date())
	if eday:
		query = query.filter(sleepT.day <= datetime.strptime(eday, "%Y-%m-%d").date())
	if stime:
		query = query.filter(sleepT.start >= datetime.strptime(stime, "%H:%M").time())
	if etime:
		query = query.filter(sleepT.end <= datetime.strptime(etime, "%H:%M").time())
	if mindur:
		query = query.filter(sleepT.duration >= float(mindur))
	if maxdur:
		query = query.filter(sleepT.duration <= float(maxdur))
	
	sleeps = query.all()
	ts = sum(s.duration for s in sleeps if s.duration)
	return render_template("filter.html", sleeps=sleeps, total_sleep=ts)

@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		session.permanent = True
		user = request.form["email"]
		passw = request.form["passw"]
		print(user, passw)
		if request.form["form_name"] == "create":
				print("Creating user!!!!!!!")
				name = request.form["nm"]
				usr = users(user, name, passw)
				db.session.add(usr)
				db.session.commit()
		found_user = users.query.filter_by(email=user).first()
		if not found_user:
			print("No user found")
			return render_template("login.html")
		print(found_user.passw, passw, found_user.name, found_user.email)
		if found_user.passw != passw:
			print("Password check failed")
			return render_template("login.html")
		session["email"] = found_user.email
		session["id"] = found_user.id
		session["name"] = found_user.name
		print("Going to profile")
		return redirect(url_for("profile"))
	return render_template("login.html")

@app.route("/edit/<int:sleep_id>", methods=["GET", "POST"])
def edit(sleep_id):
	if request.method == "POST":
		slep = sleepT.query.filter_by(sid=sleep_id).first()
		start = datetime.strptime(request.form["start"], "%H:%M")
		end = datetime.strptime(request.form["end"], "%H:%M")
		slep.day = datetime.strptime(request.form["day"], "%Y-%m-%d").date()
		if (end - start).total_seconds() <= 0:
					end += timedelta(days=1)
		slep.duration = (end - start).total_seconds() / 3600
		slep.start = start.time()
		slep.end = end.time()
		db.session.commit()
		return render_template("profile.html", name=session["name"], sleeps=sleepT.query.filter_by(user_id=session["id"]).all())
	else:
		return render_template("edit.html", sleep=sleepT.query.get(sleep_id)) 


@app.route("/delete_sleep/<int:sleep_id>", methods=["POST"])
def delete_sleep(sleep_id):
    slep = sleepT.query.get_or_404(sleep_id)
    db.session.delete(slep)
    db.session.commit()
    return redirect(url_for("profile"))

@app.route("/profile", methods=["POST", "GET"])
def profile():
	if "name" in session:
		user = session["name"]
		id = session["id"]
		if request.method == "POST":
			fname = request.form["form_name"]
			start = datetime.strptime(request.form["start"], "%H:%M")
			end = datetime.strptime(request.form["end"], "%H:%M")
			day = datetime.strptime(request.form["day"], "%Y-%m-%d").date()
			if fname == "log":
				if (end - start).total_seconds() <= 0:
					end += timedelta(days=1)
				slep = sleepT(day, start.time(),
				  end.time(), (end - start).total_seconds() / 3600,
				  session["id"])
				db.session.add(slep)
				db.session.commit()
		return render_template("profile.html", name=user, sleeps=sleepT.query.filter_by(user_id=id).all())
	else:
		return redirect(url_for("login"))

@app.route("/logout")
def logout():
	session.pop("user", None)
	return redirect(url_for("login"))

if __name__ == "__main__":
	with app.app_context():
		db.create_all()
	app.run(debug=True)