from flask import Flask, request, jsonify, render_template, url_for, redirect
import sqlite3
import hashlib

app = Flask(__name__)


def get_role(username):
    connection = sqlite3.connect("databases/roles.db")
    cursor = connection.cursor()
    curr_request = 'SELECT Role FROM Roles JOIN UsersRoles ON Roles.Id = RoleId WHERE Username = "' + username + '"'
    cursor.execute(curr_request)
    role = cursor.fetchone()
    connection.close()
    return role


# Регистрация пользователя
@app.route('/register/', methods=['POST', 'get'])
def register():
    if request.method == 'POST':
        print(request.form)
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('databases/users.db')
        c = conn.cursor()
        # Хэшируем пароль перед сохранением в базу данных
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        curr_request = "SELECT * FROM users WHERE username = " + '''"''' + username + '''"'''
        c.execute(curr_request)
        user = c.fetchone()
        if user:
            message = "The user with the same name exists. Try to come up with another name."
            return render_template('login.html', message=message)
        else:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
    else:
        return render_template('register.html', message='Registration')


# Авторизация пользователя
@app.route('/login/', methods=['post', 'get'])
def login():
    message = ''
    if request.method == 'POST':
        print(request.form)
        username = request.form.get('username')
        password = request.form.get('password')

        conn = sqlite3.connect('databases/users.db')
        c = conn.cursor()
        # Хэшируем введенный пароль для сравнения с паролем из базы данных
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
        user = c.fetchone()
        conn.close()
        if user:
            role = get_role(username)
            if role:
                if role[0] == 'Admin':
                    return redirect(url_for('admin'))
                elif role[0] == 'Waiter':
                    return redirect(url_for('waiter'))
            else:
                return redirect(url_for('none'))
        else:
            message = "Wrong username or password"
            return render_template('login.html', message=message)
    else:
        return render_template('login.html', message='Log in')


@app.route('/admin/', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        print(request.form)
        username = request.form.get('username')
        role = request.form.get('role')

        connection = sqlite3.connect("databases/roles.db")
        cursor = connection.cursor()
        curr_request = 'SELECT Role FROM Roles JOIN UsersRoles ON Roles.Id = RoleId WHERE Username = "' + username + '"'
        cursor.execute(curr_request)
        curs = cursor.fetchone()
        if curs:
            cursor.close()
            return render_template('admin.html', message='This person already had a role.')
        else:
            curr_request = 'SELECT max(Id) FROM UsersRoles'
            cursor.execute(curr_request)
            id = cursor.fetchall()[0][0]
            cursor.execute("INSERT INTO UsersRoles (Id, Username, RoleId) VALUES (?, ?, ?)", (id + 1, username, role))
            connection.commit()
            connection.close()
            return render_template('admin.html', message='Successfully add a role.')
    else:
        return render_template('admin.html', message='Succesfully logged in, administrator! :)')


@app.route('/waiter/', methods=['GET'])
def waiter():
    return render_template('waiter.html', message='Succesfully logged in, waiter! :)')


@app.route('/none/', methods=['GET'])
def none():
    return render_template('none.html', message="You don't have permission :(")


if __name__ == '__main__':
    app.run(debug=True)
