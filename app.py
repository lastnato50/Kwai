from flask import Flask,request, render_template, request, redirect, url_for, session
import subprocess
import os
import signal

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key

# Dummy user database
users = {}
  
@app.route('/')
def home():
    if 'username' in session:
        return render_template('index.html', files=os.listdir('uploads'), running_processes=running_processes)
    return redirect(url_for('login'))
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('home'))
        return "Invalid credentials", 401  # Unauthorized
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        if username not in users:
            users[username] = password  # Store user
            return redirect(url_for('login'))
        return "User already exists", 409  # Conflict
    return render_template('signup.html')

running_processes = {}
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'botfile' not in request.files:
        return "No file part"
    
    files = request.files.getlist('botfile')
    for file in files:
        if file.filename == '':
            continue
        
        # Save the uploaded file
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

    return redirect(url_for('home'))

@app.route('/start/<filename>', methods=['POST'])
def start_bot(filename):
    global running_processes
    file_path = os.path.join('uploads', filename)

    # Start the new bot
    if filename not in running_processes:
        process = subprocess.Popen(['python3', file_path])
        running_processes[filename] = process.pid

    return redirect(url_for('home'))

@app.route('/stop/<filename>', methods=['POST'])
def stop_bot(filename):
    global running_processes
    if filename in running_processes:
        os.kill(running_processes[filename], signal.SIGTERM)
        del running_processes[filename]
    return redirect(url_for('home'))

if __name__ == '__main__':
    # Create uploads directory if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    
    app.run(debug=True)