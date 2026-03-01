import dash
from dash import dcc, html, Input, Output, State, no_update
import plotly.graph_objects as go
import numpy as np
from scipy.stats import norm, gaussian_kde
import plotly.express as px
from engine import SystemicRiskEngine

app = dash.Dash(__name__)
engine = SystemicRiskEngine()
engine.fetch_all_data(period="2y")

stocks_only = engine.assets_df[engine.assets_df['sector'] != 'Country']
options = [{'label': f"{r['name']} ({r['ticker']})", 'value': r['ticker']} for _, r in stocks_only.iterrows()]

app.layout = html.Div([
    # Memória da App
    dcc.Store(id='mc-paths-store'),
    dcc.Store(id='mc-es-store'), # Guarda o valor do ES simulado
    dcc.Store(id='animation-frame', data=0),
    dcc.Interval(id='animation-interval', interval=50, n_intervals=0, disabled=True),

    # Header
    html.Div([
        html.H1("QUANT RISK TERMINAL", style={'margin': '0', 'fontSize': '20px', 'letterSpacing': '2px'}),
        dcc.Dropdown(id='main-asset-dropdown', options=options, value='AAPL', 
                     style={'width': '250px', 'backgroundColor': '#1e1e1e', 'color': '#000'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '15px 30px', 'backgroundColor': '#000', 'borderBottom': '1px solid #333', 'color': '#fff'}),

    html.Div([
        # Coluna Esquerda: Histórico
        html.Div([
            html.H3("STRESS EVENTS (24M)", style={'fontSize': '12px', 'color': '#e74c3c'}),
            html.Div(id='extreme-dates-list', style={'maxHeight': '80vh', 'overflowY': 'auto'})
        ], style={'width': '200px', 'padding': '20px', 'borderRight': '1px solid #333'}),

        # Gráficos Horizontais
        html.Div([
            dcc.Graph(id='distribution-graph', style={'flex': '1'}),
            dcc.Graph(id='monte-carlo-graph', style={'flex': '1'})
        ], style={'display': 'flex', 'flex': '1', 'padding': '10px', 'gap': '15px'})
    ], style={'display': 'flex', 'backgroundColor': '#000', 'minHeight': '100vh'})
], style={'backgroundColor': '#000', 'color': '#eee', 'fontFamily': 'monospace'})

# CALLBACK 1: Setup inicial
@app.callback(
    [Output('distribution-graph', 'figure'),
     Output('extreme-dates-list', 'children'),
     Output('mc-paths-store', 'data'),
     Output('mc-es-store', 'data'), # Output para o ES
     Output('animation-interval', 'disabled'),
     Output('animation-frame', 'data')],
    [Input('main-asset-dropdown', 'value')]
)
def setup_analysis(selected_ticker):
    engine.set_main_asset(selected_ticker)
    extreme_days, var_limit, filtered_returns = engine.get_extreme_events(months=24)
    es_hist = engine.calculate_expected_shortfall(filtered_returns)

    # 1. Gráfico de Distribuição
    counts, bin_edges = np.histogram(filtered_returns, bins=80, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    is_extreme = bin_centers <= var_limit
    fig_dist = go.Figure()
    fig_dist.add_trace(go.Bar(x=bin_centers[~is_extreme], y=counts[~is_extreme], name='Normal', marker_color='#333'))
    fig_dist.add_trace(go.Bar(x=bin_centers[is_extreme], y=counts[is_extreme], name='Stress', marker_color='#c0392b'))
    
    x_range = np.linspace(filtered_returns.min(), filtered_returns.max(), 200)
    fig_dist.add_trace(go.Scatter(x=x_range, y=gaussian_kde(filtered_returns)(x_range), name='KDE', line=dict(color='#3498db', width=2)))
    fig_dist.add_trace(go.Scatter(x=x_range, y=norm.pdf(x_range, filtered_returns.mean(), filtered_returns.std()), name='Gaussian', line=dict(color='#777', dash='dash')))
    
    fig_dist.update_layout(title=f"DISTRIBUTION: {selected_ticker}", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')

    # 2. Setup Monte Carlo
    paths, sim_es = engine.run_monte_carlo(days=30, n_sims=50)
    
    list_items = [html.Div([html.Span(d.strftime('%Y-%m-%d')), html.Span(f" {extreme_days[d]:.2%}", style={'float':'right','color':'#e74c3c'})], style={'padding':'6px 0','borderBottom':'1px solid #111'}) for d in extreme_days.sort_index(ascending=False).index]

    return fig_dist, list_items, paths.tolist(), sim_es, False, 0

# CALLBACK 2: Animação e Linha de ES no final
@app.callback(
    [Output('monte-carlo-graph', 'figure'),
     Output('animation-frame', 'data', allow_duplicate=True),
     Output('animation-interval', 'disabled', allow_duplicate=True)],
    [Input('animation-interval', 'n_intervals')],
    [State('mc-paths-store', 'data'), 
     State('mc-es-store', 'data'),
     State('animation-frame', 'data')],
    prevent_initial_call=True
)
def animate_mc(n, paths, sim_es, frame):
    if paths is None: return no_update
    paths = np.array(paths)
    n_sims = paths.shape[1]
    
    # Gera um gradiente de cores estilo "rainbow" baseado na escala Spectral
    colors = px.colors.sample_colorscale("Spectral", [i/(n_sims - 1) for i in range(n_sims)])
    
    fig_mc = go.Figure()
    
    for i in range(n_sims):
        fig_mc.add_trace(go.Scatter(
            y=paths[:frame, i], 
            mode='lines', 
            line=dict(width=1.2, color=colors[i]), 
            opacity=0.7,
            showlegend=False
        ))

    if frame >= 30:
        fig_mc.add_hline(
            y=1 + sim_es, 
            line_color="#ffffff", # Branco para contrastar com o arco-íris
            line_width=2, 
            line_dash="dash",
            annotation_text=f"SIMULATED ES: {sim_es:.2%}", 
            annotation_font_color="#ffffff",
            annotation_position="bottom left"
        )
        fig_mc.update_layout(title="PROJECTION COMPLETE", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        return fig_mc, frame, True
    
    fig_mc.update_layout(
        title=f"SIMULATING PATHS (DAY {frame}/30)", 
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(range=[0, 30], gridcolor='#111'), 
        yaxis=dict(range=[np.min(paths)*0.95, np.max(paths)*1.05], gridcolor='#111')
    )

    return fig_mc, frame + 1, False

if __name__ == "__main__":
    app.run(debug=True)