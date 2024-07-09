from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Configuración de la base de datos
db_config = {
    'user': 'root',
    'password': 'tu_contraseña',
    'host': 'localhost',
    'database': 'tu_base_de_datos',
    'port': '3306'
}

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
        if 'crear_curso' in request.form:
            # Crear un nuevo curso
            nombre_curso = request.form['nombre_curso']
            if nombre_curso:
                conexion = conectar_db()
                if conexion:
                    cursor = conexion.cursor()
                    try:
                        insert_curso_query = "INSERT INTO cursos (nombre_curso) VALUES (%s)"
                        cursor.execute(insert_curso_query, (nombre_curso,))
                        conexion.commit()
                    except mysql.connector.Error as err:
                        print(f"Error al insertar curso en la base de datos: {err}")
                        conexion.rollback()
                    finally:
                        cursor.close()
                        conexion.close()
        
        elif 'registrar_alumno' in request.form:
            # Registrar un nuevo alumno
            codigo = request.form['codigo']
            nombre = request.form['nombre']
            apellido = request.form['apellido']
            dni = request.form['dni']
            curso_id = request.form['curso']  # Nuevo campo para el curso
            
            conexion = conectar_db()
            if conexion:
                cursor = conexion.cursor()
                try:
                    insert_alumno_query = "INSERT INTO alumnos (codigo, nombre, apellido, dni, id_curso) VALUES (%s, %s, %s, %s, %s)"
                    cursor.execute(insert_alumno_query, (codigo, nombre, apellido, dni, curso_id))
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

# Ruta para la página de creación de cursos
@app.route('/crear_curso', methods=['GET', 'POST'])
def crear_curso():
    if request.method == 'POST':
        # Crear un nuevo curso
        nombre_curso = request.form['nombre_curso']
        if nombre_curso:
            conexion = conectar_db()
            if conexion:
                cursor = conexion.cursor()
                try:
                    insert_curso_query = "INSERT INTO cursos (nombre_curso) VALUES (%s)"
                    cursor.execute(insert_curso_query, (nombre_curso,))
                    conexion.commit()
                except mysql.connector.Error as err:
                    print(f"Error al insertar curso en la base de datos: {err}")
                    conexion.rollback()
                finally:
                    cursor.close()
                    conexion.close()
    
    return render_template('crear_curso.html')

# Ruta para la página de ver códigos QR
@app.route('/ver_codigos_qr')
def ver_codigos_qr():
    # Lógica para obtener los códigos QR, similar a lo que tenías antes
    # Aquí puedes implementar la lógica para mostrar la página de escaneo de QR
    return render_template('scan_qr.html')

# Función para obtener la lista de cursos desde la base de datos
def obtener_cursos_desde_db():
    conexion = conectar_db()
    cursos = []
    
    if conexion:
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT id_curso, nombre_curso FROM cursos")
            cursos = cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Error al obtener cursos desde la base de datos: {err}")
        finally:
            cursor.close()
            conexion.close()
    
    return cursos

if __name__ == '__main__':
    app.run(debug=True)
