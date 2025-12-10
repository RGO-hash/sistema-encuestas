# 🚀 Ejecución desde GitHub - Opciones Disponibles

## ⚡ 3 Formas Rápidas de Ejecutar el Proyecto desde GitHub

---

## 1️⃣ **Opción Más Rápida: GitHub Codespaces** (0-2 minutos)

GitHub Codespaces permite ejecutar el proyecto directamente desde GitHub sin descargar nada.

### Pasos:
1. Ve a: https://github.com/RGO-hash/sistema-encuestas
2. Presiona el botón **Code** (verde)
3. Selecciona **Codespaces** → **Create codespace on main**
4. Espera a que cargue el editor (1-2 minutos)
5. En la terminal, ejecuta:
   ```bash
   python setup.py
   ```
6. Luego:
   ```bash
   python run.py
   ```
7. Cuando veas "Running on http://0.0.0.0:5000", presiona Ctrl+Click en el enlace

**Ventajas:** ✅ Sin instalación | ✅ Ejecuta en la nube | ✅ Completamente gratis (50 horas/mes)

---

## 2️⃣ **Opción Fácil: Clonar y Ejecutar Localmente** (5-10 minutos)

### Pasos:
1. Abre terminal/PowerShell
2. Ejecuta:
   ```bash
   git clone https://github.com/RGO-hash/sistema-encuestas.git
   cd sistema-encuestas
   python setup.py
   ```
3. Una vez termine, ejecuta:
   ```bash
   venv\Scripts\activate  # Windows
   python run.py
   ```
4. Abre: http://127.0.0.1:5000

**Ventajas:** ✅ Control total | ✅ Más rápido después de primera ejecución | ✅ Acceso completo al código

---

## 3️⃣ **Opción Mejor: Docker** (10-15 minutos)

Sin instalar Python, solo necesitas Docker.

### Pasos:
1. Clona el repositorio:
   ```bash
   git clone https://github.com/RGO-hash/sistema-encuestas.git
   cd sistema-encuestas
   ```

2. Ejecuta con Docker:
   ```bash
   docker-compose up --build
   ```

3. Espera a ver: `Running on http://0.0.0.0:5000`

4. Abre: http://localhost:5000

5. Para detener:
   ```bash
   docker-compose down
   ```

**Ventajas:** ✅ Sin dependencias Python | ✅ Perfecto para producción | ✅ Mismo resultado en cualquier máquina

---

## 🔑 Credenciales por Defecto

Una vez que la aplicación esté corriendo:

### Panel de Administración
- **Email:** admin@test.com
- **Contraseña:** test123

### Registro de Participante
- Crear nuevo en pestaña "Registro"
- Los participantes pueden votar después de registrarse

---

## 🎯 ¿Cuál Opción Elegir?

| Situación | Opción Recomendada |
|-----------|-------------------|
| Quiero probar AHORA sin instalar nada | 1️⃣ Codespaces |
| Voy a trabajar en desarrollo local | 2️⃣ Local |
| Voy a desplegar a producción | 3️⃣ Docker |
| Trabajo en empresa con limitaciones | 1️⃣ Codespaces |

---

## 📚 Documentación Completa

Para más detalles sobre cada opción:
- **INSTALLATION_GUIDE.md** - 6 opciones de instalación/deployment
- **QUICKSTART.md** - Inicio rápido de 5 minutos
- **README.md** - Documentación completa
- **GITHUB_SETUP.md** - Uso de la aplicación

---

## 🔗 Enlaces Útiles

- 📝 [Documentación Principal](README.md)
- ⚡ [Guía de Instalación](INSTALLATION_GUIDE.md)
- 🚀 [Inicio Rápido](QUICKSTART.md)
- 🤝 [Cómo Contribuir](CONTRIBUTING.md)
- 📄 [Licencia MIT](LICENSE)

---

## ❓ Preguntas Frecuentes

**P: ¿Puedo usar esto en producción?**
R: Sí, con Docker o servicios cloud como AWS/Azure/Heroku (ver INSTALLATION_GUIDE.md)

**P: ¿Necesito Python instalado?**
R: No, si usas Docker o Codespaces

**P: ¿Es seguro para votaciones reales?**
R: Tiene autenticación JWT y prevención de votos duplicados, pero revisa el código para tu caso

**P: ¿Puedo modificar el código?**
R: Sí, está bajo licencia MIT. Ver CONTRIBUTING.md

---

## 🎉 ¡Listo!

Elige tu opción favorita y empieza a usar el Sistema de Votación en minutos.

**Opción Recomendada para Empezar:** GitHub Codespaces (más rápido)

---

*Última actualización: Diciembre 2025*
