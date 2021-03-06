import hashlib
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.session import make_transient

from ..operaciones.managers import *

from ..database.connection import transaction
from server.common.managers import SuperManager, Error
from .models import *
from sqlalchemy.sql import func

import string
from random import *
import random



class UsuarioManager(SuperManager):
    def __init__(self, db):
        super().__init__(Usuario, db)

    def usuario_id(self,id):
        usuario= self.db.query(Usuario).filter(Usuario.id == id ).first()
        return usuario

    def listar_usuario_sucursal(self,sucursal_id):
        return self.db.query(Usuario).filter(Usuario.fksucursal == sucursal_id).filter(Rol.id != 1).all()


    def listar_usuario(self,usuario):
        usuario=self.db.query(Usuario).filter(Usuario.usuario==usuario).first()
        return usuario

    def name_role(self, rol):
        role = self.db.query(Rol).filter_by(id=rol).first()
        nombre_rol = role.nombre
        return nombre_rol

    def get_random_string(self):
        random_list = []
        for i in range(8):
            random_list.append(random.choice(string.ascii_uppercase + string.digits))
        return ''.join(random_list)

    def insert(self, Usuario):
        if Usuario.fkrol > 0:
            Usuario.password = hashlib.sha512(Usuario.password.encode()).hexdigest()
            if Usuario.nombre is not None:
                Usuario.nombre = Usuario.nombre.upper()
            if Usuario.apellidos is not None:
                Usuario.apellidos = Usuario.apellidos.upper()
            fecha = BitacoraManager(self.db).fecha_actual()
            b = Bitacora(fkusuario=Usuario.user_id,  accion="Se registró un usuario.", fecha=fecha)
            super().insert(b)
            u = super().insert(Usuario)
            return u
        return Error('unknown')

    def update(self, Usuarioupd):
        if Usuarioupd.password != None:
            Usuarioupd.password = hashlib.sha512(Usuarioupd.password.encode()).hexdigest()
        if Usuarioupd.nombre is not None:
            Usuarioupd.nombre = Usuarioupd.nombre.upper()
        if Usuarioupd.apellidos is not None:
            Usuarioupd.apellidos = Usuarioupd.apellidos.upper()
        fecha = BitacoraManager(self.db).fecha_actual()
        b = Bitacora(fkusuario=Usuarioupd.id, accion="Se modificó un usuario.", fecha=fecha)
        super().insert(b)

        user = self.db.query(Usuario).filter(Usuario.id == Usuarioupd.id).one()
        return super().update(Usuarioupd)

    def update_users(self, emailprev, emailnew, nameprev, namenew):
        u = self.db.query(Usuario).filter(Usuario.correo == emailprev).one()

        if u:
            ap_user = u.apellido
            result = nameprev.index(ap_user)
            print(result)
            u.correo = emailnew

    def delete_user(self, usuario, Usuariocr):
        if usuario.enabled==True:
            usuario.enabled=False
            message = "Se inhabilitó un usuario."
        else:
            usuario.enabled=True
            message = "Se habilitó un usuario."
        fecha = BitacoraManager(self.db).fecha_actual()
        b = Bitacora(fkusuario=Usuariocr, accion=message, fecha=fecha)
        super().insert(b)
        super().insert(usuario)
        return True

    def activate_Usuarios(self, id, Usuario, ip):
        x = self.db.query(Usuario).filter(Usuario.id == id).one()
        x.enabled = 1
        fecha = BitacoraManager(self.db).fecha_actual()
        b = Bitacora(fkusuario=Usuario, ip=ip, accion="Se activó un usuario.", fecha=fecha)
        super().insert(b)
        self.db.merge(x)
        self.db.commit()

    def get_privileges(self, id, route):
        parent_module = self.db.query(Modulo).\
            join(Rol.modulos).join(Usuario).\
            filter(Modulo.ruta == route).\
            filter(Usuario.id == id).\
            filter(Usuario.enabled).\
            first()
        if not parent_module:
            return dict()
        modules = self.db.query(Modulo).\
            join(Rol.modulos).join(Usuario).\
            filter(Modulo.fkmodulo == parent_module.id).\
            filter(Usuario.id == id).\
            filter(Usuario.enabled)
        privileges = {parent_module.nombre: parent_module}
        for module in modules:
            privileges[module.nombre] = module
        return privileges

    def list_all(self,usuario):
        if usuario.fksucursal == 1:
            return dict(objects=self.db.query(Usuario).filter(Usuario.fkrol == Rol.id).filter(Rol.id != 1).distinct().all())
        else:
            return dict(objects=self.db.query(Usuario).filter(Usuario.fkrol == Rol.id).filter(Usuario.fksucursal == usuario.fksucursal).filter(Rol.id != 1).distinct().all())
    def ordenar_usuario(self,usuarios):
        lista = list()
        for usuario in usuarios:
            rol= usuario.rol.nombre
            sucursal= usuario.sucursal.nombre
            usuario= usuario.get_dict()
            usuario['sucursal']= sucursal
            usuario['rol']= rol
            lista.append(usuario)
        return lista

    def listar(self):
        return self.db.query(Usuario).filter(Usuario.enabled == True).filter(Rol.nombre != "ADMINISTRADOR").distinct()


    def has_access(self, id, route):
        aux = self.db.query(Usuario.id).\
            join(Rol).join(Acceso).join(Modulo).\
            filter(Usuario.id == id).\
            filter(Modulo.ruta == route).\
            filter(Usuario.enabled).\
            all()
        return len(aux) != 0

    def get_page(self, page_nr=1, max_entries=10, like_search=None, order_by=None, ascendant=True, query=None):
        query = self.db.query(Usuario).join(Rol).filter(Rol.id > 1)
        return super().get_page(page_nr, max_entries, like_search, order_by, ascendant, query)

    def login_Usuario(self, username, password):
        password = hashlib.sha512(password.encode()).hexdigest()
        return self.db.query(Usuario).filter(Usuario.usuario == username).filter(Usuario.password == password).filter(
            Usuario.enabled == 1)

    def get_userById(self, id):
        return dict(profile=self.db.query(Usuario).filter(Usuario.id == id).first())

    def update_password(self, Usuario):
        Usuario.password = hashlib.sha512(Usuario.password.encode()).hexdigest()
        return super().update(Usuario)

    def get_by_password(self, Usuario_id, password):
        return self.db.query(Usuario).filter(Usuario.id == Usuario_id). \
            filter(Usuario.password == hashlib.sha512(str(password).encode()).hexdigest()).first()

    def get_by_pass(self, Usuario_id):
        return self.db.query(Usuario).filter(Usuario.id == Usuario_id).first()

    def update_profile(self, Usuarioprf):
        usuario = self.db.query(Usuario).filter_by(id=Usuarioprf.id).first()
        usuario.nombre = Usuarioprf.nombre
        usuario.apellido = Usuarioprf.apellido
        usuario.correo = Usuarioprf.correo
        self.db.merge(usuario)
        b = Bitacora(fkusuario=usuario.id, accion="Se actualizó perfil de usuario.", fecha=fecha_zona, tabla='cb_usuarios_usuario', identificador=usuario.id)
        super().insert(b)
        self.db.commit()
        return usuario

    def validar_usuario(self, username, password):
        password = hashlib.sha512(password.encode()).hexdigest()
        return self.db.query(func.count(Usuario.id)).filter(Usuario.usuario == username).filter(
            Usuario.enabled == True).filter(Usuario.password == password).scalar()

    def validar_usuario_sesion(self, codigo, usuario):
        return self.db.query(func.count(Usuario.id)).filter(
            Usuario.enabled == True).filter(Usuario.id == usuario).scalar()

    def activate_Usuario(self, usuario):
        usuario = self.db.query(Usuario).filter_by(id=usuario).first()
        usuario.activo = 1
        self.db.merge(usuario)
        self.db.commit()

    def update_codigo(self, usuario):
        x = self.db.query(Usuario).filter(Usuario.id == usuario).one()
        x.activo = 0
        x.codigo = self.get_random_string()
        x.token = "Sin Token"
        self.db.commit()
        self.db.close()
        return x

    def listar_todo(self):
        return self.db.query(Usuario).filter(Usuario.fkrol == Rol.id).filter(Rol.id != 1).distinct().all()

    def funcion_aux(self, objeto):
        lista = list()
        for o in objeto:
            rol = o.rol.nombre
            o = o.get_dict()
            o['rol']=rol
            lista.append(o)
        return lista

