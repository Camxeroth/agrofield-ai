# AgroField AI — Interfaz para Personal de Campo (Streamlit)

Esta interfaz está diseñada para que técnicos y agrónomos puedan ejecutar los agentes de inteligencia de `AgroField AI` sin necesidad de ver código fuente, interactuar con la terminal o poseer conocimientos de programación.

## ¿Qué hace esta herramienta?
Procesa datos de una parcela específica utilizando Satélites (Sentinel-2), Clima (NASA) y Suelos (SoilGrids) y devuelve un Reporte Agronómico traducido a lenguaje humano, señalando riesgos temporales y acciones sugeridas de monitoreo. Toda la complejidad de Machine Learning y Extracción queda oculta detrás de la plataforma.

---

## 1. Instrucciones de uso para el Técnico (Usuario Final)

1. Abre el enlace web de la herramienta proporcionado por tu departamento.
2. En la pantalla principal verás un formulario titulado **Parámetros de la Evaluación**.
3. Ingresa el nombre de la parcela (solo referencial) y las **coordenadas geográficas** correspondientes (Latitud, Longitud).
4. Elige el **Tipo de Cultivo** a evaluar.
5. Haz clic en **Analizar Parcela** y espera unos segundos. La barra de carga te indicará que el sistema está contactando bases de datos externas.
6. A continuación, el reporte aparecerá en pantalla. Puedes navegar por las pestañas de "Clima", "Suelo", y "Vegetación".
7. Al final del reporte, tienes la opción de generar un documento en PDF mediante el botón **Descargar Reporte PDF**.

---

## 2. Ejecutar la plataforma localmente (Para Administradores)

La plataforma corre en Python mediante **Streamlit**. 

En Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Tu navegador web predeterminado se abrirá automáticamente de forma local.

---

## 3. Despliegue Público Gratuito on Streamlit Community Cloud

Para que cualquier operario use la app desde su celular en el campo:

1. Crea o sube este repositorio a [GitHub](https://github.com/).
2. Accede a [Streamlit Community Cloud (share.streamlit.io)](https://share.streamlit.io/) e inicia sesión con tu GitHub.
3. Haz clic en "New app".
4. Selecciona tu repositorio, rama (ej. `main`), y como "Main file path" indica `app.py`.
5. Haz clic en "Deploy".
6. Streamlit se encargará de instalar todo vía `requirements.txt` y en un par de minutos tendrás un enlace web público que puedes compartir con el equipo técnico.
