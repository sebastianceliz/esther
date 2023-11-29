import json
from util import CustomJsonEncoder
from apis_net_pe import ApisNetPe
from config import Config



def buscarDNI(dni):
    try:
        api_consultas = ApisNetPe(Config.APIS_TOKEN)
        datos=api_consultas.get_person(str(dni))
        if datos:
            return datos
        else:
            return json.dumps({'status': False, 'data':'Número de DNI no encontrado'})
    except:
        return json.dumps({'status':False, 'data':'El servicio está dehabilitado'},cls=CustomJsonEncoder)
        
