# comunidad

## Crear entorno virtual con virtualenv:
```
sudo apt-get install virtualenv
virtualenv env # estando en la ruta donde se desea crear el entorno virtual
source env/bin/activate
```

## Instalar dependencias:
```
pip install -r requirements.txt
```

## Instalar servidor de redis:
```
sudo apt-get install redis-server
redis-cli ping # si responde PONG es que está corriendo
sudo service redis-server start
```

## Crear tablas en la base de datos de postgresql:
```
cd comunidad/
python manage.py makemigrations
python manage.py migrate
```

## Ejecutar servidor:
```
python manage.py runserver
```
## Copar el archivo defaults.py en la siguiente direccion:
/venv/lib/python3.11/site-packages/django/views/defaults.py
