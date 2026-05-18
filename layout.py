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
    'width': '450px', 
    'minWidth': '450px', 
    'border': '1px solid #34495e',
    'borderRadius': '12px', 
    'padding': '25px', 
    'marginLeft': '20px',
    'backgroundColor': 'rgba(52, 73, 94, 0.2)',
    'color': '#ecf0f1',
    'fontFamily': '"EB Garamond", serif',
    'fontSize': '17px', 
    'lineHeight': '1.6', 
    'boxSizing': 'border-box',
    'boxShadow': '0 4px 15px rgba(0,0,0,0.3)'
}


story_style = {
    'height': 'calc(100vh - 50px)', 
    'display': 'flex', 
    'flexDirection': 'column', 
    'justifyContent': 'center', 
    'alignItems': 'center',
    'padding': '0 5%', 
    'textAlign': 'center',
    'scrollSnapAlign': 'start', 
    'borderBottom': '1px solid #111',
    'position': 'relative',
    'boxSizing': 'border-box'
}


tabs_styles = {
    'height': '60px',
    'backgroundColor': '#000',
}
tab_style = {
    'borderBottom': '1px solid #333',
    'backgroundColor': '#0a0a0a',
    'color': '#555',
    'padding': '15px',
    'fontWeight': 'bold',
    'fontSize': '16px',
    'borderTop': 'none',
    'borderLeft': 'none',
    'borderRight': 'none',
    'fontFamily': '"EB Garamond", serif',
    'letterSpacing': '1px'
}
tab_selected_style = {
    'borderTop': '3px solid #39FF14', 
    'borderBottom': 'none',
    'backgroundColor': '#111',
    'color': '#39FF14',
    'padding': '15px',
    'fontWeight': 'bold',
    'fontSize': '16px',
    'borderLeft': 'none',
    'borderRight': 'none',
    'fontFamily': '"EB Garamond", serif',
    'letterSpacing': '1px'
}


