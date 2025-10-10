# Proyecto: Asistencias para Diplomaturas (Django)

## Descripción
Aplicación Django para registrar clases y permitir que estudiantes marquen "Presente" dentro de una ventana de tiempo acotada. 
- **Usuario no logueado**: puede marcar presente por DNI cuando una clase está habilitada y consultar su historial de asistencias por DNI.
- **Usuario logueado (docente)**: puede crear Diplomaturas, Materias y Clases; ver listados combinados de asistencias por materia; exportar PDF.

Incluye estilos integrados (CSS simple) y exportación a PDF con ReportLab.

## Relaciones de objetos (mínimo)
- **Diplomatura** 1 — N **Materia**  
  Una diplomatura agrupa varias materias.
- **Materia** 1 — N **Clase**  
  Cada clase pertenece a una materia.
- **Alumno** N — N **Clase** a través de **Asistencia**  
  La asistencia vincula un alumno con una clase e indica si estuvo presente, con marca de tiempo.

Campos relevantes:
- **Alumno**: apellido1, apellido2, nombre1, nombre2, DNI (único), correo.
- **Clase**: fecha, `inicio_habilitacion` y `fin_habilitacion` (ventana en la que se permite marcar presente), tema opcional.

## Rutas principales
- `/publico/` — Clases habilitadas "ahora" para marcar presente.
- `/publico/marcar/<clase_id>/` — Formulario (DNI) para marcar presente (sólo dentro de la ventana habilitada).
- `/publico/consulta/?dni=...` — Consulta de asistencias por DNI.
- `/gestion/` — Panel básico para docentes (requiere login).
- `/gestion/*` — Formularios para crear diplomaturas, materias y clases.
- `/gestion/materia/<id>/clases/` — Listado de clases y asistencias de una materia.
- `/gestion/materia/<id>/asistencias/pdf` — Exportación a PDF.

## Requisitos e instalación rápida (Linux/Mac/WSL)
1. Crear entorno virtual e instalar dependencias:
   ```bash
   cd DiplomaturasAsistencias
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Migraciones y superusuario:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser ->admin admin@admin.com admin

   python manage.py makemigrations asistencias
   python manage.py migrate

   ```
3. Ejecutar dev server:
   ```bash
   python manage.py runserver
   ```
4. Acceder a:
   - Sitio: http://127.0.0.1:8000
   - Admin: http://127.0.0.1:8000/admin

## Windows (PowerShell)
```powershell
cd DiplomaturasAsistencias
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Carga de alumnos
- Usar el panel **/admin** (modelo **Alumno**) para cargar: apellidos, nombres, DNI (único) y correo.
- Alternativamente, se pueden crear fixtures o importadores más adelante.

## Notas de uso
- Para que estudiantes marquen presente, crear una **Clase** con `inicio_habilitacion` y `fin_habilitacion` cubriendo el período deseado.
- Sólo se permite **una asistencia por alumno y clase** (restricción `unique_together`). Si el alumno intenta marcar dos veces, el sistema avisa.
- El PDF usa ReportLab (no requiere navegador headless).

## Estructura
```
DiplomaturasAsistencias/
├── asistencias/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── diplomaturas/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── static/core/styles.css
└── templates/
    ├── base.html
    ├── registration/login.html
    └── asistencias/*.html
```

## Próximos pasos (ideas)
- Permisos por rol (Grupo "Docentes") en vez de cualquier usuario autenticado.
- Importación CSV de alumnos desde admin.
- Códigos QR por clase para facilitar marcado con celular.
- Vistas de estadísticas (porcentaje de asistencia por alumno/materia).
- Exportación a CSV además de PDF.
