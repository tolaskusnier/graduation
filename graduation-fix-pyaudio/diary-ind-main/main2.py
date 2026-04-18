#hapus entri dengan hapus instance dan buat ulang db
#hapus rekaman dengan restart di VsCode dan jalankan lagi
#rekaman bagus setelah loading 1 kali

# Import
from flask import Flask, render_template, request, redirect
from speech import speech
# Menghubungkan perpustakaan database
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
# Menghubungkan SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Membuat sebuah DB
db = SQLAlchemy(app)

# Membuat sebuah tabel cardpy.
class Card(db.Model):
    # Membuat kolom-kolom
    # id(kolom #1)
    id = db.Column(db.Integer, primary_key=True)
    # Judul
    title = db.Column(db.String(100), nullable=False)
    # Deskripsi
    subtitle = db.Column(db.String(300), nullable=False)
    # Teks up to 30 000 char
    text = db.Column(db.Text, nullable=False)

    #Parameterized Constructor accepts additional arguments
    def __init__(self, title, subtitle, text):
        self.title = title
        self.subtitle = subtitle
        self.text = text

    # Menampilkan objek dan id
    # The __repr__ method is a special method in Python that defines how an object 
    # should be represented as a string. 
    # It is used to provide a human-readable representation of the object, typically 
    # for debugging purposes.
    def __repr__(self):
        return f'<Card {self.id}>'
    
# Tugas #1. Membuat tabel Pengguna
class User(db.Model):
    # Membuat kolom
    # id
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Login
    login = db.Column(db.String(100),  nullable=False)
    # Kata sandi
    password = db.Column(db.String(30), nullable=False)

    #Parameterized Constructor accepts additional arguments
    def __init__(self, login, password):
        self.login = login
        self.password = password
    
# Menjalankan halaman konten
@app.route('/', methods=['GET','POST'])
def login():
    error = ''
    if request.method == 'POST':
        form_login = request.form['email']
        form_password = request.form['password']
        
        # Tugas #2. Menerapkan otorisasi
        users_db = User.query.all()
        user_found = False
        for user in users_db:
            if form_login == user.login and form_password == user.password:
                user_found = True
                return redirect('/index')
            elif user_found==False or form_login != user.login or form_password != user.password:
                error = 'Belum terdaftar silakan Daftar atau periksa Email dan kata Sandi tidak tepat'
                return render_template('login.html', error=error)
            
    return render_template('login.html', error=error)
    
        


@app.route('/reg', methods=['GET','POST'])
def reg():
    if request.method == 'POST':
        login= request.form['email']
        password = request.form['password']
        
        #Tugas #3. Buat agar data pengguna direkam ke dalam database
        user = User(login=login, password=password)
        db.session.add(user)
        db.session.commit()

        
        return redirect('/')
    
    else:    
        return render_template('registration.html')


# Menjalankan halaman konten
@app.route('/index')
def index():
    # Menampilkan catatan-catatan dari database
    cards = Card.query.order_by(Card.id).all()
    return render_template('index.html', cards=cards)

# Menjalankan halaman dengan entri tersebut
@app.route('/card/<int:id>')
def card(id):
    card = Card.query.get(id)
    return render_template('card.html', card=card)

# Menjalankan halaman pembuatan entri
@app.route('/create')
def create():
    return render_template('create_card.html')

# Formulir entri
@app.route('/form_create', methods=['GET','POST'])
def form_create():
    if request.method == 'POST':
        title =  request.form['title']
        subtitle =  request.form['subtitle']
        text =  request.form['text']

        # Membuat objek yang akan dikirim ke DB
        card = Card(title=title, subtitle=subtitle, text=text)
        db.session.add(card)
        db.session.commit()
        return redirect('/index')
    else:
        return render_template('create_card.html')



#old record
# @app.route('/voice')
# def voices():
#     try:
#         text = speech()
#     except:
#         text = "Ada yang salah"
#     return render_template('create_card.html', text=text)
recorded_texts = []
@app.route('/voice')
def voices():
    try:
        text = speech()
        recorded_texts.append(text)
    except:
        recorded_texts.append("Ada yang salah")
    
    combined_text = " ".join(recorded_texts)
    return render_template('create_card.html', text=combined_text)

# no use if we run on pythonanywhere
if __name__ == "__main__":
    app.run(debug=True)
