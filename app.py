import dash
from dash import dcc, html, Input, Output, State, no_update, ALL, callback_context
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd
from scipy.stats import norm, gaussian_kde
from engine import SystemicRiskEngine
import json

external_stylesheets = ['https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;700&display=swap']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
engine = SystemicRiskEngine()
engine.fetch_all_data(period="2y") # Garantir que tens dados suficientes para o período de 1 ano calmo

LATEX_FONT = dict(family="EB Garamond, serif", size=16)

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

explanation_box_style = {
    'width': '450px',
    'minWidth': '450px',
    'border': '2px solid #39FF14',
    'borderRadius': '15px',
    'padding': '25px',
    'marginLeft': '20px',
    'backgroundColor': 'rgba(57, 255, 20, 0.05)',
    'color': '#FFFFFF',
    'fontFamily': '"EB Garamond", "Times New Roman", Times, serif',
    'fontSize': '18px',
    'lineHeight': '1.6',
    'overflowY': 'auto',
    'boxSizing': 'border-box'
}

app.layout = html.Div([
    dcc.Store(id='mc-paths-store'),
    dcc.Store(id='mc-es-store'),
    dcc.Store(id='animation-frame', data=0),
    dcc.Store(id='selected-stress-date', data=None),
    dcc.Interval(id='animation-interval', interval=50, n_intervals=0, disabled=True),

    html.Div([
        html.H1("QUANT RISK TERMINAL", style={'margin': '0', 'fontSize': '18px', 'letterSpacing': '2px'}),
        dcc.Dropdown(id='main-asset-dropdown', options=options, value='AAPL', 
                     style={'width': '250px', 'color': '#000'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 
              'padding': '10px 30px', 'borderBottom': '1px solid #333', 'height': '60px'}),

    dcc.Tabs(id="tabs", value='tab-dist', children=[
        
        # TAB 1: Distribuição
        dcc.Tab(label='Distribuição', value='tab-dist', children=[
            html.Div([
                html.Div([
                    html.Div([
                        html.H3("STRESS EVENTS", style={'fontSize': '11px', 'color': '#e74c3c', 'marginBottom': '10px'}),
                        html.Div(id='extreme-dates-list', style={'height': 'calc(100% - 30px)', 'overflowY': 'auto', 'fontSize': '14px'})
                    ], style={'width': '200px', 'padding': '15px', 'borderRight': '1px solid #333', 'backgroundColor': '#0a0a0a'}),
                    html.Div([dcc.Graph(id='distribution-graph', style={'height': '100%'}, mathjax=True)], style={'flex': '1'})
                ], style={'display': 'flex', 'flex': '1', 'backgroundColor': '#000'}),
                
                html.Div([
                    html.H3("METODOLOGIA", style={'color': '#39FF14', 'marginTop': 0, 'fontSize': '16px', 'fontFamily': 'sans-serif'}),
                    dcc.Markdown(r"""
Esta secção modela a densidade empírica dos *log-returns*:

$$ r_t = \ln\left(\frac{P_t}{P_{t-1}}\right) $$

O risco de cauda é delimitado pelo **Value at Risk (VaR)** a 99%, definindo a região crítica de perdas extremas:

$$ \Pr(r_t \le -VaR_{0.99}) = 0.01 $$

O ajuste compara a distribuição histórica com uma Gaussiana teórica para evidenciar a presença de caudas pesadas (*fat tails*).
                    """, mathjax=True)
                ], style=explanation_box_style)
                
            ], style={'display': 'flex', 'height': 'calc(100vh - 104px)', 'padding': '15px', 'boxSizing': 'border-box'})
        ], style={'backgroundColor': '#111', 'color': '#888', 'border': 'none', 'padding': '10px'}, 
           selected_style={'backgroundColor': '#000', 'color': '#fff', 'borderTop': '2px solid #e74c3c', 'borderBottom': 'none', 'padding': '10px'}),

        # TAB 2: Monte Carlo
        dcc.Tab(label='Monte Carlo', value='tab-mc', children=[
            html.Div([
                html.Div([dcc.Graph(id='monte-carlo-graph', style={'height': '100%'}, mathjax=True)], style={'flex': '1', 'backgroundColor': '#000'}),
                
                html.Div([
                    html.H3("DINÂMICA ESTOCÁSTICA", style={'color': '#39FF14', 'marginTop': 0, 'fontSize': '16px', 'fontFamily': 'sans-serif'}),
                    dcc.Markdown(r"""
Projeção de caminhos gerados através de *bootstrapping* do histórico de retornos empíricos. O processo evolui segundo a dinâmica:

$$ S_T = S_0 \exp\left(\sum_{t=1}^T r_t\right) $$

A banda inferior rastreia dinamicamente o **Expected Shortfall (ES)** a 1%, quantificando o valor esperado da perda severa:

$$ ES_{0.01} = \mathbb{E}[r_t \mid r_t \le -VaR_{0.01}] $$
                    """, mathjax=True)
                ], style=explanation_box_style)
                
            ], style={'display': 'flex', 'height': 'calc(100vh - 104px)', 'padding': '15px', 'boxSizing': 'border-box'})
        ], style={'backgroundColor': '#111', 'color': '#888', 'border': 'none', 'padding': '10px'}, 
           selected_style={'backgroundColor': '#000', 'color': '#fff', 'borderTop': '2px solid #3498db', 'borderBottom': 'none', 'padding': '10px'}),

        # TAB 3: Mapa
        dcc.Tab(label='Mapa', value='tab-map', children=[
            html.Div([
                html.Div([
                    html.Div([
                        html.H3("STRESS EVENTS (Click)", style={'fontSize': '11px', 'color': '#e74c3c', 'marginBottom': '10px'}),
                        html.Div(id='extreme-dates-list-map', style={'height': 'calc(100% - 30px)', 'overflowY': 'auto', 'fontSize': '14px'})
                    ], style={'width': '200px', 'padding': '15px', 'borderRight': '1px solid #333', 'backgroundColor': '#0a0a0a'}),
                    
                    html.Div([
                        html.Div([
                            dcc.RadioItems(
                                id='map-vis-type',
                                options=[
                                    {'label': ' Δρ (Salto) ', 'value': 'delta'},
                                    {'label': ' ρ (Stress) ', 'value': 'stress'},
                                    {'label': ' ρ (Calmo) ', 'value': 'calm'}
                                ],
                                value='delta', inline=True, style={'color': '#fff', 'marginRight': '30px', 'fontSize': '16px'}
                            ),
                            html.Span("Período Calmo pré-choque: ", style={'color': '#888', 'fontSize': '14px', 'marginRight': '10px'}),
                            dcc.RadioItems(
                                id='calm-period-selector',
                                options=[
                                    {'label': ' 1 Mês ', 'value': '1M'},
                                    {'label': ' 3 Meses ', 'value': '3M'},
                                    {'label': ' 1 Ano ', 'value': '1Y'}
                                ],
                                value='3M', inline=True, style={'color': '#fff', 'fontSize': '16px'}
                            )
                        ], style={'padding': '15px', 'backgroundColor': '#111', 'borderBottom': '1px solid #333', 'display': 'flex', 'alignItems': 'center'}),
                        
                        dcc.Graph(id='contagion-map', style={'flex': '1', 'height': '100%'}, mathjax=True)
                    ], style={'flex': '1', 'display': 'flex', 'flexDirection': 'column'}),
                    
                    html.Div([
                        html.H3("SAFE HAVENS", style={'fontSize': '11px', 'color': '#2ecc71', 'marginBottom': '10px'}),
                        html.Div(id='safe-havens-list', style={'height': 'calc(100% - 30px)', 'overflowY': 'auto', 'fontSize': '14px'})
                    ], style={'width': '200px', 'padding': '15px', 'borderLeft': '1px solid #333', 'backgroundColor': '#0a0a0a'})
                ], style={'display': 'flex', 'flex': '1', 'backgroundColor': '#000'}),
                
                html.Div([
                    html.H3("RISCO SISTÉMICO", style={'color': '#39FF14', 'marginTop': 0, 'fontSize': '16px', 'fontFamily': 'sans-serif'}),
                    dcc.Markdown(r"""
Análise do contágio em eventos específicos ($\pm 15$ dias). O choque de correlação é definido por:

$$ \Delta \rho = \rho_{\text{stress}} - \rho_{\text{calm}} $$

Ativos que apresentam $\Delta \rho < 0$ atuam como refúgios (*Safe Havens*) perante quebras do mercado principal. Altera a visualização nos botões superiores.
                    """, mathjax=True)
                ], style=explanation_box_style)
                
            ], style={'display': 'flex', 'height': 'calc(100vh - 104px)', 'padding': '15px', 'boxSizing': 'border-box'})
        ], style={'backgroundColor': '#111', 'color': '#888', 'border': 'none', 'padding': '10px'}, 
           selected_style={'backgroundColor': '#000', 'color': '#fff', 'borderTop': '2px solid #2ecc71', 'borderBottom': 'none', 'padding': '10px'})

    ], style={'height': '44px', 'backgroundColor': '#111', 'borderBottom': '1px solid #333'})

], style={'backgroundColor': '#000', 'color': '#eee', 'fontFamily': '"EB Garamond", serif', 'height': '100vh', 'overflow': 'hidden'})

# Captura de Clique nos Eventos de Stress
@app.callback(
    Output('selected-stress-date', 'data'),
    [Input({'type': 'stress-date-btn', 'date': ALL}, 'n_clicks')],
    [State({'type': 'stress-date-btn', 'date': ALL}, 'id')]
)
def update_selected_date(n_clicks, ids):
    ctx = callback_context
    if not ctx.triggered: return no_update
    prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if 'date' in prop_id:
        return json.loads(prop_id)['date']
    return no_update

# Análise Principal (Distribuição, Monte Carlo e População das Listas de Stress)
@app.callback(
    [Output('distribution-graph', 'figure'),
     Output('extreme-dates-list', 'children'), Output('extreme-dates-list-map', 'children'),
     Output('mc-paths-store', 'data'), Output('mc-es-store', 'data'), 
     Output('animation-interval', 'disabled'), Output('animation-frame', 'data')],
    [Input('main-asset-dropdown', 'value')]
)
def setup_analysis(selected_ticker):
    engine.set_main_asset(selected_ticker)
    extreme_days, var_limit, filtered_returns = engine.get_extreme_events(months=12)
    
    counts, bin_edges = np.histogram(filtered_returns, bins=80, density=True)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    
    fig_dist = go.Figure()
    fig_dist.add_trace(go.Bar(x=bin_centers[bin_centers > var_limit], y=counts[bin_centers > var_limit], 
                              marker_color='#333', name='Normal', showlegend=False))
    fig_dist.add_trace(go.Bar(x=bin_centers[bin_centers <= var_limit], y=counts[bin_centers <= var_limit], 
                              marker_color='#c0392b', name='Tail Stress', showlegend=False))
    
    x_range = np.linspace(filtered_returns.min(), filtered_returns.max(), 250)
    fig_dist.add_trace(go.Scatter(x=x_range, y=gaussian_kde(filtered_returns)(x_range), 
                                  name='KDE', line=dict(color='#3498db', width=2.5)))
    fig_dist.add_trace(go.Scatter(x=x_range, y=norm.pdf(x_range, filtered_returns.mean(), filtered_returns.std()), 
                                  name='Gaussian', line=dict(color='#777', dash='dash', width=1.5)))
    
    fig_dist.add_vline(x=var_limit, line_dash="dash", line_color="#e74c3c")
    fig_dist.add_annotation(x=var_limit, y=0.95, yref="paper", text=rf"$VaR_{{99\%}} = {var_limit:.2%}$",
                            showarrow=False, font=dict(color="#e74c3c", size=16), bgcolor="rgba(0,0,0,0.5)")

    fig_dist.update_layout(title=rf"$\text{{Return Distribution: }} \text{{{selected_ticker}}}$", 
                          font=LATEX_FONT, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', 
                          plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=40, r=20, t=50, b=40), xaxis_title=r"$\Delta \ln(P_t)$")

    list_items = [html.Div([html.Span(d.strftime('%Y-%m-%d')), html.Span(f" {extreme_days[d]:.2%}", 
                  style={'float':'right','color':'#e74c3c'})], style={'padding':'4px 0','borderBottom':'1px solid #111'}) 
                  for d in extreme_days.sort_index(ascending=False).index]

    list_items_clickable = [
        html.Button(
            [html.Span(d.strftime('%Y-%m-%d')), html.Span(f" {extreme_days[d]:.2%}", style={'float':'right','color':'#e74c3c'})],
            id={'type': 'stress-date-btn', 'date': d.strftime('%Y-%m-%d')},
            style={'width': '100%', 'backgroundColor': 'transparent', 'border': 'none', 'color': '#eee', 'textAlign': 'left', 'cursor': 'pointer', 'padding': '6px 0', 'borderBottom': '1px solid #222', 'fontFamily': 'inherit', 'fontSize': '14px'}
        ) for d in extreme_days.sort_index(ascending=False).index
    ]

    paths, sim_es = engine.run_monte_carlo(n_sims=80)
    return fig_dist, list_items, list_items_clickable, paths.tolist(), sim_es, False, 0


# Atualização do Mapa Interativo
@app.callback(
    [Output('contagion-map', 'figure'), Output('safe-havens-list', 'children')],
    [Input('selected-stress-date', 'data'), Input('map-vis-type', 'value'), 
     Input('calm-period-selector', 'value'), Input('main-asset-dropdown', 'value')]
)
def render_map(selected_date, vis_type, calm_period, main_ticker):
    engine.set_main_asset(main_ticker)
    extreme_days, _, _ = engine.get_extreme_events(months=12)
    
    # Se não houver data selecionada, assume a queda mais recente
    target_date = selected_date if selected_date else (extreme_days.index[-1].strftime('%Y-%m-%d') if not extreme_days.empty else None)
    
    if not target_date:
        return go.Figure(), [html.Div("Dados insuficientes.")]

    country_assets = engine.assets_df[engine.assets_df['sector'] == 'Country']
    map_rows = []
    
    for _, row in country_assets.iterrows():
        metrics = engine.get_event_contagion(row['ticker'], target_date, calm_period)
        if metrics:
            delta_rho, stress_rho, calm_rho = metrics
            coords = COUNTRY_COORDS.get(row['country'])
            if coords:
                val = delta_rho if vis_type == 'delta' else (stress_rho if vis_type == 'stress' else calm_rho)
                map_rows.append({'Val': val, 'Delta': delta_rho, 'Lat': coords[0], 'Lon': coords[1], 'Name': row['name']})
    
    if not map_rows: return go.Figure(), [html.Div("Dados insuficientes.")]
    
    df_map = pd.DataFrame(map_rows)
    
    title_map = {
        'delta': rf"$\text{{Contágio no Evento ({target_date}): }} \Delta \rho$",
        'stress': rf"$\text{{Correlação de Stress ({target_date} }} \pm 15 \text{{ dias)}}$",
        'calm': rf"$\text{{Correlação Calma ({calm_period} pré-choque)}}$"
    }

    fig_map = go.Figure(go.Scattergeo(
        lat=df_map['Lat'], lon=df_map['Lon'],
        marker=dict(
            size=15, 
            color=df_map['Val'], colorscale='RdBu_r', cmid=0, cmin=-1, cmax=1, # <--- CORRIGIDO AQUI
            showscale=True, colorbar=dict(title=vis_type.upper(), thickness=15),
            line=dict(width=1, color='white')
        ),
        text=[f"{n}<br>Valor: {v:.2f}" for n, v in zip(df_map['Name'], df_map['Val'])]
    ))
    fig_map.update_geos(projection_type="natural earth", showland=True, landcolor="#080808", 
                        oceancolor="#000", showcountries=True, countrycolor="#222", bgcolor="rgba(0,0,0,0)")
    fig_map.update_layout(title=title_map[vis_type], font=LATEX_FONT, template="plotly_dark", 
                          margin=dict(l=10, r=10, t=50, b=10), paper_bgcolor='rgba(0,0,0,0)')

    safe_havens = sorted([row for row in map_rows if row['Delta'] < 0], key=lambda x: x['Delta'])
    safe_list_items = [
        html.Div([
            html.Span(sh['Name']), 
            html.Span("{:.2f}".format(sh['Delta']), style={'float':'right','color':'#2ecc71'})
        ], style={'padding':'4px 0','borderBottom':'1px solid #111'}) 
        for sh in safe_havens
    ]
    if not safe_list_items: safe_list_items = [html.Div("Sem safe havens.", style={'color': '#777'})]

    return fig_map, safe_list_items


# Animação Monte Carlo
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
    current_paths = paths[:frame+1, :]
    mean_path = np.mean(current_paths, axis=1)
    
    lower_bound = np.zeros(frame + 1)
    upper_bound = np.zeros(frame + 1)
    for t in range(frame + 1):
        step_vals = current_paths[t, :]
        var_down = np.percentile(step_vals, 1)
        lower_bound[t] = np.mean(step_vals[step_vals <= var_down])
        var_up = np.percentile(step_vals, 99)
        upper_bound[t] = np.mean(step_vals[step_vals >= var_up])
        
    x_vals = np.arange(frame + 1)
    base_line = np.ones_like(x_vals) 
    
    fig_mc = go.Figure()
    fig_mc.add_trace(go.Scatter(x=x_vals, y=base_line, mode='lines', line=dict(width=0), showlegend=False))
    fig_mc.add_trace(go.Scatter(
        x=x_vals, y=lower_bound, mode='lines', fill='tonexty',
        fillgradient=dict(type='vertical', colorscale=[[0, '#FF0000'], [1, 'rgba(0,0,0,0)']]),
        line=dict(width=1, color='#FF0000', shape='spline'), showlegend=False
    ))

    fig_mc.add_trace(go.Scatter(x=x_vals, y=base_line, mode='lines', line=dict(width=0), showlegend=False))
    fig_mc.add_trace(go.Scatter(
        x=x_vals, y=upper_bound, mode='lines', fill='tonexty',
        fillgradient=dict(type='vertical', colorscale=[[0, 'rgba(0,0,0,0)'], [1, '#39FF14']]),
        line=dict(width=1, color='#39FF14', shape='spline'), showlegend=False
    ))

    fig_mc.add_trace(go.Scatter(x=x_vals, y=mean_path, mode='lines', line=dict(width=2, color='#FFFFFF', shape='spline'), showlegend=False))

    if frame >= 30:
        final_es_ret = lower_bound[-1] - 1
        fig_mc.add_hline(y=lower_bound[-1], line_dash="dash", line_color="#FF0000",
                         annotation_text=rf"$ES_{{1\%}} = {final_es_ret:.2%}$", annotation_position="bottom left",
                         annotation_font=dict(color="#FF0000", size=16))
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