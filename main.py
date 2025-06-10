from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from sqlmodel import SQLModel
from db.database import engine
import uvicorn
from routes import auth, user, order, items_ordered, report

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# Configuración de Jinja2
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("forgot_password.html", {"request": request})

# Definir las rutas de la API
app.include_router(user.router, prefix="/api", tags=["Users"])
app.include_router(order.router, prefix="/api", tags=["Orders"])
app.include_router(items_ordered.router, prefix="/api", tags=["Items Ordered"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(report.router, prefix="/api", tags=["Report"])

# Manejo de excepciones globales
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred.", "error": str(exc)},
    )

def init_db():
    SQLModel.metadata.create_all(engine)

if __name__ == "__main__":
    init_db
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)