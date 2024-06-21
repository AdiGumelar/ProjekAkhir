import os
from flask import Flask, jsonify, render_template, redirect, url_for, request, session
import hashlib

from pymongo import MongoClient

MONGODB_CONNECTION_STRING = "mongodb+srv://test:sparta@cluster0.w9suhru.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGODB_CONNECTION_STRING)
db = client.Sekolah

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/homeuser')
def homeuser():
    return render_template('home.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST" :
        email_receive = request.form["email_give"]
        pw_receive = request.form["pw_give"]

        pw_hash = hashlib.sha256(pw_receive.encode("utf-8")).hexdigest()

        findUser = db.user.find_one({"email": email_receive, "pw": pw_hash})
        
        if findUser:
            session['user'] = email_receive
            return jsonify({"result": "success"})
        else :
            return jsonify({"result": "error"})

    return render_template('login.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST" :
        email_receive = request.form["email_give"]
        pw_receive = request.form["pw_give"]
        name_receive = request.form["name_give"]
        
        pw_hash = hashlib.sha256(pw_receive.encode("utf-8")).hexdigest()

        findEmail = db.user.find_one({"email": email_receive})

        if findEmail:
            return jsonify({"result": "error"})

        else:
            db.user.insert_one({"name" : name_receive, "email": email_receive, "pw": pw_hash})

    return render_template('register.html')

@app.route('/pengumuman')
def pengumuman():
    return render_template('pengumuman.html')

@app.route('/profile',methods=["GET", "POST"])
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == "POST" :
        nama_receive = request.form["nama_give"]
        gender_receive = request.form["gender_give"]
        alamat_receive = request.form["alamat_give"]
        tempatLahir_receive = request.form["tempatLahir_give"]
        tanggalLahir_receive = request.form["tanggalLahir_give"]
       

        

         # Pastikan foto_give ada dalam request.files sebelum mencoba mengaksesnya
        if 'foto_give' in request.files:
            foto_receive = request.files["foto_give"]
            foto_path = f"static/profile_pics/{(foto_receive.filename)}"
            foto_receive.save(foto_path)
        else:
            # Jika foto_give tidak ada dalam request.files, berikan nilai default
            foto_path = "/static/profile_pics/profile_placeholder.jpeg"

        doc = {
        "nama" : nama_receive,
        "gender" : gender_receive,
        "alamat" : alamat_receive,
        "tempatLahir" : tempatLahir_receive,
        "tanggalLahir" : tanggalLahir_receive,
        "email" : session['user'],
        "foto" : foto_path
        }

        profile = db.profile.find_one({"email" : session['user']})

        if profile :
            db.profile.update_one(
                {"email": session['user']},  # Filter berdasarkan email
                {"$set": {
                    "nama": nama_receive,
                    "gender": gender_receive,
                    "alamat": alamat_receive,
                    "tempatLahir": tempatLahir_receive,
                    "tanggalLahir": tanggalLahir_receive,
                    "foto" : foto_path
                }}
            )
        else :
            db.profile.insert_one(doc)
        return jsonify({"result" : "success"})

    profile = db.profile.find_one({"email" : session['user']})

    user_info = {
        "nama" : profile['nama'],
        "gender" : profile['gender'],
        "alamat" : profile['alamat'],
        "tempatLahir" : profile['tempatLahir'],
        "tanggalLahir" : profile['tanggalLahir'],
        "foto" : profile['foto']
    }
    return render_template('profile.html', user_info=user_info)

@app.route('/pendaftaran')
def daftar():
    return render_template('pendaftaran.html')

#untuk mengirim data pendaftaran
@app.route('/kirim-data', methods=["POST"])
def kirim_data():
    form_data = {key: request.form[key] for key in [
        'nama_lengkap', 'nama_panggilan', 'asal_provinsi', 
        'asal_kota', 'asal_desa', 'jenis_kelamin', 'nomor_hp'
    ]}
    
    dokumen = request.files['dokumen']
    if dokumen and allowed_file(dokumen.filename):
        filename = secure_filename(dokumen.filename)
        dokumen.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        form_data['dokumen'] = filename
    else:
        form_data['dokumen'] = None

    form_data['status'] = 'menunggu'

    db.pendaftaran.insert_one(form_data)
    return redirect(url_for('daftar'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/homeadmin')
def homeadmin():
    return render_template('dashboard.html')

@app.route('/datamasuk')
def datamasuk():
    return render_template('datamasuk.html')

@app.route('/datasiswa')
def datasiswa():
    return render_template('datasiswa.html')

@app.route('/editdokumentasi', methods=['POST'])
def editdokumentasi():
    if request.method == 'POST':
        judul = request.form['judul']
        deskripsi = request.form['deskripsi']
        file = request.files['inputFile']
        
        return "Dokumentasi berhasil disimpan!"
    return render_template('editdokumentasi.html')


@app.route('/updateprofile', methods=["POST"])
def updateprofile():
    return render_template('profile.html')

if __name__ == '__main__':
    app.run("0.0.0.0", port=5000, debug=True)