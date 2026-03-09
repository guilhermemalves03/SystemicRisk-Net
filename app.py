import dash
from dash import dcc, html, Input, Output, State, no_update, ALL, callback_context
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from scipy.stats import norm, gaussian_kde
from engine import SystemicRiskEngine
import json
from plotly.colors import sample_colorscale

external_stylesheets = ['https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;700&display=swap']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
engine = SystemicRiskEngine()
engine.fetch_all_data(period="2y")

LATEX_FONT = dict(family="EB Garamond, serif", size=16)

COUNTRY_COORDS = {
    'USA': [37.0, -95.0], 'Germany': [51.0, 10.0], 'Japan': [36.0, 138.0],
    'China': [35.0, 103.0], 'Australia': [-25.0, 133.0], 'Brazil': [-14.0, -51.0],
    'Italy': [41.0, 12.0], 'Malaysia': [4.0, 109.0], 'Singapore': [1.3, 103.8],
    'Canada': [56.0, -106.0], 'France': [46.0, 2.0], 'Spain': [40.0, -3.0],
    'Hong Kong': [22.3, 114.1], 'Sweden': [60.0, 18.0], 'Netherlands': [52.0, 5.0],
    'UK': [55.0, -3.0], 'Switzerland': [46.8, 8.2], 'South Korea': [35.9, 127.7],
    'Taiwan': [23.6, 120.9], 'India': [20.5, 78.9], 'Mexico': [23.6, -102.5],
    'South Africa': [-30.5, 22.9], 'Saudi Arabia': [23.8, 45.0], 'Turkey': [38.9, 35.2],
    'Poland': [51.9, 19.1], 'Indonesia': [-0.7, 113.9], 'Thailand': [15.8, 100.9],
    'Philippines': [12.8, 121.7], 'Vietnam': [14.0, 108.2], 'Chile': [-35.6, -71.5],
    'Peru': [-9.1, -75.0], 'Colombia': [4.5, -74.0], 'Argentina': [-38.4, -63.6],
    'Greece': [39.0, 22.0], 'Israel': [31.0, 34.8], 'Egypt': [26.8, 30.8],
    'Austria': [47.5, 14.5], 'Belgium': [50.5, 4.5], 'Denmark': [56.0, 10.0],
    'Finland': [61.9, 25.7], 'Ireland': [53.1, -7.7], 'Norway': [60.5, 8.5],
    'Portugal': [39.4, -8.2], 'New Zealand': [-40.9, 174.8], 'UAE': [23.4, 53.8],
    'Qatar': [25.3, 51.5], 'Nigeria': [9.1, 8.6], 'Pakistan': [30.4, 69.3],
    'Kenya': [-1.3, 36.8], 'Morocco': [31.8, -7.1]
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
    'boxSizing': 'border-box'
}