story_sections = html.Div([
    
    
    html.Div([
        html.Img(
            src='/assets/titulo_3d.png', 
            style={
                'maxWidth': '800px',      
                'width': '100%',          
                'height': 'auto',         
                'marginBottom': '10px',   
                'display': 'block',
                'marginLeft': 'auto',     
                'marginRight': 'auto'
            }
        ),
        
        html.P(
            "A comprehensive solution to fortify capital against extreme market volatility.", 
            style={
                'color': '#d1d5db', 
                'fontSize': '1.6em', 
                'fontFamily': '"EB Garamond", serif',
                'letterSpacing': '1px',
                'marginTop': '10px'
            }
        ),
        
       
        html.Div([
            html.Span("↑ ", style={'fontSize': '1.3em', 'fontWeight': 'bold'}),
            html.Span("Select 'Main Dashboard' in the top menu for immediate access")
        ], style={
            'color': '#888888', 
            'marginTop': '60px', 
            'fontSize': '1.1em',
            'letterSpacing': '1px',
            'fontFamily': '"EB Garamond", serif'
        }),
                 
        html.P(
            "Or scroll down to understand the mechanics: A case study on Apple Inc.", 
            style={
                'color': '#666666', 
                'marginTop': '25px', 
                'fontSize': '1.2em',
                'fontStyle': 'italic',
                'fontFamily': '"EB Garamond", serif'
            }
        ),
        
        html.Div(
            "↓", 
            style={
                'color': "#b07b5a", 
                'position': 'absolute', 
                'bottom': '30px', 
                'fontSize': '2em'
            }
        )
    ], style=story_style),


    html.Div([
        html.H1("The Foundations of Risk", 
                style={'color': '#d4af37', 'fontSize': '3.2em', 'marginBottom': '40px', 'fontWeight': 'normal'}),
        
        
        html.Div([
            
            
            html.Div([
                html.Div(html.I(className="fa-solid fa-chart-line"), style={'fontSize': '40px', 'color': '#d4af37', 'marginBottom': '20px'}),
                html.H3("1. Daily Returns", style={'color': '#fff', 'marginBottom': '15px'}),
                dcc.Markdown(r"""
At its core, we just want to know the daily variation: *Did the stock go up or down today compared to yesterday?*

To calculate this, we use a mathematical tool called a **Logarithm**:

$$r_t = \ln\left(\frac{P_t}{P_{t-1}}\right)$$

* $P_t$: Price **Today**
* $P_{t-1}$: Price **Yesterday**

*Why this tool?* It translates raw price changes into a standardized format, allowing us to easily visualize and compare a 150 stock alongside a 3,000 stock without visual distortion.
                """, mathjax=True, style={'color': '#bbb', 'fontSize': '1.1em'})
            ], style={'flex': '1', 'padding': '30px', 'backgroundColor': '#0a0a0a', 'borderRadius': '10px', 'border': '1px solid #222', 'margin': '0 15px'}),


            
            html.Div([
                html.Div(html.I(className="fa-solid fa-chart-area"), style={'fontSize': '40px', 'color': '#d4af37', 'marginBottom': '20px'}),
                html.H3("2. Distributions", style={'color': '#fff', 'marginBottom': '15px'}),
                dcc.Markdown(r"""
Once we calculate those daily returns, we stack them up. *How do we sort days by 'how good' or 'how bad' they were?*

We organize them into a **Probability Curve**:

* **The Center**: Normal, boring days. The stock barely moves.
* **The Edges**: Solid gains or noticeable drops. Common, but not historic.
* **The Left Tail**: The incredibly rare, historic "Black Swan" crashes.

*Why does it matter?* Our dashboard focuses on measuring exactly how 'thick' that dangerous left tail really is.
                """, mathjax=True, style={'color': '#bbb', 'fontSize': '1.1em'})
            ], style={'flex': '1', 'padding': '30px', 'backgroundColor': '#0a0a0a', 'borderRadius': '10px', 'border': '1px solid #222', 'margin': '0 15px'}),


            
            html.Div([
                html.Div(html.I(className="fa-solid fa-link"), style={'fontSize': '40px', 'color': '#d4af37', 'marginBottom': '20px'}),
                html.H3("3. Correlation", style={'color': '#fff', 'marginBottom': '15px'}),
                dcc.Markdown(r"""
Correlation measures the invisible elastic band tying two assets together. *Do they move in sync?*

It runs on a strict mathematical scale ($\rho$) from -1 to 1:

* **+1 (Lockstep)**: If one falls, the other falls with it.
* **0 (Strangers)**: Their movements are completely independent.
* **-1 (Safe Havens)**: When one crashes, the other soars.

*The Danger:* During a market panic, assets that normally act like strangers suddenly spike to +1. Everything crashes together. We call this **Contagion**.
                """, mathjax=True, style={'color': '#bbb', 'fontSize': '1.1em'})
            ], style={'flex': '1', 'padding': '30px', 'backgroundColor': '#0a0a0a', 'borderRadius': '10px', 'border': '1px solid #222', 'margin': '0 15px'})

        ], style={'display': 'flex', 'justifyContent': 'center', 'width': '90%', 'maxWidth': '1200px'}),
        html.P("Now that you know the basics, let's see them in action.", 
               style={'color': '#666', 'marginTop': '20px', 'fontSize': '1.2em', 'fontStyle': 'italic'}),
        
        html.Div("↓", style={'color': '#d4af37', 'position': 'absolute', 'bottom': '30px', 'fontSize': '2em'})
    ], style=story_style),
    
    
    html.Div([
        
        html.Div([
            dcc.Graph(id='intro-apple-dist', config={'displayModeBar': False},mathjax=True, style={'height': '550px', 'width': '100%'}),
            
            
            html.Button("ZOOM: LEFT TAIL", id='zoom-btn-intro', n_clicks=0, 
                style={
                    'marginTop': '20px', 
                    'transform': 'translateX(-50px)',
                    'backgroundColor': '#e74c3c', 
                    'color': '#ffffff',               
                    'border': 'none',    
                    'padding': '12px 25px', 
                    'cursor': 'pointer', 
                    'fontSize': '14px',
                    'fontWeight': 'bold',
                    'borderRadius': '8px',
                    'boxShadow': '0 4px 10px rgba(231, 76, 60, 0.4)',
                    'transition': '0.3s'            
                })
        ], style={'flex': '1', 'padding': '40px', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'}),
        
        
        html.Div([
            html.H1("What is an Extreme Event?", style={'color': '#e74c3c', 'fontSize': '3.5em','marginTop': '0px', 'marginBottom': '15px', 'textAlign': 'left'}),
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
                    
                    
                    html.Button("Highlight Case Study", id='focus-example-btn', n_clicks=0, 
                                style={
                                    'backgroundColor': '#39FF14', 
                                    'color': '#ffffff', 
                                    'fontWeight': 'bold',
                                    'border': 'none',
                                    'borderRadius': '8px', 
                                    'padding': '8px 15px', 
                                    'cursor': 'pointer',
                                    'fontSize': '0.85em', 
                                    'fontFamily': 'inherit', 
                                    'transition': '0.3s',
                                    'marginLeft': '20px',
                                    'boxShadow': '0 4px 10px rgba(57, 255, 20, 0.4)'
                                })
                ], style={'fontSize': '1.2em', 'margin': '10px 0', 'textAlign': 'left', 'display': 'flex', 'alignItems': 'center'})
            ], style={'backgroundColor': '#0a0a0a', 'padding': '25px', 'borderRadius': '10px', 'border': '1px solid #333', 'marginTop': '20px', 'width': '100%'}),
        ], style={'flex': '1', 'padding': '40px', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}),

        html.Div("↓", style={'color': '#e74c3c','position': 'absolute', 'bottom': '30px', 'fontSize': '2em', 'left': '50%', 'transform': 'translateX(-50%)'})
    ], style=dict(story_style, **{'flexDirection': 'row', 'alignItems': 'stretch', 'padding': '0 5%'})),

    
    html.Div([
        
        html.Div([
            html.H1("Predicting the Unpredictable", 
                   style={'color': '#3498db', 'fontSize': '3.2em', 'marginTop': '0px', 'marginBottom': '10px', 'textAlign': 'left', 'fontWeight': 'normal'}),
            
            html.P("Looking at past data is useful, but the real question is: what could happen to my investment over the next month?", 
                   style={'color': '#bbb', 'fontSize': '1.5em', 'textAlign': 'left', 'marginBottom': '20px'}),

            html.P("To answer this, we run a Monte Carlo simulation. Think of it as generating thousands of parallel universes for this stock, based on how it has behaved historically. The chart on the right aggregates all these possible futures into a clear map.", 
                   style={'color': '#888', 'fontSize': '1.1em', 'textAlign': 'left', 'marginBottom': '20px'}),

            html.P("By checking the boxes below the chart, you can quickly understand your risk:", 
                   style={'color': '#888', 'fontSize': '1.1em', 'textAlign': 'left', 'marginBottom': '15px'}),

           
            html.Div([
                html.Div([
                    html.B("The Worst-Case Scenario (Red Box): ", style={'color': '#e74c3c'}),
                    "If the market crashes, this is a realistic estimate of the maximum drop you could face over the next 30 days."
                ], style={'color': '#888', 'fontSize': '1.1em', 'marginBottom': '15px', 'textAlign': 'left'}),

                html.Div([
                    html.B("The Most Likely Outcome (Yellow Box): ", style={'color': '#f1c40f'}),
                    "This is the average expected return. If the stock follows a normal path without major surprises, your return should be close to this number."
                ], style={'color': '#888', 'fontSize': '1.1em', 'marginBottom': '15px', 'textAlign': 'left'}),

                html.Div([
                    html.B("The Best-Case Scenario (Green Box): ", style={'color': '#2ecc71'}),
                    "If conditions are exceptionally favorable, this represents the ceiling of your potential gains."
                ], style={'color': '#888', 'fontSize': '1.1em', 'textAlign': 'left'}),
            ])
            
        ], style={'width': '50%', 'padding': '40px', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}),

        
        html.Div([
            dcc.Graph(
                id='intro-mc-sim', 
                config={'displayModeBar': False}, 
                mathjax=True, 
                style={'height': '450px', 'width': '100%'}
            ),
            
            
            html.Div(style={'width': '100%', 'padding': '15px 0', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-evenly'}, children=[
                html.Div(dcc.Markdown(id='intro-stat-max', mathjax=True, style={'margin': 0}), style={'color': '#2ecc71', 'border': '1px solid #2ecc71', 'padding': '10px 20px', 'borderRadius': '10px', 'backgroundColor': 'rgba(46, 204, 113, 0.05)', 'fontSize': '16px'}),
                html.Div(dcc.Markdown(id='intro-stat-mean', mathjax=True, style={'margin': 0}), style={'color': '#f1c40f', 'border': '1px solid #f1c40f', 'padding': '10px 20px', 'borderRadius': '10px', 'backgroundColor': 'rgba(241, 196, 15, 0.05)', 'fontSize': '16px'}),
                html.Div(dcc.Markdown(id='intro-stat-min', mathjax=True, style={'margin': 0}), style={'color': '#e74c3c', 'border': '1px solid #e74c3c', 'padding': '10px 20px', 'borderRadius': '10px', 'backgroundColor': 'rgba(231, 76, 60, 0.05)', 'fontSize': '16px'})
            ]),

            html.Button("SHOW INDIVIDUAL PATHS", id='mc-paths-btn', n_clicks=0, 
                        style={
                            'marginTop': '25px', 
                            'backgroundColor': '#3498db', 
                            'color': '#ffffff',            
                            'border': 'none',              
                            'padding': '12px 25px',        
                            'cursor': 'pointer', 
                            'fontSize': '14px',
                            'fontWeight': 'bold',          
                            'borderRadius': '8px',         
                            'boxShadow': '0 4px 10px rgba(52, 152, 219, 0.4)', 
                            'transition': '0.3s'            
                        })
        ], style={'width': '50%', 'padding': '40px', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'}),

        html.Div("↓", style={'color': '#3498db','position': 'absolute', 'bottom': '30px', 'fontSize': '2em',  'left': '50%', 'transform': 'translateX(-50%)'})
    ], style=dict(story_style, **{'flexDirection': 'row', 'alignItems': 'stretch', 'padding': '0 5%'})),

    
    html.Div([
        
        html.Div([
            html.H1(
                "Mapping the Contagion Network",
                style={
                    'color': '#f1c40f',
                    'fontSize': '3.5em', 
                    'marginBottom': '15px',
                    'textAlign': 'left',
                    'fontWeight': 'normal',
                    'lineHeight': '1.1',
                    'marginTop': '0px'
                }
            ),
            html.P("Geographical borders aren't the only boundaries breached during a crisis. Shocks transmit rapidly across industries and corporate sectors.", 
                   style={
                       'color': '#bbb', 
                       'fontSize': '1.6em', 
                       'textAlign': 'left',
                       'marginTop': '0px',
                       'marginBottom': '15px'
                   }),
            
            html.P("By visualizing the market as a network topology, we can identify which assets amplify the crash and which act as defensive shields.", 
                   style={
                       'color': '#888', 
                       'fontSize': '1.2em', 
                       'textAlign': 'left', 
                       'marginTop': '15px',
                       'marginBottom': '0px'
                   }),

            
            html.Div([
                
                html.Div([
                    html.Span("●", style={'color': '#e74c3c', 'width': '35px', 'display': 'inline-block', 'fontSize': '1.5em', 'textAlign': 'center'}),
                    html.Span([html.B("Top (Red): "), "Systemic Risk. Assets that crash alongside the main asset."])
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '12px'}),
                
                
                html.Div([
                    html.Span("●", style={'color': '#2ecc71', 'width': '35px', 'display': 'inline-block', 'fontSize': '1.5em', 'textAlign': 'center'}),
                    html.Span([html.B("Bottom (Green): "), "Safe Havens. Assets that protect the portfolio."])
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '12px'}),
                
                
                html.Div([
                    html.Span("━", style={'color': '#fff', 'width': '35px', 'display': 'inline-block', 'fontWeight': 'bold', 'textAlign': 'center', 'fontSize': '1.2em'}),
                    html.Span([html.B("Line Thickness: "), "Absolute strength of the stress correlation (ρ)."])
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '12px'}),

                
                html.Div([
                    html.Span("↔", style={'color': '#3498db', 'width': '35px', 'display': 'inline-block', 'fontWeight': 'bold', 'textAlign': 'center', 'fontSize': '1.5em'}),
                    html.Span([html.B("Distance: "), "Shock (Δρ). Closer nodes suffered a sudden jump in correlation."])
                ], style={'display': 'flex', 'alignItems': 'center', 'marginBottom': '12px'}),

                
                html.Div([
                    html.Span("⬤", style={'color': '#fff', 'width': '35px', 'display': 'inline-block', 'fontSize': '1.3em', 'textAlign': 'center'}),
                    html.Span([html.B("Bubble Size: "), "Trading Volume. Larger nodes represent heavily traded."])
                ], style={'display': 'flex', 'alignItems': 'center'})

            ], style={
                'marginTop': '20px', 
                'backgroundColor': '#0a0a0a', 
                'padding': '25px', 
                'borderRadius': '10px', 
                'border': '1px solid #333', 
                'color': '#eee', 
                'fontSize': '1.05em', 
                'display': 'flex', 
                'flexDirection': 'column', 
                'alignItems': 'flex-start'
            })
        ], style={'width': '50%', 'padding': '40px', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'center'}),

        
        html.Div([
            dcc.Graph(
                id='intro-network-graph', 
                config={'displayModeBar': False}, 
                mathjax=True, 
                style={'height': '650px', 'width': '100%'}
            ),
            
            
            html.Button("HIGHLIGHT SAFE HAVENS", id='network-highlight-btn', n_clicks=0, 
                        style={
                            'marginTop': '10px', 
                            'backgroundColor': '#f1c40f', 
                            'color': '#ffffff', 
                            'border': 'none', 
                            'padding': '12px 25px', 
                            'cursor': 'pointer', 
                            'fontSize': '14px', 
                            'fontWeight': 'bold',
                            'borderRadius': '8px',
                            'boxShadow': '0 4px 10px rgba(241, 196, 15, 0.4)',
                            'transition': '0.3s'
                        })
        ], style={'width': '50%', 'padding': '40px', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'justifyContent': 'center'}),

        html.Div("↓", style={'color': '#f1c40f','position': 'absolute', 'bottom': '30px', 'fontSize': '2em', 'left': '50%', 'transform': 'translateX(-50%)'})
    ], style=dict(story_style, **{'flexDirection': 'row-reverse', 'alignItems': 'stretch', 'padding': '0 5%'})),

    
    html.Div([
        
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
            
            html.P("While systemic risks often spread invisibly across the globe, there are exceptions. During the Apple shock, while much of Asia crashed, Vietnam acted as a 'safe haven,' completely decoupling from the market (a -0.73 correlation jump). Identifying these anomalies allows you to build effective geographical shields to protect your portfolio during crises.", 
                   style={'color': '#bbb', 'fontSize': '1.4em', 'textAlign': 'left'}),            
            
            html.Div(id='asia-impact-table', style={'marginTop': '30px', 'width': '100%'}),
            
        ], style={
            'width': '50%', 
            'padding': '50px 40px 40px 40px', 
            'display': 'flex', 
            'flexDirection': 'column', 
            'justifyContent': 'flex-start'     
        }),

        
        html.Div([
            dcc.Graph(
                id='intro-contagion-map', 
                config={'displayModeBar': False}, 
                mathjax=True, 
                style={'height': '500px', 'width': '100%'}
            ),
            
            
            html.Button("ZOOM: ASIA FOCUS", id='zoom-asia-btn', n_clicks=0, 
                        style={
                            'marginTop': '20px', 
                            'backgroundColor': '#2ecc71', 
                            'color': '#ffffff', 
                            'border': 'none', 
                            'padding': '12px 25px', 
                            'cursor': 'pointer', 
                            'fontSize': '14px', 
                            'fontWeight': 'bold',
                            'borderRadius': '8px',
                            'boxShadow': '0 4px 10px rgba(46, 204, 113, 0.4)',
                            'transition': '0.3s'
                        })
        ], style={
            'width': '50%', 
            'padding': '50px 40px 40px 40px', 
            'display': 'flex', 
            'flexDirection': 'column', 
            'alignItems': 'center', 
            'justifyContent': 'flex-start'     
        }),
        
        
        html.Div("READY? SELECT 'MAIN DASHBOARD'", 
                 style={
                     'position': 'absolute', 
                     'bottom': '30px',            
                     'left': '50%', 
                     'transform': 'translateX(-50%)',
                     'fontSize': '1.1em', 
                     'color': '#2ecc71',  
                     'fontWeight': 'bold',
                     'letterSpacing': '2px',
                     'backgroundColor': 'rgba(57, 255, 20, 0.05)',
                     'padding': '10px 25px',
                     'borderRadius': '30px',
                     'border': '1px solid rgba(57, 255, 20, 0.3)'
                 })
    ], style=dict(story_style, **{'flexDirection': 'row', 'alignItems': 'stretch', 'padding': '0 5%', 'borderBottom': 'none'})),
    
], style={
    'height': 'calc(100vh - 50px)',  
    'overflowY': 'scroll',           
    'scrollSnapType': 'y mandatory', 
    'backgroundColor': '#000',
    'overflowX': 'hidden'            
})

