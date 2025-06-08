#!/bin/sh

# Esperar a que la base de datos esté disponible
echo "Esperando a que la base de datos en $DB_HOST:5432 esté lista..."
until nc -z -v -w30 $DB_HOST 5432
do
  echo "Esperando base de datos..."
  sleep 1
done

echo "Base de datos lista, ejecutando seeder.py..."
python seeder.py

echo "Seeder terminado, iniciando uvicorn..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload