import dash
from dash import dcc, html, Input, Output, State, no_update
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from scipy.stats import norm, gaussian_kde
from engine import SystemicRiskEngine

external_stylesheets = ['https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;700&display=swap']
external_scripts = ['https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, external_scripts=external_scripts)
engine = SystemicRiskEngine()
engine.fetch_all_data(period="2y")

LATEX_FONT = dict(family="EB Garamond, serif", size=16)

# Coordenadas geográficas para o Dorling Cartogram
COUNTRY_COORDS = {
    'USA': [37.0, -95.0], 'Germany': [51.0, 10.0], 'France': [46.0, 2.0],
    'UK': [55.0, -3.0], 'Japan': [36.0, 138.0], 'Hong Kong': [22.3, 114.1],
    'Brazil': [-14.0, -51.0], 'Mexico': [23.0, -102.0], 'India': [20.0, 78.0],
    'China': [35.0, 103.0], 'Singapore': [1.3, 103.8], 'Netherlands': [52.0, 5.0],
    'Spain': [40.0, -3.0], 'Canada': [56.0, -106.0], 'Sweden': [60.0, 18.0],
    'Italy': [41.0, 12.0], 'Switzerland': [46.0, 8.0], 'Australia': [-25.0, 133.0]
}

options = [{'label': f"{r['name']} ({r['ticker']})", 'value': r['ticker']} 
           for _, r in engine.assets_df[engine.assets_df['sector'] != 'Country'].iterrows()]

app.layout = html.Div([
    dcc.Store(id='mc-paths-store'),
    dcc.Store(id='mc-es-store'),
    dcc.Store(id='animation-frame', data=0),
    dcc.Interval(id='animation-interval', interval=50, n_intervals=0, disabled=True),

    # Header
    html.Div([
        html.H1("QUANT RISK TERMINAL", style={'margin': '0', 'fontSize': '18px', 'letterSpacing': '2px'}),
        dcc.Dropdown(id='main-asset-dropdown', options=options, value='AAPL', 
                     style={'width': '250px', 'color': '#000'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 
              'padding': '10px 30px', 'borderBottom': '1px solid #333', 'height': '60px'}),

    # Main Split Layout (50/50)
    html.Div([
        
        # Linha Superior: Análise Detalhada
        html.Div([
            html.Div([
                html.H3("STRESS EVENTS", style={'fontSize': '11px', 'color': '#e74c3c', 'marginBottom': '10px'}),
                html.Div(id='extreme-dates-list', style={'height': 'calc(100% - 30px)', 'overflowY': 'auto', 'fontSize': '12px'})
            ], style={'width': '200px', 'padding': '15px', 'borderRight': '1px solid #333'}),

            html.Div([
                dcc.Graph(id='distribution-graph', style={'height': '100%'}, mathjax=True),
            ], style={'flex': '1'}),
            html.Div([
                dcc.Graph(id='monte-carlo-graph', style={'height': '100%'}, mathjax=True)
            ], style={'flex': '1'})
        ], style={'display': 'flex', 'flex': '1', 'borderBottom': '1px solid #333'}),

        # Linha Inferior: Mapa Global e Safe Havens
        html.Div([
            dcc.Graph(id='contagion-map', style={'flex': '3', 'height': '100%'}, mathjax=True),
            
            # Nova coluna de Safe Havens
            html.Div([
                html.H3("SAFE HAVENS", style={'fontSize': '11px', 'color': '#2ecc71', 'marginBottom': '10px'}),
                html.Div(id='safe-havens-list', style={'height': 'calc(100% - 30px)', 'overflowY': 'auto', 'fontSize': '12px'})
            ], style={'flex': '1', 'padding': '15px', 'borderLeft': '1px solid #333', 'backgroundColor': '#0a0a0a'})
            
        ], style={'flex': '1', 'display': 'flex'})

    ], style={'display': 'flex', 'flexDirection': 'column', 'height': 'calc(100vh - 60px)'})

], style={'backgroundColor': '#000', 'color': '#eee', 'fontFamily': 'EB Garamond, serif', 'height': '100vh', 'overflow': 'hidden'})


@app.callback(
    [Output('distribution-graph', 'figure'), Output('contagion-map', 'figure'),
     Output('extreme-dates-list', 'children'), Output('safe-havens-list', 'children'),
     Output('mc-paths-store', 'data'), Output('mc-es-store', 'data'), 
     Output('animation-interval', 'disabled'), Output('animation-frame', 'data')],
    [Input('main-asset-dropdown', 'value')]
)
def setup_analysis(selected_ticker):
    engine.set_main_asset(selected_ticker)
    extreme_days, var_limit, filtered_returns = engine.get_extreme_events(months=24)
    
    # 1. Gráfico de Distribuição Restaurado
    counts, bin_edges = np.histogram(filtered_returns, bins=80, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    fig_dist = go.Figure()
    # Barras de Histograma
    fig_dist.add_trace(go.Bar(x=bin_centers[bin_centers > var_limit], y=counts[bin_centers > var_limit], 
                              marker_color='#333', name='Normal', showlegend=False))
    fig_dist.add_trace(go.Bar(x=bin_centers[bin_centers <= var_limit], y=counts[bin_centers <= var_limit], 
                              marker_color='#c0392b', name='Tail Stress', showlegend=False))
    
    # Curvas de Distribuição
    x_range = np.linspace(filtered_returns.min(), filtered_returns.max(), 250)
    fig_dist.add_trace(go.Scatter(x=x_range, y=gaussian_kde(filtered_returns)(x_range), 
                                  name='KDE', line=dict(color='#3498db', width=2.5)))
    fig_dist.add_trace(go.Scatter(x=x_range, y=norm.pdf(x_range, filtered_returns.mean(), filtered_returns.std()), 
                                  name='Gaussian', line=dict(color='#777', dash='dash', width=1.5)))
    
    # Linha e Anotação VaR
    fig_dist.add_vline(x=var_limit, line_dash="dash", line_color="#e74c3c")
    fig_dist.add_annotation(x=var_limit, y=0.95, yref="paper", text=rf"$VaR_{{99\%}} = {var_limit:.2%}$",
                            showarrow=False, font=dict(color="#e74c3c", size=16), bgcolor="rgba(0,0,0,0.5)")

    fig_dist.update_layout(title=rf"$\text{{Return Distribution: }} \text{{{selected_ticker}}}$", 
                          font=LATEX_FONT, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', 
                          plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=40, r=20, t=50, b=40), xaxis_title=r"$\Delta \ln(P_t)$")

    # 2. Mapa Dorling (Salto de Correlação)
    country_assets = engine.assets_df[engine.assets_df['sector'] == 'Country']
    map_rows = []
    for _, row in country_assets.iterrows():
        metrics = engine.get_contagion_metrics(row['ticker'], extreme_days.index, filtered_returns.index)
        if metrics:
            delta_rho, _, _ = metrics
            coords = COUNTRY_COORDS.get(row['country'])
            if coords:
                map_rows.append({'$\Delta \\rho$': delta_rho, 'Lat': coords[0], 'Lon': coords[1], 'Name': row['name']})
    
    df_map = pd.DataFrame(map_rows)
    fig_map = go.Figure(go.Scattergeo(
        lat=df_map['Lat'], lon=df_map['Lon'],
        marker=dict(
            size=np.abs(df_map['$\Delta \\rho$']) * 130 + 12, 
            color=df_map['$\Delta \\rho$'], colorscale='RdBu_r', cmid=0,
            showscale=True, colorbar=dict(title=r"$\Delta \rho$", thickness=15),
            line=dict(width=1, color='white')
        ),
        text=[f"{n}<br>$\Delta \\rho$: {d:.2f}" for n, d in zip(df_map['Name'], df_map['$\Delta \\rho$'])]
    ))
    fig_map.update_geos(projection_type="natural earth", showland=True, landcolor="#080808", 
                        oceancolor="#000", showcountries=True, countrycolor="#222", bgcolor="rgba(0,0,0,0)")
    fig_map.update_layout(title=rf"$\text{{Systemic Contagion Map: }} \Delta \rho = \rho_{{\text{{stress}}}} - \rho_{{\text{{calm}}}}$",
                          font=LATEX_FONT, template="plotly_dark", margin=dict(l=10, r=10, t=50, b=10), paper_bgcolor='rgba(0,0,0,0)')

    # Lógica de Safe Havens (Correlação Negativa) usando .format()
    safe_havens = sorted([row for row in map_rows if row['$\Delta \\rho$'] < 0], key=lambda x: x['$\Delta \\rho$'])
    
    safe_list_items = [
        html.Div([
            html.Span(sh['Name']), 
            html.Span("{:.2f}".format(sh['$\Delta \\rho$']), style={'float':'right','color':'#2ecc71'})
        ], style={'padding':'4px 0','borderBottom':'1px solid #111'}) 
        for sh in safe_havens
    ]
    
    if not safe_list_items:
        safe_list_items = [html.Div("No safe havens found.", style={'color': '#777', 'padding': '10px 0'})]

    # 3. Monte Carlo e Lista
    paths, sim_es = engine.run_monte_carlo(n_sims=80)
    list_items = [html.Div([html.Span(d.strftime('%Y-%m-%d')), html.Span(f" {extreme_days[d]:.2%}", 
                  style={'float':'right','color':'#e74c3c'})], style={'padding':'4px 0','borderBottom':'1px solid #111'}) 
                  for d in extreme_days.sort_index(ascending=False).index]

    return fig_dist, fig_map, list_items, safe_list_items, paths.tolist(), sim_es, False, 0


@app.callback(
    [Output('monte-carlo-graph', 'figure'), Output('animation-frame', 'data', allow_duplicate=True),
     Output('animation-interval', 'disabled', allow_duplicate=True)],
    [Input('animation-interval', 'n_intervals')],
    [State('mc-paths-store', 'data'), State('mc-es-store', 'data'), State('animation-frame', 'data')],
    prevent_initial_call=True
)
def animate_mc(n, paths, sim_es, frame):
    if paths is None: return no_update
    paths = np.array(paths)
    n_sims = paths.shape[1]
    colors = px.colors.sample_colorscale("Spectral", [i/(n_sims-1) for i in range(n_sims)])
    
    fig_mc = go.Figure()
    for i in range(n_sims):
        fig_mc.add_trace(go.Scatter(y=paths[:frame+1, i], mode='lines', 
                                   line=dict(width=1, color=colors[i]), opacity=0.6, showlegend=False))

    if frame >= 30:
        fig_mc.add_hline(y=1 + sim_es, line_dash="dash", line_color="#fff",
                         annotation_text=rf"$ES_{{0.01}} = {sim_es:.2%}$", annotation_position="bottom left",
                         annotation_font=dict(color="#fff", size=16))
        fig_mc.update_layout(title=r"$\text{Simulated Paths: } S_t = S_0 \exp\left(\sum r_i\right)$", 
                            font=LATEX_FONT, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=40, r=20, t=50, b=40))
        return fig_mc, frame, True
    
    fig_mc.update_layout(title=f"Monte Carlo Projection (Day {frame}/30)", template="plotly_dark",
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=LATEX_FONT,
                        margin=dict(l=40, r=20, t=50, b=40), xaxis=dict(range=[0, 30]), 
                        yaxis=dict(range=[np.min(paths)*0.95, np.max(paths)*1.05]))
    return fig_mc, frame + 1, False


if __name__ == "__main__":
    app.run(debug=True)