# Proceso para Django:

## Crear entorno virtual con virtualenv:
```
sudo apt-get install virtualenv
virtualenv env # estando en la ruta donde se desea crear el entorno virtual en comunidad/
source env/bin/activate # en comunidad/
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
cd comunidad/ # en comunidad/
python manage.py makemigrations
python manage.py migrate
```

## Ejecutar servidor:
```
python manage.py runserver
```

# Proceso para React con Vite:

### NOTA IMPORTANTE: TODO A PARTIR DE AHORA SE REALIZA EN OTRA TERMINAL 
###                 INDEPENDIENTE DE LA ANTERIOR Y CON EL SERVIDOR DE DJANGO LEVANTADO.

## Instalar nvm y Node.js + npm:
```
# instalar nvm (Node Version Manager) 
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash (se requiere cerrar sesión al terminar)

# verificar la version instalada de nvm
nvm -v # debería imprimir `v0.40.0`

# descargar e instalar Node.js (se requiere cerrar todas las terminales al terminar)
nvm install 22

# verificar la version instalada de Node.js
node -v # debería imprimir `v22.9.0`

# verificar la version instalada de npm
npm -v # debería imprimir `10.8.3`
```

## Preparar parte de React:
```
cd frontend/ # en comunidad/

npm install # instalar dependencias
```

## Arrancar servidor de React + Vite:
```
npm run dev
```