def calculate_dorling_layout(lons, lats, radii, max_iter=300):
    x, y, r = np.array(lons, dtype=float), np.array(lats, dtype=float), np.array(radii, dtype=float)
    for _ in range(max_iter):
        max_overlap = 0
        for i in range(len(x)):
            for j in range(i+1, len(x)):
                dx, dy = x[i] - x[j], y[i] - y[j]
                dist = np.sqrt(dx**2 + dy**2)
                min_dist = r[i] + r[j] + 1.0 
                
                if dist < min_dist:
                    overlap = min_dist - dist
                    max_overlap = max(max_overlap, overlap)
                    if dist == 0:
                        dx, dy = np.random.randn(), np.random.randn()
                        dist = np.sqrt(dx**2 + dy**2)
                    
                    push_x = (dx / dist) * overlap * 0.5
                    push_y = (dy / dist) * overlap * 0.5
                    x[i] += push_x
                    y[i] += push_y
                    x[j] -= push_x
                    y[j] -= push_y
                    
        x += (np.array(lons) - x) * 0.05
        y += (np.array(lats) - y) * 0.05
        if max_overlap < 0.1: break
    return x, y

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
        dcc.Tab(label='Distribution', value='tab-dist', children=[
            html.Div([
                html.Div([
                    html.Div([
                        html.H3("STRESS EVENTS", style={'fontSize': '11px', 'color': '#e74c3c', 'marginBottom': '10px'}),
                        html.Div(id='extreme-dates-list', style={'fontSize': '14px', 'maxHeight': '800px', 'overflowY': 'auto', 'paddingRight': '5px'})
                    ], style={'width': '200px', 'padding': '15px', 'borderRight': '1px solid #333', 'backgroundColor': '#0a0a0a'}),
                    
                    html.Div([
                        dcc.Graph(id='distribution-graph', style={'flex': '1', 'minHeight': '400px'}, mathjax=True),
                        dcc.Graph(id='ridgeline-graph', style={'flex': '1', 'minHeight': '500px', 'borderTop': '1px solid #222'}, mathjax=True)
                    ], style={'flex': '1', 'display': 'flex', 'flexDirection': 'column'})
                ], style={'display': 'flex', 'flex': '1', 'backgroundColor': '#000'}),
                
                html.Div([
                    html.H3("METHODOLOGY", style={'color': '#39FF14', 'marginTop': 0, 'fontSize': '16px', 'fontFamily': 'sans-serif'}),
                    dcc.Markdown(r"""
This section models the empirical density of *log-returns*:

$$r_t = \ln\left(\frac{P_t}{P_{t-1}}\right)$$

The tail risk is bounded by the **Value at Risk (VaR)** at 99%, defining the critical region of extreme losses:

$$\Pr(r_t \le -VaR_{0.99}) = 0.01$$

The Ridgeline Plot models the density KDE over the last 12 months, split by quarters.
                    """, mathjax=True)
                ], style=explanation_box_style)
                
            ], style={'display': 'flex', 'minHeight': 'calc(100vh - 104px)', 'padding': '15px', 'boxSizing': 'border-box'})
        ], style={'backgroundColor': '#111', 'color': '#888', 'border': 'none', 'padding': '10px'}, 
           selected_style={'backgroundColor': '#000', 'color': '#fff', 'borderTop': '2px solid #e74c3c', 'borderBottom': 'none', 'padding': '10px'}),

        dcc.Tab(label='Monte Carlo', value='tab-mc', children=[
            html.Div([
                html.Div([
                    dcc.Graph(id='monte-carlo-graph', style={'height': '400px'}, mathjax=True),
                    html.Div(id='mc-stats-box', style={'flex': '1', 'padding': '20px', 'backgroundColor': '#0a0a0a', 'borderTop': '1px solid #222', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-evenly'}, children=[
                        html.Div(dcc.Markdown(id='stat-max', mathjax=True, style={'margin': 0}), style={'color': '#2ecc71', 'border': '1px solid #2ecc71', 'padding': '10px 25px', 'borderRadius': '10px', 'backgroundColor': 'rgba(46, 204, 113, 0.05)', 'fontSize': '18px'}),
                        html.Div(dcc.Markdown(id='stat-mean', mathjax=True, style={'margin': 0}), style={'color': '#f1c40f', 'border': '1px solid #f1c40f', 'padding': '10px 25px', 'borderRadius': '10px', 'backgroundColor': 'rgba(241, 196, 15, 0.05)', 'fontSize': '18px'}),
                        html.Div(dcc.Markdown(id='stat-min', mathjax=True, style={'margin': 0}), style={'color': '#e74c3c', 'border': '1px solid #e74c3c', 'padding': '10px 25px', 'borderRadius': '10px', 'backgroundColor': 'rgba(231, 76, 60, 0.05)', 'fontSize': '18px'})
                    ])
                ], style={'flex': '1', 'backgroundColor': '#000', 'display': 'flex', 'flexDirection': 'column'}),
                
                html.Div([
                    html.H3("STOCHASTIC DYNAMICS", style={'color': '#39FF14', 'marginTop': 0, 'fontSize': '16px', 'fontFamily': 'sans-serif'}),
                    dcc.Markdown(r"""
Projection of paths generated through *bootstrapping* the historical empirical returns. The process evolves according to the dynamics:

$$S_T = S_0 \exp\left(\sum_{t=1}^T r_t\right)$$

The lower band dynamically tracks the **Expected Shortfall (ES)** at 1%, quantifying the expected value of severe loss:

$$ES_{0.01} = \mathbb{E}[r_t \mid r_t \le -VaR_{0.01}]$$
                    """, mathjax=True)
                ], style=explanation_box_style)
                
            ], style={'display': 'flex', 'minHeight': 'calc(100vh - 104px)', 'padding': '15px', 'boxSizing': 'border-box'})
        ], style={'backgroundColor': '#111', 'color': '#888', 'border': 'none', 'padding': '10px'}, 
           selected_style={'backgroundColor': '#000', 'color': '#fff', 'borderTop': '2px solid #3498db', 'borderBottom': 'none', 'padding': '10px'}),

        dcc.Tab(label='Map', value='tab-map', children=[
            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            html.H3("STRESS EVENTS (Click)", style={'fontSize': '11px', 'color': '#e74c3c', 'marginBottom': '10px'}),
                            html.Div(id='extreme-dates-list-map', style={'fontSize': '14px', 'maxHeight': '320px', 'overflowY': 'auto', 'paddingRight': '5px'})
                        ], style={'marginBottom': '20px'}),
                        
                        html.Hr(style={'borderColor': '#333', 'margin': '0 0 15px 0', 'width': '100%'}),
                        
                        html.Div([
                            html.H3("SAFE HAVENS", style={'fontSize': '11px', 'color': '#2ecc71', 'marginBottom': '10px'}),
                            html.Div(id='safe-havens-list', style={'fontSize': '14px', 'maxHeight': '320px', 'overflowY': 'auto', 'paddingRight': '5px'})
                        ])
                    ], style={'width': '250px', 'padding': '15px', 'borderRight': '1px solid #333', 'backgroundColor': '#0a0a0a'}),
                    
                    html.Div([
                        html.Div([
                            dcc.RadioItems(
                                id='map-vis-type',
                                className='custom-radio',
                                options=[
                                    {'label': ' Δρ (Shock) ', 'value': 'delta'},
                                    {'label': ' ρ (Stress) ', 'value': 'stress'},
                                    {'label': ' ρ (Calm) ', 'value': 'calm'}
                                ],
                                value='delta', inline=True, style={'color': '#fff', 'marginRight': '30px', 'fontSize': '15px'},
                                labelStyle={'cursor': 'pointer', 'marginRight': '10px', 'backgroundColor': '#2c3e50', 'padding': '6px 12px', 'borderRadius': '4px', 'border': '1px solid #34495e'}
                            ),
                            html.Span("Pre-shock Calm Period: ", style={'color': '#888', 'fontSize': '14px', 'marginRight': '10px'}),
                            dcc.RadioItems(
                                id='calm-period-selector',
                                className='custom-radio',
                                options=[
                                    {'label': ' 1 Month ', 'value': '1M'},
                                    {'label': ' 3 Months ', 'value': '3M'},
                                    {'label': ' 1 Year ', 'value': '1Y'}
                                ],
                                value='3M', inline=True, style={'color': '#fff', 'fontSize': '15px'},
                                labelStyle={'cursor': 'pointer', 'marginRight': '10px', 'backgroundColor': '#2c3e50', 'padding': '6px 12px', 'borderRadius': '4px', 'border': '1px solid #34495e'}
                            )
                        ], style={'padding': '15px', 'backgroundColor': '#111', 'borderBottom': '1px solid #333', 'display': 'flex', 'alignItems': 'center'}),
                        
                        dcc.Graph(id='contagion-map', style={'flex': '1', 'minHeight': '500px'}, mathjax=True)
                    ], style={'flex': '1', 'display': 'flex', 'flexDirection': 'column'}),
                ], style={'display': 'flex', 'minHeight': '600px', 'backgroundColor': '#000'}),
                
                html.Div("↓ SCROLL DOWN FOR MORE ↓", className='scroll-indicator'),

                html.Div([
                    html.H3("SYSTEMIC RISK", style={'color': '#39FF14', 'marginTop': 0, 'fontSize': '16px', 'fontFamily': 'sans-serif'}),
                    dcc.Markdown(r"""
Dorling Cartogram (Circles = Trading Volume).
Contagion analysis on specific events ($\pm 15$ days). The correlation shock is defined by:

$$\Delta \rho = \rho_{\text{stress}} - \rho_{\text{calm}}$$

Assets that exhibit $\Delta \rho < 0$ **and** $\rho_{\text{stress}} \le 0$ act as true *Safe Havens* during main market crashes.
                    """, mathjax=True)
                ], style=dict(explanation_box_style, **{
                    'width': '100%', 
                    'minWidth': '100%', 
                    'marginLeft': '0', 
                    'marginTop': '20px', 
                    'height': 'auto'
                }))
                
            ], style={'display': 'flex', 'flexDirection': 'column', 'minHeight': 'calc(100vh - 104px)', 'padding': '15px', 'boxSizing': 'border-box'})
        ], style={'backgroundColor': '#111', 'color': '#888', 'border': 'none', 'padding': '10px'}, 
           selected_style={'backgroundColor': '#000', 'color': '#fff', 'borderTop': '2px solid #2ecc71', 'borderBottom': 'none', 'padding': '10px'})

    ], style={'height': '44px', 'backgroundColor': '#111', 'borderBottom': '1px solid #333'}),

    html.Div(id='volatility-modal', style={'display': 'none', 'position': 'fixed', 'zIndex': '1000', 'left': '0', 'top': '0', 'width': '100%', 'height': '100%', 'backgroundColor': 'rgba(0,0,0,0.8)'}, children=[
        html.Div(style={'position': 'relative', 'margin': '10% auto', 'padding': '20px', 'width': '60%', 'backgroundColor': '#111', 'borderRadius': '10px', 'border': '1px solid #333'}, children=[
            html.Button('✖', id='close-modal-btn', style={'position': 'absolute', 'right': '15px', 'top': '15px', 'backgroundColor': 'transparent', 'color': '#e74c3c', 'border': 'none', 'fontSize': '20px', 'cursor': 'pointer', 'zIndex': '10'}),
            dcc.Graph(id='volatility-graph')
        ])
    ])

], style={'backgroundColor': '#000', 'color': '#eee', 'fontFamily': '"EB Garamond", serif', 'minHeight': '100vh'})


