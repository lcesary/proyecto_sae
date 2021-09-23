from tornado.gen import coroutine
from .managers import *
from ..usuarios.managers import *
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from requests.exceptions import HTTPError

from ..common.controllers import CrudController, SuperController, ApiController
#from xhtml2pdf import pisa
import os.path

import requests
import json
class Report:
    """
    def html_to_pdf(self, sourceHtml, nombre):
        outputFilename = 'server/common/resources/downloads/' + nombre

        resultFile = open(outputFilename, "w+b")
        pisaStatus = pisa.CreatePDF(
            sourceHtml,
            dest=resultFile)
        resultFile.close()

        return pisaStatus.err
    """
global report
report = Report()
global image_report
image_report = "server/common/resources/images/pst.jpg"
MY_API_KEY="770cecab-b21a-4d10-98f1-35196301e715"

class BitacoraController(CrudController):

    manager = BitacoraManager
    html_index = "operaciones/views/bitacora/index.html"
    html_table = "operaciones/views/bitacora/table.html"
    routes = {
        '/bitacora': {'GET': 'index', 'POST': 'table'},
        '/api/mandar_notificacion': {'POST': 'mandar_notificacion'},

    }   
    def index(self):
        self.set_session()
        self.verif_privileges()
        result = self.manager(self.db).list_all()
        result['privileges'] = UsuarioManager(self.db).get_privileges(self.get_user_id(), self.request.uri)
        result['ubicaciones'] = BitacoraManager(self.db).obtenerUbicaciones()
        result.update(self.get_extra_data())
        self.render(self.html_index, **result)
        self.db.close()


    def mandar_notificacion(self):
        header = {"Content-Type": "application/json; charset=utf-8",
                "Authorization": "Basic MWQwYjZjMjUtYTE1Ni00ZjlhLWFjMjItMjk0ZjA2ZjljZWU2"}

  
        payload = {"app_id": "770cecab-b21a-4d10-98f1-35196301e715",
                "included_segments": ["All"],
                "contents": {"en": "Notificacion de Hernando "}}
        
        req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
        print(req.status_code, req.reason)

class ApiAppController(ApiController):
    routes = {
        '/api/v3/test_sae': {'POST': 'test_sae'},

    }   

    def test_sae(self):
      self.set_session()
      data = json.loads(self.request.body.decode('utf-8'))
      print("Funciona estos son los datos ||Bateria-> "+str(data['bateria'])+"% ||Longitud-> "+str(data['longitud'])+" ||Latitud-> "+str(data['latitud']))
      self.respond(success=True, message="Datos insertados correctamente", response=data)
      self.db.close()

    