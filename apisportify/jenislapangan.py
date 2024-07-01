import os
from flask import Blueprint, jsonify, request
from helper.db_helper import get_connection

jenislapangan_bp = Blueprint('jenislapangan', __name__)

@jenislapangan_bp.route('/read/jenislapangan', methods=['GET'])
def readjenislapangan():
    """Routes for module get list jenis_lapangan"""
    connection = get_connection()
    cursor = connection.cursor(dictionary=True)
    
    select_query = "SELECT * FROM jenislapangan"
    cursor.execute(select_query)
    
    results = cursor.fetchall()
    
    cursor.close() 
    connection.close()# Close the cursor after query execution
    return jsonify({"message": "OK", "datas": results}), 200

@jenislapangan_bp.route('/create/jenislapangan', methods=['POST'])
def createjenislapangan():
    """Routes for module to create a new jenis_lapangan"""
    # Get the form data
    id_jenislap = request.form.get('id_jenislap')
    jenis_lapangan = request.form.get('jenis_lapangan')
    
    # Check if the necessary data is provided
    if not id_jenislap or not jenis_lapangan:
        return jsonify({"message": "ID Jenislap and Jenis Lapangan are required"}), 400

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Define the insert query
        insert_query = """
        INSERT INTO jenislapangan (id_jenislap, jenis_lapangan)
        VALUES (%s, %s)
        """

        # Execute the query with form data
        cursor.execute(insert_query, (id_jenislap, jenis_lapangan))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "Jenis lapangan created successfully"}), 201

    except Exception as e:
        return jsonify({"message": "An error occurred: " + str(e)}), 500
    
    
@jenislapangan_bp.route('/update/jenislapangan', methods=['PUT'])
def updatejenislapangan():
    """Route for updating an existing jenis_lapangan"""
    # Get the form data
    id_jenislap = request.form.get('id_jenislap')
    jenis_lapangan = request.form.get('jenis_lapangan')

    # Check if the necessary data is provided
    if not id_jenislap or not jenis_lapangan:
        return jsonify({"message": "ID Jenislap and Jenis Lapangan are required"}), 400

    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Define the update query
        update_query = """
        UPDATE jenislapangan
        SET jenis_lapangan = %s
        WHERE id_jenislap = %s
        """

        # Execute the query with form data
        cursor.execute(update_query, (jenis_lapangan, id_jenislap))
        connection.commit()

        # Check if the update was successful
        if cursor.rowcount == 0:
            return jsonify({"message": "No record found with the given ID"}), 404

        cursor.close()
        connection.close()

        return jsonify({"message": "Jenis lapangan updated successfully"}), 200

    except Exception as e:
        return jsonify({"message": "An error occurred: " + str(e)}), 500
    

@jenislapangan_bp.route('/delete/jenislapangan/<id_jenislap>', methods=['DELETE'])
def deletejenislapangan(id_jenislap):
    """Route for deleting an existing jenis_lapangan by id_jenislap"""
    
    try:
        connection = get_connection()
        cursor = connection.cursor()

        # Define the delete query
        delete_query = """
        DELETE FROM jenislapangan
        WHERE id_jenislap = %s
        """

        # Execute the query with the provided id_jenislap
        cursor.execute(delete_query, (id_jenislap,))
        connection.commit()

        # Check if the deletion was successful
        if cursor.rowcount == 0:
            return jsonify({"message": "No record found with the given ID"}), 404

        cursor.close()
        connection.close()

        return jsonify({"message": "Jenis lapangan deleted successfully"}), 200

    except Exception as e:
        return jsonify({"message": "An error occurred: " + str(e)}), 500