@app.callback(
    [Output('volatility-modal', 'style'), Output('volatility-graph', 'figure')],
    [Input('contagion-map', 'clickData'), Input('close-modal-btn', 'n_clicks')],
    [State('volatility-modal', 'style'), State('selected-stress-date', 'data')]
)
def toggle_modal(clickData, close_clicks, modal_style, selected_date):
    ctx = callback_context
    if not ctx.triggered:
        return no_update, no_update
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'close-modal-btn':
        modal_style['display'] = 'none'
        return modal_style, go.Figure()
        
    if trigger_id == 'contagion-map' and clickData:
        try:
            ticker = clickData['points'][0]['customdata']
            if isinstance(ticker, list):
                ticker = ticker[0]
        except KeyError:
            return no_update, no_update
            
        vol_data = engine.get_realized_volatility(ticker)
        if vol_data is None: 
            return no_update, no_update
        
        fig = go.Figure(go.Scatter(x=vol_data.index, y=vol_data.values, mode='lines', line=dict(color='#e74c3c', width=2)))
        
        if selected_date:
            fig.add_vline(x=selected_date, line_dash="dash", line_color="#39FF14")
            fig.add_annotation(
                x=selected_date, 
                y=0.95, 
                yref="paper", 
                text="Stress Event", 
                showarrow=False, 
                xanchor="left",
                font=dict(color="#39FF14", size=14)
            )

        fig.update_layout(
            title=rf"$\text{{Annualized Realized Volatility (21d) - }} {ticker}$", 
            template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=20, t=50, b=40),
            font=LATEX_FONT,
            yaxis_tickformat='.2%'
        )
        
        modal_style['display'] = 'block'
        return modal_style, fig
        
    return no_update, no_update


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

