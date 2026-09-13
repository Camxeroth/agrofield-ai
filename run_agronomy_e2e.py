"""
run_agronomy_e2e.py
===================
Prueba end-to-end del Agronomy Agent usando:
  - Datos climáticos reales del CSV de NASA POWER
  - Resultados reales documentados del ML Agent (Día 23)
  - Datos de suelo reales de SoilGrids (Día 9-10)

NO usa Earth Engine ni ninguna dependencia de red.
"""

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import pandas as pd
import agents.climate_agent as climate_agent
import agents.agronomy_agent as agronomy_agent


def main():
    # ------------------------------------------------------------------
    # 1. Datos climáticos REALES (NASA POWER CSV procesado)
    # ------------------------------------------------------------------
    csv_path = os.path.join("data", "processed",
                            "nasa_power_colta_12m_vpd_20250823_20260822.csv")
    clim_df = pd.read_csv(csv_path, parse_dates=["fecha"])
    climate_result = climate_agent.run(clim_df)

    # ------------------------------------------------------------------
    # 2. NDVI — valores representativos documentados en el proyecto
    # (dataset integrado: 53 obs satelitales, rango aprox. 0.25–0.55)
    # Fuente: documentación Día 23 (docs/dia23_ml_agent.md)
    # ------------------------------------------------------------------
    ndvi_values = [
        0.35, 0.42, 0.38, 0.40, 0.36, 0.28, 0.45, 0.33, 0.29, 0.41,
        0.37, 0.44, 0.32, 0.39, 0.35, 0.41, 0.43, 0.30, 0.28, 0.38,
        0.46, 0.31, 0.40, 0.27, 0.34, 0.48, 0.37, 0.29, 0.42, 0.36,
        0.39, 0.44, 0.33, 0.28, 0.41, 0.35, 0.50, 0.38, 0.32, 0.43,
        0.29, 0.47, 0.36, 0.31, 0.40, 0.38, 0.35, 0.42, 0.27, 0.44,
        0.33, 0.39, 0.41,
    ]  # 53 valores — misma cantidad que observaciones reales

    # ------------------------------------------------------------------
    # 3. Resultado ML Día 23 (VALORES REALES documentados)
    # ------------------------------------------------------------------
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
        "advertencias": [
            "R2 negativo en Test: El baseline rinde peor que predecir simplemente la media.",
        ],
        "limitaciones": [
            "Un baseline no representa todavía un modelo productivo.",
            "Ausencia de Lags: El clima actual impacta poco el NDVI del mismo instante.",
            "Región interandina: Observaciones satelitales bajas limitan el muestreo.",
        ],
    }

    # ------------------------------------------------------------------
    # 4. Datos de suelo (SoilGrids — Colta, Chimborazo, 0–30 cm)
    # ------------------------------------------------------------------
    soil_result = {
        "summary": "Análisis de suelo completado para la capa 0–30 cm.",
        "ph_interpretation": (
            "Óptimo para cultivo de papa. Buena disponibilidad de nutrientes."
        ),
        "organic_carbon_interpretation": (
            "Contenido medio a adecuado de materia orgánica."
        ),
        "texture_interpretation": (
            "Textura equilibrada a pesada. Monitorear el drenaje para evitar "
            "asfixia radicular en lluvias intensas."
        ),
        "agronomic_notes": [
            "pH actual: 5.90 - Óptimo para cultivo de papa.",
            "Carbono orgánico: 3.20% - Contenido medio a adecuado.",
            "Textura (Arena: 35%, Limo: 40%, Arcilla: 25%) - Textura franca.",
        ],
    }

    # ------------------------------------------------------------------
    # 5. Correlaciones estadísticas (Pearson — Statistics Agent Día 20)
    # ------------------------------------------------------------------
    stats_result = {
        "correlations": {
            "ndvi": {
                "ndvi": 1.0,
                "T2M": 0.21,
                "PRECTOTCORR": -0.05,
                "VPD": 0.18,
                "RH2M": -0.14,
                "ALLSKY_SFC_SW_DWN": 0.09,
            }
        },
        "warnings": [
            "LIMITACIÓN ESTADÍSTICA: Correlación no implica causalidad. "
            "Una alta correlación de Pearson describe asociación lineal, "
            "pero no demuestra relación causal."
        ],
    }

    # ------------------------------------------------------------------
    # 6. Ejecutar Agronomy Agent
    # ------------------------------------------------------------------
    try:
        result = agronomy_agent.run(
            ndvi_values=ndvi_values,
            climate_result=climate_result,
            soil_result=soil_result,
            stats_result=stats_result,
            ml_result=ml_result,
        )
        agents_status = "READY"
    except Exception as exc:
        result = str(exc)
        agents_status = "ERROR"

    # ------------------------------------------------------------------
    # 7. Renderizar en la terminal usando Rich
    # ------------------------------------------------------------------
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich import box

    console = Console()

    # ── Cabecera principal ─────────────────────────────────────────────
    header = Text(justify="center")
    header.append("\nAGROFIELD AI\n", style="bold bright_green")
    header.append("Agricultural Intelligence System\n", style="green")
    header.append("Colta · Chimborazo · Ecuador\n", style="dim green")
    console.print(Panel(header, box=box.DOUBLE_EDGE, padding=(0, 4)))
    console.print()

    # ── Estado del sistema ─────────────────────────────────────────────
    status_table = Table(box=box.SIMPLE_HEAD, show_header=True, expand=True)
    status_table.add_column("Agent", style="cyan", width=24)
    status_table.add_column("Status", justify="center", width=12)
    status_table.add_column("Mode", style="dim")

    agent_info = [
        ("Climate Agent",    "Real NASA POWER CSV"),
        ("Soil Agent",       "Real SoilGrids data (pre-loaded)"),
        ("Data Agent",       "Left-join integration (pre-built, N=53)"),
        ("Statistics Agent", "Pearson r (pre-computed, N=53)"),
        ("ML Agent",         "Linear Regression baseline (pre-run)"),
        ("Agronomy Agent",   "Interpretive synthesis — live"),
    ]
    for ag_name, mode in agent_info:
        if agents_status == "READY":
            status_table.add_row(ag_name, "[bold green]✓ READY[/]", mode)
        else:
            status_table.add_row(ag_name, "[bold red]✗ ERROR[/]", mode)

    console.print(Panel(status_table,
                        title="[bold]SYSTEM STATUS[/]",
                        title_align="left",
                        border_style="blue"))
    console.print()

    # ── Abortar si hay error ───────────────────────────────────────────
    if agents_status == "ERROR":
        err = Text()
        err.append("✗  SYSTEM FAILURE\n\n", style="bold red")
        err.append(str(result), style="red")
        console.print(Panel(err, title="[bold red]ERROR[/]", border_style="red"))
        sys.exit(1)

    # ── Pipeline multi-agente ──────────────────────────────────────────
    flow = Text(justify="center")
    flow.append("  [Climate Agent]\n", style="bold cyan")
    flow.append("        ↓\n", style="dim")
    flow.append("  [Soil Agent]\n", style="bold cyan")
    flow.append("        ↓\n", style="dim")
    flow.append("  [Data Agent]\n", style="bold cyan")
    flow.append("        ↓\n", style="dim")
    flow.append("  [Statistics Agent]\n", style="bold cyan")
    flow.append("        ↓\n", style="dim")
    flow.append("  [ML Agent]\n", style="bold cyan")
    flow.append("        ↓\n", style="dim")
    flow.append("  [Agronomy Agent]\n", style="bold bright_green")
    console.print(Panel(flow,
                        title="[bold]PIPELINE MULTI-AGENT[/]",
                        title_align="left",
                        expand=False))
    console.print()

    # ── VEGETATION / NDVI ─────────────────────────────────────────────
    ns = result["ndvi_section"]

    ndvi_kv = Table(box=None, show_header=False, padding=(0, 1))
    ndvi_kv.add_column("Key", style="bold", min_width=22)
    ndvi_kv.add_column("Value")
    ndvi_kv.add_row("Observations",  str(ns.get("n_observations")))
    ndvi_kv.add_row("Mean NDVI",     str(ns.get("ndvi_mean")))
    ndvi_kv.add_row("Range",         f"{ns.get('ndvi_min')} — {ns.get('ndvi_max')}")
    ndvi_kv.add_row("Confidence",    f"[bold green]{ns.get('confidence')}[/]")

    ndvi_obs = Text()
    ndvi_obs.append("\nObservation:\n", style="bold")
    ndvi_obs.append(ns.get("observation", ""), style="italic")
    ndvi_obs.append("\n\nLimitation:\n", style="bold dim")
    ndvi_obs.append(ns.get("limitation", ""), style="dim")

    ndvi_inner = Table.grid(padding=(0, 0))
    ndvi_inner.add_row(ndvi_kv)
    ndvi_inner.add_row(ndvi_obs)
    console.print(Panel(ndvi_inner,
                        title="[bold]VEGETATION / NDVI[/]",
                        title_align="left",
                        border_style="green"))

    # ── CLIMATE ANALYSIS ──────────────────────────────────────────────
    cs = result["climate_section"]

    climate_kv = Table(box=None, show_header=False, padding=(0, 1))
    climate_kv.add_column("Key", style="bold", min_width=22)
    climate_kv.add_column("Value")
    climate_kv.add_row("Confidence", f"[yellow]{cs.get('confidence')}[/]")
    climate_kv.add_row("Summary",    cs.get("summary", ""))

    climate_obs = Text("\nObservations:\n", style="bold")
    for obs in cs.get("observations", []):
        climate_obs.append(f"  • {obs}\n")

    climate_inner = Table.grid()
    climate_inner.add_row(climate_kv)
    climate_inner.add_row(climate_obs)
    console.print(Panel(climate_inner,
                        title="[bold]CLIMATE ANALYSIS[/]",
                        title_align="left",
                        border_style="blue"))

    # ── SOIL ANALYSIS ────────────────────────────────────────────────
    ss = result["soil_section"]

    soil_kv = Table(box=None, show_header=False, padding=(0, 1))
    soil_kv.add_column("Key", style="bold", min_width=22)
    soil_kv.add_column("Value")
    soil_kv.add_row("Confidence", f"[yellow]{ss.get('confidence')}[/]")

    soil_obs = Text("\nObservations:\n", style="bold")
    for obs in ss.get("observations", []):
        soil_obs.append(f"  • {obs}\n")

    soil_inner = Table.grid()
    soil_inner.add_row(soil_kv)
    soil_inner.add_row(soil_obs)
    console.print(Panel(soil_inner,
                        title="[bold]SOIL ANALYSIS[/]",
                        title_align="left",
                        border_style="yellow"))

    # ── STATISTICAL ANALYSIS ──────────────────────────────────────────
    sts = result["stats_section"]
    corrs = sts.get("pearson_correlations_with_target", {})

    pearson_table = Table(box=box.SIMPLE_HEAD, show_header=True)
    pearson_table.add_column("Variable (vs NDVI)", style="cyan", min_width=24)
    pearson_table.add_column("Pearson r", justify="right", style="magenta", min_width=12)
    pearson_table.add_column("Direction", min_width=14)

    for var, r_val in corrs.items():
        if var == "ndvi":
            continue
        sign = "+" if r_val > 0 else ""
        direction = "[green]positive ↑[/]" if r_val > 0 else "[red]negative ↓[/]"
        pearson_table.add_row(var, f"{sign}{r_val:.3f}", direction)

    stats_note = Text()
    stats_note.append("\n[!] correlation ≠ causation\n", style="bold yellow")
    stats_note.append(
        "Pearson r describes linear association strength only. "
        "A high |r| does not demonstrate biological causality.\n",
        style="dim"
    )
    for obs in sts.get("observations", []):
        stats_note.append(f"  • {obs}\n", style="italic dim")
    stats_note.append(f"\nLimitation: {sts.get('limitation', '')}", style="dim")

    stats_inner = Table.grid()
    stats_inner.add_row(pearson_table)
    stats_inner.add_row(stats_note)
    console.print(Panel(stats_inner,
                        title="[bold]STATISTICAL ANALYSIS[/]",
                        title_align="left",
                        border_style="magenta"))

    # ── MACHINE LEARNING / BASELINE ───────────────────────────────────
    ms = result["ml_section"]
    metrics = ml_result["metricas_test"]

    ml_kv = Table(box=None, show_header=False, padding=(0, 1))
    ml_kv.add_column("Key", style="bold", min_width=22)
    ml_kv.add_column("Value")
    ml_kv.add_row("Model",      ml_result["modelo"])
    ml_kv.add_row("Samples",    str(ml_result["n_observaciones_totales"]))
    ml_kv.add_row("Train",      str(ml_result["n_train"]))
    ml_kv.add_row("Test",       str(ml_result["n_test"]))
    ml_kv.add_row("",           "")
    ml_kv.add_row("MAE",        f"{metrics['MAE']:.4f}")
    ml_kv.add_row("RMSE",       f"{metrics['RMSE']:.4f}")
    ml_kv.add_row("[bold red]R²[/]",        f"[bold red]{metrics['R2']:.3f}[/]")
    ml_kv.add_row("",           "")
    ml_kv.add_row("Status",     "[bold red]BASELINE / LIMITED[/]")
    ml_kv.add_row("Confidence", f"[bold red]{ms.get('confidence')}[/]")

    ml_obs = Text("\nInterpretation:\n", style="bold")
    for obs in ms.get("observations", []):
        ml_obs.append(f"  • {obs}\n", style="italic")
    ml_obs.append("\nLimitation:\n", style="bold dim")
    ml_obs.append(ms.get("limitation", ""), style="dim")

    ml_inner = Table.grid()
    ml_inner.add_row(ml_kv)
    ml_inner.add_row(ml_obs)
    console.print(Panel(ml_inner,
                        title="[bold]MACHINE LEARNING / BASELINE[/]",
                        title_align="left",
                        border_style="red"))

    # ── RISK INDICATORS ───────────────────────────────────────────────
    if result.get("risk_indicators"):
        risk_text = Text()
        for ri in result["risk_indicators"]:
            risk_text.append(f"[{ri['confidence']}] ", style="bold")
            risk_text.append(f"{ri['indicator']}\n", style="bold yellow")
            risk_text.append("Potential implication:\n", style="bold dim")
            risk_text.append(f"  {ri['context']}\n", style="italic")
            risk_text.append(
                "Interpretation: Contextual observation only — not a diagnosis.\n\n",
                style="dim"
            )
        console.print(Panel(risk_text,
                            title="[bold]RISK INDICATORS[/]",
                            title_align="left",
                            border_style="yellow"))

    # ── AGRONOMY AGENT — FINAL REPORT ────────────────────────────────
    ag_header = Text()
    ag_header.append("Confidence: MEDIUM\n\n", style="bold cyan")
    ag_header.append("✓ Climate assessment\n", style="green")
    ag_header.append("✓ Soil assessment\n", style="green")
    ag_header.append("✓ Vegetation assessment (NDVI spectral index)\n", style="green")
    ag_header.append("✓ Statistical evidence (Pearson, N=53)\n", style="green")
    ag_header.append("✓ ML evidence (Linear Regression baseline)\n", style="green")

    ag_actions = Text("\nMONITORING ACTIONS\n", style="bold underline")
    for i, act in enumerate(result["monitoring_actions"], 1):
        ag_actions.append(f"  {i}. {act}\n")

    ag_note = Text("\n[TERMINOLOGY NOTE]\n", style="bold dim")
    ag_note.append(result["terminology_note"], style="dim")

    ag_inner = Table.grid()
    ag_inner.add_row(ag_header)
    ag_inner.add_row(ag_actions)
    ag_inner.add_row(ag_note)
    console.print(Panel(ag_inner,
                        title="[bold]AGRONOMY AGENT — FINAL REPORT[/]",
                        title_align="left",
                        border_style="cyan"))

    # ── LIMITACIONES ──────────────────────────────────────────────────
    lim_text = Text()
    lim_text.append(
        "• E2E demo uses mock/pre-calculated satellite & ML inputs "
        "(real GEE extraction requires authenticated API)\n",
        style="bold"
    )
    for lim in result["global_limitations"]:
        lim_text.append(f"• {lim}\n", style="dim")
    console.print(Panel(lim_text,
                        title="[bold]LIMITATIONS[/]",
                        title_align="left",
                        border_style="dim"))

    # ── Footer / cierre ───────────────────────────────────────────────
    footer = Text(justify="center")
    footer.append("\nANALYSIS COMPLETED\n\n", style="bold bright_green")
    footer.append("AgroField AI  ·  Colta, Chimborazo  ·  Ecuador\n", style="green")
    footer.append("Agronomy Agent: SUCCESS\n", style="bold green")
    console.print(Panel(footer, box=box.DOUBLE_EDGE, padding=(0, 4)))


if __name__ == "__main__":
    main()
