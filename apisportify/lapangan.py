import os
from flask import Blueprint, jsonify, request, send_from_directory
from helper.db_helper import get_connection
from werkzeug.utils import secure_filename

lapangan_bp = Blueprint('lapangan', __name__)

UPLOAD_FOLDER = 'img'


@lapangan_bp.route('/read/lapangan', methods=['GET'])
def read_all_lapangan():
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Get query parameters
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=5, type=int)
    offset = (page - 1) * per_page
    
    # Query untuk melakukan join antara tabel lapangan dan jenis_lapangan dengan paginasi
    select_query = """
    SELECT l.id_lapangan, l.nama_lapangan, l.alamat_lapangan, l.deskripsi, l.gambar_lapangan, l.harga_sewa, l.id_jenislap, j.jenis_lapangan
    FROM lapangan l
    JOIN jenislapangan j ON l.id_jenislap = j.id_jenislap
    WHERE l.id_jenislap = %s
    LIMIT %s OFFSET %s
    """
    
    # List of id_jenislap to iterate over
    id_jenislap_list = ['JL1', 'JL2', 'JL3', 'JL4', 'JL5']
    results = []

    for id_jenislap in id_jenislap_list:
        cursor.execute(select_query, (id_jenislap, per_page, offset))
        rows = cursor.fetchall()
        results.extend(rows)
    
    cursor.close()
    connection.close()
    
    return jsonify({"message": "OK", "datas": results}), 200

@lapangan_bp.route('/read/lapangan/<string:id>', methods=['GET'])
def read_lapangan(id):
    """Routes for module get details of a specific lapangan by id"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Query to get details of a specific lapangan by id
    select_query = """
    SELECT l.id_lapangan, l.nama_lapangan, l.alamat_lapangan, l.deskripsi, l.gambar_lapangan, l.harga_sewa, l.id_jenislap, j.jenis_lapangan
    FROM lapangan l
    JOIN jenislapangan j ON l.id_jenislap = j.id_jenislap
    WHERE l.id_lapangan = %s
    """
    cursor.execute(select_query, (id,))
    
    result = cursor.fetchone()
    
    cursor.close()
    connection.close()  # Close the cursor after query execution
    
    if result:
        return jsonify({"message": "OK", "datas": result}), 200
    else:
        return jsonify({"message": "Lapangan not found."}), 404


@lapangan_bp.route('/read/sessions', methods=['GET'])
def read_sessions():
    """Routes for module get list of session times"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Query to get session times
    select_query = """
    SELECT id_sesi, waktu
    FROM sesi
    """
    cursor.execute(select_query)
    
    results = cursor.fetchall()
    
    cursor.close()
    connection.close()  # Close the cursor after query execution
    return jsonify({"message": "OK", "datas": results}), 200

