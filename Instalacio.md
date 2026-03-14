# Claro, aquí tienes todo el contenido en formato de archivo README.md o Instrucciones.md:

# EDF Catalogación QR

Aplicación para la catalogación de contenedores mediante códigos QR.

## Estructura del Proyecto

```bat {"id":"01J23VGE2TR9GJ04C52QYDMAZM"}
edf-catalogacion-qr/
│
├── config/
│   └── db.js
├── controllers/
│   ├── authController.js
│   ├── containerController.js
├── middlewares/
│   └── authMiddleware.js
├── models/
│   ├── User.js
│   ├── Container.js
├── routes/
│   ├── authRoutes.js
│   ├── containerRoutes.js
├── views/
│   ├── index.ejs
│   └── container.ejs
├── .env
├── server.js
├── package.json
└── README.md

Aplicación para la catalogación de contenedores mediante códigos QR.

## Estructura del Proyecto

```bat {"id":"01J23VGE2TR9GJ04C52QYDMAZM"}
edf-catalogacion-qr/
│
├── config/
│   └── db.js
├── controllers/
│   ├── authController.js
│   ├── containerController.js
├── middlewares/
│   └── authMiddleware.js
├── models/
│   ├── User.js
│   ├── Container.js
├── routes/
│   ├── authRoutes.js
│   ├── containerRoutes.js
├── views/
│   ├── index.ejs
│   └── container.ejs
├── .env
├── server.js
├── package.json
└── README.md
```

## Instalación y Configuración

### 1. Clonar el Repositorio

```bash {"id":"01J23VFD0G67GJG0DVGR056V7D"}
git clone <URL_DEL_REPOSITORIO>
cd edf-catalogacion-qr

2. Instalar Dependencias

npm install

3. Crear el Archivo .env

Crea un archivo .env en la raíz del proyecto con las siguientes variables:

PORT=3000
MONGO_URI=mongodb+srv://<your_mongodb_username>:<your_mongodb_password>@cluster0.mongodb.net/edf_catalogacion_qr?retryWrites=true&w=majority
JWT_SECRET=your_jwt_secret_key

4. Iniciar el Servidor en Desarrollo

npm run dev

5. Despliegue en Producción

Para desplegar en Heroku, sigue estos pasos:

	1.	Iniciar Sesión en Heroku:

heroku login


	2.	Crear una Aplicación en Heroku:

heroku create edf-catalogacion-qr


	3.	Configurar Variables de Entorno en Heroku:

heroku config:set MONGO_URI=mongodb+srv://<your_mongodb_username>:<your_mongodb_password>@cluster0.mongodb.net/edf_catalogacion_qr?retryWrites=true&w=majority
heroku config:set JWT_SECRET=your_jwt_secret_key


	4.	Desplegar a Heroku:

git push heroku main


	5.	Verificar el Despliegue:

heroku open



Configuración de Archivos

server.js

require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const cors = require('cors');
const connectDB = require('./config/db');
const authRoutes = require('./routes/authRoutes');
const containerRoutes = require('./routes/containerRoutes');

const app = express();
const PORT = process.env.PORT || 3000;

// Conectar a MongoDB
connectDB();

// Middlewares
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// View Engine Setup
app.set('view engine', 'ejs');

// Rutas
app.use('/api/auth', authRoutes);
app.use('/api/containers', containerRoutes);

app.get('/', (req, res) => {
  res.render('index');
});

// Error Handling Middleware
app.use((req, res) => {
  res.status(404).send('Ruta no encontrada');
});

app.listen(PORT, () => {
  console.log(`Servidor corriendo en el puerto ${PORT}`);
});

config/db.js

const mongoose = require('mongoose');

const connectDB = async () => {
  try {
    await mongoose.connect(process.env.MONGO_URI, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      useCreateIndex: true
    });
    console.log('MongoDB conectado');
  } catch (err) {
    console.error(err.message);
    process.exit(1);
  }
};

module.exports = connectDB;

controllers/authController.js

const User = require('../models/User');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

// Registro de usuarios
exports.register = async (req, res) => {
  const { name, email, password } = req.body;

  try {
    let user = await User.findOne({ email });

    if (user) {
      return res.status(400).json({ msg: 'Usuario ya registrado' });
    }

    user = new User({
      name,
      email,
      password
    });

    const salt = await bcrypt.genSalt(10);
    user.password = await bcrypt.hash(password, salt);

    await user.save();

    const payload = {
      user: {
        id: user.id
      }
    };

    jwt.sign(
      payload,
      process.env.JWT_SECRET,
      { expiresIn: '1h' },
      (err, token) => {
        if (err) throw err;
        res.json({ token });
      }
    );
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Error en el servidor');
  }
};

// Inicio de sesión de usuarios
exports.login = async (req, res) => {
  const { email, password } = req.body;

  try {
    let user = await User.findOne({ email });

    if (!user) {
      return res.status(400).json({ msg: 'Credenciales inválidas' });
    }

    const isMatch = await bcrypt.compare(password, user.password);

    if (!isMatch) {
      return res.status(400).json({ msg: 'Credenciales inválidas' });
    }

    const payload = {
      user: {
        id: user.id
      }
    };

    jwt.sign(
      payload,
      process.env.JWT_SECRET,
      { expiresIn: '1h' },
      (err, token) => {
        if (err) throw err;
        res.json({ token });
      }
    );
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Error en el servidor');
  }
};

controllers/containerController.js

const Container = require('../models/Container');

// Crear nuevo contenedor
exports.createContainer = async (req, res) => {
  const { name, description } = req.body;

  try {
    const newContainer = new Container({
      name,
      description,
      user: req.user.id
    });

    const container = await newContainer.save();
    res.json(container);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Error en el servidor');
  }
};

// Obtener todos los contenedores del usuario
exports.getContainers = async (req, res) => {
  try {
    const containers = await Container.find({ user: req.user.id });
    res.json(containers);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Error en el servidor');
  }
};

middlewares/authMiddleware.js

const jwt = require('jsonwebtoken');

module.exports = function(req, res, next) {
  // Leer el token del header
  const token = req.header('x-auth-token');

  // Revisar si no hay token
  if (!token) {
    return res.status(401).json({ msg: 'No hay token, permiso no válido' });
  }

  // Validar el token
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded.user;
    next();
  } catch (err) {
    res.status(401).json({ msg: 'Token no es válido' });
  }
};

models/User.js

const mongoose = require('mongoose');

const UserSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true
  },
  email: {
    type: String,
    required: true,
    unique: true
  },
  password: {
    type: String,
    required: true
  }
});

module.exports = mongoose.model('User', UserSchema);

models/Container.js

const mongoose = require('mongoose');

const ContainerSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  }
});

module.exports = mongoose.model('Container', ContainerSchema);

routes/authRoutes.js

const express = require('express');
const router = express.Router();
const { register, login } = require('../controllers/authController');

// Rutas de autenticación
router.post('/register', register);
router.post('/login', login);

module.exports = router;

routes/containerRoutes.js

const express = require('express');
const router = express.Router();
const { createContainer, getContainers } = require('../controllers/containerController');
const auth = require('../middlewares/authMiddleware');

// Rutas de contenedores
router.post('/', auth, createContainer);
router.get('/', auth, getContainers);

module.exports = router;

views/index.ejs

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=
```