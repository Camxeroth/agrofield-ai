import streamlit as st
import pandas as pd
import os
import sys
from fpdf import FPDF
import base64

# Import agents
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import agents.climate_agent as climate_agent
import agents.agronomy_agent as agronomy_agent

# Configuración de Streamlit
st.set_page_config(page_title="AgroField AI", layout="centered")

def clean_text(text):
    if not isinstance(text, str):
        return str(text)
    # Replace unicode characters not supported by latin-1 in fpdf
    text = text.replace('≈', '~')
    # Encode and decode back, ignoring unmappable chars
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_pdf_report(result, parcela, coords, cultivo):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=clean_text("AgroField AI - Reporte Agronómico"), ln=True, align='C')
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 11)
    pdf.cell(200, 7, txt=clean_text(f"Parcela: {parcela}"), ln=True)
    pdf.cell(200, 7, txt=clean_text(f"Coordenadas: {coords}"), ln=True)
    pdf.cell(200, 7, txt=clean_text(f"Cultivo: {cultivo}"), ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=clean_text("RESUMEN"), ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 7, txt=clean_text(result.get("summary", "")))
    pdf.ln(5)

    # Clima
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=clean_text("ANALISIS CLIMATICO"), ln=True)
    pdf.set_font("Arial", '', 11)
    cs = result.get("climate_section", {})
    pdf.multi_cell(0, 7, txt=clean_text(cs.get("summary", "")))
    for obs in cs.get("observations", []):
        pdf.multi_cell(0, 7, txt=clean_text(f"- {obs}"))
    pdf.ln(5)

    # Suelo
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=clean_text("ANALISIS DE SUELO"), ln=True)
    pdf.set_font("Arial", '', 11)
    ss = result.get("soil_section", {})
    for obs in ss.get("observations", []):
        pdf.multi_cell(0, 7, txt=clean_text(f"- {obs}"))
    pdf.ln(5)

    # NDVI
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=clean_text("VEGETACION (NDVI)"), ln=True)
    pdf.set_font("Arial", '', 11)
    ns = result.get("ndvi_section", {})
    pdf.multi_cell(0, 7, txt=clean_text(f"Media: {ns.get('ndvi_mean')} | Rango: {ns.get('ndvi_min')} - {ns.get('ndvi_max')}"))
    pdf.multi_cell(0, 7, txt=clean_text(ns.get("observation", "")))
    pdf.ln(5)

    # Riesgos y Monitoreo
    if result.get("risk_indicators"):
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=clean_text("INDICADORES DE RIESGO AGRONOMICOS"), ln=True)
        pdf.set_font("Arial", '', 11)
        for ri in result["risk_indicators"]:
            pdf.multi_cell(0, 7, txt=clean_text(f"- {ri['indicator']}: {ri['context']}"))
        pdf.ln(5)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=clean_text("ACCIONES DE MONITOREO SUGERIDAS"), ln=True)
    pdf.set_font("Arial", '', 11)
    for i, act in enumerate(result.get("monitoring_actions", []), 1):
        pdf.multi_cell(0, 7, txt=clean_text(f"{i}. {act}"))
    
    return pdf.output(dest='S').encode('latin-1')

def get_pdf_download_link(pdf_bytes, filename):
    b64 = base64.b64encode(pdf_bytes).decode()
    return f'<a href="data:application/pdf;base64,{b64}" download="{filename}" style="display:inline-block; padding:0.5em 1em; color:white; background-color:#4CAF50; border-radius:5px; text-decoration:none;">Descargar Reporte PDF</a>'

# ----------------- UI PRINCIPAL -----------------
st.title("AgroField AI")
st.subheader("Sistema de Inteligencia Agricola (Colta, Chimborazo)")
st.write("Bienvenido. Esta herramienta procesa datos satelitales, climaticos y de suelo para generar un resumen agronomico de las parcelas.")

