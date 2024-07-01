from flask import Blueprint, jsonify, request
from helper.db_helper import get_connection
from datetime import datetime

reservasi_bp = Blueprint('reservasi', __name__)

@reservasi_bp.route('/read/reservasi', methods=['GET'])
def read_all_reservasi():
    """Routes for module get list of reservations"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    select_query = "SELECT * FROM reservasi"
    cursor.execute(select_query)
    
    results = cursor.fetchall()
    
    cursor.close() 
    connection.close()# Close the cursor after query execution
    return jsonify({"message": "OK", "datas": results}), 200

@reservasi_bp.route('/read/reservasi/<id_pengguna>', methods=['GET'])
def read_reservasi(id_pengguna):
    """Routes for module get list of reservations by user id"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    select_query = "SELECT * FROM reservasi WHERE id_pengguna = %s"
    cursor.execute(select_query, (id_pengguna,))
    
    results = cursor.fetchall()
    
    cursor.close() 
    connection.close()  # Close the cursor after query execution
    return jsonify({"message": "OK", "datas": results}), 200


@reservasi_bp.route('/create/reservasi', methods=['POST'])
def create_reservasi():
    """Routes for module create a reservation"""
    id_pengguna = request.form.get('id_pengguna')
    id_lapangan = request.form.get('id_lapangan')
    id_sesi = request.form.get('id_sesi')
    tgl_sewa = request.form.get('tgl_sewa')
    harga = request.form.get('harga')
    pembayaran = request.form.get('pembayaran', '0')  # Default to 'not paid yet'
    
    if not (id_pengguna and id_lapangan and id_sesi and tgl_sewa and harga and pembayaran):
        return jsonify({"message": "Semua field diperlukan."}), 400

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Validasi waktu
        current_time = datetime.now()
        booking_time = datetime.strptime(f"{tgl_sewa}", "%Y-%m-%d %H:%M")
        
        if booking_time < current_time:
            cursor.close()
            connection.close()
            return jsonify({"message": "Tidak bisa booking untuk waktu yang sudah berlalu."}), 400

        # Cek apakah sudah ada reservasi untuk lapangan dan sesi yang sama
        check_query = "SELECT * FROM reservasi WHERE id_lapangan = %s AND id_sesi = %s AND tgl_sewa = %s"
        cursor.execute(check_query, (id_lapangan, id_sesi, tgl_sewa))
        existing_reservation = cursor.fetchone()

        if existing_reservation:
            cursor.close()
            connection.close()
            return jsonify({"message": "Lapangan sudah dipesan untuk sesi dan tanggal yang dipilih."}), 409

        # Query untuk insert data reservasi
        insert_query = "INSERT INTO reservasi (id_pengguna, id_lapangan, id_sesi, tgl_sewa, harga, pembayaran) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (id_pengguna, id_lapangan, id_sesi, tgl_sewa, harga, pembayaran)
        cursor.execute(insert_query, values)
        connection.commit()

        affected_rows = cursor.rowcount
        cursor.close()
        connection.close()

        if affected_rows > 0:
            return jsonify({"message": "Reservasi berhasil dibuat"}), 201
        else:
            return jsonify({"message": "Gagal membuat reservasi"}), 500

    except Exception as e:
        return jsonify({"error": str(e), "message": "Gagal membuat reservasi"}), 500
