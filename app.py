from flask import Flask, render_template_string, request, redirect, session, url_for
import random, smtplib, ssl, time
from email.mime.text import MIMEText
import mysql.connector

app = Flask(__name__)
app.secret_key = 'CHANGE_ME'

with open('emsdf.ef', 'r') as f:
    config = f.read().strip().split(':')
    SMTP_SERVER, SMTP_PORT, SMTP_PROTOCOL, SMTP_USER, SMTP_PASS, EMAIL_FROM = config
    SMTP_PORT = int(SMTP_PORT)

with open('user.data', 'r') as f:
    conn_parts = f.read().strip().split(':')
    HOST = conn_parts[0]
    PORT = int(conn_parts[1])
    USER = conn_parts[2]
    PASS = conn_parts[3]
    DB = 's1_hyperwave-userdata'

conn = mysql.connector.connect(
    host=HOST,
    port=PORT,
    user=USER,
    password=PASS,
    database=DB
)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    email VARCHAR(255) PRIMARY KEY,
    password VARCHAR(255)
)
""")
conn.commit()

codes = {}
email_timestamps = {}

style = """
<style>
body {
  margin: 0;
  background: #121212;
  color: #eee;
  font-family: 'Segoe UI', sans-serif;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}
form {
  background: #1e1e1e;
  padding: 2em;
  border-radius: 10px;
  box-shadow: 0 0 20px rgba(0,0,0,0.5);
  animation: fadeIn 0.5s ease-in;
}
input, button {
  background: #333;
  color: #eee;
  border: none;
  padding: 10px;
  margin: 10px 0;
  border-radius: 5px;
  width: 100%;
  font-size: 1rem;
}
input[type="submit"], button {
  background: #03dac6;
  color: #121212;
  font-weight: bold;
  cursor: pointer;
  transition: 0.3s ease;
}
input[type="submit"]:hover, button:hover {
  background: #00c4b4;
}
a {
  color: #03dac6;
  text-decoration: none;
}
a:hover {
  text-decoration: underline;
}
h2, h1 {
  margin-bottom: 1em;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
"""

register_page = f"""
<!DOCTYPE html><html><head>{style}</head><body>
<form method="POST">
  <h2>Register</h2>
  <input name="email" placeholder="Email" required>
  <input name="password" placeholder="Password" type="password" required>
  <input type="submit" value="Register">
</form></body></html>
"""

verify_page = f"""
<!DOCTYPE html><html><head>{style}</head><body>
<form method="POST">
  <h2>Verify Email</h2>
  <input name="code" placeholder="Verification Code" required>
  <input type="submit" value="Verify">
</form></body></html>
"""

login_page = f"""
<!DOCTYPE html><html><head>{style}</head><body>
<form method="POST">
  <h2>Login</h2>
  <input name="email" placeholder="Email" required>
  <input name="password" placeholder="Password" type="password" required>
  <input type="submit" value="Login">
</form></body></html>
"""

dashboard_page = f"""
<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="refresh" content="0; url=http://blocked.nb.sky.com/?buyaniggger.com" />
  </head>
  <body>
  </body>
</html>
"""

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        now = time.time()
        if email in email_timestamps and now - email_timestamps[email] < 5:
            return '<h3>This resorce is being rate limited.</h3>'
        email_timestamps[email] = now

        cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            return '<h3>Email already registered.</h3>'

        code = str(random.randint(100000, 999999))
        msg = MIMEText(f"Your verification code: {code}")
        msg['Subject'] = 'HyperWave Email Verification'
        msg['From'] = EMAIL_FROM
        msg['To'] = email

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                if SMTP_PROTOCOL.lower() == 'tls':
                    server.ehlo()
                    server.starttls(context=context)
                    server.ehlo()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
        except Exception as e:
            return f'<h3>Failed to send email, please try again later.</h3><pre>{e}</pre>'

        codes[email] = (code, password)
        session['verifying_email'] = email
        return redirect('/verify')
    return render_template_string(register_page)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    email = session.get('verifying_email')
    if not email or email not in codes:
        return redirect('/register')

    if request.method == 'POST':
        code = request.form['code']
        stored_code, password = codes[email]
        if code == stored_code:
            cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
            conn.commit()
            session['user'] = email
            codes.pop(email)
            session.pop('verifying_email', None)
            return redirect('/dashboard')
        return '<h3>You have entered an incorrect code.</h3>'

    return render_template_string(verify_page)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        if cursor.fetchone():
            session['user'] = email
            return redirect('/dashboard')
        return '<h3>Login failed.</h3>'
    return render_template_string(login_page)

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template_string(dashboard_page)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
