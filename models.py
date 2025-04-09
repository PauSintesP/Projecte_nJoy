from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Numeric, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Localidad(Base):
    __tablename__ = "LOCALIDAD"
    
    id = Column(Integer, primary_key=True, index=True)
    ciudad = Column(String(100), nullable=False)
    
    eventos = relationship("Evento", back_populates="localidad")

class Organizador(Base):
    __tablename__ = "ORGANIZADOR"
    
    dni = Column(String(20), primary_key=True)
    ncompleto = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    telefono = Column(String(15), nullable=False)
    web = Column(String(255))
    
    eventos = relationship("Evento", back_populates="organizador")

class Genero(Base):
    __tablename__ = "GENERO"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)

class Artista(Base):
    __tablename__ = "ARTISTA"
    
    id = Column(Integer, primary_key=True, index=True)
    nartistico = Column(String(100), nullable=False)
    nreal = Column(String(100), nullable=False)

class Usuario(Base):
    __tablename__ = "USUARIO"
    
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String(50), nullable=False, unique=True)
    ncompleto = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    fnacimiento = Column(Date, nullable=False)
    contrasena = Column(String(255), nullable=False)
    
    pagos = relationship("Pago", back_populates="usuario")

class Evento(Base):
    __tablename__ = "EVENTO"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(201), nullable=False)
    localidad_id = Column(Integer, ForeignKey("LOCALIDAD.id"), nullable=False)
    recinto = Column(String(100), nullable=False)
    plazas = Column(Integer, nullable=False)
    fechayhora = Column(DateTime, nullable=False)
    tipo = Column(String(50), nullable=False)
    categoria_precio = Column(String(50), nullable=False)
    organizador_dni = Column(String(20), ForeignKey("ORGANIZADOR.dni"), nullable=False)
    genero = Column(Integer, ForeignKey("GENERO.id"), nullable=False)
    
    localidad = relationship("Localidad", back_populates="eventos")
    organizador = relationship("Organizador", back_populates="eventos")
    tickets = relationship("Ticket", back_populates="evento")

class Ticket(Base):
    __tablename__ = "TICKET"
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("EVENTO.id"), nullable=False)
    activado = Column(Boolean, default=True)
    evento = relationship("Evento", back_populates="tickets")
    pago = relationship("Pago", back_populates="ticket", uselist=False)

class Pago(Base):
    __tablename__ = "PAGO"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("USUARIO.id"), nullable=False)
    metodo_pago = Column(String(50), nullable=False)
    total = Column(Numeric(10, 2), nullable=False)
    fecha = Column(DateTime, nullable=False)
    ticket_id = Column(Integer, ForeignKey("TICKET.id"), unique=True)
    
    usuario = relationship("Usuario", back_populates="pagos")
    ticket = relationship("Ticket", back_populates="pago")