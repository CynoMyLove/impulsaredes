import os
from flask import Flask, render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded


app = Flask(__name__)

# Clave secreta para sesiones y CSRF.
# En producción se recomienda configurarla como variable de entorno.
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError("Falta configurar SECRET_KEY como variable de entorno.")

# Configuración básica de seguridad para cookies.
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = True

# En producción con HTTPS puedes activar esto:
# app.config["SESSION_COOKIE_SECURE"] = True

# Protección CSRF
csrf = CSRFProtect(app)

# Límite de peticiones para evitar abuso del botón de simulación.
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Listas permitidas para validar datos en backend.
PLATAFORMAS = ["Instagram", "TikTok", "Facebook", "YouTube"]

TIPOS_CONTENIDO = [
    "Video corto",
    "Imagen o fotografía",
    "Historia",
    "Carrusel",
    "Publicación informativa"
]

FRECUENCIAS = [
    "Todos los días",
    "3 a 4 veces por semana",
    "1 o 2 veces por semana",
    "Casi nunca"
]

DURACIONES = ["Corta", "Media", "Larga"]

TENDENCIAS = ["Sí", "No"]


def validar_datos(datos):
    """
    Valida que los datos enviados desde el formulario pertenezcan
    a las listas permitidas. Esto evita manipulación del formulario.
    """
    errores = []

    if datos.get("plataforma") not in PLATAFORMAS:
        errores.append("La plataforma seleccionada no es válida.")

    if datos.get("tipo_contenido") not in TIPOS_CONTENIDO:
        errores.append("El tipo de contenido seleccionado no es válido.")

    if datos.get("frecuencia") not in FRECUENCIAS:
        errores.append("La frecuencia seleccionada no es válida.")

    if datos.get("duracion") not in DURACIONES:
        errores.append("La duración seleccionada no es válida.")

    if datos.get("tendencias") not in TENDENCIAS:
        errores.append("La opción de tendencias no es válida.")

    return errores


def calcular_simulacion(datos):
    """
    Calcula una simulación sencilla con base en las variables seleccionadas.
    """
    plataforma = datos["plataforma"]
    tipo_contenido = datos["tipo_contenido"]
    frecuencia = datos["frecuencia"]
    duracion = datos["duracion"]
    tendencias = datos["tendencias"]

    puntaje = 1000

    # Evaluación por plataforma
    if plataforma == "TikTok":
        puntaje += 950
    elif plataforma == "Instagram":
        puntaje += 850
    elif plataforma == "YouTube":
        puntaje += 650
    elif plataforma == "Facebook":
        puntaje += 450

    # Evaluación por tipo de contenido
    if tipo_contenido == "Video corto":
        puntaje += 1100
    elif tipo_contenido == "Carrusel":
        puntaje += 750
    elif tipo_contenido == "Imagen o fotografía":
        puntaje += 550
    elif tipo_contenido == "Historia":
        puntaje += 450
    elif tipo_contenido == "Publicación informativa":
        puntaje += 400

    # Evaluación por frecuencia
    if frecuencia == "Todos los días":
        puntaje += 850
    elif frecuencia == "3 a 4 veces por semana":
        puntaje += 650
    elif frecuencia == "1 o 2 veces por semana":
        puntaje += 350
    elif frecuencia == "Casi nunca":
        puntaje -= 250

    # Evaluación por duración
    if duracion == "Corta":
        puntaje += 500
    elif duracion == "Media":
        puntaje += 300
    elif duracion == "Larga":
        puntaje += 100

    # Evaluación por uso de tendencias
    if tendencias == "Sí":
        puntaje += 750
    else:
        puntaje -= 150

    alcance = puntaje * 3
    visualizaciones = puntaje * 2
    likes = int(puntaje * 0.35)
    comentarios = int(puntaje * 0.08)
    compartidos = int(puntaje * 0.05)

    if puntaje >= 4300:
        nivel = "Alto"
        porcentaje = 88
        clase_nivel = "alto"
        recomendacion = (
            "La estrategia tiene alto potencial. Se recomienda mantener el formato elegido, "
            "usar tendencias y publicar con constancia."
        )
    elif puntaje >= 2700:
        nivel = "Medio"
        porcentaje = 62
        clase_nivel = "medio"
        recomendacion = (
            "La estrategia puede funcionar, pero se recomienda reforzar el tipo de contenido, "
            "aumentar la frecuencia o aprovechar tendencias."
        )
    else:
        nivel = "Bajo"
        porcentaje = 38
        clase_nivel = "bajo"
        recomendacion = (
            "La estrategia necesita mejorar. Se recomienda usar videos cortos, publicar con mayor "
            "frecuencia y aprovechar tendencias actuales."
        )

    resumen = f"{plataforma} · {tipo_contenido} · {frecuencia} · Duración {duracion} · Tendencias: {tendencias}"

    resultado = {
        "plataforma": plataforma,
        "tipo_contenido": tipo_contenido,
        "frecuencia": frecuencia,
        "duracion": duracion,
        "tendencias": tendencias,
        "alcance": alcance,
        "visualizaciones": visualizaciones,
        "likes": likes,
        "comentarios": comentarios,
        "compartidos": compartidos,
        "nivel": nivel,
        "porcentaje": porcentaje,
        "clase_nivel": clase_nivel,
        "recomendacion": recomendacion,
        "resumen": resumen
    }

    chart_data = {
        "metricas": {
            "labels": ["Alcance", "Visualizaciones", "Likes", "Comentarios", "Compartidos"],
            "values": [alcance, visualizaciones, likes, comentarios, compartidos]
        },
        "interaccion": {
            "labels": ["Likes", "Comentarios", "Compartidos"],
            "values": [likes, comentarios, compartidos]
        },
        "engagement": {
            "labels": ["Engagement estimado", "Restante"],
            "values": [porcentaje, 100 - porcentaje]
        }
    }

    return resultado, chart_data


