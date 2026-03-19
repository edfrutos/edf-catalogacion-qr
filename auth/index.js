const express = require('express');
const { betterAuth } = require('better-auth');
const { mongodbAdapter } = require('better-auth/adapters/mongodb');
const { MongoClient } = require('mongodb');
const { toNodeHandler } = require("better-auth/node");
const cors = require('cors');
const path = require('path');

// Carga del .env: forzar desde archivo para que BETTER_AUTH_SECRET coincida con Flask
const envPath = path.resolve(process.cwd(), '.env');
const envPathAlt = path.resolve(__dirname, '../.env');
require('dotenv').config({ path: envPath, override: true }) ||
  require('dotenv').config({ path: envPathAlt, override: true });
if (!process.env.BETTER_AUTH_SECRET) {
  console.warn('[auth] BETTER_AUTH_SECRET no definido. OAuth puede fallar.');
}

const app = express();
app.use(cors({
    origin: ["http://localhost:5020", "http://localhost:5000", "http://127.0.0.1:5020", "http://127.0.0.1:5000"],
    credentials: true,
}));
app.use(express.json());

const client = new MongoClient(process.env.MONGO_URI);
const db = client.db();

const { jwt } = require("better-auth/plugins");

const auth = betterAuth({
    database: mongodbAdapter(db),
    secret: process.env.BETTER_AUTH_SECRET || process.env.SECRET_KEY,
    baseURL: process.env.BETTER_AUTH_URL || "http://localhost:3000",
    trustedOrigins: [
        "http://localhost:3000",
        "http://localhost:5020",
        "http://localhost:5000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5020",
        "http://127.0.0.1:5000",
    ],
    socialProviders: {
        google: {
            clientId: process.env.GOOGLE_CLIENT_ID,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET,
        },
        github: {
            clientId: process.env.GITHUB_CLIENT_ID,
            clientSecret: process.env.GITHUB_CLIENT_SECRET,
        },
    },
    plugins: [jwt()],
});

/**
 * Página de redirección para pasar el token JWT al cliente Flask (cross-origin).
 * Better-Auth redirige aquí tras OAuth; esta página obtiene el token y redirige a Flask.
 */
app.get("/redirect-to-client", (req, res) => {
  const clientCallback = req.query.clientCallback;
  if (!clientCallback) {
    return res.status(400).send("Missing clientCallback");
  }
  console.log("[redirect-to-client] OAuth completado, sirviendo página de paso de token");
  const escaped = clientCallback.replace(/\\/g, "\\\\").replace(/'/g, "\\'");
  const html = `<!DOCTYPE html>
<html><head><meta charset="utf-8"></head><body>
<div id="msg">Obteniendo token...</div>
<script>
(async () => {
  const cb = '${escaped}';
  const msg = document.getElementById('msg');
  try {
    const r = await fetch('/api/auth/token', { credentials: 'include' });
    const d = await r.json().catch(() => ({}));
    const token = d?.token || d?.data?.token || d?.jwt;
    if (token) {
      msg.textContent = 'Token OK. Redirigiendo...';
    } else {
      msg.textContent = 'Sin token (status ' + r.status + '). Redirigiendo...';
    }
    const url = new URL(cb);
    if (token) url.searchParams.set('token', token);
    else url.searchParams.set('error', d?.error || 'no_token');
    setTimeout(() => { window.location.href = url.toString(); }, 1500);
  } catch (e) {
    msg.textContent = 'Error: ' + e.message;
    setTimeout(() => {
      window.location.href = cb + (cb.includes('?') ? '&' : '?') + 'error=auth_failed';
    }, 1500);
  }
})();
</script>
</body></html>`;
  res.type("html").send(html);
});

/**
 * INTEGRACIÓN OFICIAL:
 * Usamos app.use sin asteriscos para evitar el error de Express 5.
 * Better-Auth manejará todo lo que empiece por /api/auth.
 */
app.use("/api/auth", toNodeHandler(auth));

app.listen(3000, () => {
    console.log(`✅ Auth Server ready on port 3000`);
});
