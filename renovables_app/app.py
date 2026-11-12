"""Energías renovables en Argentina: dashboard interactivo."""
import inspect
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

AUTOR = "Tu nombre"  # editá esto
DATA = Path(__file__).parent / "data"

st.set_page_config(page_title="Renovables en Argentina", page_icon="🌬️", layout="wide")

BG, PANEL, LINE, TXT, MUTED = "#07131C", "#0E2230", "#1B3A4D", "#E8F1F2", "#8FA9B5"
COLORES = {"Eólica": "#4FD1C5", "Solar": "#FFB547", "Hidro ≤50 MW": "#4C8DFF",
           "Biomasa": "#9BDB5B", "Biogás": "#E070C8", "Biodiésel": "#9AA7B2"}
FUENTES = {"EOLICO": "Eólica", "SOLAR": "Solar", "HIDRO <=50MW": "Hidro ≤50 MW",
           "BIOMASA": "Biomasa", "BIOGAS": "Biogás", "BIODIESEL": "Biodiésel"}
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
PROV = {  # nombre, lat, lon
    "BUENOS AIRES": ("Buenos Aires", -36.6, -60.0), "CHUBUT": ("Chubut", -43.8, -68.8),
    "LA RIOJA": ("La Rioja", -29.7, -67.0), "TUCUMAN": ("Tucumán", -26.9, -65.4),
    "CORDOBA": ("Córdoba", -31.4, -64.0), "MENDOZA": ("Mendoza", -34.6, -68.5),
    "SAN JUAN": ("San Juan", -30.9, -68.9), "JUJUY": ("Jujuy", -23.3, -65.4),
    "SANTIAGO DEL ESTERO": ("Santiago del Estero", -27.8, -63.3), "MISIONES": ("Misiones", -26.9, -54.6),
    "LA PAMPA": ("La Pampa", -37.1, -65.4), "SANTA FE": ("Santa Fe", -30.9, -60.9),
    "SALTA": ("Salta", -24.8, -65.4), "RIO NEGRO": ("Río Negro", -40.0, -67.5),
    "SAN LUIS": ("San Luis", -33.7, -66.0), "CATAMARCA": ("Catamarca", -27.3, -66.9),
    "SANTA CRUZ": ("Santa Cruz", -48.8, -70.0), "NEUQUÉN": ("Neuquén", -38.9, -70.1),
    "CORRIENTES": ("Corrientes", -28.7, -57.8), "CHACO": ("Chaco", -26.4, -60.8),
    "FORMOSA": ("Formosa", -24.9, -60.0),
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;700;800&family=Figtree:wght@400;500;600&display=swap');
:root{--bg:#07131C;--panel:#0E2230;--line:#1B3A4D;--txt:#E8F1F2;--muted:#8FA9B5;--eo:#4FD1C5;--sol:#FFB547}
.stApp{background:radial-gradient(1200px 500px at 85% -10%,#0f3a4a55,transparent),var(--bg)}
.stApp,.stMarkdown,p,label,li,.stTabs button,[data-testid="stSidebar"]{font-family:'Figtree',sans-serif}
h1,h2,h3,.hero-title,.kpi b{font-family:'Bricolage Grotesque',sans-serif!important;letter-spacing:-.01em}
.block-container{padding-top:1.4rem;max-width:1280px}
header[data-testid="stHeader"]{background:transparent}
footer,#MainMenu{visibility:hidden}
.hero{display:grid;grid-template-columns:1.3fr .7fr;gap:20px;align-items:center;background:linear-gradient(120deg,#0E2230,#0A1B27 65%);border:1px solid var(--line);border-radius:22px;padding:34px 40px;margin-bottom:22px;overflow:hidden}
.hero-title{font-size:2.55rem;line-height:1.08;font-weight:800;margin:0 0 14px;color:var(--txt)}
.hero p{color:var(--muted);font-size:1.05rem;max-width:60ch;margin:0}
.stats{display:flex;gap:30px;margin-top:24px;flex-wrap:wrap}
.stats div{border-left:3px solid var(--c);padding-left:12px;color:var(--muted);font-size:.9rem}
.stats b{display:block;font-size:1.6rem;color:var(--txt);font-family:'Bricolage Grotesque',sans-serif}
.hero-svg{width:100%;height:auto;max-height:280px}
.rotor{transform-origin:110px 96px;animation:giro 14s linear infinite}
.rotor2{transform-origin:210px 150px;animation:giro 9s linear infinite}
@keyframes giro{to{transform:rotate(360deg)}}
@media (prefers-reduced-motion:reduce){.rotor,.rotor2{animation:none}}
@media (max-width:820px){.hero{grid-template-columns:1fr;padding:24px}.hero-title{font-size:1.9rem}}
.kpi{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--c);border-radius:12px;padding:14px 16px;height:100%}
.kpi b{display:block;font-size:1.7rem;color:var(--txt)}
.kpi span{color:var(--muted);font-size:.88rem}
.nota{border-left:3px solid var(--sol);background:rgba(255,181,71,.08);padding:12px 16px;border-radius:6px;color:var(--txt);margin:8px 0 14px}
.ok{border-left-color:var(--eo);background:rgba(79,209,197,.08)}
.stTabs [data-baseweb="tab-list"]{gap:4px;border-bottom:1px solid var(--line)}
.stTabs [data-baseweb="tab"]{font-weight:600;padding:10px 16px}
h3{margin-top:.6rem}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def html(s: str):
    st.markdown(" ".join(l.strip() for l in s.splitlines()), unsafe_allow_html=True)


def n(x, d=0):
    return f"{x:,.{d}f}".replace(",", "§").replace(".", ",").replace("§", ".")


def kpi(col, valor, etiqueta, color="#4FD1C5"):
    col.markdown(f'<div class="kpi" style="--c:{color}"><b>{valor}</b><span>{etiqueta}</span></div>',
                 unsafe_allow_html=True)


def _kw(fn):
    return {"width": "stretch"} if "width" in inspect.signature(fn).parameters else {"use_container_width": True}


def mostrar(fig, alto=420, leyenda=True):
    fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="Figtree, sans-serif", color=TXT), height=alto,
                      margin=dict(l=8, r=8, t=48, b=8), showlegend=leyenda,
                      legend=dict(orientation="h", y=-0.14, title_text=""),
                      title=dict(font=dict(family="Bricolage Grotesque, sans-serif", size=18)),
                      hoverlabel=dict(bgcolor=PANEL, font_color=TXT))
    fig.update_xaxes(gridcolor=LINE, zeroline=False)
    fig.update_yaxes(gridcolor=LINE, zeroline=False)
    st.plotly_chart(fig, theme=None, config={"displaylogo": False}, **_kw(st.plotly_chart))


def tabla(df, **kw):
    st.dataframe(df, hide_index=True, **_kw(st.dataframe), **kw)


@st.cache_data
def cargar():
    base = pd.read_csv(DATA / "base_centrales_anual.csv")
    base["fuente_n"] = base.fuente.map(FUENTES)
    base["prov_n"] = base.provincia.map(lambda p: PROV.get(p, (p.title(), None, None))[0])
    men = pd.read_csv(DATA / "historico_mensual_fuentes.csv", encoding="utf-8-sig", parse_dates=["MES"])
    men["fuente_n"] = men.Fuente.map(FUENTES)
    pron = pd.read_csv(DATA / "pronostico_renovables_12_24_meses.csv", encoding="utf-8-sig")
    pron["fecha"] = pd.to_datetime(pron.Mes_objetivo + "-01")
    back = pd.read_csv(DATA / "backtest_renovables_12_24_meses.csv", encoding="utf-8-sig")
    back["fecha"] = pd.to_datetime(back.Objetivo + "-01")
    met = pd.read_csv(DATA / "metricas_backtest_12_24_meses.csv", encoding="utf-8-sig")
    return base, men, pron, back, met


base, men, pron, back, met = cargar()
total_mes = men.groupby("MES", as_index=False).Generacion_GWh.sum()
meses_por_anio = men.groupby(men.MES.dt.year).MES.nunique()
ULT = int(meses_por_anio[meses_por_anio == 12].index.max())
anual_tot = base.groupby("anio").gwh.sum()
ratio = anual_tot[ULT] / anual_tot[ULT - 10]
pct_eo = base[(base.anio == ULT) & (base.fuente == "EOLICO")].gwh.sum() / anual_tot[ULT] * 100

# ---------------- barra lateral ----------------
with st.sidebar:
    st.markdown("### Filtros")
    desde, hasta = st.slider("Período", int(base.anio.min()), int(base.anio.max()), (ULT - 10, ULT))
    opciones = list(COLORES)
    sel = st.multiselect("Fuentes", opciones, default=[o for o in opciones if o != "Biodiésel"])
    st.caption("Biodiésel solo tiene datos de 2011 a 2012. 2026 llega hasta agosto.")
    st.markdown("---")
    st.caption(f"Proyecto académico, Ciencia de Datos e IA. Autor: {AUTOR}")
if not sel:
    st.warning("Elegí al menos una fuente en la barra lateral.")
    st.stop()

b = base[base.anio.between(desde, hasta) & base.fuente_n.isin(sel)]
m = men[men.MES.dt.year.between(desde, hasta) & men.fuente_n.isin(sel)]

# ---------------- hero ----------------
def aspa(cx, cy, largo, ancho):
    return "".join(f'<path d="M{cx} {cy} L{cx-ancho} {cy-6} L{cx} {cy-largo} L{cx+ancho} {cy-6} Z" '
                   f'transform="rotate({a} {cx} {cy})" fill="#E8F7F5"/>' for a in (0, 120, 240))

svg = f"""<svg viewBox="0 0 320 300" class="hero-svg" role="img" aria-label="Aerogeneradores frente al sol">
<defs><radialGradient id="sol"><stop offset="0%" stop-color="#FFD27A"/><stop offset="55%" stop-color="#FFB547" stop-opacity=".5"/>
<stop offset="100%" stop-color="#FFB547" stop-opacity="0"/></radialGradient>
<linearGradient id="cerro" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#14425a"/><stop offset="100%" stop-color="#0b2433"/></linearGradient></defs>
<circle cx="238" cy="92" r="82" fill="url(#sol)"/><circle cx="238" cy="92" r="25" fill="#FFC15E"/>
<path d="M0 262 Q80 222 160 246 T320 232 V300 H0 Z" fill="url(#cerro)"/>
<polygon points="108,100 112,100 116,262 104,262" fill="#CFE9E6"/>
<polygon points="209,153 211,153 214,252 206,252" fill="#CFE9E6"/>
<g class="rotor">{aspa(110, 96, 78, 3)}</g><circle cx="110" cy="96" r="5" fill="#4FD1C5"/>
<g class="rotor2">{aspa(210, 150, 50, 2.4)}</g><circle cx="210" cy="150" r="4" fill="#4FD1C5"/></svg>"""
html(f"""<div class="hero"><div>
<div class="hero-title">En {ULT}, Argentina generó {n(ratio, 1)} veces más energía renovable que en {ULT - 10}</div>
<p>Quince años de generación por fuente, provincia y central, más un pronóstico a 24 meses puesto a prueba con un backtest.</p>
<div class="stats">
<div style="--c:#4FD1C5"><b>{n(anual_tot[ULT])} GWh</b>generados en {ULT}</div>
<div style="--c:#FFB547"><b>{n(pct_eo)}%</b>fue energía eólica</div>
<div style="--c:#4C8DFF"><b>{base.central.nunique()} centrales</b>en {base.provincia.nunique()} provincias</div>
</div></div><div>{svg}</div></div>""")

t1, t2, t3, t4, t5, t6 = st.tabs(["Panorama", "Mapa", "Ritmo del año", "Pronóstico", "¿Cuánto confiar?", "Datos y método"])

# ---------------- 1. panorama ----------------
with t1:
    anual = b.groupby(["anio", "fuente_n"], as_index=False).gwh.sum()
    ult = anual[anual.anio == anual.anio.max()].sort_values("gwh", ascending=False)
    c = st.columns(4)
    tot_ult, tot_ini = ult.gwh.sum(), anual[anual.anio == anual.anio.min()].gwh.sum()
    kpi(c[0], f"{n(tot_ult)} GWh", f"generación en {anual.anio.max()}")
    kpi(c[1], f"×{n(tot_ult / tot_ini, 1)}" if tot_ini else "-", f"vs {anual.anio.min()}", "#FFB547")
    kpi(c[2], ult.iloc[0].fuente_n, f"fuente líder ({n(ult.iloc[0].gwh / tot_ult * 100)}%)", "#4C8DFF")
    pico = total_mes.loc[total_mes.Generacion_GWh.idxmax()]
    kpi(c[3], f"{n(pico.Generacion_GWh)} GWh", f"mes récord: {MESES[pico.MES.month - 1]} {pico.MES.year}", "#9BDB5B")
    st.write("")
    a, bcol = st.columns([1.6, 1])
    with a:
        fig = px.area(anual, x="anio", y="gwh", color="fuente_n", color_discrete_map=COLORES,
                      labels={"anio": "", "gwh": "GWh", "fuente_n": ""}, title="Generación anual por fuente")
        fig.update_traces(line_width=1.2)
        mostrar(fig, 430)
    with bcol:
        anios = sorted(anual.anio.unique())
        ya = st.select_slider("Año del reparto", anios, value=anios[-1] if anios[-1] != 2026 or len(anios) == 1 else anios[-2])
        rep = anual[anual.anio == ya]
        fig = px.pie(rep, names="fuente_n", values="gwh", hole=0.62, color="fuente_n", color_discrete_map=COLORES,
                     title=f"Reparto en {ya}")
        fig.update_traces(textinfo="percent", sort=False)
        fig.add_annotation(text=f"<b>{n(rep.gwh.sum())}</b><br>GWh", showarrow=False, font=dict(size=16))
        mostrar(fig, 400)
    if desde < hasta:
        pv = anual.pivot(index="fuente_n", columns="anio", values="gwh").fillna(0)
        crec = (pv[pv.columns.max()] - pv[pv.columns.min()]).sort_values().reset_index(name="gwh")
        fig = px.bar(crec, x="gwh", y="fuente_n", orientation="h", color="fuente_n", color_discrete_map=COLORES,
                     labels={"gwh": "Cambio en GWh", "fuente_n": ""},
                     title=f"Crecimiento absoluto {pv.columns.min()} a {pv.columns.max()}")
        mostrar(fig, 300, False)
        top = crec.iloc[-1]
        html(f'<div class="nota ok">La fuente que más creció fue <b>{top.fuente_n}</b>, con {n(top.gwh)} GWh más por año que en {pv.columns.min()}.</div>')

# ---------------- 2. mapa ----------------
with t2:
    py = b.groupby(["anio", "provincia"], as_index=False).gwh.sum()
    py = py[py.gwh > 0].copy()
    py["nombre"] = py.provincia.map(lambda p: PROV[p][0])
    py["lat"] = py.provincia.map(lambda p: PROV[p][1])
    py["lon"] = py.provincia.map(lambda p: PROV[p][2])
    py = py.sort_values("anio")
    st.markdown("### Dónde se genera")
    st.caption("Apretá ▶ para ver cómo se fue encendiendo el mapa año a año.")
    escala = ["#12384a", "#4FD1C5", "#FFB547"]
    args = dict(lat="lat", lon="lon", size="gwh", color="gwh", hover_name="nombre", animation_frame="anio",
                size_max=58, zoom=2.7, center=dict(lat=-38.5, lon=-65), range_color=[0, py.gwh.max()],
                color_continuous_scale=escala, labels={"gwh": "GWh"})
    if hasattr(px, "scatter_map"):
        fig = px.scatter_map(py, map_style="carto-darkmatter", **args)
    else:
        fig = px.scatter_mapbox(py, mapbox_style="carto-darkmatter", **args)
    try:
        fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 800
        fig.layout.updatemenus[0].font.color = "#07131C"
        fig.layout.sliders[0].font.color = TXT
    except (IndexError, AttributeError, TypeError):
        pass
    fig.update_layout(coloraxis_colorbar=dict(title="GWh"))
    mostrar(fig, 640, False)

    izq, der = st.columns([1, 1])
    with izq:
        anios_m = sorted(b.anio.unique())
        ym = st.selectbox("Año del ranking", anios_m, index=len(anios_m) - 1)
        rk = b[b.anio == ym].groupby(["prov_n", "fuente_n"], as_index=False).gwh.sum()
        orden = rk.groupby("prov_n").gwh.sum().nlargest(10).index
        rk = rk[rk.prov_n.isin(orden)]
        fig = px.bar(rk, x="gwh", y="prov_n", color="fuente_n", orientation="h", color_discrete_map=COLORES,
                     category_orders={"prov_n": list(orden[::-1])}, labels={"gwh": "GWh", "prov_n": ""},
                     title=f"Top 10 provincias en {ym}")
        mostrar(fig, 430)
    with der:
        cen = (b.groupby(["central", "fuente_n", "prov_n"], as_index=False).gwh.sum()
               .nlargest(12, "gwh").rename(columns={"central": "Central", "fuente_n": "Fuente",
                                                    "prov_n": "Provincia", "gwh": "GWh acumulados"}))
        st.markdown(f"**Las 12 centrales que más generaron entre {desde} y {hasta}**")
        tabla(cen, column_config={"GWh acumulados": st.column_config.ProgressColumn(
            "GWh acumulados", format="%d", min_value=0, max_value=float(cen["GWh acumulados"].max()))})

# ---------------- 3. ritmo del año ----------------
with t3:
    st.markdown("### El pulso mensual")
    tm = m.groupby("MES", as_index=False).Generacion_GWh.sum()
    if tm.empty:
        st.info("Las fuentes elegidas no tienen datos mensuales en este período (biodiésel no figura en la serie mensual).")
    else:
        tm["anio"], tm["mes"] = tm.MES.dt.year, tm.MES.dt.month
        pv = tm.pivot(index="anio", columns="mes", values="Generacion_GWh").reindex(columns=range(1, 13))
        pv.index = pv.index.astype(str)
        pv.columns = MESES
        fig = px.imshow(pv, aspect="auto", color_continuous_scale=["#0a1b27", "#164c57", "#4FD1C5", "#FFB547"],
                        labels=dict(x="", y="", color="GWh"), title="Generación por mes y año (GWh)")
        mostrar(fig, 480, False)
        perfil = m.groupby([m.MES.dt.month.rename("mes"), "fuente_n"], as_index=False).Generacion_GWh.mean()
        perfil["Mes"] = perfil.mes.map(lambda i: MESES[i - 1])
        fig = px.line(perfil, x="Mes", y="Generacion_GWh", color="fuente_n", markers=True,
                      color_discrete_map=COLORES, labels={"Generacion_GWh": "GWh promedio", "Mes": "", "fuente_n": ""},
                      title="Perfil de un año típico, por fuente")
        mostrar(fig, 400)
        pt = perfil.groupby("mes").Generacion_GWh.sum()
        html(f'<div class="nota ok">Promediando el período, el mes más fuerte es <b>{MESES[pt.idxmax() - 1]}</b> y el más flojo <b>{MESES[pt.idxmin() - 1]}</b>. '
             f'Esa estacionalidad es justo lo que aprovechan los modelos de pronóstico.</div>')

# ---------------- 4. pronóstico ----------------
with t4:
    st.markdown("### Qué se espera para los próximos meses")
    hor = st.radio("Horizonte", [12, 24], horizontal=True, format_func=lambda h: f"{h} meses")
    p = pron[pron.Horizonte_meses <= hor]
    hist = total_mes.tail(36)
    ult_fecha = hist.MES.iloc[-1]
    fig = go.Figure()
    fig.add_scatter(x=hist.MES, y=hist.Generacion_GWh, name="Real", mode="lines", line=dict(color="#4FD1C5", width=3))
    fx = [ult_fecha] + list(p.fecha)
    fy = [hist.Generacion_GWh.iloc[-1]] + list(p.Pronostico_GWh)
    fig.add_scatter(x=fx, y=fy, name="Pronóstico (Ridge)", mode="lines", line=dict(color="#FFB547", width=3, dash="dash"))
    pb = p.dropna(subset=["Inferior_GWh"])
    fig.add_scatter(x=pb.fecha, y=pb.Pronostico_GWh, name="Banda ± RMSE del backtest", mode="markers",
                    marker=dict(color="#FFB547", size=10, line=dict(color="#07131C", width=2)),
                    error_y=dict(type="data", symmetric=False, array=pb.Superior_GWh - pb.Pronostico_GWh,
                                 arrayminus=pb.Pronostico_GWh - pb.Inferior_GWh, color="#FFB547", thickness=2, width=7))
    x0 = ult_fecha.strftime("%Y-%m-%d")
    fig.add_shape(type="line", x0=x0, x1=x0, y0=0, y1=1, yref="paper", line=dict(color=MUTED, width=1, dash="dot"))
    fig.add_annotation(x=x0, y=1, yref="paper", text="hoy", showarrow=False, yshift=10, font=dict(color=MUTED))
    fig.update_yaxes(title="GWh por mes")
    fig.update_layout(title="Generación renovable total: últimos 36 meses y pronóstico")
    mostrar(fig, 470)
    prox = pron.Pronostico_GWh.iloc[:12].sum()
    ant = hist.Generacion_GWh.tail(12).sum()
    r12, r24 = pron[pron.Horizonte_meses == 12].iloc[0], pron[pron.Horizonte_meses == 24].iloc[0]
    c = st.columns(3)
    kpi(c[0], f"{n(prox)} GWh", f"próximos 12 meses ({n((prox / ant - 1) * 100, 1)}% vs los 12 anteriores)")
    kpi(c[1], f"{n(r12.Pronostico_GWh)} GWh", f"en {r12.Mes_objetivo}, entre {n(r12.Inferior_GWh)} y {n(r12.Superior_GWh)}", "#FFB547")
    kpi(c[2], f"{n(r24.Pronostico_GWh)} GWh", f"en {r24.Mes_objetivo}, entre {n(r24.Inferior_GWh)} y {n(r24.Superior_GWh)}", "#4C8DFF")
    html('<div class="nota">La banda es el error típico (RMSE) que tuvo el modelo en el backtest a ese horizonte. '
         'Sirve como orden de magnitud, no es un intervalo de confianza formal.</div>')
    out = p[["Mes_objetivo", "Pronostico_GWh", "Inferior_GWh", "Superior_GWh"]].rename(
        columns={"Mes_objetivo": "Mes", "Pronostico_GWh": "Pronóstico GWh", "Inferior_GWh": "Mínimo GWh", "Superior_GWh": "Máximo GWh"})
    with st.expander("Ver la tabla y descargarla"):
        tabla(out)
        st.download_button("Descargar CSV", out.to_csv(index=False).encode("utf-8"), "pronostico_renovables.csv", "text/csv")

# ---------------- 5. backtest ----------------
with t5:
    st.markdown("### ¿Le creemos al modelo?")
    st.caption("Backtest: pronosticar meses que ya ocurrieron y comparar contra lo real.")
    h = st.radio("Horizonte a evaluar", [12, 24], horizontal=True, key="hb", format_func=lambda h: f"{h} meses")
    bk = back[back.Horizonte_meses == h].sort_values("fecha")
    fig = go.Figure()
    fig.add_scatter(x=bk.fecha, y=bk.Real_GWh, name="Real", line=dict(color="#FFFFFF", width=4))
    for col, nom, color, dash in [("Ridge_GWh", "Ridge", "#4FD1C5", "solid"),
                                  ("Estacional_ingenuo_GWh", "Estacional ingenuo", "#FFB547", "solid"),
                                  ("Media_12m_GWh", "Media 12 meses", "#9AA7B2", "dot")]:
        fig.add_scatter(x=bk.fecha, y=bk[col], name=nom, line=dict(color=color, width=2.5, dash=dash))
    fig.update_layout(title=f"Real vs modelos con horizonte de {h} meses")
    fig.update_yaxes(title="GWh por mes")
    mostrar(fig, 430)
    mh = met[met.Horizonte == h].set_index("Modelo")
    mejor = mh["WAPE_%"].idxmin().replace("_", " ")
    sesgo = (bk.Ridge_GWh - bk.Real_GWh).mean()
    c = st.columns(3)
    kpi(c[0], mejor, f"menor error a {h} meses (WAPE {n(mh['WAPE_%'].min(), 1)}%)")
    kpi(c[1], f"{n(mh.loc['Ridge', 'MAE_GWh'])} GWh", "error absoluto medio de Ridge", "#FFB547")
    kpi(c[2], f"{n(sesgo)} GWh", "sesgo medio de Ridge (negativo: se queda corto)", "#E070C8")
    st.write("")
    mt = met.copy()
    mt["Horizonte"] = mt.Horizonte.astype(str) + " meses"
    mt["Modelo"] = mt.Modelo.str.replace("_", " ")
    fig = px.bar(mt, x="Modelo", y="WAPE_%", color="Horizonte", barmode="group", text_auto=".1f",
                 color_discrete_map={"12 meses": "#4FD1C5", "24 meses": "#FFB547"},
                 labels={"WAPE_%": "WAPE (%)", "Modelo": ""}, title="Error porcentual por modelo (menos es mejor)")
    mostrar(fig, 380)
    html('<div class="nota"><b>Lectura honesta:</b> a 12 meses el modelo estacional ingenuo le gana a Ridge, y a 24 meses Ridge le gana a todos. '
         'El R² es negativo en todos los casos: con solo 12 puntos de evaluación y una serie con tendencia fuerte, ningún modelo supera '
         'al promedio del período evaluado. Es una señal de cautela y conviene presentarla tal cual.</div>')
    with st.expander("Tabla de métricas"):
        tabla(met)

# ---------------- 6. datos y método ----------------
with t6:
    st.markdown("### De dónde salen los números")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
**Fuente.** Base de datos de generación renovable de Argentina (mensual por central, 2011 a agosto 2026).

**Limpieza.**
- Se eliminó una columna auxiliar casi vacía y las filas duplicadas.
- *Demanda MEM* se excluyó: es demanda eléctrica, no generación.
- Se limpiaron espacios en los nombres de categorías.
- 2026 llega solo hasta agosto, por eso los análisis anuales usan años completos.
- Biodiésel solo tiene datos 2011 a 2012: se muestra en la historia pero no se proyecta.
""")
    with c2:
        st.markdown("""
**Pronóstico.** Regresión Ridge con estacionalidad y tendencia sobre la serie total agregada por mes, a 12 y 24 meses.

**Backtest.** Se pronostica meses pasados desde un origen anterior y se compara con lo real, frente a dos referencias simples: estacional ingenuo (mismo mes del año anterior) y media móvil de 12 meses.

**Métricas.** MAE: error medio en GWh. RMSE: penaliza más los errores grandes. WAPE: error total relativo a lo generado. R²: cuánto mejora al promedio.
""")
    st.caption(f"Hecho con Streamlit y Plotly. Autor: {AUTOR}")
