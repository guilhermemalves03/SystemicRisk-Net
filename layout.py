from dash import dcc, html

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

explanation_box_style = {
    'width': '450px', 'minWidth': '450px', 'border': '2px solid #39FF14',
    'borderRadius': '15px', 'padding': '25px', 'marginLeft': '20px',
    'backgroundColor': 'rgba(57, 255, 20, 0.05)', 'color': '#FFFFFF',
    'fontFamily': '"EB Garamond", "Times New Roman", Times, serif',
    'fontSize': '18px', 'lineHeight': '1.6', 'boxSizing': 'border-box'
}

story_style = {
    'height': '100vh', 
    'display': 'flex', 
    'flexDirection': 'column', 
    'justifyContent': 'center', 
    'alignItems': 'center',
    'padding': '0 20%',
    'textAlign': 'center',
    'scrollSnapAlign': 'start',
    'borderBottom': '1px solid #111',
    'position': 'relative'
}

story_sections = html.Div([
    
    # =====================================================================
    # 1º SLIDE: TÍTULO INICIAL
    # =====================================================================
    html.Div([
        html.H1("Systemic Risk-Net", style={'color': '#e74c3c', 'fontSize': '3.5em', 'marginBottom': '20px'}),
        html.P("This dashboard helps the investor to not lose money in extreme financial losses", style={'color':'#e74c3c', 'fontSize': '1.8em'}),
        html.A("ENTER THE DASHBOARD", href="#main-dashboard", style={'marginTop': '60px', 'color': '#000', 'backgroundColor': '#39FF14', 'textDecoration': 'none', 'fontSize': '1.2em', 'fontWeight': 'bold', 'padding': '15px 30px', 'borderRadius': '5px', 'transition': '0.3s'}),
        html.P("But how? Lets look at Apple stocks example.", style={'color': '#888', 'marginTop': '20px', 'fontSize': '1.2em'}),
        html.Div("↓", style={'position': 'absolute', 'bottom': '30px', 'fontSize': '2em', 'color': '#555'})
    ], style=story_style),
    
    # =====================================================================
    # 2º SLIDE: WHAT IS AN EXTREME EVENT? (Distribuição e Caixas de Texto)
    # =====================================================================
    html.Div([
        # Coluna Esquerda: Gráfico
        html.Div([
            dcc.Graph(id='intro-apple-dist', config={'displayModeBar': False},mathjax=True, style={'height': '550px', 'width': '100%'}),
            html.Button("ZOOM: LEFT TAIL", id='zoom-btn-intro', n_clicks=0, 
                style={
                    'marginTop': '20px', 'backgroundColor': 'transparent', 
                    'color': '#39FF14', 'border': '1px solid #39FF14', 
                    'padding': '10px 20px', 'cursor': 'pointer', 'fontSize': '14px'
                })
        ], style={'flex': '1', 'padding': '40px', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'}),
        # Coluna Direita: Texto e Eventos
        html.Div([
            html.H1("What is an Extreme Event?", style={'color': '#e74c3c', 'fontSize': '3.5em', 'marginBottom': '20px', 'textAlign': 'left'}),
            html.P("In simple terms, an extreme event is a sharp, sudden drop in a stock's price from one day to the next. In statistical terms, we visualize these severe losses in the far left tail of the return distribution.", style={'color': '#bbb', 'fontSize': '1.6em', 'textAlign': 'left'}),
            
            html.Div([
                html.Div("Left side tail Extreme Events from the last 2 years: Apple (AAPL)", style={'color': '#fff', 'fontSize': '1.3em', 'marginBottom': '15px', 'fontWeight': 'bold'}),
                
                html.Div([
                    html.Span("2026-04-03", style={'color': '#bbb', 'display': 'inline-block', 'width': '120px'}),
                    html.Span("-5.13%", style={'color': '#e74c3c', 'fontWeight': 'bold', 'display': 'inline-block', 'width': '80px'}),
                    html.Span("Start of Middle-East war", style={'color': '#fff'}) 
                ], style={'fontSize': '1.2em', 'margin': '10px 0', 'textAlign': 'left'}),
                
                html.Div([
                    html.Span("2026-04-04", style={'color': '#bbb', 'display': 'inline-block', 'width': '120px'}),
                    html.Span("-3.52%", style={'color': '#e74c3c', 'fontWeight': 'bold', 'display': 'inline-block', 'width': '80px'}),
                    html.Span("Conflict Amplification", style={'color': '#fff'}) 
                ], style={'fontSize': '1.2em', 'margin': '10px 0', 'textAlign': 'left'}),

                html.Div([
                    html.Span("2025-10-10", style={'color': '#bbb', 'display': 'inline-block', 'width': '120px'}),
                    html.Span("-3.51%", style={'color': '#e74c3c', 'fontWeight': 'bold', 'display': 'inline-block', 'width': '80px'}),
                    html.Span("Tariffs on China", style={'color': '#fff'}),
                    html.Span("Lets focus on this example", style={'color': '#39FF14', 'fontWeight': 'bold', 'display': 'inline-block', 'marginLeft': '20px'})
                ], style={'fontSize': '1.2em', 'margin': '10px 0', 'textAlign': 'left'})
            ], style={'backgroundColor': '#0a0a0a', 'padding': '25px', 'borderRadius': '10px', 'border': '1px solid #333', 'marginTop': '30px', 'width': '100%'}),
        ], style={'flex': '1', 'padding': '40px', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}),

        html.Div("↓", style={'position': 'absolute', 'bottom': '30px', 'fontSize': '2em', 'color': '#555', 'left': '50%', 'transform': 'translateX(-50%)'})
    ], style=dict(story_style, **{'flexDirection': 'row', 'alignItems': 'stretch', 'padding': '0 5%'})),

    # =====================================================================
    # 3º SLIDE: PREDICTING THE UNPREDICTABLE (Monte Carlo)
    # =====================================================================
    html.Div([
        # --- COLUNA ESQUERDA: Texto Explicativo ---
        html.Div([
            html.H1("Predicting the Unpredictable?", 
                   style={'color': '#3498db', 'fontSize': '3.5em', 'marginBottom': '20px', 'textAlign': 'left', 'fontWeight': 'normal'}),
            html.P("Even in volatile markets, Monte Carlo Simulation allows us to map the future.", 
                   style={'color': '#bbb', 'fontSize': '1.8em', 'textAlign': 'left'}),
            html.P("By projecting thousands of paths based on historical returns, we transform uncertainty into measurable probabilities.", 
                   style={'color': '#888', 'fontSize': '1.2em', 'textAlign': 'left', 'marginTop': '20px'}),
        ], style={'width': '50%', 'padding': '40px', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}),

        # --- COLUNA DIREITA: Visualização da Simulação ---
        html.Div([
            dcc.Graph(
                id='intro-mc-sim', 
                config={'displayModeBar': False}, 
                mathjax=True, 
                style={'height': '450px', 'width': '100%'}
            ),
            
            # --- CAIXAS DE ESTATÍSTICAS NOVAS ---
            html.Div(style={'width': '100%', 'padding': '15px 0', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-evenly'}, children=[
                html.Div(dcc.Markdown(id='intro-stat-max', mathjax=True, style={'margin': 0}), style={'color': '#2ecc71', 'border': '1px solid #2ecc71', 'padding': '10px 20px', 'borderRadius': '10px', 'backgroundColor': 'rgba(46, 204, 113, 0.05)', 'fontSize': '16px'}),
                html.Div(dcc.Markdown(id='intro-stat-mean', mathjax=True, style={'margin': 0}), style={'color': "#ffffff", 'border': '1px solid #f1c40f', 'padding': '10px 20px', 'borderRadius': '10px', 'backgroundColor': 'rgba(241, 196, 15, 0.05)', 'fontSize': '16px'}),
                html.Div(dcc.Markdown(id='intro-stat-min', mathjax=True, style={'margin': 0}), style={'color': '#e74c3c', 'border': '1px solid #e74c3c', 'padding': '10px 20px', 'borderRadius': '10px', 'backgroundColor': 'rgba(231, 76, 60, 0.05)', 'fontSize': '16px'})
            ]),

            html.Button("SHOW INDIVIDUAL PATHS", id='mc-paths-btn', n_clicks=0, 
                        style={
                            'marginTop': '10px', 'backgroundColor': 'transparent', 
                            'color': '#bbb', 'border': '1px solid #555', 
                            'padding': '10px 20px', 'cursor': 'pointer', 'fontSize': '14px', 'borderRadius': '5px'
                        })
        ], style={'width': '50%', 'padding': '40px', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'}),

        html.Div("↓", style={'position': 'absolute', 'bottom': '30px', 'fontSize': '2em', 'color': '#555', 'left': '50%', 'transform': 'translateX(-50%)'})
    ], style=dict(story_style, **{'flexDirection': 'row', 'alignItems': 'stretch', 'padding': '0 5%'})),

    # =====================================================================
    # 4º SLIDE: GRAFO DA REDE DE CONTÁGIO (Network)
    # =====================================================================
    html.Div([
        # --- COLUNA ESQUERDA: Texto + Legenda ---
        html.Div([
            html.H1(
                "Mapping the Contagion Network",
                style={
                    'color': '#f1c40f',
                    'fontSize': '3.5em', 
                    'marginBottom': '20px', 
                    'textAlign': 'left',
                    'fontWeight': 'normal',
                    'lineHeight': '1.1'
                }
            ),
            html.P("Geographical borders aren't the only boundaries breached during a crisis. Shocks transmit rapidly across industries and corporate sectors.", 
                   style={'color': '#bbb', 'fontSize': '1.6em', 'textAlign': 'left'}),
            
            html.P("By visualizing the market as a network topology, we can identify which assets amplify the crash and which act as defensive shields.", 
                   style={'color': '#888', 'fontSize': '1.2em', 'textAlign': 'left', 'marginTop': '20px'}),

            # Legenda Explicativa
            html.Div([
                html.Div([html.Span("●", style={'color': '#e74c3c', 'marginRight': '10px', 'fontSize': '1.5em'}), html.B("Top (Red): "), "Systemic Risk. Assets that crash alongside the main asset."]),
                html.Div([html.Span("●", style={'color': '#2ecc71', 'marginRight': '10px', 'fontSize': '1.5em'}), html.B("Bottom (Green): "), "Safe Havens. Assets that protect the portfolio."]),
                html.Div([html.Span("━", style={'color': '#fff', 'marginRight': '10px', 'fontWeight': 'bold'}), html.B("Line Thickness: "), "Absolute strength of the stress correlation."])
            ], style={'marginTop': '30px', 'backgroundColor': '#0a0a0a', 'padding': '20px', 'borderRadius': '10px', 'border': '1px solid #333', 'color': '#eee', 'fontSize': '1.2em', 'lineHeight': '2'})

        ], style={'width': '50%', 'padding': '40px', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}),

        # --- COLUNA DIREITA: Gráfico do Grafo + Botão ---
        html.Div([
            dcc.Graph(
                id='intro-network-graph', 
                config={'displayModeBar': False}, 
                mathjax=True, 
                style={'height': '550px', 'width': '100%'}
            ),
            html.Button("HIGHLIGHT SAFE HAVENS", id='network-highlight-btn', n_clicks=0, 
                        style={
                            'marginTop': '20px', 'backgroundColor': 'transparent', 
                            'color': '#f1c40f', 'border': '1px solid #f1c40f', 
                            'padding': '10px 20px', 'cursor': 'pointer', 'fontSize': '14px', 'borderRadius': '5px'
                        })
        ], style={'width': '50%', 'padding': '40px', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'}),

        html.Div("↓", style={'position': 'absolute', 'bottom': '30px', 'fontSize': '2em', 'color': '#555', 'left': '50%', 'transform': 'translateX(-50%)'})
    ], style=dict(story_style, **{'flexDirection': 'row', 'alignItems': 'stretch', 'padding': '0 5%'})),

    # =====================================================================
    # 5º SLIDE: MAPA (How can we understand...)
    # =====================================================================
    html.Div([
        # --- COLUNA ESQUERDA: Texto + Tabela de Impacto ---
        html.Div([
            html.H1(
                "How can we understand the nature of these events?",
                style={
                    'color': '#2ecc71', 
                    'fontSize': '3.5em', 
                    'marginBottom': '20px', 
                    'textAlign': 'left',
                    'fontWeight': 'normal', 
                    'lineHeight': '1.1' 
                }
            ),
            html.P("While public news is universally accessible, systemic risks often spread unseen across borders and sectors. During this specific shock, the correlation between Apple and Asian markets spiked to unprecedented levels.", 
                   style={'color': '#bbb', 'fontSize': '1.6em', 'textAlign': 'left'}),            
            html.Div(id='asia-impact-table', style={'marginTop': '30px', 'width': '100%'}),
            
        ], style={'width': '50%', 'padding': '40px', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}),

        # --- COLUNA DIREITA: Mapa + Botão Zoom ---
        html.Div([
            dcc.Graph(
                id='intro-contagion-map', 
                config={'displayModeBar': False}, 
                mathjax=True, 
                style={'height': '500px', 'width': '100%'}
            ),
            html.Button("ZOOM: ASIA FOCUS", id='zoom-asia-btn', n_clicks=0, 
                        style={
                            'marginTop': '0px', 'backgroundColor': 'transparent', 
                            'color': '#2ecc71', 'border': '1px solid #2ecc71', 
                            'padding': '10px 20px', 'cursor': 'pointer', 'fontSize': '14px'
                        })
        ], style={'width': '50%', 'padding': '40px', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'}),

        html.Div("↓", style={'position': 'absolute', 'bottom': '30px', 'fontSize': '2em', 'color': '#555', 'left': '50%', 'transform': 'translateX(-50%)'})
    ], style=dict(story_style, **{'flexDirection': 'row', 'alignItems': 'stretch', 'padding': '0 5%'})),

])

def get_layout(engine):
    options = [{'label': f"{r['name']} ({r['ticker']})", 'value': r['ticker']} 
               for _, r in engine.assets_df[engine.assets_df['sector'] != 'Country'].iterrows()]

    dashboard_layout = html.Div([
        dcc.Store(id='mc-paths-store'),
        dcc.Store(id='mc-es-store'),
        dcc.Store(id='animation-frame', data=0),
        dcc.Store(id='selected-stress-date', data=None),
        dcc.Interval(id='animation-interval', interval=100, n_intervals=0, disabled=True),

        html.Div([
            html.H1("SYSTEMIC RISK-NET", style={'margin': '0', 'fontSize': '18px', 'letterSpacing': '2px'}),
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
                            dcc.Graph(id='distribution-graph', style={'flex': '1', 'minHeight': '400px'}, mathjax=True, config={'displayModeBar': False}),
                            dcc.Graph(id='ridgeline-graph', style={'flex': '1', 'minHeight': '500px', 'borderTop': '1px solid #222'}, mathjax=True, config={'displayModeBar': False})
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
                        dcc.Graph(id='monte-carlo-graph', style={'height': '400px'}, mathjax=True, config={'displayModeBar': False}),
                        html.Div(id='mc-stats-box', style={'flex': '1', 'padding': '20px', 'backgroundColor': '#0a0a0a', 'borderTop': '1px solid #222', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-evenly'}, children=[
                            html.Div(dcc.Markdown(id='stat-max', mathjax=True, style={'margin': 0}), style={'color': '#2ecc71', 'border': '1px solid #2ecc71', 'padding': '10px 25px', 'borderRadius': '10px', 'backgroundColor': 'rgba(46, 204, 113, 0.05)', 'fontSize': '18px'}),
                            html.Div(dcc.Markdown(id='stat-mean', mathjax=True, style={'margin': 0}), style={'color': "#ffffff", 'border': '1px solid #f1c40f', 'padding': '10px 25px', 'borderRadius': '10px', 'backgroundColor': 'rgba(241, 196, 15, 0.05)', 'fontSize': '18px'}),
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

            dcc.Tab(label='Network', value='tab-network', children=[
                html.Div([
                    html.Div([
                        dcc.Graph(id='network-graph', style={'flex': '1', 'minHeight': '600px'}, config={'displayModeBar': False})
                    ], style={'flex': '1', 'backgroundColor': '#000', 'display': 'flex', 'flexDirection': 'column'}),
                    
                    html.Div([
                        html.H3("CONTAGION TOPOLOGY", style={'color': '#ddd', 'marginTop': 0, 'fontSize': '16px', 'fontFamily': 'sans-serif'}),
                        dcc.Markdown(r"""
Grafo em estrela das dependências em eventos extremos.

* **Top (Vermelho):** Ativos com maior correlação positiva (Risco Sistémico / Efeito Contágio).
* **Bottom (Verde):** Ativos com menor correlação ou correlação negativa (Hedges / Safe Havens).

A espessura da ligação representa a força absoluta da correlação ($\rho_{\text{stress}}$).
                        """, mathjax=True)
                    ], style=explanation_box_style)
                    
                ], style={'display': 'flex', 'minHeight': 'calc(100vh - 104px)', 'padding': '15px', 'boxSizing': 'border-box'})
            ], style={'backgroundColor': '#111', 'color': '#888', 'border': 'none', 'padding': '10px'}, 
               selected_style={'backgroundColor': '#000', 'color': '#fff', 'borderTop': '2px solid #f1c40f', 'borderBottom': 'none', 'padding': '10px'}),

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
                            
                            dcc.Graph(id='contagion-map', style={'flex': '1', 'minHeight': '500px'}, mathjax=True, config={'displayModeBar': False})
                        ], style={'flex': '1', 'display': 'flex', 'flexDirection': 'column'}),
                    ], style={'display': 'flex', 'minHeight': '600px', 'backgroundColor': '#000'}),

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
                dcc.Graph(id='volatility-graph', config={'displayModeBar': False})
            ])
        ])

    ], id='main-dashboard', style={'scrollSnapAlign': 'start', 'minHeight': '100vh'})

    return html.Div([
        story_sections,
        dashboard_layout
    ], style={
        'height': '100vh', 
        'overflowY': 'scroll', 
        'scrollSnapType': 'y mandatory',
        'backgroundColor': '#000',
        'fontFamily': '"EB Garamond", serif',
        'scrollBehavior': 'smooth'
    })