from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, BigInteger, Text
from sqlalchemy.sql.schema import ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database.models import Base
from ..database.serializable import Serializable
import pytz

global fecha_zona
fecha_zona = datetime.now(pytz.timezone('America/La_Paz'))


class Bitacora(Serializable, Base):
    way = {'usuario': {}}

    __tablename__ = 'USRMBITACORA'

    id = Column('id', BigInteger, primary_key=True)
    fkusuario = Column('fkusuario', Integer, ForeignKey('USRMUSUARIO.id'), nullable=True)
    ip = Column('ip', String(100), nullable=True)
    accion = Column('accion', String(200), nullable=True)
    fecha = Column('fecha', DateTime, nullable=False, default=fecha_zona)
    tabla = Column('tabla', String(200), nullable=True)
    identificador = Column('identificador', Integer, nullable=True)

    usuario = relationship('Usuario')

class Tracking(Serializable, Base):
    way = {'usuario': {}}

    __tablename__ = 'USRMTRACKING'

    id = Column('id', BigInteger, primary_key=True)
    latitud = Column('latitud', String(255), nullable=True)
    longitud = Column('longitud', String(255), nullable=True)
    bateria = Column('bateria', String(255), nullable=True)
    nombre_usuario = Column('nombre_usuario', String(255), nullable=True)
    fkusuario = Column('fk_usuario', Integer, ForeignKey('USRMUSUARIO.id'), nullable=True)

    usuario = relationship('Usuario')
