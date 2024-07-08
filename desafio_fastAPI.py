from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from datetime import datetime
from fastapi_pagination import Page, add_pagination, paginate

#### Database Configuration ####

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#### Models ####

class Categoria(Base):
    __tablename__ = "categorias"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)

class CentroDeTreinamento(Base):
    __tablename__ = "centros_de_treinamento"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    endereco = Column(String)
    proprietario = Column(String)

class Atleta(Base):
    __tablename__ = "atletas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    cpf = Column(String, unique=True, index=True)
    idade = Column(Integer)
    peso = Column(Integer)
    altura = Column(Integer)
    sexo = Column(String)
    centro_de_treinamento_id = Column(Integer, ForeignKey('centros_de_treinamento.id'))
    categoria_id = Column(Integer, ForeignKey('categorias.id'))
    data_insercao = Column(DateTime, default=datetime.utcnow)

    centro_de_treinamento = relationship("CentroDeTreinamento")
    categoria = relationship("Categoria")

#### Schemas ####

class CategoriaBase(BaseModel):
    nome: str

class CategoriaCreate(CategoriaBase):
    pass

class Categoria(CategoriaBase):
    id: int

    class Config:
        orm_mode = True

class CentroDeTreinamentoBase(BaseModel):
    nome: str
    endereco: str
    proprietario: str

class CentroDeTreinamentoCreate(CentroDeTreinamentoBase):
    pass

class CentroDeTreinamento(CentroDeTreinamentoBase):
    id: int

    class Config:
        orm_mode = True

class AtletaBase(BaseModel):
    nome: str
    cpf: str
    idade: int
    peso: int
    altura: int
    sexo: str
    centro_de_treinamento_id: int
    categoria_id: int

class AtletaCreate(AtletaBase):
    pass

class Atleta(AtletaBase):
    id: int
    data_insercao: datetime
    centro_de_treinamento: CentroDeTreinamento
    categoria: Categoria

    class Config:
        orm_mode = True

#### FastAPI Application and Routers ####

app = FastAPI()

Base.metadata.create_all(bind=engine)

#### Dependency ####

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#### Routers ####

@app.post("/categorias/", response_model=Categoria)
def create_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    db_categoria = Categoria(nome=categoria.nome)
    db.add(db_categoria)
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

@app.get("/categorias/", response_model=Page[Categoria])
def read_categorias(db: Session = Depends(get_db)):
    categorias = db.query(Categoria).all()
    return paginate(categorias)

@app.post("/centros_de_treinamento/", response_model=CentroDeTreinamento)
def create_centro_de_treinamento(centro: CentroDeTreinamentoCreate, db: Session = Depends(get_db)):
    db_centro = CentroDeTreinamento(**centro.dict())
    db.add(db_centro)
    db.commit()
    db.refresh(db_centro)
    return db_centro

@app.get("/centros_de_treinamento/", response_model=Page[CentroDeTreinamento])
def read_centros(db: Session = Depends(get_db)):
    centros = db.query(CentroDeTreinamento).all()
    return paginate(centros)

@app.post("/atletas/", response_model=Atleta)
def create_atleta(atleta: AtletaCreate, db: Session = Depends(get_db)):
    try:
        db_atleta = Atleta(**atleta.dict())
        db.add(db_atleta)
        db.commit()
        db.refresh(db_atleta)
        return db_atleta
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=303, detail=f"Já existe um atleta cadastrado com o CPF: {atleta.cpf}!")

@app.get("/atletas/", response_model=Page[Atleta])
def read_atletas(nome: str = None, cpf: str = None, db: Session = Depends(get_db)):
    query = db.query(Atleta)
    if nome:
        query = query.filter(Atleta.nome == nome)
    if cpf:
        query = query.filter(Atleta.cpf == cpf)
    atletas = query.all()
    return paginate(atletas)

#### Pagination Configuration ####

add_pagination(app)
