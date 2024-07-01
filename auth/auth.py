from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, decode_token
from flask_bcrypt import Bcrypt
import mysql.connector

from helper.db_helper import get_connection

bcrypt = Bcrypt()
auth_bp = Blueprint('users', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.json['email']
    katasandi = request.json['kata_sandi']

    if not email or not katasandi:
        return jsonify({"msg": "Email and password are required"}), 400

    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE email = %s"
    request_query = (email,)
    cursor.execute(query, request_query)
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if not user or not bcrypt.check_password_hash(user.get('kata_sandi'), katasandi):
        return jsonify({"msg": "Bad username or password"}), 401

    # Buat data user tanpa menyertakan kata_sandi
    user_data = {
        "id_pengguna": user.get("id_pengguna"),
        "nama_pengguna": user.get("nama_pengguna"),
        "email": user.get("email"),
        "jenis_pengguna": user.get("jenis_pengguna"),
        "nickname": user.get("nickname"),
        "alamat": user.get("alamat"),
        "jenis_kelamin": user.get("jenis_kelamin"),
        "tgl_lahir": user.get("tgl_lahir"),
        "no_telp": user.get("no_telp"),
        "foto_profil": user.get("foto_profil"),
    }

    user_role = user.get('jenis_pengguna')
    access_token = create_access_token(identity={'email': email, 'username': user.get('nama_pengguna')}, additional_claims={'roles': user_role})
    decoded_token = decode_token(access_token)
    expires = decoded_token['exp']
    return jsonify({"access_token": access_token, "expires_in": expires, "token_type": "Bearer", "data_user": user_data})


@auth_bp.route('/register', methods=['POST'])
def register():
    """Routes for register"""
    namapengguna = request
    namapengguna = request.json['nama_pengguna']
    email = request.json['email']
    katasandi = request.json['kata_sandi']

    # Check if email already exists
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    query = "SELECT * FROM users WHERE email = %s"
    request_query = (email,)
    cursor.execute(query, request_query)
    existing_user = cursor.fetchone()
    cursor.close()
    connection.close()

    if existing_user:
        return jsonify({"msg": "Email already exists"}), 400

    # Proceed with registration if email is unique
    hashed_password = bcrypt.generate_password_hash(katasandi).decode('utf-8')

    try:
        connection = get_connection()
        cursor = connection.cursor()
        insert_query = "INSERT INTO users (nama_pengguna, email, kata_sandi) VALUES (%s, %s, %s)"
        request_insert = (namapengguna, email, hashed_password)
        cursor.execute(insert_query, request_insert)
        connection.commit()
        new_id = cursor.lastrowid
        cursor.close()
        connection.close()

        if new_id:
            return jsonify({"message": "OK", "description": "User created", "username": namapengguna, "email": email}), 201
        return jsonify({"message": "Failed, can't register user"}), 501
    
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return jsonify({"msg": "Internal Server Error"}), 500
    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"msg": "Internal Server Error"}), 500