def get_layout(engine):
    options = [{'label': f"{r['name']} ({r['ticker']})", 'value': r['ticker']} 
               for _, r in engine.assets_df[engine.assets_df['sector'] != 'Country'].iterrows()]

    
    stores_and_modals = html.Div([
        dcc.Store(id='mc-paths-store'),
        dcc.Store(id='intro-mc-paths-store'),
        dcc.Store(id='mc-es-store'),
        dcc.Store(id='animation-frame', data=0),
        dcc.Store(id='selected-stress-date', data=None),
        dcc.Interval(id='animation-interval', interval=100, n_intervals=0, disabled=True),
        
        
        html.Div(id='volatility-modal', style={'display': 'none', 'position': 'fixed', 'zIndex': '1000', 'left': '0', 'top': '0', 'width': '100%', 'height': '100%', 'backgroundColor': 'rgba(0,0,0,0.8)'}, children=[
            html.Div(style={'position': 'relative', 'margin': '10% auto', 'padding': '20px', 'width': '60%', 'backgroundColor': '#111', 'borderRadius': '10px', 'border': '1px solid #333'}, children=[
                html.Button('✖', id='close-modal-btn', style={'position': 'absolute', 'right': '15px', 'top': '15px', 'backgroundColor': 'transparent', 'color': '#e74c3c', 'border': 'none', 'fontSize': '20px', 'cursor': 'pointer', 'zIndex': '10'}),
                dcc.Graph(id='volatility-graph', config={'displayModeBar': False})
            ])
        ])
    ])

    
    dashboard_content = html.Div([
        html.Div([
                
                html.Div([
                    dcc.Dropdown(
                        id='main-asset-dropdown',
                        options=options,
                        value='AAPL',
                        clearable=False,
                        className='', 
                        style={'color': '#000'}
)
                ], style={'width': '300px', 'marginLeft': '20px'}), 

                
                html.Div([
                    dcc.Markdown(
                        r"# $\text{SYSTEMIC RISK-NET}$",  
                        mathjax=True,
                        className="meu-titulo-latex",
                        style={
                            'margin': '0', 
                            'color': '#ffffff', 
                            'letterSpacing': '2px',
                            'marginRight': '20px'
                        }
                    )
                ])

            ], style={
                'display': 'flex', 
                'justifyContent': 'space-between', 
                'alignItems': 'center',            
                'padding': '8px 0', 
                'backgroundColor': '#111111',      
                'borderBottom': '1px solid #333'
            }),

        dcc.Tabs(id="tabs", value='tab-dist', children=[
            dcc.Tab(label='Risk Profile', value='tab-dist', children=[
                html.Div([
                    html.Div([
                        html.Div([
                            html.H3("STRESS EVENTS", style={'fontSize': '20px', 'color': '#e74c3c', 'marginBottom': '10px'}),
                            html.Div(id='extreme-dates-list', style={'fontSize': '18px', 'maxHeight': '800px', 'overflowY': 'auto', 'paddingRight': '5px'})
                        ], style={'width': '200px', 'padding': '15px', 'borderRight': '1px solid #333', 'backgroundColor': '#0a0a0a'}),
                        
                        html.Div([
                            
                            html.Div([
                                
                                html.Div([
                                    dcc.Graph(id='distribution-graph', style={'height': '550px', 'width': '100%'}, mathjax=True, config={'displayModeBar': False})
                                ], id='container-distribution', style={'display': 'flex', 'flexDirection': 'column', 'width': '100%', 'height': '100%'}),
                                
                                
                                html.Div([
                                    dcc.Graph(id='ridgeline-graph', style={'height': '550px', 'width': '100%'}, mathjax=True, config={'displayModeBar': False})
                                ], id='container-ridgeline', style={'display': 'none', 'flexDirection': 'column', 'width': '100%', 'height': '100%'}),
                            ], style={'height': '550px', 'width': '100%'}), 

                            
                            html.Button(
                                "SHOW MONTHLY DISTRIBUTION PLOT", 
                                id='toggle-risk-graphs-btn', 
                                n_clicks=0, 
                                style={
                                    'marginTop': '25px', 
                                    'backgroundColor': '#f1c40f',  
                                    'color': '#ffffff',            
                                    'border': 'none',              
                                    'padding': '12px 25px',        
                                    'cursor': 'pointer', 
                                    'fontSize': '14px',
                                    'fontWeight': 'bold',
                                    'borderRadius': '8px',         
                                    'boxShadow': '0 4px 10px rgba(241, 196, 15, 0.4)', 
                                    'transition': '0.3s',
                                    'alignSelf': 'center'             
                                }
                            )
                        ], style={'display': 'flex', 'flexDirection': 'column', 'flex': '1', 'alignItems': 'center'})
                    ], style={'display': 'flex', 'flex': '1', 'backgroundColor': '#000'}),
                    
                    html.Div([
                        html.H3("RISK PROFILE ANALYSIS", style={'color': '#3498db', 'marginTop': 0, 'fontSize': '16px', 'fontFamily': 'sans-serif', 'letterSpacing': '1px'}),
                        dcc.Markdown("""
This chart maps daily return frequencies. Normal days group around the center (0%).

**The Danger Zone (Left Tail)**

The red dashed line is the **Value at Risk (VaR)**, bounding the worst 1% of days.

* A **"fat" left tail** shows high vulnerability to extreme crashes.
* **Red bars** highlight the exact days the asset hit this critical zone.

**Tracking Risk Over Time**

Market risk is dynamic. Click **SHOW MONTHLY DISTRIBUTION PLOT** below to view monthly shifts and:

1. Identify the worst-performing months.
2. Spot seasonal volatility.
3. Monitor if tail risk is expanding or shrinking.
                        """, style={'color': '#bbb', 'fontSize': '15px', 'lineHeight': '1.6'})
                    ], style=explanation_box_style)
                    
                ], style={'display': 'flex', 'height': 'calc(100vh - 164px)', 'padding': '15px', 'boxSizing': 'border-box', 'overflow': 'hidden'}) # <--- ALTERAÇÕES FEITAS AQUI!
            ], style={'backgroundColor': '#111', 'color': '#888', 'border': 'none', 'padding': '10px'}, 
               selected_style={'backgroundColor': '#000', 'color': '#fff', 'borderTop': '2px solid #e74c3c', 'borderBottom': 'none', 'padding': '10px'}),

            dcc.Tab(label='Stress Test', value='tab-mc', children=[
                html.Div([
                    html.Div([
                        dcc.Graph(id='monte-carlo-graph', style={'height': '400px'}, mathjax=True, config={'displayModeBar': False}),
                        html.Div(id='mc-stats-box', style={'flex': '1', 'padding': '20px', 'backgroundColor': '#0a0a0a', 'borderTop': '1px solid #222', 'display': 'flex', 'alignItems': 'center', 'justifyContent': 'space-evenly'}, children=[
                            html.Div(dcc.Markdown(id='stat-max', mathjax=True, style={'margin': 0}), style={'color': '#2ecc71', 'border': '1px solid #2ecc71', 'padding': '10px 25px', 'borderRadius': '10px', 'backgroundColor': 'rgba(46, 204, 113, 0.05)', 'fontSize': '18px'}),
                            html.Div(dcc.Markdown(id='stat-mean', mathjax=True, style={'margin': 0}), style={'color': "#f1c40f", 'border': '1px solid #f1c40f', 'padding': '10px 25px', 'borderRadius': '10px', 'backgroundColor': 'rgba(241, 196, 15, 0.05)', 'fontSize': '18px'}),
                            html.Div(dcc.Markdown(id='stat-min', mathjax=True, style={'margin': 0}), style={'color': '#e74c3c', 'border': '1px solid #e74c3c', 'padding': '10px 25px', 'borderRadius': '10px', 'backgroundColor': 'rgba(231, 76, 60, 0.05)', 'fontSize': '18px'})
                        ])
                    ], style={'flex': '1', 'backgroundColor': '#000', 'display': 'flex', 'flexDirection': 'column'}),
                    
                    html.Div([
                        html.H3("STRESS TEST ANALYSIS", style={'color': '#3498db', 'marginTop': 0, 'fontSize': '16px', 'fontFamily': 'sans-serif', 'letterSpacing': '1px'}),
                        dcc.Markdown("""
This simulation projects thousands of possible future paths over the next 30 days based on the asset's historical behavior. 

Instead of showing a messy web of lines, we aggregate the outcomes into clear probability zones:

* **Green Band (Top 1%):** The best-case optimistic scenarios.
* **Yellow Line (Mean):** The average expected trajectory.
* **Red Band (Bottom 1%):** The critical danger zone.

**Focusing on the Downside**

The dashed red line dynamically tracks the **Expected Shortfall (ES)**. While the previous chart showed you *where* the worst days start, this line estimates *how much* you are actually expected to lose when a severe crash happens over a 30-day period.

**Investor Insight**

Compare the final stats below the chart. If the potential minimum loss (Min) drastically outweighs the potential maximum gain (Max), the asset carries extreme asymmetrical risk.
                        """, style={'color': '#bbb', 'fontSize': '15px', 'lineHeight': '1.6'})
                    ], style=explanation_box_style)
                    
                ], style={'display': 'flex', 'minHeight': 'calc(100vh - 164px)', 'padding': '15px', 'boxSizing': 'border-box'})
            ], style={'backgroundColor': '#111', 'color': '#888', 'border': 'none', 'padding': '10px'}, 
               selected_style={'backgroundColor': '#000', 'color': '#fff', 'borderTop': '2px solid #3498db', 'borderBottom': 'none', 'padding': '10px'}),

            dcc.Tab(label='Market Connections', value='tab-network', children=[
                html.Div([
                    
                    dcc.Store(id='selected-network-date', data=None),
                    dcc.Store(id='node-click-memory', data=None),
                    
                    
                    html.Div([
                        html.H3("STRESS EVENTS (Click)", style={'fontSize': '20px', 'color': '#e74c3c', 'marginBottom': '10px'}),
                        html.Div(id='extreme-dates-list-network', style={'fontSize': '18px', 'maxHeight': '800px', 'overflowY': 'auto', 'paddingRight': '5px'})
                    ], style={'width': '200px', 'padding': '15px', 'borderRight': '1px solid #333', 'backgroundColor': '#0a0a0a', 'height': '100%', 'boxSizing': 'border-box'}),
                    
                    
                    html.Div([
                        dcc.Graph(
                            id='network-graph', 
                            config={'displayModeBar': False}, 
                            mathjax=True, 
                            style={'height': '100%', 'width': '100%'} 
                        )
                    ], style={'flex': '1', 'display': 'flex', 'flexDirection': 'column', 'height': '100%'}),
                    
                    
                    html.Div([
                        html.H3("CONTAGION TOPOLOGY ANALYSIS", style={'color': '#3498db', 'marginTop': 0, 'fontSize': '16px', 'fontFamily': 'sans-serif', 'letterSpacing': '1px'}),
                        dcc.Markdown(r"""
This star network visualizes interconnected market dependency during extreme stress events. 

When your main asset crashes, shocks transmit across corporate boundaries. Use this topology to read the direction of market pressure:

**Systemic Risk Amplifiers (Top Hemisphere - Red)**
Assets mapped to the upper section fall alongside your main stock. A thick line indicates high statistical dependency ($\rho$), signaling that a crash here will heavily drag down or multiply losses in your focal asset due to systemic contagion.

**Defensive Shields & Safe Havens (Bottom Hemisphere - Green)**
Assets in the lower section move independently or in opposite directions during a crash, serving as natural portfolio hedges.

**Trading Volume & Scale**
The size of each peripheral node reflects its trading volume. Large bubbles indicate heavy market capitalization and institutional liquidity, showing you whether your portfolio shields or risk threats are major market players or smaller assets.
                        """,mathjax=True, style={'color': '#bbb', 'fontSize': '15px', 'lineHeight': '1.6'})
                        
                    
                    ], style=dict(explanation_box_style, **{'height': '100%', 'overflowY': 'auto'})), 
                    
                
                ], style={'display': 'flex', 'height': 'calc(100vh - 164px)', 'padding': '15px', 'boxSizing': 'border-box'})
                
            ], style={'backgroundColor': '#111', 'color': '#888', 'border': 'none', 'padding': '10px'}, 
               selected_style={'backgroundColor': '#000', 'color': '#fff', 'borderTop': '2px solid #e74c3c', 'borderBottom': 'none', 'padding': '10px'}),
                           
            dcc.Tab(label='Global Contagion', value='tab-map', children=[
                dcc.Store(id='selected-map-date', data=None),
                
                html.Div([
                    
                    
                    html.Div([
                        html.Div([
                            html.H3("STRESS EVENTS (Click)", style={'fontSize': '20px', 'color': '#e74c3c', 'marginBottom': '10px'}),
                            html.Div(id='extreme-dates-list-map', className='custom-radio', style={'fontSize': '18px', 'maxHeight': '320px', 'overflowY': 'auto', 'paddingRight': '5px'})
                        ], style={'marginBottom': '20px'}),
                        
                        html.Hr(style={'borderColor': '#333', 'margin': '0 0 15px 0', 'width': '100%'}),
                        
                        html.Div([
                            html.H3("SAFE HAVENS", style={'fontSize': '20px', 'color': '#2ecc71', 'marginBottom': '10px'}),
                            html.Div(id='safe-havens-list', style={'fontSize': '18px', 'maxHeight': '320px', 'overflowY': 'auto', 'paddingRight': '5px'})
                        ])
                    ], style={
                        'width': '250px', 'minWidth': '250px', 'padding': '15px', 
                        'borderRight': '1px solid #333', 'backgroundColor': '#0a0a0a', 
                        'boxSizing': 'border-box'
                        
                    }),
                    
                   
                    html.Div([
                        
                      
                        html.Div([
                            dcc.RadioItems(
                                id='map-vis-type',
                                className='custom-radio',
                                options=[
                                    {'label': ' Δρ (Shock)', 'value': 'delta'},
                                    {'label': ' ρ (Stress)', 'value': 'stress'},
                                    {'label': ' ρ (Calm)', 'value': 'calm'}
                                ],
                                value='delta', 
                                inline=True, 
                                style={'display': 'flex', 'alignItems': 'center', 'color': 'white', 'marginRight': '30px'},
                                
                                labelStyle={'cursor': 'pointer', 'marginRight': '10px', 'fontFamily': '"EB Garamond", serif', 'fontSize': '16px', 'whiteSpace': 'nowrap'}
                            ),
                            
                            html.Span("Pre-shock Calm Period: ", style={'color': 'white', 'fontSize': '14px', 'marginRight': '10px', 'fontFamily': 'sans-serif', 'whiteSpace': 'nowrap'}),
                            
                            dcc.RadioItems(
                                id='calm-period-type',
                                className='custom-radio',
                                options=[
                                    {'label': '1 Month', 'value': '1M'},
                                    {'label': '3 Months', 'value': '3M'},
                                    {'label': '1 Year', 'value': '1Y'}
                                ],
                                value='1M', 
                                inline=True, 
                                style={'display': 'flex', 'alignItems': 'center'},
                                
                                labelStyle={'cursor': 'pointer', 'marginRight': '10px', 'fontFamily': 'sans-serif', 'fontSize': '14px', 'fontWeight': 'bold'}
                            )
                        
                        ], style={'padding': '10px 20px', 'backgroundColor': '#111', 'borderBottom': '1px solid #333', 'display': 'flex', 'flexDirection': 'row', 'alignItems': 'center', 'flexWrap': 'nowrap'}),
                        
                        
                        html.Div([
                            dcc.Graph(
                                id='contagion-map', 
                                className='clicavel', 
                                mathjax=True, 
                                config={'displayModeBar': False},
                                style={'flex': '1', 'width': '100%', 'height': '100%'} 
                            )
                        ], style={'flex': '1', 'display': 'flex', 'flexDirection': 'column'})
                        
                    ], style={'flex': '1', 'display': 'flex', 'flexDirection': 'column', 'backgroundColor': '#000'}),
                    
                    
                    html.Div([
                        html.H3("GLOBAL CONTAGION ANALYSIS", style={'color': '#3498db', 'marginTop': 0, 'fontSize': '16px', 'fontFamily': 'sans-serif', 'letterSpacing': '1px'}),
                        dcc.Markdown(r"""
This Dorling cartogram maps geographic shock transmission, scaling countries by trading volume to remove area bias.

**Visual Metric Guide:**
* **Red Bubbles:** Markets where dependency spiked ($\Delta\rho > 0$) during the crash (High Contagion).
* **Blue Bubbles:** Markets that decoupled ($\Delta\rho < 0$), absorbing the shock efficiently.
* **Bubble Size:** Represents market liquidity and trading volume.

**Portfolio Protection:**
Check the **Safe Havens** sidebar. It automatically filters countries where the shock dropped ($\Delta\rho < 0$) *and* absolute stress correlation remained negative or zero ($\rho_{\text{stress}} \le 0$). Use these assets as your core structural diversifiers.
                        """, mathjax=True, style={'color': '#bbb', 'fontSize': '15px', 'lineHeight': '1.6'})
                    ], style=dict(explanation_box_style, **{
                        'width': '300px',            
                        'minWidth': '300px', 
                        'margin': '15px',            
                        'boxSizing': 'border-box',
                        'display': 'flex',
                        'flexDirection': 'column',
                        'justifyContent': 'flex-start',
                        'height': 'auto'             
                    }))
                    
                ], style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'stretch', 'minHeight': 'calc(100vh - 164px)', 'backgroundColor': '#000'}) 
                
            ], style={'backgroundColor': '#111', 'color': '#888', 'border': 'none', 'padding': '10px'}, 
               selected_style={'backgroundColor': '#000', 'color': '#fff', 'borderTop': '2px solid #2ecc71', 'borderBottom': 'none', 'padding': '10px'})

        ], style={'height': '44px', 'backgroundColor': '#111', 'borderBottom': '1px solid #333'})
    ])

    
    estilo_aba_inativa = {
        'backgroundColor': '#222222', 
        'color': '#888888',           
        'fontSize': '18px',           
        'fontWeight': 'bold',
        'border': '1px solid #333',   
        'padding': '12px'             
    }

    estilo_aba_ativa = {
    'backgroundColor': '#111111',
    'color': '#d4af37',               
    'fontSize': '18px',
    'fontWeight': 'bold',
    'borderTop': '3px solid #d4af37', 
    'borderBottom': 'none',
    'borderLeft': '1px solid #333',
    'borderRight': '1px solid #333',
    'padding': '12px'
    }

    
    return html.Div([
        stores_and_modals, 
        
        dcc.Tabs(
            id="main-tabs",
            value='tab-story', 
            children=[
                
                dcc.Tab(
                    label='Story Mode', 
                    value='tab-story',
                    style=estilo_aba_inativa,
                    selected_style=estilo_aba_ativa,
                    children=[story_sections] 
                ),
                
                dcc.Tab(
                    label='Main Dashboard', 
                    value='tab-main',
                    style=estilo_aba_inativa,
                    selected_style=estilo_aba_ativa,
                    children=[dashboard_content] 
                )
            ],
            style={'backgroundColor': '#111111'} 
        )
    ])