from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import qrcode
import os
from datetime import datetime

app = Flask(__name__)

# Configuración de la base de datos
db_config = {
    'user': 'root',
    'password': '12062007',
    'host': 'localhost',
    'database': 'ecu2',
    'port': '3306'
}

# Crear carpeta para guardar los QR si no existe
os.makedirs('static/img_qr', exist_ok=True)

# Función para conectar a la base de datos
def conectar_db():
    try:
        conexion = mysql.connector.connect(**db_config)
        return conexion
    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
        return None

# Ruta para la página de inicio / registro de alumnos
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Registrar un nuevo alumno
        codigo = request.form['codigo']
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        dni = request.form['dni']
        curso_id = request.form['curso']
        
        # Generar QR code
        qr_data = f"{codigo}_{nombre}_{apellido}"
        qr_img = qrcode.make(qr_data)
        qr_img_path = f"static/img_qr/{codigo}_{nombre}_{apellido}.png"
        qr_img.save(qr_img_path)
        
        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            try:
                insert_alumno_query = "INSERT INTO alumnos (codigo, nombre, apellido, dni, img_qr, Curso_id_curso) VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(insert_alumno_query, (codigo, nombre, apellido, dni, qr_img_path, curso_id))
                conexion.commit()
            except mysql.connector.Error as err:
                print(f"Error al insertar alumno en la base de datos: {err}")
                conexion.rollback()
            finally:
                cursor.close()
                conexion.close()
    
    # Obtener la lista de cursos desde la base de datos
    cursos = obtener_cursos_desde_db()
    
    return render_template('index.html', cursos=cursos)

# Ruta para la página de escaneo de QR
@app.route('/scan_qr', methods=['GET', 'POST'])
def scan_qr():
    if request.method == 'POST':
        qr_data = request.form['qr_data']
        llegada = calcular_llegada(qr_data)
        registrar_asistencia(qr_data, llegada)
        return redirect(url_for('index'))
    
    return render_template('scan_qr.html')

# Ruta para la página de creación de cursos
@app.route('/crear_curso', methods=['GET', 'POST'])
def crear_curso():
    if request.method == 'POST':
        anio = request.form['Anio']
        turno = request.form['Turno']
        division = request.form['Division']
        ciclo = request.form['Ciclo']
        
        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            try:
                insert_curso_query = "INSERT INTO Curso (Anio, Turno, Division, Ciclo) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert_curso_query, (anio, turno, division, ciclo))
                conexion.commit()
            except mysql.connector.Error as err:
                print(f"Error al insertar curso en la base de datos: {err}")
                conexion.rollback()
            finally:
                cursor.close()
                conexion.close()
    
    return render_template('crear_curso.html')

# Función para calcular el estado de llegada
def calcular_llegada(qr_data):
    # Obtener el horario de entrada desde la base de datos
    conexion = conectar_db()
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute("SELECT horario_E FROM Taller WHERE id_T = %s", (qr_data.split('_')[0],))
            horario_entrada = cursor.fetchone()['horario_E']
        except mysql.connector.Error as err:
            print(f"Error al obtener horario desde la base de datos: {err}")
        finally:
            cursor.close()
            conexion.close()
    
    hora_actual = datetime.now().time()
    if hora_actual <= horario_entrada:
        return "Bien"
    else:
        return "Tarde"

# Función para registrar la asistencia en la base de datos
def registrar_asistencia(qr_data, llegada):
    conexion = conectar_db()
    if conexion:
        cursor = conexion.cursor()
        try:
            insert_asistencia_query = "INSERT INTO Comprobante_A (Ingreso, llegada, Taller_id_T, Curso_id_curso) VALUES (NOW(), %s, %s, %s)"
            cursor.execute(insert_asistencia_query, (llegada, qr_data.split('_')[0], qr_data.split('_')[1]))
            conexion.commit()
        except mysql.connector.Error as err:
            print(f"Error al registrar asistencia en la base de datos: {err}")
            conexion.rollback()
        finally:
            cursor.close()
            conexion.close()

# Función para obtener la lista de cursos desde la base de datos
def obtener_cursos_desde_db():
    conexion = conectar_db()
    cursos = []
    
    if conexion:
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id_curso, Anio, Turno, Ciclo, Division FROM Curso")
            cursos = cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error al obtener cursos desde la base de datos: {err}")
        finally:
            cursor.close()
            conexion.close()
    
    return cursos

# Ruta para la página de creación de talleres
@app.route('/crear_taller', methods=['GET', 'POST'])
def crear_taller():
    if request.method == 'POST':
        nombre = request.form['nombre']
        horario_e = request.form['horario_E']
        horario_s = request.form['horario_S']
        curso_id = request.form['curso']
        
        conexion = conectar_db()
        if conexion:
            cursor = conexion.cursor()
            try:
                insert_taller_query = "INSERT INTO Taller (nombre_T, horario_E, horario_S, Curso_id_curso) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert_taller_query, (nombre, horario_e, horario_s, curso_id))
                conexion.commit()
            except mysql.connector.Error as err:
                print(f"Error al insertar taller en la base de datos: {err}")
                conexion.rollback()
            finally:
                cursor.close()
                conexion.close()
    
    # Obtener la lista de cursos desde la base de datos
    cursos = obtener_cursos_desde_db()
    
    return render_template('crear_taller.html', cursos=cursos)

if __name__ == '__main__':
    app.run(debug=True)