@app.callback(
    [Output('animation-interval', 'disabled', allow_duplicate=True),
     Output('animation-frame', 'data', allow_duplicate=True)],
    [Input('tabs', 'value')],
    prevent_initial_call=True
)
def auto_play_mc(tab_value):
    if tab_value == 'tab-mc':
        return False, 0 
    return no_update, no_update

@app.callback(
    [Output('distribution-graph', 'figure'),
     Output('ridgeline-graph', 'figure'),
     Output('extreme-dates-list', 'children'), Output('extreme-dates-list-map', 'children'),
     Output('mc-paths-store', 'data'), Output('mc-es-store', 'data'), 
     Output('animation-interval', 'disabled'), Output('animation-frame', 'data')],
    [Input('main-asset-dropdown', 'value')]
)
def setup_analysis(selected_ticker):
    engine.set_main_asset(selected_ticker)
    extreme_days, var_limit, filtered_returns = engine.get_extreme_events(months=12)
    
    # --- 1. Static Distribution Graph ---
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
    fig_dist.add_annotation(x=var_limit, y=0.95, yref="paper", text=rf"$VaR_{{99\%}} = {var_limit*100:.2f}\%$",
                            showarrow=False, font=dict(color="#e74c3c", size=16), bgcolor="rgba(0,0,0,0.5)")

    fig_dist.update_layout(title=rf"$\text{{Aggregated Return Distribution: }} \text{{{selected_ticker}}}$", 
                          font=LATEX_FONT, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', 
                          plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=40, r=20, t=50, b=10), xaxis_title=r"$\Delta \ln(P_t)$")

    # --- 2. Classic 2D Ridgeline Plot (Joyplot Reference) ---
    fig_ridge = go.Figure()
    df_returns = pd.DataFrame({'return': filtered_returns})
    df_returns['Month'] = df_returns.index.to_period('M')
    
    unique_months = df_returns['Month'].unique()[-12:] 
    
    # Escala de cores para distinguir
    colors = sample_colorscale('Aggrnyl', np.linspace(0, 1, len(unique_months)))
    
    for i, month in enumerate(unique_months):
        month_data = df_returns[df_returns['Month'] == month]['return']
        if len(month_data) > 2:
            m_ret = month_data.mean()
            q_str = f"Q{month.quarter}"
            month_label = f"{month.strftime('%b %Y')} ({q_str})"
            
            # Adiciona o gráfico de violino horizontal com largura > 1 para forçar a sobreposição
            fig_ridge.add_trace(go.Violin(
                x=month_data,
                y=[month_label] * len(month_data),
                name=month_label,
                line_color='white',
                line_width=1,
                fillcolor=colors[i],
                opacity=0.9,
                side='positive',
                width=3.5,  # Controla o quanto se sobrepõem
                orientation='h',
                points=False,
                showlegend=False
            ))
            
            # Adiciona a caixa com a média flutuante
            fig_ridge.add_annotation(
                x=m_ret,
                y=month_label,
                text=f"μ: {m_ret*100:.2f}%",
                showarrow=False,
                yshift=18, # Sobe a caixa ligeiramente acima da base
                bgcolor="rgba(0,0,0,0.7)",
                bordercolor=colors[i],
                font=dict(color="white", size=11, family="sans-serif")
            )

    fig_ridge.update_layout(
        title=rf"$\text{{Ridgeline Plot (Last 12 Months)}}$",
        xaxis_title=r"$\Delta \ln(P_t)$",
        font=LATEX_FONT, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=20, t=30, b=40),
        violingap=0, violingroupgap=0, violinmode='overlay' # Crucial para o efeito cascata
    )

    # --- 3. Extra Setup Logic ---
    list_items = [html.Div([html.Span(d.strftime('%Y-%m-%d')), html.Span(f" {extreme_days[d]:.2%}", 
                  style={'float':'right','color':'#e74c3c'})], style={'padding':'4px 0','borderBottom':'1px solid #111'}) 
                  for d in extreme_days.sort_index(ascending=False).index]

    list_items_clickable = [
        html.Button(
            [html.Span(d.strftime('%Y-%m-%d'), style={'fontWeight': 'bold'}), html.Span(f" {extreme_days[d]:.2%}", style={'float':'right','color':'#ff6b6b'})],
            id={'type': 'stress-date-btn', 'date': d.strftime('%Y-%m-%d')},
            style={'width': '100%', 'backgroundColor': '#1e1e1e', 'border': '1px solid #444', 'borderRadius': '5px', 'color': '#eee', 'textAlign': 'left', 'cursor': 'pointer', 'padding': '8px 10px', 'marginBottom': '6px', 'fontFamily': 'inherit', 'fontSize': '14px'}
        ) for d in extreme_days.sort_index(ascending=False).index
    ]

    paths, sim_es = engine.run_monte_carlo(n_sims=80)
    return fig_dist, fig_ridge, list_items, list_items_clickable, paths.tolist(), sim_es, False, 0

