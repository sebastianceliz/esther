from flask import jsonify
import psycopg2
import csv
import os
from datetime import datetime
import hashlib

#Funciones
def calcular_edad(fecha_nacimiento):
    fecha_actual = datetime.now()
    edad = fecha_actual.year - fecha_nacimiento.year - ((fecha_actual.month, fecha_actual.day) < (fecha_nacimiento.month, fecha_nacimiento.day))   
    return edad

def encriptar(contraseña):
    sha256 = hashlib.sha256()
    text_bytes = contraseña.encode('utf-8')
    sha256.update(text_bytes)
    hash_hex = sha256.hexdigest().upper()

    return hash_hex

########
  
def getUsuarios():
    connection = psycopg2.connect(
        dbname='bdtesis',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor = connection.cursor()
    query = "select u.idusuario, u.usuario, ((string_to_array(tr.nombres, ' '))[1] || ' ' || tr.apellido_paterno) AS nombres, ti.tipo from usuario u inner join tipousuario ti on ti.idtipo=u.tipousuarioid inner join trabajador tr on tr.idusuario=u.idusuario where u.tipousuarioid=2;"
    try:
        cursor.execute(query)
        users=cursor.fetchall()
        return users
    except Exception as e:
        print(e)

def getPacientes():
    connection = psycopg2.connect(
        dbname='bdtesis',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor = connection.cursor()
    query = "SELECT idpaciente, CONCAT(nombres, ' ', apellido_paterno) AS nombre_completo, fecha_nacimiento, CASE WHEN genero = '1' THEN 'Femenino' ELSE 'Masculino' END AS genero, peso, altura FROM paciente;"
    try:
        cursor.execute(query)
        pacientes=cursor.fetchall()
        return pacientes
    except Exception as e:
        print(e)

def getTrabajadores():
    connection = psycopg2.connect(
        dbname='bdtesis',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor = connection.cursor()
    query = "SELECT idtrabajador, CONCAT(nombres, ' ', apellido_paterno) AS nombre_completo,CASE WHEN genero = '1' THEN 'Femenino' ELSE 'Masculino' END AS genero, fecha_nacimiento, email FROM trabajador;"
    try:
        cursor.execute(query)
        pacientes=cursor.fetchall()
        return pacientes
    except Exception as e:
        print(e)

#Usuario
def agregarusuario(nombres,apellidopaterno,apellidomaterno,fechanacimiento,correo,contraseña,genero,dni):
    connection = psycopg2.connect(
        dbname='bdtesis',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor= connection.cursor()
    query = "select idusuario from usuario order by idusuario desc limit 1"
    cursor.execute(query)
    corr=cursor.fetchone()
    if corr is None:
        corr= 1
    else:
        corr=corr[0]+1
    
    cursor2= connection.cursor()
    query2="insert into usuario values(%s,%s,%s,2)"
    try:
        cursor2.execute(query2,(corr,correo,encriptar(contraseña)))

        cursor3= connection.cursor()
        query3 = "select idtrabajador from trabajador order by idtrabajador desc limit 1"
        cursor3.execute(query3)
        corrp=cursor3.fetchone()
        if corrp is None:
            corrp= 1
        else:
            corrp=corrp[0]+1 
        cursor4=connection.cursor()
        query4="insert into trabajador values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        cursor4.execute(query4,(corrp,nombres,apellidopaterno,apellidomaterno,correo,genero,corr,fechanacimiento,encriptar(dni)))
        return "Registrado correctamente"
    except Exception as e:
        print(e)

def agregarpaciente(nombres,apellidopaterno,apellidomaterno,genero,peso,altura,fechanacimiento,dni):
    connection = psycopg2.connect(
        dbname='bdtesis',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor= connection.cursor()
    query = "select idpaciente from paciente order by idpaciente desc limit 1"
    cursor.execute(query)
    corr=cursor.fetchone()
    if corr is None:
        corr= 1
    else:
        corr=corr[0]+1
    
    cursor2= connection.cursor()
    query2="insert into paciente values(%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    try:
        cursor2.execute(query2,(corr,nombres,apellidopaterno,apellidomaterno,fechanacimiento,genero,peso,altura,encriptar(dni)))
        return "Registrado correctamente"
    except Exception as e:
        print(e)

def consultarDatos(id):
    connection = psycopg2.connect(
        dbname='bdtesis',
        user='postgres',
        password='71889623',
    ) 
    connection.autocommit = True
    cursor= connection.cursor()

    try:
        query = "select fecha_nacimiento, altura, peso, genero from paciente where idpaciente=%s"
        cursor.execute(query,(id))
        datos=cursor.fetchone()        
        return datos
    except Exception as e:
        print(e)

def borrarPaciente(paciente_id):
    connection = psycopg2.connect(
        dbname='bdtesis',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor = connection.cursor()
    query = "DELETE FROM paciente WHERE idpaciente = %s"
    try:
        cursor.execute(query, (paciente_id,))
        response = {'message': 'Paciente eliminado exitosamente'}
        return jsonify(response)
    except Exception as e:
        print(e)
        response = {'message': 'Error al eliminar el paciente'}
        return jsonify(response), 500
    
def borrarUsuario(user_id):
    connection = psycopg2.connect(
        dbname='bdtesis',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor = connection.cursor()
    query = "DELETE FROM trabajador WHERE idusuario = %s"
    try:
        cursor.execute(query, (user_id,))
        cursor1 = connection.cursor()
        query1 = "DELETE FROM usuario WHERE idusuario = %s"
        cursor1.execute(query1, (user_id,))
        response = {'message': 'Usuario eliminado exitosamente'}
        return jsonify(response)
    except Exception as e:
        print(e)
        response = {'message': 'Error al eliminar el usuario'}
        return jsonify(response), 500

def borrarTrabajador(trabajador_id):
    connection = psycopg2.connect(
        dbname='bdtesis',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor = connection.cursor()
    query = "DELETE FROM trabajador WHERE idtrabajador = %s"
    try:
        cursor.execute(query, (trabajador_id,))
        response = {'message': 'Trabajador eliminado exitosamente'}
        return jsonify(response)
    except Exception as e:
        print(e)
        response = {'message': 'Error al eliminar el trabajador'}
        return jsonify(response), 500  
    
'''
#Funcionalidad
def consultarGenero():
    connection = psycopg2.connect(
        dbname='tesisdietas',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor = connection.cursor()
    query = "SELECT COUNT(*) AS cantidad FROM perfilpaciente where genero=%s;"
    try:
        cursor.execute(query,(0,))
        val=cursor.fetchone()
        cursor1 = connection.cursor()
        query1 = "SELECT COUNT(*) AS cantidad FROM perfilpaciente where genero=%s;"
        cursor1.execute(query1,(1,))
        val1=cursor1.fetchone()

        lista =[val,val1]
        print(lista)
        return lista
    except Exception as e:
        print(e)
        response = {'message': 'Error al consultar el perfil del paciente'}
        return jsonify(response), 500
    
def cantidadUsuarios():
    connection = psycopg2.connect(
        dbname='tesisdietas',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor = connection.cursor()
    query = "SELECT COUNT(*) from usuario;"
    try:
        cursor.execute(query)
        val=cursor.fetchone()
        return val
    except Exception as e:
        print(e)
        response = {'message': 'Error al consultar el perfil del paciente'}
        return jsonify(response), 500
       
def mostrarusuario(idusuario):
    connection = psycopg2.connect(
        dbname='tesisdietas',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor= connection.cursor()
    query="select u.idusuario, p.nombres, p.apellidos, p.correo from paciente p inner join usuario u on u.idusuario=p.idusuario where u.idusuario=%s;"
    try:
        cursor.execute(query,(idusuario,))
        datos=cursor.fetchone()
        return datos
    except Exception as e:
        print(e)

def editarusuario(nombre,apellidos,correo, idusuario):
    connection = psycopg2.connect(
        dbname='tesisdietas',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor= connection.cursor()
    query="update usuario set usuario=%s where idusuario=%s;"
    try:
        cursor.execute(query,(correo,idusuario))
        cursor2=connection.cursor()
        query2="update paciente set nombres=%s,apellidos=%s,correo=%s where idusuario=%s;"
        cursor2.execute(query2,(nombre,apellidos,correo,idusuario))
        return "Actualizado correctamente"
    except Exception as e:
        print(e)

def mostrarpaciente(idpaciente):
    connection = psycopg2.connect(
        dbname='tesisdietas',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor= connection.cursor()
    query="select pa.idpaciente,pa.nombres,pa.apellidos,pa.fechanacimiento,pa.correo,pp.genero,pp.peso,pp.altura,pp.actividadfisica from paciente pa inner join perfilpaciente pp on pp.idpaciente=pa.idpaciente where pa.idpaciente=%s order by fecha DESC LIMIT 1;"
    try:
        cursor.execute(query,(idpaciente,))
        datos=cursor.fetchone()
        return datos
    except Exception as e:
        print(e)

def calcularedad(fecha_nacimiento):
    fecha_actual = datetime.now()
    fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
    edad = fecha_actual.year - fecha_nacimiento.year
    if fecha_actual.month < fecha_nacimiento.month:
        edad -= 1
    elif fecha_actual.month == fecha_nacimiento.month and fecha_actual.day < fecha_nacimiento.day:
        edad -= 1
    return edad

def editarpaciente(nombres, apellidos, fechanacimiento, correo, genero, peso, actividad, altura, idpaciente):
    connection = psycopg2.connect(
        dbname='tesisdietas',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor= connection.cursor()
    query="update paciente set nombres=%s, apellidos=%s, correo=%s, fechanacimiento=%s where idpaciente=%s "
    try:
        cursor.execute(query,(nombres,apellidos,correo,fechanacimiento,idpaciente))
        cursor2= connection.cursor()
        query2="update perfilpaciente set edad=%s, altura=%s, peso=%s, genero=%s, actividadfisica=%s, fecha=CURRENT_DATE where idpaciente=%s "
        partesfecha=fechanacimiento.split("-")
        ordenado=partesfecha[2]+"-"+partesfecha[1]+"-"+partesfecha[0]
        print(ordenado)
        cursor2.execute(query2,(calcularedad(ordenado),altura,peso,genero,actividad,idpaciente))
        return "Actualizado correctamente"
    except Exception as e:
        print(e)

def pacientessinperfil():
    connection = psycopg2.connect(
        dbname='tesisdietas',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor= connection.cursor()
    query = "select CONCAT(pa.idpaciente,' - ',pa.nombres, '_', pa.apellidos,' - ',pa.correo) from paciente pa left join perfilpaciente pp on pp.idpaciente=pa.idpaciente where pp.idpaciente is null"
    cursor.execute(query)
    valores=cursor.fetchall()
    return valores
    
def agregarpaciente(idpaciente,genero,peso,altura,actividad,fechanacimiento):
    connection = psycopg2.connect(
        dbname='tesisdietas',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor= connection.cursor()
    query = "select idperfil from perfilpaciente order by idperfil desc limit 1"
    cursor.execute(query)
    val=cursor.fetchone()
    if val is None:
        nval= 1
    else:
        nval=val[0]+1
    
    cursor2= connection.cursor()
    query2="insert into perfilpaciente values(%s,%s,%s,%s,%s,%s,%s,CURRENT_DATE,1)"
    try:
        partesfecha=fechanacimiento.split("-")
        ordenado=partesfecha[2]+"-"+partesfecha[1]+"-"+partesfecha[0]
        cursor2.execute(query2,(nval,calcularedad(ordenado),altura,peso,actividad,genero,idpaciente))
        return "Registrado correctamente"
    except Exception as e:
        print(e)

def filtrarmes(mes):
    connection = psycopg2.connect(
        dbname='tesisdietas',
        user='postgres',
        password='71889623',
    )
    connection.autocommit = True
    cursor= connection.cursor()
    try:
        query="SELECT pa.idpaciente, CONCAT(pa.nombres, ' ', pa.apellidos) AS nombre_completo, DATE_PART('year', AGE(pa.fechanacimiento)) AS edad, pa.correo, CASE WHEN pp.genero = 0 THEN 'Masculino' ELSE 'Femenino' END AS genero , pp.peso, pp.altura FROM paciente pa inner join perfilpaciente pp on pp.idpaciente=pa.idpaciente where EXTRACT(MONTH FROM fecha) = %s order by pa.idpaciente;"
        cursor.execute(query,(mes,))
        valores=cursor.fetchall()
        print(valores)
        return valores
    except Exception as e:
        print(e)'''
