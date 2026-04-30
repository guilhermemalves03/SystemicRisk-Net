from dash import Input, Output, State, no_update, ALL, callback_context, html
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from scipy.stats import norm, gaussian_kde
import json
from plotly.colors import sample_colorscale
from layout import COUNTRY_COORDS

LATEX_FONT = dict(family="EB Garamond, serif", size=16)

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

def register_callbacks(app, engine):
    
    @app.callback(
        [Output('volatility-modal', 'style'), Output('volatility-graph', 'figure')],
        [Input('contagion-map', 'clickData'), Input('close-modal-btn', 'n_clicks')],
        [State('volatility-modal', 'style'), State('selected-stress-date', 'data')]
    )
    def toggle_modal(clickData, close_clicks, modal_style, selected_date):
        ctx = callback_context
        if not ctx.triggered: return no_update, no_update
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'close-modal-btn':
            modal_style['display'] = 'none'
            return modal_style, go.Figure()
        if trigger_id == 'contagion-map' and clickData:
            try:
                ticker = clickData['points'][0]['customdata']
                if isinstance(ticker, list): ticker = ticker[0]
            except KeyError: return no_update, no_update
                
            vol_data = engine.get_realized_volatility(ticker)
            if vol_data is None: return no_update, no_update
            
            fig = go.Figure(go.Scatter(x=vol_data.index, y=vol_data.values, mode='lines', line=dict(color='#e74c3c', width=2)))
            
            if selected_date:
                fig.add_vline(x=selected_date, line_dash="dash", line_color="#39FF14")
                fig.add_annotation(x=selected_date, y=0.95, yref="paper", text="Stress Event", showarrow=False, xanchor="left", font=dict(color="#39FF14", size=14))

            fig.update_layout(title=rf"$\text{{Annualized Realized Volatility (21d) - }} {ticker}$", template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=40, r=20, t=50, b=40), font=LATEX_FONT, yaxis_tickformat='.2%')
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
        if 'date' in prop_id: return json.loads(prop_id)['date']
        return no_update

    @app.callback(
        [Output('animation-interval', 'disabled', allow_duplicate=True),
         Output('animation-frame', 'data', allow_duplicate=True)],
        [Input('tabs', 'value')], prevent_initial_call=True
    )
    def auto_play_mc(tab_value):
        if tab_value == 'tab-mc': return False, 0 
        return no_update, no_update

    @app.callback(
        [Output('intro-apple-dist', 'figure'), Output('distribution-graph', 'figure'), Output('ridgeline-graph', 'figure'),
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
        fig_dist.add_trace(go.Bar(
            x=bin_centers[bin_centers > var_limit], 
            y=counts[bin_centers > var_limit], 
            marker_color='#333', 
            name=r'$\text{Normal}$', # <--- MUDAR AQUI
            showlegend=True # Ativei para veres a legenda
        ))        
        
        fig_dist.add_trace(go.Bar(
            x=bin_centers[bin_centers <= var_limit], 
            y=counts[bin_centers <= var_limit], 
            marker_color='#c0392b', 
            name=r'$\text{Tail Stress}$', # <--- MUDAR AQUI
            showlegend=True
        ))
        
        x_range = np.linspace(filtered_returns.min(), filtered_returns.max(), 250)
        fig_dist.add_trace(go.Scatter(x=x_range, y=gaussian_kde(filtered_returns)(x_range), name=r'$\text{KDE}$', line=dict(color='#3498db', width=2.5)))
        fig_dist.add_trace(go.Scatter(x=x_range, y=norm.pdf(x_range, filtered_returns.mean(), filtered_returns.std()), name=r'$\text{Gaussian}$', line=dict(color='#777', dash='dash', width=1.5)))
        
        fig_dist.add_vline(x=var_limit, line_dash="dash", line_color="#e74c3c")
        fig_dist.add_annotation(x=var_limit, y=0.95, yref="paper", text=rf"$VaR_{{99\%}} = {var_limit*100:.2f}\%$", showarrow=False, font=dict(color="#e74c3c", size=16), bgcolor="rgba(0,0,0,0.5)")

        fig_dist.update_layout(title=rf"$\text{{Aggregated Return Distribution: }} \text{{{selected_ticker}}}$", font=LATEX_FONT, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=40, r=20, t=50, b=10), xaxis_title=r"$\Delta \ln(P_t)$")

        fig_ridge = go.Figure()
        df_returns = pd.DataFrame({'return': filtered_returns})
        df_returns['Month'] = df_returns.index.to_period('M')
        
        unique_months = df_returns['Month'].unique()[-12:] 
        colors = sample_colorscale('Aggrnyl', np.linspace(0, 1, len(unique_months)))
        
        for i, month in enumerate(unique_months):
            month_data = df_returns[df_returns['Month'] == month]['return']
            if len(month_data) > 2:
                m_ret = month_data.mean()
                q_str = f"Q{month.quarter}"
                month_label = f"{month.strftime('%b %Y')} ({q_str})"
                
                fig_ridge.add_trace(go.Violin(x=month_data, y=[month_label] * len(month_data), name=month_label, line_color='white', line_width=1, fillcolor=colors[i], opacity=0.9, side='positive', width=3.5, orientation='h', points=False, showlegend=False))
                fig_ridge.add_annotation(x=m_ret, y=month_label, text=f"μ: {m_ret*100:.2f}%", showarrow=False, yshift=18, bgcolor="rgba(0,0,0,0.7)", bordercolor=colors[i], font=dict(color="white", size=11, family="sans-serif"))

        fig_ridge.update_layout(title=rf"$\text{{Ridgeline Plot (Last 12 Months)}}$", xaxis_title=r"$\Delta \ln(P_t)$", font=LATEX_FONT, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=20, t=30, b=40), violingap=0, violingroupgap=0, violinmode='overlay')

        list_items = [html.Div([html.Span(d.strftime('%Y-%m-%d')), html.Span(f" {extreme_days[d]:.2%}", style={'float':'right','color':'#e74c3c'})], style={'padding':'4px 0','borderBottom':'1px solid #111'}) for d in extreme_days.sort_index(ascending=False).index]

        list_items_clickable = [html.Button([html.Span(d.strftime('%Y-%m-%d'), style={'fontWeight': 'bold'}), html.Span(f" {extreme_days[d]:.2%}", style={'float':'right','color':'#ff6b6b'})], id={'type': 'stress-date-btn', 'date': d.strftime('%Y-%m-%d')}, style={'width': '100%', 'backgroundColor': '#1e1e1e', 'border': '1px solid #444', 'borderRadius': '5px', 'color': '#eee', 'textAlign': 'left', 'cursor': 'pointer', 'padding': '8px 10px', 'marginBottom': '6px', 'fontFamily': 'inherit', 'fontSize': '14px'}) for d in extreme_days.sort_index(ascending=False).index]

        paths, sim_es = engine.run_monte_carlo(n_sims=80)
        return fig_dist, fig_dist, fig_ridge, list_items, list_items_clickable, paths.tolist(), sim_es, False, 0

    @app.callback(
        [Output('intro-apple-dist', 'figure', allow_duplicate=True),
         Output('zoom-btn-intro', 'children')], # <-- NOVO: Controlar o texto do botão
        [Input('zoom-btn-intro', 'n_clicks')],
        [State('intro-apple-dist', 'figure')],
        prevent_initial_call=True
    )
    def toggle_intro_zoom(n_clicks, fig):
        if fig is None: return no_update, no_update
        
        patched_fig = go.Figure(fig)
        patched_fig.update_layout(transition=dict(duration=500, easing="cubic-in-out"))
        
        if n_clicks % 2 == 1:
            # --- ESTADO: ZOOM IN ---
            x_min, x_max = -0.065, -0.015  # <-- CORRIGIDO: Corta o espaço vazio à esquerda
            max_y = 0
            
            for trace in patched_fig.data:
                if trace.x is not None and trace.y is not None:
                    try:
                        x_vals = np.array(trace.x, dtype=float)
                        y_vals = np.array(trace.y, dtype=float)
                        mask = (x_vals >= x_min) & (x_vals <= x_max)
                        
                        if np.any(mask):
                            local_max = np.max(y_vals[mask])
                            if local_max > max_y:
                                max_y = local_max
                    except (ValueError, TypeError):
                        continue
                            
            if max_y == 0: max_y = 5 
            
            patched_fig.update_xaxes(autorange=False, range=[x_min, x_max])
            patched_fig.update_yaxes(autorange=False, range=[0, max_y * 1.1])
            patched_fig.update_layout(title_text=r"$\text{Left Tail Focus (Extreme Losses)}$")
            
            btn_text = "WHOLE DISTRIBUTION" # <-- Muda o texto do botão
            
        else:
            patched_fig.update_xaxes(autorange=True)
            patched_fig.update_yaxes(autorange=True)
            patched_fig.update_layout(title_text=r"$\text{Aggregated Return Distribution: AAPL}$")
            
            btn_text = "ZOOM: LEFT TAIL" # <-- Volta ao texto original
            
        return patched_fig, btn_text

    @app.callback(
        [Output('intro-contagion-map', 'figure'), 
         Output('asia-impact-table', 'children'),
         Output('zoom-asia-btn', 'children')],
        [Input('main-asset-dropdown', 'value'), Input('zoom-asia-btn', 'n_clicks')],
        [State('intro-contagion-map', 'figure')]
    )
    def update_intro_map_and_table(main_ticker, n_clicks, current_fig):
        target_date = '2025-10-10'
        calm_period = '1M'
        
        engine.set_main_asset(main_ticker)
        country_assets = engine.assets_df[engine.assets_df['sector'] == 'Country']
        map_rows = []
        target_countries = ['China', 'Hong Kong', 'Singapore', 'Vietnam']
        table_data = []


        # 1. LÓGICA DE ZOOM MOVIDA PARA CIMA (Cartesiano)
        if n_clicks is None or n_clicks == 0:
            # ESTADO 0: Limites assimétricos! 
            # Cortamos o oceano à esquerda (-140) e damos folga à Nova Zelândia na direita (190)
            x_range = [-140, 190] 
            y_range = [-60, 80]
            btn_text = "ZOOM: ASIA FOCUS"
            trans_cfg = None  
        elif n_clicks % 2 == 1:
            # ESTADO 1: Zoom na Ásia
            x_range = [60, 160]
            y_range = [-20, 60]
            btn_text = "WORLD VIEW"
            trans_cfg = dict(duration=500, easing="cubic-in-out")
        else:
            # ESTADO 2: Voltar à Visão Mundial (Iguais ao Estado 0)
            x_range = [-140, 190]
            y_range = [-60, 80]
            btn_text = "ZOOM: ASIA FOCUS"
            trans_cfg = dict(duration=500, easing="cubic-in-out")

            
        # 2. PROCESSAMENTO DE DADOS
        for _, row in country_assets.iterrows():
            metrics = engine.get_event_contagion(row['ticker'], target_date, calm_period)
            if metrics:
                (delta_rho, stress_rho, _), (delta_vol, _, _) = metrics
                coords = COUNTRY_COORDS.get(row['country'])
                if coords:
                    map_rows.append({'Val': delta_rho, 'Vol': abs(delta_vol), 'Lat': coords[0], 'Lon': coords[1], 'Country': row['country'], 'Ticker': row['ticker']})
                
                if row['country'] in target_countries:
                    table_data.append({'Country': row['country'], 'Jump': delta_rho})
        
        if not map_rows:
            fig = go.Figure()
            fig.update_layout(title=f"Sem dados para {target_date}", template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            return fig, html.Div(), "ZOOM: ASIA FOCUS"
            
        # 3. CÁLCULO E DESENHO DAS BOLHAS DE DORLING
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
            fig_map.add_trace(go.Scatter(x=cx, y=cy, fill='toself', fillcolor=colors[i], line=dict(color='white', width=1.5), mode='lines', name=map_rows[i]['Country'], text=f"<b>{map_rows[i]['Country']}</b><br>Δρ: {c_vals[i]:.2f}", hoverinfo='text', showlegend=False))
            fig_map.add_trace(go.Scatter(x=[new_x[i]], y=[new_y[i]], mode='text', text=[map_rows[i]['Ticker']], textfont=dict(color='white', size=11, family="sans-serif"), hoverinfo='skip', showlegend=False))

        # 4. LAYOUT FINAL E ANIMAÇÃO
        fig_map.update_layout(
            # Título usando texto normal e caracteres Unicode. Nunca falha!
            title=f"Shock (Δρ) - {target_date} (Calm: 1M)",
            title_x=0.5,
            title_y=0.92,   
            font=LATEX_FONT, 
            template="plotly_dark",
            
            # Controla o zoom e a proporção matemática (círculos perfeitos)
            xaxis=dict(visible=False, range=x_range, autorange=False), 
            yaxis=dict(visible=False, range=y_range, scaleanchor="x", scaleratio=1, autorange=False),
            
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            # Aumentámos a margem de topo (t) para 60 para garantir que o título tem espaço
            margin=dict(l=0, r=0, t=30, b=0),
            transition=trans_cfg,
            uirevision='constant' # Impede os bugs teimosos de redimensionamento do Plotly
        )
        # 5. CONSTRUÇÃO DA TABELA
        table_header = html.Thead(html.Tr([html.Th("Country"), html.Th("Correlation Jump (Δρ)")]))
        
        rows = []
        for d in sorted(table_data, key=lambda x: x['Jump'], reverse=True):
            display_value = f"{d['Jump']:+.4f}"
            intensity = min(abs(d['Jump']) + 0.3, 1.0) 
            
            if d['Jump'] < 0:
                text_color = f"rgba(52, 152, 219, {intensity})"
            else:
                text_color = f"rgba(231, 76, 60, {intensity})"
            
            rows.append(html.Tr([
                html.Td(d['Country']), 
                html.Td(display_value, style={'color': text_color, 'fontWeight': 'bold'})
            ]))

        table_body = html.Tbody(rows)
        
        impact_table = html.Table(
            [table_header, table_body], 
            className='intro-table', 
            style={'width': '100%', 'color': '#fff', 'borderCollapse': 'collapse', 'fontSize': '1.2em'}
        )

        # 6. RETORNO CORRIGIDO (impact_table em vez de table_div)
        return fig_map, impact_table, btn_text

    @app.callback(
        [Output('contagion-map', 'figure'), Output('safe-havens-list', 'children')],
        [Input('selected-stress-date', 'data'), Input('map-vis-type', 'value'), 
         Input('calm-period-selector', 'value'), Input('main-asset-dropdown', 'value')]
    )
    def render_map(selected_date, vis_type, calm_period, main_ticker):
        engine.set_main_asset(main_ticker)
        extreme_days, _, _ = engine.get_extreme_events(months=12)
        target_date = selected_date if selected_date else (extreme_days.index[-1].strftime('%Y-%m-%d') if not extreme_days.empty else None)
        
        if not target_date: return go.Figure(), [html.Div("Insufficient data.")]

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
                    map_rows.append({'Val': val, 'Vol': vol, 'Delta': delta_rho, 'Stress': stress_rho, 'Lat': coords[0], 'Lon': coords[1], 'Name': row['name'], 'Country': row['country'], 'Ticker': row['ticker']})
        
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
            fig_map.add_trace(go.Scatter(x=cx, y=cy, fill='toself', fillcolor=colors[i], line=dict(color='white', width=1.5), mode='lines', name=map_rows[i]['Country'], text=f"<b>{map_rows[i]['Country']}</b><br>Metric: {c_vals[i]:.2f}<br>Δ Volume: {v_vals[i]:.2%}", customdata=[map_rows[i]['Ticker']] * len(cx), hoverinfo='text', showlegend=False))
            fig_map.add_trace(go.Scatter(x=[new_x[i]], y=[new_y[i]], mode='text', text=[map_rows[i]['Ticker']], textfont=dict(color='white', size=11, family="sans-serif"), hoverinfo='skip', showlegend=False))

        fig_map.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(colorscale='RdBu_r', cmin=-1, cmax=1, showscale=True, colorbar=dict(title="ρ", thickness=15)), hoverinfo='none', showlegend=False))
        fig_map.update_layout(title=rf"$\text{{Systemic Risk Cartogram - }} {target_date}$", font=LATEX_FONT, template="plotly_dark", xaxis=dict(visible=False, scaleanchor="y", scaleratio=1), yaxis=dict(visible=False), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=50, b=10))

        safe_havens = sorted([row for row in map_rows if row['Delta'] < 0 and row['Stress'] <= 0], key=lambda x: x['Stress'])
        safe_list_items = [html.Div([html.Span(sh['Country']), html.Span("{:.2f}".format(sh['Delta']), style={'float':'right','color':'#2ecc71'})], style={'padding':'6px 0','borderBottom':'1px solid #222'}) for sh in safe_havens]
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
        
        # 1. Converter para NumPy
        paths = np.array(paths)
        
        # Se o frame já chegou ao fim (30 dias), paramos a animação e não fazemos nada
        if frame >= 30:
            return no_update, frame, True, no_update, no_update, no_update

        # 2. VETORIZAÇÃO: Em vez de loops, calculamos as bandas de risco para a matriz inteira de uma vez!
        mean_path = np.mean(paths, axis=1)[:frame+1]
        lower_bound = np.percentile(paths, 1, axis=1)[:frame+1]
        upper_bound = np.percentile(paths, 99, axis=1)[:frame+1]
        
        x_vals = np.arange(frame + 1)
        base_line = np.ones_like(x_vals) 
        
        # 3. Estatísticas do frame atual
        current_vals = paths[frame, :] - 1
        max_val, mean_val, min_val = np.max(current_vals), np.mean(current_vals), np.min(current_vals)
        
        str_max = rf"$\text{{Max: }} {max_val*100:+.2f}\%$"
        str_mean = rf"$\text{{Mean: }} {mean_val*100:+.2f}\%$"
        str_min = rf"$\text{{Worst: }} {min_val*100:+.2f}\%$"
        
        # 4. Construir a figura MUITO mais leve (sem fillgradient)
        fig_mc = go.Figure()
        fig_mc.add_trace(go.Scatter(x=x_vals, y=base_line, mode='lines', line=dict(width=0), showlegend=False))
        fig_mc.add_trace(go.Scatter(x=x_vals, y=lower_bound, mode='lines', fill='tonexty', fillcolor='rgba(231, 76, 60, 0.2)', line=dict(width=1, color='#FF0000', shape='spline'), showlegend=False))
        fig_mc.add_trace(go.Scatter(x=x_vals, y=base_line, mode='lines', line=dict(width=0), showlegend=False))
        fig_mc.add_trace(go.Scatter(x=x_vals, y=upper_bound, mode='lines', fill='tonexty', fillcolor='rgba(46, 204, 113, 0.2)', line=dict(width=1, color='#39FF14', shape='spline'), showlegend=False))
        fig_mc.add_trace(go.Scatter(x=x_vals, y=mean_path, mode='lines', line=dict(width=2, color='#FFFFFF', shape='spline'), showlegend=False))

        # Congelar os eixos Y para não tremerem durante a animação
        y_min, y_max = np.min(paths) * 0.95, np.max(paths) * 1.05

        # Se for o último frame (Dia 30)
        if frame == 29: 
            final_es_ret = lower_bound[-1] - 1
            fig_mc.add_hline(y=lower_bound[-1], line_dash="dash", line_color="#FF0000", annotation_text=rf"$ES_{{1\%}} = {final_es_ret*100:.2f}\%$", annotation_position="bottom left", annotation_font=dict(color="#FF0000", size=16))
            fig_mc.update_layout(title=r"$\text{Simulated Paths: } S_t = S_0 \exp\left(\sum r_i\right)$", font=LATEX_FONT, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=40, r=20, t=50, b=40), xaxis=dict(range=[0, 30]), yaxis=dict(range=[y_min, y_max]))
            
            # Devolvemos frame + 1, e metemos disabled=True para parar
            return fig_mc, frame + 1, True, str_max, str_mean, str_min
        
        # Frames do Dia 0 ao Dia 28
        fig_mc.update_layout(title=f"Monte Carlo Projection (Day {frame}/30)", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=LATEX_FONT, margin=dict(l=40, r=20, t=50, b=40), xaxis=dict(range=[0, 30]), yaxis=dict(range=[y_min, y_max]))
        
        return fig_mc, frame + 1, False, str_max, str_mean, str_min    

    @app.callback(
        [Output('intro-mc-sim', 'figure'),
         Output('mc-paths-btn', 'children'),
         Output('intro-stat-max', 'children'),  # <-- NOVO: Caixa Max
         Output('intro-stat-mean', 'children'), # <-- NOVO: Caixa Mean
         Output('intro-stat-min', 'children')], # <-- NOVO: Caixa Min
        [Input('mc-paths-btn', 'n_clicks'), Input('mc-paths-store', 'data')]
    )
    def toggle_intro_mc(n_clicks, paths_data):
        if paths_data is None: 
            return go.Figure(), no_update, "", "", ""
        
        paths = np.array(paths_data) # [31 steps, 80 sims]
        x_vals = np.arange(len(paths))
        show_paths = n_clicks % 2 == 1
        
        fig = go.Figure()
        fig.update_layout(transition=dict(duration=500, easing="cubic-in-out"))

        if show_paths:
            # Mostrar caminhos individuais coloridos
            colors = sample_colorscale('Rainbow', np.linspace(0, 1, 40))
            for i in range(40):
                fig.add_trace(go.Scatter(
                    x=x_vals, y=paths[:, i], 
                    mode='lines', line=dict(width=1, color=colors[i]),
                    opacity=0.5, showlegend=False
                ))
            title = r"$\text{Random Walk Simulations (Bootstrapping)}$"
            btn_text = "SHOW RISK BANDS" 
            
        else:
            # Mostrar a visualização agregada
            mean_path = np.mean(paths, axis=1)
            lower_bound = np.percentile(paths, 1, axis=1)
            upper_bound = np.percentile(paths, 99, axis=1)
            base_line = np.ones_like(x_vals)

            fig.add_trace(go.Scatter(x=x_vals, y=base_line, mode='lines', line=dict(width=0), showlegend=False))
            fig.add_trace(go.Scatter(x=x_vals, y=upper_bound, mode='lines', fill='tonexty', 
                                     fillcolor='rgba(46, 204, 113, 0.1)', line=dict(width=1, color='#2ecc71'), showlegend=False))
            fig.add_trace(go.Scatter(x=x_vals, y=base_line, mode='lines', line=dict(width=0), showlegend=False))
            fig.add_trace(go.Scatter(x=x_vals, y=lower_bound, mode='lines', fill='tonexty', 
                                     fillcolor='rgba(231, 76, 60, 0.1)', line=dict(width=1, color='#e74c3c'), showlegend=False))
            fig.add_trace(go.Scatter(x=x_vals, y=mean_path, mode='lines', line=dict(width=3, color='#FFFFFF'), showlegend=False))
            title = r"$\text{Aggregated Expected Shortfall (Risk Bands)}$"
            btn_text = "SHOW INDIVIDUAL PATHS" 

        fig.update_layout(
            title=title, title_x=0.5, font=LATEX_FONT, template="plotly_dark",
            xaxis_title="Days", yaxis_title=r"$\text{Price Multiplier } (S_t / S_0)$",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=20, t=50, b=40)
        )

        # --- NOVA LÓGICA DAS ESTATÍSTICAS ---
        # Vamos buscar a última linha de dados (o dia 30) de todas as simulações
        final_returns = paths[-1, :] - 1
        
        # Calculamos os valores finais reais para as caixas
        max_val = np.max(final_returns)
        mean_val = np.mean(final_returns)
        min_val = np.min(final_returns)

        # Formatamos em LaTeX para ficar elegante e com cores
        str_max = rf"$\text{{Max: }} {max_val*100:+.2f}\%$"
        str_mean = rf"$\text{{Mean: }} {mean_val*100:+.2f}\%$"
        str_min = rf"$\text{{Worst: }} {min_val*100:+.2f}\%$"

        return fig, btn_text, str_max, str_mean, str_min    

    @app.callback(
        [Output('intro-network-graph', 'figure'),
         Output('network-highlight-btn', 'children')],
        [Input('main-asset-dropdown', 'value'), Input('network-highlight-btn', 'n_clicks')]
    )
    def update_intro_network(main_ticker, n_clicks):
        target_date = '2025-10-10'
        engine.set_main_asset(main_ticker)

        top_pos, top_neg = engine.get_network_data(target_date, top_n=4)
        fig = go.Figure()

        if not top_pos:
            return fig, "HIGHLIGHT SAFE HAVENS"

        show_safe = n_clicks % 2 == 1

        # --- Lógica de desenho ---
        def add_nodes_edges(nodes, angles, color, is_top, highlight_mode):
            x_nodes, y_nodes, texts, hover_texts = [], [], [], []
            for i, node in enumerate(nodes):
                x, y = np.cos(angles[i]), np.sin(angles[i])
                x_nodes.append(x)
                y_nodes.append(y)
                texts.append(node['ticker'])
                hover_texts.append(f"{node['name']}<br>ρ: {node['rho']:.2f}")

                line_opacity = 0.1 if (highlight_mode and is_top) else 0.6
                edge_width = max(1, abs(node['rho']) * 6)

                fig.add_trace(go.Scatter(x=[0, x], y=[0, y], mode='lines',
                                         line=dict(width=edge_width, color=color),
                                         opacity=line_opacity, hoverinfo='none', showlegend=False))

            node_opacity = 0.15 if (highlight_mode and is_top) else 1.0
            fig.add_trace(go.Scatter(x=x_nodes, y=y_nodes, mode='markers+text', text=texts,
                                     textposition="top center" if is_top else "bottom center",
                                     textfont=dict(color=f'rgba(255,255,255,{node_opacity})', size=13),
                                     marker=dict(size=25, color=color, opacity=node_opacity, 
                                                 line=dict(width=1, color=f'rgba(255,255,255,{node_opacity})')),
                                     hovertext=hover_texts, hoverinfo='text', showlegend=False,
                                     cliponaxis=False)) # Impede corte do texto

        # Adicionar os grupos
        pos_angles = np.linspace(np.pi/6, 5*np.pi/6, len(top_pos))
        add_nodes_edges(top_pos, pos_angles, '#e74c3c', is_top=True, highlight_mode=show_safe)

        neg_angles = np.linspace(7*np.pi/6, 11*np.pi/6, len(top_neg))
        add_nodes_edges(top_neg, neg_angles, '#2ecc71', is_top=False, highlight_mode=show_safe)

        # Nó Central
        fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers+text', text=[f"<b>{main_ticker}</b>"],
                                 textposition="middle center", textfont=dict(color='black', size=14),
                                 marker=dict(size=45, color='#f1c40f', line=dict(width=2, color='white')),
                                 hoverinfo='text', name='Center', showlegend=False, cliponaxis=False))

        # --- CORREÇÃO DEFINITIVA (Fim dos bugs de escala) ---
        # Eixos fixos, ancorados para ser um círculo perfeito, COM limites cravados em 2.2.
        x_axis = dict(visible=False, range=[-1.7, 1.7], autorange=False)
        y_axis = dict(visible=False, range=[-1.7, 1.7], autorange=False, scaleanchor="x", scaleratio=1)

        fig.update_layout(
            title=rf"$\text{{Contagion Network - }} {target_date}$", title_x=0.5,
            font=LATEX_FONT, template="plotly_dark",
            xaxis=x_axis,
            yaxis=y_axis,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=50, b=40),
            uirevision='constant' # Tranca a visão para impedir auto-zoom
            # A PROPRIEDADE 'transition' FOI REMOVIDA DAQUI!
        )

        btn_text = "SHOW FULL NETWORK" if show_safe else "HIGHLIGHT SAFE HAVENS"
        return fig, btn_text
        
    @app.callback(
        Output('network-graph', 'figure'),
        [Input('selected-stress-date', 'data'), Input('main-asset-dropdown', 'value')]
    )
    def render_network(selected_date, main_ticker):
        engine.set_main_asset(main_ticker)
        extreme_days, _, _ = engine.get_extreme_events(months=12)
        target_date = selected_date if selected_date else (extreme_days.index[-1].strftime('%Y-%m-%d') if not extreme_days.empty else None)
        
        if not target_date:
            return go.Figure()

        top_pos, top_neg = engine.get_network_data(target_date, top_n=4)
        if not top_pos:
            return go.Figure()

        fig = go.Figure()

        # Função auxiliar para desenhar nós e arestas
        def add_nodes_edges(nodes, angles, color, is_top):
            x_nodes, y_nodes, texts, hover_texts = [], [], [], []
            
            for i, node in enumerate(nodes):
                x, y = np.cos(angles[i]), np.sin(angles[i])
                x_nodes.append(x)
                y_nodes.append(y)
                texts.append(node['ticker'])
                hover_texts.append(f"{node['name']}<br>ρ: {node['rho']:.2f}")
                
                # Espessura da aresta baseada na correlação
                edge_width = max(1, abs(node['rho']) * 6)
                
                fig.add_trace(go.Scatter(x=[0, x], y=[0, y], mode='lines', 
                                         line=dict(width=edge_width, color=color), 
                                         opacity=0.6, hoverinfo='none', showlegend=False))
            
            fig.add_trace(go.Scatter(x=x_nodes, y=y_nodes, mode='markers+text', text=texts,
                                     textposition="top center" if is_top else "bottom center",
                                     textfont=dict(color='white', size=13),
                                     marker=dict(size=25, color=color, line=dict(width=1, color='white')),
                                     hovertext=hover_texts, hoverinfo='text', showlegend=False))

        # Arestas e Nós de Contágio (Superiores)
        pos_angles = np.linspace(np.pi/6, 5*np.pi/6, len(top_pos))
        add_nodes_edges(top_pos, pos_angles, '#e74c3c', is_top=True)

        # Arestas e Nós de Proteção (Inferiores)
        neg_angles = np.linspace(7*np.pi/6, 11*np.pi/6, len(top_neg))
        add_nodes_edges(top_neg, neg_angles, '#2ecc71', is_top=False)

        # Nó Central (Desenhado no fim para ficar por cima das linhas)
        fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers+text', text=[f"<b>{main_ticker}</b>"], 
                                 textposition="middle center", textfont=dict(color='black', size=14),
                                 marker=dict(size=45, color='#f1c40f', line=dict(width=2, color='white')),
                                 hoverinfo='text', name='Center', showlegend=False))

        # Limpar os eixos e o fundo
        fig.update_layout(title=rf"$\text{{Contagion Network - }} {target_date}$",
                          font=LATEX_FONT, template="plotly_dark",
                          xaxis=dict(visible=False, range=[-1.5, 1.5]),
                          yaxis=dict(visible=False, range=[-1.5, 1.5]),
                          plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
                          margin=dict(l=20, r=20, t=50, b=20))

        return fig