@lapangan_bp.route('/read/session/<string:id>', methods=['GET'])
def read_session(id):
    """Routes for module get details of a specific session by id"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    # Query to get details of a specific session by id
    select_query = """
    SELECT id_sesi, waktu
    FROM sesi
    WHERE id_sesi = %s
    """
    cursor.execute(select_query, (id,))
    
    result = cursor.fetchone()
    
    cursor.close()
    connection.close()  # Close the cursor after query execution
    
    if result:
        return jsonify({"message": "OK", "datas": result}), 200
    else:
        return jsonify({"message": "Session not found."}), 404


@lapangan_bp.route('/create/lapangan', methods=['POST'])
def create():
    """Routes for creating a lapangan"""
    idLapangan = request.form.get('id_lapangan')
    idJenisLapangan = request.form.get('id_jenislap')
    nama_lapangan = request.form.get('nama_lapangan')
    deskripsi = request.form.get('deskripsi')
    alamat_lapangan = request.form.get('alamat_lapangan')
    harga_sewa = request.form.get('harga_sewa')
    uploaded_file = request.files.get('gambar_lapangan')

    if not all([idLapangan, idJenisLapangan, nama_lapangan, deskripsi, alamat_lapangan, harga_sewa, uploaded_file]):
        return jsonify({"message": "All fields are required"}), 400

    if uploaded_file.filename == '':
        return jsonify({"message": "Image file is required"}), 400

    filename = secure_filename(uploaded_file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    uploaded_file.save(file_path)
    gambar_lapangan = file_path

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO lapangan 
    (id_lapangan, id_jenislap, nama_lapangan, deskripsi, alamat_lapangan, harga_sewa, gambar_lapangan) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    values = (idLapangan, idJenisLapangan, nama_lapangan, deskripsi, alamat_lapangan, harga_sewa, gambar_lapangan)

    try:
        cursor.execute(query, values)
        connection.commit()

        affected_row = cursor.rowcount

        if affected_row > 0:
            return jsonify({"id_lapangan": idLapangan, "message": "Inserted"}), 201
        return jsonify({"message": "Can't Insert Data"}), 500

    except Exception as e:
        return jsonify({"error": str(e), "message": "Gagal menambahkan data"}), 500

    finally:
        cursor.close()
        connection.close()

@lapangan_bp.route('/update/lapangan', methods=['PUT'])
def update_lapangan():
    """Update an existing lapangan entry with the given data."""

    # Mengambil data dari form
    idLapangan = request.form.get('id_lapangan')
    idJenisLapangan = request.form.get('id_jenislap')
    nama_lapangan = request.form.get('nama_lapangan')
    deskripsi = request.form.get('deskripsi')
    alamat_lapangan = request.form.get('alamat_lapangan')
    harga_sewa = request.form.get('harga_sewa')
    uploaded_file = request.files.get('gambar_lapangan')

    # Debugging prints
    print(f"Received data: idLapangan={idLapangan}, idJenisLapangan={idJenisLapangan}, nama_lapangan={nama_lapangan}, deskripsi={deskripsi}, alamat_lapangan={alamat_lapangan}, harga_sewa={harga_sewa}, uploaded_file={uploaded_file}")

    if not idLapangan:
        return jsonify({"message": "Field 'id_lapangan' diperlukan untuk update."}), 400

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Ambil data lapangan yang ada
        cursor.execute("SELECT * FROM lapangan WHERE id_lapangan = %s", (idLapangan,))
        existing_lapangan = cursor.fetchone()

        print(f"Existing lapangan data: {existing_lapangan}")

        if not existing_lapangan:
            return jsonify({"message": f"Lapangan dengan ID {idLapangan} tidak ditemukan."}), 404

        # Siapkan nilai yang akan di-update
        updates = []
        values = []

        if idJenisLapangan:
            updates.append("id_jenislap = %s")
            values.append(idJenisLapangan)

        if nama_lapangan:
            updates.append("nama_lapangan = %s")
            values.append(nama_lapangan)
            
        if deskripsi:
            updates.append("deskripsi = %s")
            values.append(deskripsi)

        if alamat_lapangan:
            updates.append("alamat_lapangan = %s")
            values.append(alamat_lapangan)

        if harga_sewa:
            updates.append("harga_sewa = %s")
            values.append(int(harga_sewa))

        if uploaded_file and uploaded_file.filename != '':
            # Hapus file gambar lama jika ada
            if existing_lapangan['gambar_lapangan'] and os.path.exists(existing_lapangan['gambar_lapangan']):
                print(f"Removing old image: {existing_lapangan['gambar_lapangan']}")
                os.remove(existing_lapangan['gambar_lapangan'])
            
            # Simpan file baru
            file_path = os.path.join(UPLOAD_FOLDER, uploaded_file.filename)
            print(f"Saving new image to: {file_path}")
            uploaded_file.save(file_path)
            updates.append("gambar_lapangan = %s")
            values.append(uploaded_file.filename)
        else:
            file_path = existing_lapangan['gambar_lapangan']  # Tetap gunakan gambar lama jika tidak ada yang baru

        print(f"Updates: {updates}")
        print(f"Values: {values}")

        # Update query hanya jika ada perubahan
        if updates:
            query = f"UPDATE lapangan SET {', '.join(updates)} WHERE id_lapangan = %s"
            values.append(idLapangan)
            print(f"Executing query: {query} with values: {values}")
            cursor.execute(query, values)
            connection.commit()
 

            if cursor.rowcount > 0:
                cursor.close()
                connection.close()
                return jsonify({
                    "message": "Lapangan berhasil diperbarui",
                    "id_lapangan": idLapangan,
                    "file_path": file_path
                }), 201
            else:
                cursor.close()
                connection.close()
                return jsonify({"message": "Tidak ada perubahan yang dilakukan pada data lapangan."}), 200

        return jsonify({"message": "Tidak ada data yang di-update."}), 400

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return jsonify({"error": str(e), "message": "Gagal memperbarui data"}), 500
    
    
@lapangan_bp.route('/delete/lapangan/<string:id_lapangan>', methods=['DELETE'])
def delete_lapangan(id_lapangan):
    """Delete a lapangan entry based on its ID."""
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        # Cek apakah lapangan dengan ID tersebut ada
        cursor.execute("SELECT * FROM lapangan WHERE id_lapangan = %s", (id_lapangan,))
        lapangan = cursor.fetchone()

        if not lapangan:
            return jsonify({"message": f"Lapangan dengan ID {id_lapangan} tidak ditemukan."}), 404

        # Hapus gambar jika ada
        gambar_path = lapangan['gambar_lapangan']
        if gambar_path and os.path.exists(gambar_path):
            try:
                os.remove(gambar_path)
            except Exception as e:
                return jsonify({"message": "Error removing image file", "error": str(e)}), 500

        # Hapus data dari database
        cursor.execute("DELETE FROM lapangan WHERE id_lapangan = %s", (id_lapangan,))
        connection.commit()
        affected_rows = cursor.rowcount

        cursor.close()
        connection.close()

        if affected_rows > 0:
            return jsonify({"message": f"Lapangan dengan ID {id_lapangan} berhasil dihapus."}), 200
        else:
            return jsonify({"message": f"Gagal menghapus lapangan dengan ID {id_lapangan}."}), 500

    except Exception as e:
        return jsonify({"message": "Gagal menghapus data lapangan", "error": str(e)}), 500