@app.after_request
def agregar_headers_seguridad(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' https://cdn.jsdelivr.net https://cdn.matomo.cloud; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data:; "
        "connect-src 'self' https://impulsaredes.matomo.cloud; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self';"
    )

    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )

    return response


@app.route("/", methods=["GET", "POST"])
@limiter.limit("15 per minute")
def index():
    resultado = None
    chart_data = None
    errores = []
    mensaje = None
    form_data = {}

    if request.method == "POST":
        form_data = {
            "plataforma": request.form.get("plataforma", ""),
            "tipo_contenido": request.form.get("tipo_contenido", ""),
            "frecuencia": request.form.get("frecuencia", ""),
            "duracion": request.form.get("duracion", ""),
            "tendencias": request.form.get("tendencias", "")
        }

        errores = validar_datos(form_data)

        if not errores:
            resultado, chart_data = calcular_simulacion(form_data)
            mensaje = "Análisis generado correctamente. Revisa tus resultados abajo."

    return render_template(
        "index.html",
        plataformas=PLATAFORMAS,
        tipos_contenido=TIPOS_CONTENIDO,
        frecuencias=FRECUENCIAS,
        duraciones=DURACIONES,
        tendencias_opciones=TENDENCIAS,
        resultado=resultado,
        chart_data=chart_data,
        errores=errores,
        mensaje=mensaje,
        form_data=form_data
    )


@app.errorhandler(CSRFError)
def manejar_error_csrf(error):
    return render_template(
        "index.html",
        plataformas=PLATAFORMAS,
        tipos_contenido=TIPOS_CONTENIDO,
        frecuencias=FRECUENCIAS,
        duraciones=DURACIONES,
        tendencias_opciones=TENDENCIAS,
        resultado=None,
        chart_data=None,
        errores=["La sesión del formulario expiró o el envío no es válido. Vuelve a intentarlo."],
        mensaje=None,
        form_data={}
    ), 400


@app.errorhandler(RateLimitExceeded)
def manejar_limite_peticiones(error):
    return render_template(
        "index.html",
        plataformas=PLATAFORMAS,
        tipos_contenido=TIPOS_CONTENIDO,
        frecuencias=FRECUENCIAS,
        duraciones=DURACIONES,
        tendencias_opciones=TENDENCIAS,
        resultado=None,
        chart_data=None,
        errores=["Se realizaron demasiadas simulaciones en poco tiempo. Espera unos minutos e inténtalo de nuevo."],
        mensaje=None,
        form_data={}
    ), 429


if __name__ == "__main__":
    # debug=False para evitar exponer información sensible.
    app.run(debug=False)