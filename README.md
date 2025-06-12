## Configuración del Proyecto

### Variables de Entorno

El proyecto utiliza un único archivo `.env` para configuraciones tanto locales como en Docker. En el archivo .env.example se encuentra una configuración de ejemplo.

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

## Funcionalidades clave

### Modelo de base de datos

La información de la base de datos está organizada en tres tablas
- **Users** (donde se almacenan los usuarios con sus datos correspondientes)
- **Orders** (donde se almacenan los pedidos, con un owner_id que hace referencia al usuario al que está asignado)
- **Items_ordered** (donde se almacenan los datos de los productos incluidos en los pedidos con referencia al id de pedido)

La información de los productos que se pueden agregar a los pedidos de la API se consumen desde la sección de productos de la API externa [DummyJSON](https://dummyjson.com)

El script seeder.py puebla la base de datos al iniciar los microservicios. La base de datos persiste aunque se paren los microservicios y se eliminen los contenedores. En caso de que se desee eliminar los datos guardados e iniciar con datos básicos para hacer pruebas, se puede reiniciar la base de datos al poner en marcha el proyecto con la variable CONFIRM_DROP de la siguiente manera:
```bash
CONFIRM_DROP: yes
```
o mantener los datos existentes con:
```bash
CONFIRM_DROP: no
```

### Sistema de roles y autenticación

En cuanto al sistema de roles y autenticación, hay dos tipos de usuarios, administradores y clientes.
Los clientes pueden:
- Modificar sus datos de usuario
- Consultar sus datos de usuario
- Eliminar su usuario
- Crear pedidos
- Consultar sus pedidos
- Eliminar sus pedidos
- Añadir productos a sus pedidos
- Consultar los productos en sus pedidos
- Modificar la cantidad de unidades de un producto de su pedido
- Eliminar productos de sus pedidos

Los administradores pueden realizar las acciones anteriores para cualquier usuario y además:
- Crear usuarios
- Cambiar el dueño de un pedido

Además, el sistema de autenticación permite a los usuarios:
- Registrarse
- Iniciar sesión
- Cerrar sesión
- Refrescar el token de sesión
- Reiniciar la constraseña
- Cambiar la contraseña

Los tokens de inicio de sesión expirados se almacenan con un sistema de Redis. Estos datos también tienen persistencia. Como posible mejora futura se podría cambiar para que se almacenen solo los tokens en activo y se borren una vez expiren para evitar que el tamaño del volumen vaya aumentando indefinidamente.

## Endpoints principales

### Gestión de usuarios

#### POST - Crear usuario

Solo disponible para admin. Crea un usuario con los siguientes datos:
- username
- email
- role
- password

#### GET - Consultar usuario

Por defecto devuelve los datos de todos los usuarios (admin) con un límite de 100 entradas o el usuario registrado (cliente). Se puede concretar la búsqueda con parametros id, username o email. Devuelve:
- username
- email
- role 

#### PUT - Modificar usuario

Edita los datos para el usuario seleccionado (admin) o para el usuario registrado (cliente). Los datos que se pueden modificar son:
- username
- email
- role   (Para clientes esto no debería ser posible, es un fallo de seguridad, pero me he dado cuenta a última hora)
- password

#### DELETE - Eliminar usuario

Elimina el usuario seleccionado (admin) o el usuario registrado (cliente). Esto elimina los pedidos asociados a este usuario y los productos asociados a los pedidos del usuario.

### Gestión de pedidos

#### POST - Crear pedido

Crea un pedido y lo asigna al usuario seleccionado (admin) o al usuario registrado (cliente)

#### GET - Consultar pedidos

Por defecto devuelve todos los pedidos (admin) con un límite de 100 entradas o los pedidos asignados al usuario registrado (cliente). Se puede concretar la búsqueda con parametros id de pedido, id de usuario, username o email. Devuelve:
- owner_id     (id del usuario al que está asociado el pedido)
- id           (id del pedido)
- created_at   (fecha y hora de creación del pedido)

#### PUT - Modificar pedido

Solo disponible para admin. Edita el valor del usuario al que está asignado un pedido. 

#### DELETE - Eliminar pedido

Elimina el pedido seleccionado y los productos asociados al pedido. El admin puede eliminar cualquier pedido pero el cliente sólo puede eliminar sus propios pedidos.

### Gestión de artículos en los pedidos

#### POST - Añadir producto a un pedido

Añade un producto a un pedido en la cantidad introducida. El usuario admin puede introducirlo en cualquier pedido y el usuario cliente solo a sus propios pedidos. Los datos del producto se extraen de la API externa, entre ellos: 
- title
- description
- category
- price
- rating
- brand

Si se introduce un producto que ya estaba en el pedido, se suman las cantidades.

#### GET - Consultar los productos de un pedido

Devuelve los datos de los datos de los productos que contiene el pedido. El usuario admin puede consultar cualquier pedido y el usuario cliente solo sus propios pedidos.

#### PUT - Modificar las unidades de un producto

Edita el valor quantity de un producto asociado a un pedido. El usuario admin puede modificar productos de cualquier pedido y el usuario cliente solo de sus propios pedidos.
Si la nueva cantidad de unidades del producto es 0, se elimina el producto del pedido.

#### DELETE - Eliminar un producto de un pedido

Elimina el producto seleccionado de un pedido. El usuario admin puede eliminar productos de cualquier pedido y el usuario cliente solo de sus propios pedidos