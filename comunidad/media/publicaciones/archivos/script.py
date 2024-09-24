import xmlrpc.client
from datetime import datetime

# Configuración del servidor
'''
url = 'https://www.asisurl.cu'
db = 'asisurl'
username = 'admin_asisurl'
password = '%eHX3DeG^6UNe@N3v&G9C9NhN'
'''
url = 'https://www.asisurl.cu'
db = 'asisurl'
username = 'luis.gonzalez'
password = 'Blackflag.2023*'
'''
url = 'http://localhost:8069'
db = 'admin'
username = 'dsa'
password = '1'
'''
# Conexión al servidor
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
print("common: ", common)
uid = common.authenticate(db, username, password, {})
print("uid: ", uid)

# Conexión al objeto
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
print("models: ", models)

user = models.execute_kw(db, uid, password, 'res.users', 'read', [uid], {'fields': ['partner_id']})
partner_id = user[0]['partner_id'][0]
print("partner_id: ", partner_id)

# Obtener IDs de eventos en los que el usuario es asistente
attendee_ids = models.execute_kw(db, uid, password, 'calendar.attendee', 'search', [[['partner_id', '=', partner_id]]])
print("attendee_ids: ", attendee_ids)
'''
# Obtener detalles de los eventos creados por el usuario logueado
events = models.execute_kw(db, uid, password, 'calendar.event', 'search_read', [[['user_id', '=', uid]]], {'fields': ['name', 'start', 'stop', 'description', 'attendee_ids']})

if not events:
    print("Nada")
else:
    print("Cantidad de eventos creados por el usuario: ", len(events))
    events.reverse()
    for event in events:
        print("event: ", event)
        # Obtener los partner_id de los attendee_ids
        for attendee_id in event['attendee_ids']:
            attendee = models.execute_kw(db, uid, password, 'calendar.attendee', 'read', [attendee_id], {'fields': ['partner_id']})
            print("attendee_id: ", attendee_id, "partner_id: ", attendee[0]['partner_id'])

'''
print("/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////")
# Obtener eventos cuyos attendee_ids incluyen alguno de los attendee_ids relacionados con el usuario
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
related_events = models.execute_kw(db, uid, password, 'calendar.event', 'search_read', [[['attendee_ids', 'in', attendee_ids],['start','>=',now]]], {'fields': ['name', 'start', 'stop', 'description', 'attendee_ids']})

if not related_events:
    print("No hay eventos relacionados")
else:
    print("Cantidad de eventos relacionados: ", len(related_events))
    related_events.reverse()
    for event in related_events:
        print("related event: ", event['name'], event['start'])
        # Obtener los partner_id de los attendee_ids
        '''
        for attendee_id in event['attendee_ids']:
            attendee = models.execute_kw(db, uid, password, 'calendar.attendee', 'read', [attendee_id], {'fields': ['partner_id']})
            print("attendee_id: ", attendee_id, "partner_id: ", attendee[0]['partner_id'])
            '''




'''
primero, respondeme en mi idioma, lo otro, necesito que me ayudes a desarrollar una apk para android desde linux con flutter para android con el android studio, ten en cuenta que ya lo tengo instalado y configurado pero no conozco la sintaxis ni estructura que requiere, entonces quiero que empecemos por algo basico e irlo extendiendo poco a poco, lo primero que necesito es que la aplicacion se conecte a una bd muy especifica de odoo 16 en internet, despues te especifico los detalles de esta, y muestre en pantalla el estado de la conexion y demas informaciones utiles, el funcionamiento esperado a algo similar a lo que realiza este script de python que creé y probé que funciona bien:
script.py:
import xmlrpc.client
from datetime import datetime

# Configuración del servidor
'''
url = 'https://www.asisurl.cu'
db = 'asisurl'
username = 'admin_asisurl'
password = '%eHX3DeG^6UNe@N3v&G9C9NhN'
'''
url = 'https://www.asisurl.cu'
db = 'asisurl'
username = 'luis.gonzalez'
password = 'Blackflag.2023*'
'''
url = 'http://localhost:8069'
db = 'admin'
username = 'dsa'
password = '1'
'''
# Conexión al servidor
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
print("common: ", common)
uid = common.authenticate(db, username, password, {})
print("uid: ", uid)

# Conexión al objeto
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
print("models: ", models)

user = models.execute_kw(db, uid, password, 'res.users', 'read', [uid], {'fields': ['partner_id']})
partner_id = user[0]['partner_id'][0]
print("partner_id: ", partner_id)

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
related_events = models.execute_kw(db, uid, password, 'calendar.event', 'search_read', [[['attendee_ids', 'in', attendee_ids],['start','>=',now]]], {'fields': ['name', 'start', 'stop', 'description', 'attendee_ids']})

if not related_events:
    print("No hay eventos relacionados")
else:
    print("Cantidad de eventos relacionados: ", len(related_events))
    related_events.reverse()
    for event in related_events:
        print("related event: ", event['name'], event['start'])

# Obtener IDs de eventos en los que el usuario es asistente
attendee_ids = models.execute_kw(db, uid, password, 'calendar.attendee', 'search', [[['partner_id', '=', partner_id]]])
print("attendee_ids: ", attendee_ids)
los datos de conexion son los mismos que estan en el script, crees que puedes hacerlo? necesito que seas muy detallista y me expliques paso por paso sin dejarte nada lo que debo hacer y donde debo poner el codigo que me des, no te limites a la hora de escribir el codigo, damelo COMPLETO y no supongas que se hacer ciertas cosas que pueden ser obvias, quiero aprender
'''
