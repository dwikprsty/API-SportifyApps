import os
from flask import Blueprint, jsonify, request
from helper.db_helper import get_connection
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
user_bp = Blueprint('user', __name__)

UPLOAD_FOLDER = 'img'

@user_bp.route('/read/user', defaults={'idPengguna': None})
@user_bp.route('/read/user/<idPengguna>', methods=['GET'])
def readpengguna(idPengguna):
    """Routes for module get list user"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    if idPengguna:
        select_query = "SELECT * FROM users WHERE id_pengguna = %s"
        value = (idPengguna,)
        cursor.execute(select_query, value)
    else:
        select_query = "SELECT * FROM users"
        cursor.execute(select_query)
    
    results = cursor.fetchall()
    
    cursor.close() 
    connection.close()# Close the cursor after query execution
    return jsonify({"message": "OK", "datas": results}), 200

@user_bp.route('/user/create', methods=['POST'])
def create():
    """Routes for module create a user"""
    #idpengguna = request.form['id_pengguna']
    jenispengguna = request.form['jenis_pengguna']
    namapengguna = request.form['nama_pengguna']
    email = request.form['email']
    katasandi = request.form['kata_sandi']
    nickname = request.form['nickname']
    alamat = request.form['alamat']
    jenis_kelamin = request.form['jenis_kelamin']
    tgllahir = request.form['tgl_lahir']
    notelp = request.form['no_telp']
    
    uploaded_file = request.files['foto_profil']
    if uploaded_file.filename != '':
        file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename) #img\namafoto.jpg
        uploaded_file.save(file_path) #ngirim
    
    # Enkripsi kata sandi menggunakan bcrypt
    hashed_password = bcrypt.generate_password_hash(katasandi).decode('utf-8')

    connection = get_connection()
    cursor = connection.cursor()
    
    query = "INSERT INTO users (jenis_pengguna, nama_pengguna,  email, kata_sandi, nickname, alamat, jenis_kelamin, tgl_lahir, no_telp, foto_profil) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    value = (jenispengguna, namapengguna, email, hashed_password, nickname, alamat, jenis_kelamin, tgllahir, notelp, uploaded_file.filename)
    cursor.execute(query, value)
    connection.commit()
    
    affected_row = cursor.rowcount
    cursor.close()
    
    if affected_row > 0:
        return jsonify({"nama_pelanggan": namapengguna, "message": "User created successfully"}), 201
    else:
        return jsonify({"message": "Failed to create user"}), 500

@user_bp.route('/user/update/<id_pengguna>', methods=['PUT'])
def update_user(id_pengguna):
    try:
        # Ambil data dari form request
        namapengguna = request.form.get('nama_pengguna')
        email = request.form.get('email')
        nickname = request.form.get('nickname')
        alamat = request.form.get('alamat')
        jenis_kelamin = request.form.get('jenis_kelamin')
        tgllahir = request.form.get('tgl_lahir')
        notelp = request.form.get('no_telp')
        foto_profil = request.files.get('foto_profil')

        # Pastikan id_pengguna tidak kosong
        if not id_pengguna:
            return jsonify({"message": "id_pengguna is required"}), 400

        # Koneksi ke database
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Ambil user yang akan diupdate
        cursor.execute("SELECT * FROM users WHERE id_pengguna = %s", (id_pengguna,))
        existing_user = cursor.fetchone()

        # Jika user tidak ditemukan
        if not existing_user:
            cursor.close()
            connection.close()
            return jsonify({"message": "User tidak ditemukan."}), 404

        # Daftar field yang akan diupdate
        updates = []
        values = []

        if namapengguna:
            updates.append("nama_pengguna = %s")
            values.append(namapengguna)

        if email:
            updates.append("email = %s")
            values.append(email)

        if nickname:
            updates.append("nickname = %s")
            values.append(nickname)

        if alamat:
            updates.append("alamat = %s")
            values.append(alamat)

        if jenis_kelamin:
            updates.append("jenis_kelamin = %s")
            values.append(jenis_kelamin)

        if tgllahir:
            updates.append("tgl_lahir = %s")
            values.append(tgllahir)

        if notelp:
            updates.append("no_telp = %s")
            values.append(notelp)

        if foto_profil and foto_profil.filename != '':
            file_path = os.path.join(UPLOAD_FOLDER, foto_profil.filename)
            foto_profil.save(file_path)
            updates.append("foto_profil = %s")
            values.append(foto_profil.filename)

        # Jika ada field yang perlu diupdate
        if updates:
            query = f"UPDATE users SET {', '.join(updates)} WHERE id_pengguna = %s"
            values.append(id_pengguna)
            cursor.execute(query, values)
            connection.commit()

            affected_rows = cursor.rowcount

            query = "SELECT * FROM users WHERE id_pengguna = %s"
            value = (id_pengguna,)
            cursor.execute(query, value)
            user = cursor.fetchone()
            cursor.close()
            connection.close()

            if affected_rows > 0:

                return jsonify({"message": "Data user berhasil di-update.", "id_pengguna": id_pengguna, "data_user": user}), 200
            else:
                return jsonify({"message": "Tidak ada perubahan yang dilakukan pada data user."}), 200

        return jsonify({"message": "Tidak ada data yang di-update."}), 400

    except Exception as e:
        return jsonify({"error": str(e), "message": "Gagal memperbarui data user."}), 500