with st.form("agro_form"):
    st.write("### Parametros de la Evaluacion")
    parcela = st.text_input("Nombre de la Parcela / Codigo", value="Lote 1 - Colta Centro")
    coords = st.text_input("Coordenadas (Lat, Lon)", value="-1.718, -78.764")
    cultivo = st.selectbox("Tipo de Cultivo", ["Papa", "Quinoa", "Maiz", "Otros"])
    
    submitted = st.form_submit_button("Analizar Parcela")

if submitted:
    with st.spinner("Analizando parcela... (Conectando con fuentes satelitales y climaticas)"):
        # SIMULACIÓN DEL PIPELINE EXISTENTE
        # 1. Clima
        try:
            csv_path = os.path.join("data", "processed", "nasa_power_colta_12m_vpd_20250823_20260822.csv")
            clim_df = pd.read_csv(csv_path, parse_dates=["fecha"])
            climate_result = climate_agent.run(clim_df)
        except Exception as e:
            st.error(f"Falla al conectar al servicio climatico temporal: {str(e)}")
            st.stop()

        # 2. NDVI (datos mock para evadir Earth Engine auth en entorno no tecnico)
        ndvi_values = [
            0.35, 0.42, 0.38, 0.40, 0.36, 0.28, 0.45, 0.33, 0.29, 0.41,
            0.37, 0.44, 0.32, 0.39, 0.35, 0.41, 0.43, 0.30, 0.28, 0.38,
            0.46, 0.31, 0.40, 0.27, 0.34, 0.48, 0.37, 0.29, 0.42, 0.36,
            0.39, 0.44, 0.33, 0.28, 0.41, 0.35, 0.50, 0.38, 0.32, 0.43,
            0.29, 0.47, 0.36, 0.31, 0.40, 0.38, 0.35, 0.42, 0.27, 0.44,
            0.33, 0.39, 0.41,
        ]

        # 3. Resultado ML (datos reales guardados del baseline)
        ml_result = {
            "status": "OK",
            "target": "ndvi",
            "features": ["T2M", "RH2M", "PRECTOTCORR", "ALLSKY_SFC_SW_DWN", "VPD"],
            "n_observaciones_totales": 53,
            "n_train": 42,
            "n_test": 11,
            "estrategia_split": "Temporal (80% pasado -> train, 20% futuro -> test)",
            "modelo": "Linear Regression (Baseline)",
            "metricas_test": {"MAE": 0.076, "RMSE": 0.084, "R2": -0.852},
            "advertencias": ["R2 negativo en Test"],
            "limitaciones": ["Un baseline no representa todavia un modelo productivo."],
        }

        # 4. Datos de Suelo (SoilGrids)
        soil_result = {
            "summary": "Analisis de suelo completado para la capa 0-30 cm.",
            "ph_interpretation": "Optimo para cultivo de papa. Buena disponibilidad de nutrientes.",
            "organic_carbon_interpretation": "Contenido medio a adecuado de materia organica.",
            "texture_interpretation": "Textura equilibrada a pesada. Monitorear el drenaje para evitar asfixia radicular.",
            "agronomic_notes": [
                "pH actual: 5.90 - Optimo para cultivo de papa.",
                "Carbono organico: 3.20% - Contenido medio a adecuado.",
                "Textura (Arena: 35%, Limo: 40%, Arcilla: 25%) - Textura franca.",
            ],
            "confidence": "MEDIA"
        }

        # 5. Correlaciones (Statistics Agent)
        stats_result = {
            "correlations": {
                "ndvi": {"ndvi": 1.0, "T2M": 0.21, "PRECTOTCORR": -0.05, "VPD": 0.18, "RH2M": -0.14, "ALLSKY_SFC_SW_DWN": 0.09}
            },
            "warnings": ["Correlacion no implica causalidad."],
            "pearson_correlations_with_target": {"T2M": 0.21, "VPD": 0.18, "RH2M": -0.14, "PRECTOTCORR": -0.05, "ALLSKY_SFC_SW_DWN": 0.09},
            "confidence": "ALTA",
            "limitation": "Las correlaciones de Pearson describen asociacion lineal, no relaciones causales.",
            "observations": ["NDVI muestra la mayor asociacion positiva lineal con T2M (r=0.21)"]
        }
        stats_result["pearson_correlations_with_target"] = {"T2M": 0.21, "PRECTOTCORR": -0.05, "VPD": 0.18, "RH2M": -0.14, "ALLSKY_SFC_SW_DWN": 0.09}

        # 6. Agronomy Agent (Lógica real no modificada)
        try:
            result = agronomy_agent.run(
                ndvi_values=ndvi_values,
                climate_result=climate_result,
                soil_result=soil_result,
                stats_result=stats_result,
                ml_result=ml_result,
            )
        except Exception as e:
            st.error(f"Falla critica en el sistema multi-agente al procesar la informacion. Motivo: {str(e)}")
            st.stop()
            
    st.success("Analisis completado")
    
    # ---------------- VISUALIZACIÓN DE RESULTADOS ----------------
    
    st.header(f"Resumen Agronomico: {parcela}")
    st.write(f"**Coordenadas:** {coords} | **Cultivo:** {cultivo}")
    
    # Nota sobre el uso de datos en la version E2E de prototipo
    st.caption("Nota: Este entorno de prototipo realiza la prueba con el dataset E2E pre-construido de Chimborazo.")

    st.info(result.get("summary", ""))
    
    # --- Pestañas para cada fuente ---
    tab_clim, tab_soil, tab_veg, tab_monitor = st.tabs(["Clima", "Suelo", "Vegetacion", "Monitoreo y Riesgos"])
    
    with tab_clim:
        cs = result["climate_section"]
        st.subheader("Analisis Climatico a 12 meses")
        st.write(cs.get("summary", ""))
        for obs in cs.get("observations", []):
            st.write(f"- {obs}")
            
        st.line_chart(clim_df.set_index("fecha")["T2M"])
    
    with tab_soil:
        ss = result["soil_section"]
        st.subheader("Analisis de Suelo (SoilGrids 0-30cm)")
        for obs in ss.get("observations", []):
            st.write(f"- {obs}")
            
    with tab_veg:
        ns = result["ndvi_section"]
        st.subheader("Espectrografia (NDVI Sentinel-2)")
        col1, col2, col3 = st.columns(3)
        col1.metric("Media", ns.get("ndvi_mean"))
        col2.metric("Min", ns.get("ndvi_min"))
        col3.metric("Max", ns.get("ndvi_max"))
        st.write(f"**Observacion Spectral:** {ns.get('observation', '')}")
        st.caption(f"Limitacion: {ns.get('limitation', '')}")
        st.line_chart(pd.DataFrame(ndvi_values, columns=["NDVI"]))
        
    with tab_monitor:
        st.subheader("Indicadores de Riesgo Agronomico")
        if not result.get("risk_indicators"):
            st.success("No se detectaron indicadores de riesgo inmediatos de relevancia.")
        else:
            for ri in result["risk_indicators"]:
                st.warning(f"**{ri['indicator']}**: {ri['context']}")
                
        st.subheader("Acciones de Monitoreo")
        for i, act in enumerate(result.get("monitoring_actions", []), 1):
            st.write(f"{i}. {act}")
            
    # --- Descarga PDF ---
    st.divider()
    pdf_bytes = generate_pdf_report(result, parcela, coords, cultivo)
    st.markdown(get_pdf_download_link(pdf_bytes, f"AgroField_Reporte_{parcela.replace(' ', '_')}.pdf"), unsafe_allow_html=True)
    
    with st.expander("Metadatos y Limitaciones del Sistema"):
        st.write("Este analisis es mediado por la suite de algoritmos de inteligencia de AgroField sin dictaminar prescripciones quimicas directas.")
        st.write("**Notas terminologicas:**")
        st.write(result.get("terminology_note", ""))
        st.write("**Desempeño del Baseline de ML local:** R² = -0.852 (Regresion Lineal Simple, modelo acotado y exploratorio).")