@app.callback(
    [Output('contagion-map', 'figure'), Output('safe-havens-list', 'children')],
    [Input('selected-stress-date', 'data'), Input('map-vis-type', 'value'), 
     Input('calm-period-selector', 'value'), Input('main-asset-dropdown', 'value')]
)
def render_map(selected_date, vis_type, calm_period, main_ticker):
    engine.set_main_asset(main_ticker)
    extreme_days, _, _ = engine.get_extreme_events(months=12)
    target_date = selected_date if selected_date else (extreme_days.index[-1].strftime('%Y-%m-%d') if not extreme_days.empty else None)
    
    if not target_date:
        return go.Figure(), [html.Div("Insufficient data.")]

    country_assets = engine.assets_df[engine.assets_df['sector'] == 'Country']
    map_rows = []
    
    for _, row in country_assets.iterrows():
        metrics = engine.get_event_contagion(row['ticker'], target_date, calm_period)
        if metrics:
            (delta_rho, stress_rho, calm_rho), (delta_vol, stress_vol, calm_vol) = metrics
            coords = COUNTRY_COORDS.get(row['country'])
            if coords:
                val = delta_rho if vis_type == 'delta' else (stress_rho if vis_type == 'stress' else calm_rho)
                vol = abs(delta_vol) if vis_type == 'delta' else (stress_vol if vis_type == 'stress' else calm_vol)
                map_rows.append({
                    'Val': val, 
                    'Vol': vol, 
                    'Delta': delta_rho,
                    'Stress': stress_rho,
                    'Lat': coords[0], 
                    'Lon': coords[1], 
                    'Name': row['name'], 
                    'Country': row['country'],
                    'Ticker': row['ticker']
                })
    
    if not map_rows: return go.Figure(), [html.Div("Insufficient data.")]
    
    v_vals = np.array([row['Vol'] for row in map_rows])
    v_norm = (v_vals - np.min(v_vals)) / (np.max(v_vals) - np.min(v_vals) + 1e-9)
    radii = 3.5 + np.sqrt(v_norm) * 14.0 
    
    lons, lats = [row['Lon'] for row in map_rows], [row['Lat'] for row in map_rows]
    new_x, new_y = calculate_dorling_layout(lons, lats, radii)

    c_vals = np.array([row['Val'] for row in map_rows])
    c_norm = np.clip((c_vals - (-1.0)) / (1.0 - (-1.0)), 0, 1)
    colors = sample_colorscale('RdBu_r', c_norm)

    fig_map = go.Figure()

    for i in range(len(map_rows)):
        t = np.linspace(0, 2*np.pi, 50)
        cx, cy = new_x[i] + radii[i] * np.cos(t), new_y[i] + radii[i] * np.sin(t)
        
        fig_map.add_trace(go.Scatter(
            x=cx, y=cy, fill='toself', fillcolor=colors[i],
            line=dict(color='white', width=1.5), mode='lines',
            name=map_rows[i]['Country'], 
            text=f"<b>{map_rows[i]['Country']}</b><br>Metric: {c_vals[i]:.2f}<br>Δ Volume: {v_vals[i]:.2%}",
            customdata=[map_rows[i]['Ticker']] * len(cx),
            hoverinfo='text', showlegend=False
        ))
        
        fig_map.add_trace(go.Scatter(
            x=[new_x[i]], y=[new_y[i]], mode='text',
            text=[map_rows[i]['Ticker']], textfont=dict(color='white', size=11, family="sans-serif"),
            hoverinfo='skip', showlegend=False
        ))

    fig_map.add_trace(go.Scatter(
        x=[None], y=[None], mode='markers',
        marker=dict(colorscale='RdBu_r', cmin=-1, cmax=1, showscale=True, colorbar=dict(title="ρ", thickness=15)),
        hoverinfo='none', showlegend=False
    ))

    fig_map.update_layout(
        title=rf"$\text{{Systemic Risk Cartogram - }} {target_date}$", 
        font=LATEX_FONT, template="plotly_dark",
        xaxis=dict(visible=False, scaleanchor="y", scaleratio=1), 
        yaxis=dict(visible=False),
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=50, b=10)
    )

    safe_havens = sorted([row for row in map_rows if row['Delta'] < 0 and row['Stress'] <= 0], key=lambda x: x['Stress'])
    safe_list_items = [
        html.Div([
            html.Span(sh['Country']),
            html.Span("{:.2f}".format(sh['Delta']), style={'float':'right','color':'#2ecc71'})
        ], style={'padding':'6px 0','borderBottom':'1px solid #222'}) 
        for sh in safe_havens
    ]
    if not safe_list_items: safe_list_items = [html.Div("No safe havens.", style={'color': '#777'})]

    return fig_map, safe_list_items

