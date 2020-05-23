from flask import Flask, flash, render_template, request, redirect, url_for, session
from flaskext.mysql import MySQL

import re

app = Flask(__name__)

app.secret_key = 'sfsu'

app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'March-99'
app.config['MYSQL_DATABASE_DB'] = 'gatorsportsDB'
app.config['MYSQL_DATABASE_HOST'] = 'gatorinstance.ccomimjitskd.us-west-2.rds.amazonaws.com'

class ServerError(Exception):pass

mysql = MySQL()
mysql.init_app(app)
conn = mysql.connect()
cursor = conn.cursor()


########## LOGIN/LOGOUT AUTHENTICATION, REGISTRATION AND HOME PAGE ########## 


@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        cursor.execute('SELECT * FROM Accounts WHERE username = %s AND password = %s', (username, password))
        conn.commit()
        user = cursor.fetchall()

        if user:
            session['loggedin'] = True
            # NOTE: Due to MySQLdb not being compatible for python3.x, 
            #       I implemeted this... yet works. Fix later.
            session['a_id'] = user[0][0]
            session['username'] = user[0][0]
            return redirect(url_for('home'))
        else:
            msg = "Incorrect username/password"
    return render_template('login.html', msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if 'username' and 'password' and 'email' in request.form and request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor.execute('SELECT * FROM Accounts WHERE username LIKE %s OR password LIKE %s', (username, password))
        user = cursor.fetchall()
        if user:
            msg = 'Account already exists!!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must only contain letters and numbers.'
        elif not username or not password or not email:
            msg = 'Please complete the whole form'
        else:
            cursor.execute('INSERT INTO Accounts VALUES (NULL, %s, %s, %s)', (username, password, email))
            conn.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please complete the whole form'
    return render_template('register.html', msg=msg)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('a_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/home')
def home():
    if 'loggedin' in session:
        return render_template('home.html', username = session['username'])
    return redirect(url_for('login.html'))


########## SEARCH UTILITIES ########## 


@app.route('/searchcomp', methods=['GET', 'POST'])
def searchcomp():
    if request.method == "POST":
        competition = request.form['competition']
        cursor.execute("SELECT DISTINCT type_of_sport, location, date from Competition WHERE type_of_sport LIKE %s OR location LIKE %s OR date LIKE %s", (competition, competition, competition))
        conn.commit()
        data = cursor.fetchall()
        
        if len(data) == 0 and competition == 'all': 
            cursor.execute("SELECT DISTINCT type_of_sport, location, date from Competition")
            conn.commit()
            data = cursor.fetchall()
        return render_template('comp.html', data=data)
    return render_template('comp.html')

@app.route('/searchsports', methods=['GET', 'POST'])
def searchsports():
    if request.method == "POST":
        sport = request.form['sport']
        cursor.execute("SELECT DISTINCT type_of_sport, season from Sport WHERE type_of_sport LIKE %s OR season LIKE %s", (sport, sport))
        conn.commit()
        data = cursor.fetchall()
        
        if len(data) == 0 and sport == 'all': 
            cursor.execute("SELECT DISTINCT type_of_sport, season from Sport")
            conn.commit()
            data = cursor.fetchall()
        return render_template('sport.html', data=data)
    return render_template('sport.html')

@app.route('/searchcoach', methods=['GET', 'POST'])
def searchcoach():
    if request.method == "POST":
        coach = request.form['coach']
        cursor.execute("SELECT DISTINCT name, coach_email, type_of_sport from Coach WHERE name LIKE %s OR coach_email LIKE %s OR type_of_sport LIKE %s", (coach, coach, coach))
        conn.commit()
        data = cursor.fetchall()
        
        if len(data) == 0 and coach == 'all': 
            cursor.execute("SELECT DISTINCT name, coach_email, type_of_sport from Coach")
            conn.commit()
            data = cursor.fetchall()
        return render_template('coach.html', data=data)
    return render_template('coach.html')

@app.route('/searchticket', methods=['GET', 'POST'])
def searchticket():
    if request.method == "POST":
        ticket = request.form['ticket']
        cursor.execute("SELECT DISTINCT type_of_sport, ticket_num from Ticket WHERE type_of_sport LIKE %s OR ticket_num LIKE %s", (ticket, ticket))
        conn.commit()
        data = cursor.fetchall()
        
        if len(data) == 0 and ticket == 'all': 
            cursor.execute("SELECT DISTINCT type_of_sport, ticket_num from Ticket")
            conn.commit()
            data = cursor.fetchall()
        return render_template('ticket.html', data=data)
    return render_template('ticket.html')

@app.route('/searchlocations', methods=['GET', 'POST'])
def searchlocations():
    if request.method == "POST":
        locations = request.form['locations']
        cursor.execute("SELECT DISTINCT loc_name from Locations WHERE loc_name LIKE %s", (locations))
        conn.commit()
        data = cursor.fetchall()
        
        if len(data) == 0 and locations == 'all': 
            cursor.execute("SELECT DISTINCT loc_name from Locations")
            conn.commit()
            data = cursor.fetchall()
        return render_template('locations.html', data=data)
    return render_template('locations.html')


########## INSERT UTILITIES ########## 


@app.route('/insertcomp', methods=['GET', 'POST'])
def insertcomp():
    msg = ''
    if request.method == "POST":
        type_of_sport = request.form['type_of_sport']
        location = request.form['location']
        date = request.form['date']
        if type(type_of_sport) and type(location) and type(date) == str:
            cursor.execute("INSERT INTO Competition (type_of_sport, location, date) Values (%s, %s, %s)", (type_of_sport, location, date))
            msg = 'success'
            conn.commit()
        else:
            msg = 'invalid'
        return render_template('insertcomp.html', msg=msg)
    return render_template('insertcomp.html', msg=msg)

@app.route('/insertticket', methods=['GET', 'POST'])
def insertticket():
    msg = ''
    if request.method == "POST":
        type_of_sport = request.form['type_of_sport']
        cursor.execute("INSERT INTO Ticket (type_of_sport, ticket_num) Values (%s, RAND() * 1000)", (type_of_sport))
        conn.commit()
        data = cursor.fetchall()
        msg = "Inserted success!"
        return render_template('insertticket.html', msg=msg)
    return render_template('insertticket.html', msg=msg)

@app.route('/insertcoach', methods=['GET', 'POST'])
def insertcoach():
    msg = ''
    if request.method == "POST":
        name = request.form['name']
        coach_email = request.form['coach_email']
        type_of_sport = request.form['type_of_sport']
        cursor.execute("INSERT INTO Coach (name, coach_email, type_of_sport) Values (%s, %s, %s)", (name, coach_email, type_of_sport))
        conn.commit()
        msg = "Inserted success!"
        return render_template('insertcoach.html', msg=msg)
    return render_template('insertcoach.html', msg=msg)

@app.route('/insertsport', methods=['GET', 'POST'])
def insertsport():
    msg = ''
    if request.method == "POST":
        type_of_sport = request.form['type_of_sport']
        season = request.form['season']
        if type_of_sport.isnumeric() == False and season.isnumeric() == False:
            msg = 'success'
            cursor.execute("INSERT INTO Sport (type_of_sport, season) Values (%s, %s)", (type_of_sport, season))
            conn.commit()
        else:
            msg = "Invalid!"
        return render_template('insertsport.html', msg=msg)
    return render_template('insertsport.html', msg=msg)

@app.route('/insertloc', methods=['GET', 'POST'])
def insertloc():
    msg = ''
    if request.method == "POST":
        loc_name = request.form['loc_name']
        cursor.execute("INSERT INTO Locations (loc_name) Values (%s)", (loc_name))
        conn.commit()
        msg = "Inserted success!"
        return render_template('insertloc.html', msg=msg)
    return render_template('insertloc.html', msg=msg)


########## UPDATE UTILITIES ##########


@app.route('/deletecomp', methods=['GET', 'POST'])
def deletecomp():
    # NOTE: Using SQL statement to display table of current 
    #       values in the database Will be found in other
    #       delete statements for other tables.
    cursor.execute("SELECT DISTINCT * FROM Competition")
    data = cursor.fetchall()
    if request.method == 'POST':
        type_of_sport = request.form['type_of_sport']
        location = request.form['location']
        date = request.form['date']
        cursor.execute("DELETE FROM Competition WHERE type_of_sport=%s AND location=%s AND date=%s", (type_of_sport, location, date))
        conn.commit()
        return redirect(url_for('deletecomp'))
    return render_template('deletecomp.html', value=data)

@app.route('/deletesport', methods=['GET', 'POST'])
def deletesport():
    cursor.execute("SELECT DISTINCT * FROM Sport")
    data = cursor.fetchall()
    if request.method == 'POST':
        type_of_sport = request.form['type_of_sport']
        season = request.form['season']
        cursor.execute("DELETE FROM Sport WHERE type_of_sport=%s AND season=%s", (type_of_sport, season))
        conn.commit()
        return redirect(url_for('deletesport'))
    return render_template('deletesport.html', value=data)

@app.route('/deletecoach', methods=['GET', 'POST'])
def deletecoach():
    cursor.execute("SELECT DISTINCT * FROM Coach")
    data = cursor.fetchall()
    if request.method == 'POST':
        name = request.form['name']
        coach_email = request.form['coach_email']
        type_of_sport = request.form['type_of_sport']
        cursor.execute("DELETE FROM Coach WHERE name=%s AND coach_email=%s AND type_of_sport=%s", (name, coach_email, type_of_sport))
        conn.commit()
        return redirect(url_for('searchcoach'))
    return render_template('deletecoach.html', value=data)

@app.route('/deleteloc', methods=['GET', 'POST'])
def deleteloc():
    cursor.execute("SELECT DISTINCT * FROM Locations")
    data = cursor.fetchall()
    if request.method == 'POST':
        loc_name = request.form['loc_name']
        cursor.execute("DELETE FROM Locations WHERE loc_name=%s", (loc_name))
        conn.commit()
        return redirect(url_for('deleteloc'))
    return render_template('deleteloc.html', value=data)

@app.route('/deleteticket', methods=['GET', 'POST'])
def deleteticket():
    cursor.execute("SELECT DISTINCT * FROM Ticket")
    data = cursor.fetchall()
    if request.method == 'POST':
        type_of_sport  = request.form['type_of_sport']
        ticket_num = request.form['ticket_num']
        cursor.execute("DELETE FROM Ticket WHERE type_of_sport=%s AND ticket_num=%s", (type_of_sport, ticket_num))
        conn.commit()
        return redirect(url_for('deleteticket'))
    return render_template('deleteticket.html', value=data)


########## UPDATE UTILITIES ##########


@app.route('/updatecomp', methods = ['GET', 'POST'])
def updatecomp():
    msg = ''
    cursor.execute("SELECT DISTINCT * FROM Competition")
    data = cursor.fetchall()
    if request.method == "POST":
        cp_id = request.form['cp_id']
        type_of_sport = request.form['type_of_sport']
        location = request.form['location']
        date = request.form['date']
        cursor.execute("UPDATE Competition SET location=%s, date=%s, type_of_sport=%s WHERE cp_id=%s", (location, date, type_of_sport, cp_id))
        conn.commit()
        return redirect(url_for('updatecomp'))
    return render_template('updatecomp.html', value=data)

@app.route('/updatesport', methods=['GET', 'POST'])
def updatesport():
    cursor.execute("SELECT DISTINCT * FROM Sport")
    data = cursor.fetchall()
    if request.method == "POST":
        type_of_sport = request.form['type_of_sport']
        season = request.form['season']
        sp_id = request.form['sp_id']
        cursor.execute("UPDATE Sport SET type_of_sport=%s, season=%s WHERE sp_id=%s", (type_of_sport, season, sp_id))
        conn.commit()
        return redirect(url_for('updatesport'))
    return render_template('updatesport.html', value=data)

@app.route('/updatecoach', methods=['GET', 'POST'])
def updatecoach():
    cursor.execute("SELECT DISTINCT * FROM Coach")
    data = cursor.fetchall()
    if request.method == "POST":
        name = request.form['name']
        coach_email = request.form['coach_email']
        type_of_sport = request.form['type_of_sport']
        c_id = request.form['c_id']
        cursor.execute("UPDATE Coach SET name=%s, coach_email=%s, type_of_sport=%s WHERE c_id=%s", (name, coach_email, type_of_sport, c_id))
        conn.commit()
        return redirect(url_for('updatecoach'))
    return render_template('updatecoach.html', value=data)

@app.route('/updateticket', methods=['GET', 'POST'])
def updateticket():
    cursor.execute("SELECT DISTINCT * FROM Ticket")
    data = cursor.fetchall()
    if request.method == "POST":
        t_id = request.form['t_id']
        type_of_sport = request.form['type_of_sport']
        cursor.execute("UPDATE Ticket SET type_of_sport=%s WHERE t_id=%s", (type_of_sport, t_id))
        conn.commit()
        return redirect(url_for('updateticket'))
    return render_template('updateticket.html', value=data)

if __name__ == '__main__':
    app.debug = True
    app.run(port=3000)