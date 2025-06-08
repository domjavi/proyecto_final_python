## Configuración del Proyecto

### Variables de Entorno

El proyecto utiliza un único archivo `.env` para configuraciones tanto locales como en Docker. 

Ejemplo de `.env`:
```properties
# App DB connection
DB_USER=postgres
DB_PASSWORD=123456
# DB_HOST=localhost
DB_HOST=localhost
DB_PORT=5432
DB_NAME=db
# DB_URL=postgresql://postgres:123456@localhost:5432/db

# PostgreSQL container setup
POSTGRES_USER=postgres
POSTGRES_PASSWORD=123456
POSTGRES_DB=db

# Redis connection
REDIS_HOST=redis
REDIS_PORT=6379

# Secrets
SECRET_KEY=mysecretkey
REFRESH_SECRET_KEY=myrefreshsecretkey
```

### Cómo Ejecutar el Proyecto

#### **Ejecución con Docker**

### Requisitos

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

### Pasos para Ejecutar

1. **Construir y levantar los servicios**:
   ```bash
   docker-compose up --build -d
   ```

2. **Acceder a la aplicación**:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Redoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

3. **Parar los servicios**:
   ```bash
   docker-compose down
   ```

### Cómo Ejecutar el Seeder

El seeder se ejecuta automáticamente al levantar los servicios, pero si deseas borrar los datos y volver a poblar la base de datos con datos iniciales, puedes ejecutar el script `seeder.py` de la siguiente manera:

1. **Ejecuta el seeder dentro del contenedor de la aplicación**:
   ```bash
   docker-compose exec app python seeder.py
   ```

Esto poblará la base de datos con los datos iniciales definidos en el script `seeder.py`.