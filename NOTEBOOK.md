# NOTEBOOK - Seguimiento de Mejoras y Actualizaciones

Este cuaderno sirve para priorizar y monitorizar la implementación de las mejoras propuestas para **EDF Catalogación QR**.

## 🚀 1. Arquitectura y Despliegue
- [x] **Reestructuración del Proyecto:** Movido el código de `edf-catalogacion-qrt/` a la raíz para un despliegue estándar. (Completado 2026-03-14)
- [ ] **Almacenamiento Cloud (S3/Cloudinary):** Migrar `static/profile_pics` y `static/qr_codes` para evitar pérdida de datos en sistemas efímeros.
- [x] **Paginación en Listados:** Implementar `.paginate()` en las vistas de contenedores y usuarios. (Completado 2026-03-14)
- [ ] **Tareas en Segundo Plano (Celery/RQ):** Desvincular el envío de emails del hilo principal.

## 🛡️ 2. Seguridad y Estabilidad
- [x] **Pruebas Automatizadas (pytest):** Crear suite de tests unitarios e integración. (Completado 2026-03-14)
- [x] **Seguridad de Configuración:** Migración de secretos a `.env` y actualización de `.gitignore`. (Completado 2026-03-14)
- [x] **Gestión Segura de Admin:** Script `create_admin.py` ahora es interactivo y seguro. (Completado 2026-03-14)
- [x] **Rate Limiting (Flask-Limiter):** Protección contra fuerza bruta en login y reset de contraseña. (Completado 2026-03-14)
- [ ] **Auditoría de Dependencias:** Actualizar `Pillow` y otras librerías críticas (`pip-audit`).
- [ ] **Logs de Error Estructurados:** Implementar un logger formal para depuración en producción.

## ✨ 3. Nuevas Prestaciones (Features)
- [x] **Repositorio Profesional:** Añadidos `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` y GitHub Actions CI. (Completado 2026-03-14)
- [ ] **Escáner QR Web (html5-qrcode):** Integrar lectura de QRs desde la cámara en la aplicación.
- [x] **Sistema de Etiquetas (Tags):** Categorizar contenedores para búsquedas avanzadas. (Completado 2026-03-14)
- [ ] **Exportación de Inventario:** Generar reportes en CSV o PDF.
- [ ] **Contenedores Compartidos:** Permitir acceso multiusuario a contenedores específicos.

## 🎨 4. UX y Frontend
- [ ] **Notificaciones Toast (JS):** Mejorar la UI de los mensajes flash.
- [ ] **PWA (Progressive Web App):** Hacer la aplicación instalable en dispositivos móviles.
- [ ] **Búsqueda Dinámica (Fetch API):** Filtrado de contenedores en tiempo real sin recarga.

---

## 📝 Historial de Implementación
*   **2026-03-14:** Script de creación de admin convertido a interactivo con validaciones de seguridad.
*   **2026-03-14:** Corrección de fallos en GitHub Actions CI (inyección de config y downgrade de Flask para compatibilidad).
*   **2026-03-14:** Reestructuración de la raíz del proyecto, profesionalización del repositorio (CI, Licencia, Guías) y aseguramiento de variables de entorno (.env).
*   **2026-03-14:** Implementación de suite de pruebas con pytest y mongomock.
*   **2026-03-14:** Creación del cuaderno de seguimiento y análisis inicial del proyecto.
