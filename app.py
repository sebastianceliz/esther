from flask import Flask, render_template, redirect, url_for, request,jsonify,send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import plotly.graph_objs as go
from werkzeug.utils import secure_filename
import reniec
from datetime import datetime, date
import psycopg2
import hashlib
import db

#Funciones
def encriptar(contraseña):
    sha256 = hashlib.sha256()
    text_bytes = contraseña.encode('utf-8')
    sha256.update(text_bytes)
    hash_hex = sha256.hexdigest().upper()

    return hash_hex

from modeloprediccion import predecir
app= Flask(__name__)
app.secret_key = 'A1B2C3D421'

def funcionusuariosadmin():
    connection = psycopg2.connect(
        dbname='bdtesis',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor = connection.cursor()
    query = "select usuario, contraseña from usuario where tipousuarioid=1;"
    try:
        cursor.execute(query)
        resultados = cursor.fetchall()
        usuarios = {}
        for resultado in resultados:
            usuario, contraseña = resultado
            usuarios[usuario] = {'password': contraseña}
        return usuarios
    except Exception as e:
        print(e)

def funcionusuarios():
    connection = psycopg2.connect(
        dbname='bdtesis',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor = connection.cursor()
    query = "select usuario, contraseña from usuario where tipousuarioid=2;"
    try:
        cursor.execute(query)
        resultados = cursor.fetchall()
        usuarios = {}
        for resultado in resultados:
            usuario, contraseña = resultado
            usuarios[usuario] = {'password': contraseña}
        return usuarios
    except Exception as e:
        print(e)

usersadmin = funcionusuariosadmin()
users = funcionusuarios()


# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

#users = {'admin': {'password': 'admin'}, 'user': {'password': 'user'}}

class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

# Función para cargar el usuario
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)


def calcular_edad(fecha_nacimiento):
    fecha_actual = date.today()

    edad = fecha_actual.year - fecha_nacimiento.year - ((fecha_actual.month, fecha_actual.day) < (fecha_nacimiento.month, fecha_nacimiento.day))

    return edad

def calcular_imc(peso, altura):
    try:
        peso = float(peso)
        altura = float(altura)
        if altura <= 0 or peso <= 0:
            raise ValueError("La altura y el peso deben ser valores positivos.")
        imc = peso / (altura ** 2)
        return round(imc, 2)
    except ValueError as e:
        return str(e)
    
@app.route('/',  methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and encriptar(password) == users[username]['password']:
            user = User(username)
            login_user(user)
            return jsonify({'correctoUser': 'Ingresó'})
        elif username in usersadmin and encriptar(password) == usersadmin[username]['password']:
            user = User(username)
            login_user(user)
            return jsonify({'correctoAdmin': 'Ingresó'})
        else:
            return jsonify({'error': 'Credenciales inválidas. Inténtalo de nuevo.'})


    return render_template('login.html')

@app.route('/inicio', methods=['GET','POST'])
@login_required
def index():
    return render_template('index.html')

@app.route('/inicioAdmin', methods=['GET','POST'])
@login_required
def indexAdmin():
    return render_template('indexAdmin.html')

@app.route('/usuarios', methods=['GET','POST'])
@login_required
def usuarios():    
    users = db.getUsuarios()
    if request.method == 'POST':
        datos = db.getUsuarios()
        if datos:
            resultado = {
                'idusuario': datos[0],
                'usuario': datos[1],
                'nombres': datos[2],
                'tipo': datos[3],
            }
            return jsonify(resultado), 200
        else:
            return jsonify({'error': 'No se encontraron datos del usuario'}), 404
    return render_template('usuarios.html', usuarios=users)

@app.route('/usuariosAdmin', methods=['GET','POST'])
@login_required
def usuariosAdmin():    
    users = db.getUsuarios()
    if request.method == 'POST':
        datos = db.getUsuarios()
        if datos:
            resultado = {
                'idusuario': datos[0],
                'usuario': datos[1],
                'nombres': datos[2],
                'tipo': datos[3],
            }
            return jsonify(resultado), 200
        else:
            return jsonify({'error': 'No se encontraron datos del usuario'}), 404
    return render_template('usuariosAdmin.html', usuarios=users)

@app.route('/pacientes', methods=['GET','POST'])
def pacientes():
    datos= db.getPacientes()
    if request.method == 'POST':  
        datos= db.getPacientes()
        if datos:
            resultado = {
                'idpaciente': datos[0],
                'nombre_completo': datos[1],
                'fecha_nacimiento': datos[2].strftime("%d-%m-%Y"),
                'email': datos[3],
                'genero': datos[4],
                'peso': datos[5],
                'altura': datos[6],
            }
            return render_template('pacientes.html', pacientes=resultado)
        else:
            return jsonify({'error': 'No se encontraron datos del paciente'}), 404
    return render_template('pacientes.html', pacientes=datos)

@app.route('/trabajadores', methods=['GET','POST'])
def trabajadores():
    datos= db.getTrabajadores()
    if request.method == 'POST':  
        datos= db.getPacientes()
        if datos:
            resultado = {
                'idpaciente': datos[0],
                'nombre_completo': datos[1],
                'fecha_nacimiento': datos[2].strftime("%d-%m-%Y"),
                'email': datos[3],
                'genero': datos[4],
                'peso': datos[5],
                'altura': datos[6],
            }
            return render_template('trabajadores.html', pacientes=resultado)
        else:
            return jsonify({'error': 'No se encontraron datos del paciente'}), 404
    return render_template('trabajadores.html', trabajadores=datos)

@app.route('/evaluarpaciente', methods=['GET','POST'])
def evaluarpaciente():
    return render_template('evaluarpacientes.html')

@app.route('/evaluarpacienteAdmin', methods=['GET','POST'])
def evaluarpacienteAdmin():
    return render_template('evaluarpacientesAdmin.html')

@app.route('/analizar', methods=['POST'])
def analizar():
    if request.method == 'POST':
        datos = request.json.get('lista')

        valores =db.consultarDatos(datos.get('idpaciente'))
        print(valores)
        fuma = datos.get('fuma')
        medicamentos = datos.get('medicamentos')
        hipertension = datos.get('hipertension')
        diabetes = datos.get('diabetes')
        colesterol = datos.get('colesterol')
        presion_sistolica = datos.get('presionSistolica')
        presion_diastolica = datos.get('presionDiastolica')
        presion_cardiaca = datos.get('pulso')
        glucosa = datos.get('glucosa')
        comentarios = datos.get('comentarios')

        lista = [calcular_edad(valores[0]),int(valores[3]),int(fuma),int(medicamentos),int(hipertension),int(diabetes),float(colesterol),float(presion_sistolica),float(presion_diastolica),calcular_imc(valores[2],valores[1]),float(presion_cardiaca),float(glucosa)]
        #print(calcular_edad(fecha_nacimiento),altura,peso,genero,fuma,medicamentos,hipertension,diabetes,colesterol,presion_sistolica,presion_diastolica,presion_cardiaca,glucosa)
        resultado = predecir.analizar(lista)
        return jsonify(resultado)

    # En caso de una solicitud GET o cualquier otro método, puedes devolver la plantilla
    return render_template('evaluarpacientes.html')

@app.route('/buscardni', methods=['GET','POST'])
def buscardni():
    dni = request.json.get('dni')
    data= reniec.buscarDNI(dni)
    return jsonify(data)

#Funciones
@app.route('/agregarusuario', methods=['POST'])
def agregarusuario():
    dni=request.form.get('dniag')
    nombres=request.form.get('nombresag')
    apellidopaterno=request.form.get('apellidospaag')
    apellidomaterno=request.form.get('apellidosmaag')
    fechanacimiento=request.form.get('fechanacimiento')
    correo=request.form.get('correo')
    contraseña=request.form.get('contraseña')
    genero=request.form.get('genero')

    if dni is not None or nombres is not None or apellidopaterno is not None or apellidomaterno is not None or correo is not None or contraseña is not None or genero is not None or fechanacimiento is not None:
        db.agregarusuario(nombres,apellidopaterno,apellidomaterno,fechanacimiento,correo,contraseña,genero,dni)
        return redirect(url_for('usuariosAdmin'))
    else:
        response = {'message': 'Error: ID de usuario no proporcionado'}
        return jsonify(response), 400
    
@app.route('/agregarpaciente', methods=['POST'])
def agregarpaciente():
    dni=request.form.get('dniag')
    nombres=request.form.get('nombresag')
    apellidopaterno=request.form.get('apellidospaag')
    apellidomaterno=request.form.get('apellidosmaag')
    fechanacimiento=request.form.get('fechanacimiento')
    genero=request.form.get('genero')
    peso=request.form.get('peso')
    altura=request.form.get('altura')

    if  nombres is not None or apellidopaterno is not None or apellidomaterno is not None or genero is not None or peso is not None or altura is not None or dni is not None or fechanacimiento is not None:
        db.agregarpaciente(nombres,apellidopaterno,apellidomaterno,genero,peso,altura,fechanacimiento,dni)
        print(nombres,apellidopaterno,apellidomaterno,genero,peso,altura,fechanacimiento,dni)
        return redirect(url_for('pacientes'))
    else:
        response = {'message': 'Error: ID de paciente no proporcionado'}
        return jsonify(response), 400

@app.route('/borrarpaciente', methods=['POST'])
def borrarPaciente():
    pacienteid = request.form.get('idpacienteborrar')
    if pacienteid is not None:
        db.borrarPaciente(pacienteid)
        return redirect(url_for('pacientes'))
    else:
        response = {'message': 'Error: ID de paciente no proporcionado'}
        return jsonify(response), 400
    
@app.route('/borrarusuario', methods=['POST'])
def borrarUsuario():
    user_id = request.form.get('idusuario')
    if user_id is not None:
        db.borrarUsuario(user_id)
        return redirect(url_for('usuariosAdmin'))
    else:
        response = {'message': 'Error: ID de usuario no proporcionado'}
        return jsonify(response), 400
    
@app.route('/borrartrabajador', methods=['POST'])
def borrarTrabajador():
    trabajador_id = request.form.get('idtrabajadorbo')
    if trabajador_id is not None:
        db.borrarTrabajador(trabajador_id)
        return redirect(url_for('trabajadores'))
    else:
        response = {'message': 'Error: ID de usuario no proporcionado'}
        return jsonify(response), 400

    
@app.route('/editarusuario', methods=['POST'])
def editarusuario():
    usuarioid=request.form.get('idusuarios')
    nombre=request.form.get('nombres')
    apellidos=request.form.get('apellidos')
    correo=request.form.get('correo')
    '''if usuarioid is not None or nombre is not None or apellidos is not None or correo is not None:
        db.editarusuario(nombre,apellidos,correo,usuarioid)
        print(nombre,apellidos,correo,usuarioid)
        return redirect(url_for('usuarios'))
    else:
        response = {'message': 'Error: ID de paciente no proporcionado'}
        return jsonify(response), 400'''

'''@app.route('/editarpaciente', methods=['POST'])
def editarpaciente():
    pacienteid=request.form.get('idpacientes')
    nombre=request.form.get('nombres')
    apellidos=request.form.get('apellidos')
    fechanac=request.form.get('fechanacimiento')
    correo=request.form.get('correo')
    genero=request.form.get('genero')
    peso=request.form.get('peso')
    altura=request.form.get('altura')
    actividad=request.form.get('actividad')
    if pacienteid is not None or nombre is not None or apellidos is not None or fechanac is not None or correo is not None or genero is not None or peso is not None or altura is not None or actividad is not None:
        db.editarpaciente(nombre,apellidos,fechanac,correo,genero,peso,actividad,altura,pacienteid)
        return redirect(url_for('pacientes'))
    else:
        response = {'message': 'Error: ID de paciente no proporcionado'}
        return jsonify(response), 400'''


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