class SucursalManager(SuperManager):
    def __init__(self, db):
        super().__init__(Sucursal, db)

    def listar(self,usuario):
        if usuario.fksucursal == 1:
            a =self.db.query(Sucursal).filter(Sucursal.enabled == True)
        else:
            a = self.db.query(Sucursal).filter(Sucursal.enabled == True).filter(Sucursal.id == usuario.fksucursal )
        return a
    def listar_id(self,id):
        sucursal = self.db.query(Sucursal).filter(Sucursal.enabled == True).filter(Sucursal.id == id ).first()
        return str(sucursal.nombre)


    def list_all(self):
        return dict(objects=self.db.query(Sucursal).distinct().all())

class RolManager(SuperManager):
    def __init__(self, db):
        super().__init__(Rol, db)

    def get_page(self, page_nr=1, max_entries=10, like_search=None, order_by=None, ascendant=True, query=None):
        query = self.db.query(self.entity).filter(Rol.id > 1)
        return super().get_page(page_nr, max_entries, like_search, order_by, ascendant, query)

    def insert(self, rol):
        fecha = BitacoraManager(self.db).fecha_actual()
        b = Bitacora(fkusuario=rol.user, accion="Se registró un rol.", fecha=fecha)
        super().insert(b)
        a = super().insert(rol)
        return a

    def update(self, rol):
        fecha = BitacoraManager(self.db).fecha_actual()
        b = Bitacora(fkusuario=rol.user, ip=rol.ip, accion="Se modificó un rol.", fecha=fecha)
        super().insert(b)
        a = super().update(rol)
        return a

    def list_all(self):
        return dict(objects=self.db.query(Rol).distinct().all())

    def listar_todo(self):
        return dict(objects=self.db.query(Rol).filter(Rol.id != 1).distinct().all())

    def get_all(self):
        return self.db.query(Rol).filter(Rol.enabled == True).filter(Rol.id != 1)

    def delete_rol(self, id, enable, Usuariocr, ip):
        x = self.db.query(Rol).filter(Rol.id == id).one()
        x.enabled = enable

        if enable == True:
            message = "Se habilitó un rol."
        else:
            users = self.db.query(Usuario).filter(Usuario.enabled == True).filter(Usuario.fkrol == id).all()
            for u in users:
                u.enabled = False

            message = "Se inhabilitó un rol y usuarios relacionados."

        fecha = BitacoraManager(self.db).fecha_actual()
        b = Bitacora(fkusuario=Usuariocr, ip=ip, accion=message, fecha=fecha)
        super().insert(b)
        self.db.merge(x)
        self.db.commit()