@app.callback(
    [Output('monte-carlo-graph', 'figure'), Output('animation-frame', 'data', allow_duplicate=True),
     Output('animation-interval', 'disabled', allow_duplicate=True), 
     Output('stat-max', 'children'), Output('stat-mean', 'children'), Output('stat-min', 'children')],
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
    
    current_vals = current_paths[-1, :] - 1
    max_val = np.max(current_vals)
    mean_val = np.mean(current_vals)
    min_val = np.min(current_vals)
    
    str_max = rf"$\text{{Max: }} {max_val*100:+.2f}\%$"
    str_mean = rf"$\text{{Mean: }} {mean_val*100:+.2f}\%$"
    str_min = rf"$\text{{Worst: }} {min_val*100:+.2f}\%$"
    
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
                         annotation_text=rf"$ES_{{1\%}} = {final_es_ret*100:.2f}\%$", annotation_position="bottom left",
                         annotation_font=dict(color="#FF0000", size=16))
        fig_mc.update_layout(title=r"$\text{Simulated Paths: } S_t = S_0 \exp\left(\sum r_i\right)$", 
                            font=LATEX_FONT, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', 
                            plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=40, r=20, t=50, b=40))
        return fig_mc, frame, True, str_max, str_mean, str_min
    
    fig_mc.update_layout(title=f"Monte Carlo Projection (Day {frame}/30)", template="plotly_dark",
                        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=LATEX_FONT,
                        margin=dict(l=40, r=20, t=50, b=40), xaxis=dict(range=[0, 30]), 
                        yaxis=dict(range=[np.min(paths)*0.95, np.max(paths)*1.05]))
    return fig_mc, frame + 1, False, str_max, str_mean, str_min

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)