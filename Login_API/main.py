from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import SQLModel, Field, Session, select
from database import engine, get_session

# Definimos la aplicación FastAPI
app = FastAPI(title="API de Login")

# ------------------------
# MODELOS DE USUARIO
# ------------------------
class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password: str

# ------------------------
# CREACIÓN DE TABLAS
# ------------------------
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# ------------------------
# RUTAS DE LA API
# ------------------------
@app.get("/")
def root():
    return {"message": "Bienvenido a la API de Login 🚀"}

@app.post("/register/")
def register(user: User, session: Session = Depends(get_session)):
    # Verificar si el usuario ya existe
    statement = select(User).where(User.username == user.username)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "Usuario registrado con éxito", "user": user}

@app.post("/login/")
def login(user: User, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == user.username)
    db_user = session.exec(statement).first()

    if not db_user or db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    return {"message": f"Bienvenido {db_user.username}!"}