class ModuloManager:
    def __init__(self, db):
        self.db = db

    def list_all(self):
        return self.db.query(Modulo).filter(Modulo.fkmodulo==None)


class LoginManager:

    def login(self, username, password):
        """Retorna un usuario que coincida con el username y password dados.

        parameters
        ----------
        Usuarioname : str
        password : str
            El password deberá estar sin encriptar.

        returns
        -------
        Usuario
        None
            Retornará None si no encuentra nada.
        """
        password = hashlib.sha512(password.encode()).hexdigest()
        with transaction() as session:
            usuario = session.query(Usuario).\
                options(joinedload('rol').
                        joinedload('modulos').
                        joinedload('modulo')).\
                filter(Usuario.usuario == username).\
                filter(Usuario.password == password).\
                filter(Usuario.enabled).\
                first()
            if not usuario:
                return None
            session.expunge(usuario)
            make_transient(usuario)
        usuario.rol.modulos = self.order_modules(usuario.rol.modulos)
        return usuario



    def not_enabled(self, username, password):
        """Retorna un usuario que coincida con el username y password dados.

        parameters
        ----------
        Usuarioname : str
        password : str
            El password deberá estar sin encriptar.

        returns
        -------
        Usuario
        None
            Retornará None si no encuentra nada.
        """
        password = hashlib.sha512(password.encode()).hexdigest()
        with transaction() as session:
            usuario = session.query(Usuario).\
                options(joinedload('rol').
                        joinedload('modulos').
                        joinedload('modulo')).\
                filter(Usuario.usuario == username).\
                filter(Usuario.password == password).\
                filter(Usuario.enabled == False).\
                first()
            if not usuario:
                return None
            session.expunge(usuario)
            make_transient(usuario)
        usuario.rol.modulos = self.order_modules(usuario.rol.modulos)
        return usuario

    def get(self, key):
        with transaction() as session:
            usuario = session.query(Usuario).\
                options(joinedload('rol').
                        joinedload('modulos').
                        joinedload('modulo')).\
                filter(Usuario.id == key).\
                filter(Usuario.enabled).\
                first()
            if not usuario:
                return None
            session.expunge(usuario)
            make_transient(usuario)
        usuario.rol.modulos = self.order_modules(usuario.rol.modulos)
        return usuario

    def order_modules(self, modules):
        modules.sort(key=lambda x: x.id)
        mods_parents = []
        mods = {}
        while len(modules) > 0:
            module = modules.pop(0)
            module.modulo = []
            mods[module.id] = module
            parent_module = mods.get(module.fkmodulo, None)
            if parent_module:
                parent_module.modulo.append(module)
            else:
                mods_parents.append(module)
        return mods_parents
