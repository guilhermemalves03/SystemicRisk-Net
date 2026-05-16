from dash import Input, Output, State, no_update, ALL, callback_context, html
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from scipy.stats import norm, gaussian_kde
import json
from plotly.colors import sample_colorscale
from layout import COUNTRY_COORDS
import textwrap
import copy
import dash

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

    app.clientside_callback(
        """
        function(current_value) {
            setTimeout(function() {
                var dropdown = document.getElementById('main-asset-dropdown');
                if (dropdown) {
                    var el = dropdown.querySelector('.Select-control') || 
                             dropdown.querySelector('div[class*="control"]') || 
                             dropdown;
                    
                    el.style.animation = 'none';
                    void el.offsetWidth; // Força o reflow do browser para reiniciar a animação
                    el.style.animation = 'flash-blue 0.8s ease-in-out';
                }
            }, 60);
            return '';
        }
        """,
        Output('main-asset-dropdown', 'className'),
        Input('main-asset-dropdown', 'value'),
        prevent_initial_call=True
    )
    
    @app.callback(
        [Output('volatility-modal', 'style'), 
         Output('volatility-graph', 'figure'),
         Output('contagion-map', 'clickData')], 
        [Input('contagion-map', 'clickData'), 
         Input('close-modal-btn', 'n_clicks')],
        [State('volatility-modal', 'style'), 
         State('selected-map-date', 'data'), # <--- CORREÇÃO 1: Lê o store correto do mapa
         State('main-asset-dropdown', 'value')] 
    )
    def toggle_modal(clickData, close_clicks, modal_style, selected_date, main_ticker):
        ctx = callback_context
        if not ctx.triggered: return no_update, no_update, no_update 
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'close-modal-btn':
            modal_style['display'] = 'none'
            return modal_style, go.Figure(), None 
            
        if trigger_id == 'contagion-map' and clickData:
            try:
                ticker = clickData['points'][0]['customdata']
                if isinstance(ticker, list): ticker = ticker[0]
            except KeyError: return no_update, no_update, no_update
                
            vol_data_country = engine.get_realized_volatility(ticker)
            if vol_data_country is None: return no_update, no_update, no_update
            
            vol_data_main = engine.get_realized_volatility(main_ticker)
            
            try:
                row_c = engine.assets_df[engine.assets_df['ticker'] == ticker].iloc[0]
                nome_clicado = row_c['country']
            except:
                nome_clicado = ticker 
                
            try:
                row_m = engine.assets_df[engine.assets_df['ticker'] == main_ticker].iloc[0]
                nome_principal = row_m['name']
            except:
                nome_principal = main_ticker

            fig = go.Figure()
            
            if vol_data_main is not None:
                fig.add_trace(go.Scatter(
                    x=vol_data_main.index, 
                    y=vol_data_main.values, 
                    mode='lines', 
                    name=nome_principal,
                    line=dict(color='#3498db', width=2, dash='dot'), 
                    opacity=0.7
                ))

            fig.add_trace(go.Scatter(
                x=vol_data_country.index, 
                y=vol_data_country.values, 
                mode='lines', 
                name=nome_clicado,
                line=dict(color='#e74c3c', width=2) 
            ))
            
            # <--- CORREÇÃO 2: Garante a data por defeito se o utilizador ainda não clicou na lista
            if not selected_date:
                extreme_days, _, _ = engine.get_extreme_events(months=12)
                if not extreme_days.empty:
                    selected_date = extreme_days.index[-1].strftime('%Y-%m-%d')

            if selected_date:
                fig.add_vline(x=selected_date, line_dash="dash", line_color="#39FF14", layer="below")
                fig.add_annotation(x=selected_date, y=0.95, yref="paper", text="Stress Event", 
                                   showarrow=False, xanchor="left", font=dict(color="#39FF14", size=14))

            clean_title = f"Volatility: {nome_clicado} vs {nome_principal}"

            fig.update_layout(
                title=clean_title, 
                template="plotly_dark", 
                plot_bgcolor='rgba(0,0,0,0)', 
                paper_bgcolor='rgba(0,0,0,0)', 
                margin=dict(l=40, r=20, t=50, b=40), 
                font=LATEX_FONT, 
                hovermode='x unified', 
                hoverlabel=dict(bgcolor="rgba(17, 17, 17, 0.95)", font_color="white", bordercolor="rgba(255, 255, 255, 0.1)"),
                xaxis=dict(showgrid=False, zeroline=False, showspikes=True, spikecolor="#f1c40f", spikethickness=1, spikedash="dash", spikemode="across"),
                yaxis=dict(tickformat='.2%', showgrid=False, zeroline=False),
                legend=dict(
    orientation="v",           
    yanchor="top",             
    y=0.98,                    
    xanchor="right",           
    x=0.98,                    
    bgcolor="rgba(17, 17, 17, 1)",          # <-- CORREÇÃO: Fundo totalmente opaco (cor do modal)
    bordercolor="rgba(255, 255, 255, 0.2)", # <-- Bónus: Uma borda fina para destacar do gráfico
    borderwidth=1
)
            )
            
            modal_style['display'] = 'block'
            return modal_style, fig, no_update
            
        return no_update, no_update, no_update

    @app.callback(
        Output('selected-stress-date', 'data'),
        [Input({'type': 'stress-date-btn', 'date': ALL}, 'n_clicks')],
        [State({'type': 'stress-date-btn', 'date': ALL}, 'id')]
    )
    def update_selected_date(n_clicks, ids):
        ctx = callback_context
        
        # Se nada disparou a função, ignora
        if not ctx.triggered: 
            return no_update
            
        # O valor do disparo (o número de cliques)
        triggered_value = ctx.triggered[0]['value']
        
        # A MAGIA ESTÁ AQUI: Se for None, significa que o botão acabou de ser criado e não foi clicado!
        if triggered_value is None:
            return no_update
            
        # Se passou a barreira, é um clique real. Extrair a data:
        prop_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if 'date' in prop_id: 
            return json.loads(prop_id)['date']
            
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
        [
         Output('intro-apple-dist', 'figure'), 
         Output('intro-mc-paths-store', 'data'),
         Output('distribution-graph', 'figure'), 
         Output('ridgeline-graph', 'figure'),
         Output('extreme-dates-list', 'children'), 
         Output('mc-paths-store', 'data'), 
         Output('mc-es-store', 'data'), 
         Output('animation-interval', 'disabled'), 
         Output('animation-frame', 'data'),
        ],
        [Input('main-asset-dropdown', 'value')]
    )
    def setup_analysis(selected_ticker):
        
        # ========================================================
        # FASE 1: DASHBOARD PRINCIPAL (Usa a Dropdown)
        # ========================================================
        engine.set_main_asset(selected_ticker)
        extreme_days, var_limit, filtered_returns = engine.get_extreme_events(months=12)
        
        counts, bin_edges = np.histogram(filtered_returns, bins=80, density=True)
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
        
        fig_dist_main = go.Figure()
        
        # --- APLICADO O HOVERTEMPLATE NAS BARRAS ---
        fig_dist_main.add_trace(go.Bar(x=bin_centers[bin_centers > var_limit], y=counts[bin_centers > var_limit], marker_color='#333', name=r'$\text{Normal}$', showlegend=True,
                                       hovertemplate='Return: %{x:.2%}<br>Count: %{y:.1f}<extra>Normal</extra>'))        
        fig_dist_main.add_trace(go.Bar(x=bin_centers[bin_centers <= var_limit], y=counts[bin_centers <= var_limit], marker_color='#c0392b', name=r'$\text{Tail Stress}$', showlegend=True,
                                       hovertemplate='Return: %{x:.2%}<br>Count: %{y:.1f}<extra>Tail Stress</extra>'))
        
        x_range = np.linspace(filtered_returns.min(), filtered_returns.max(), 250)
        
        # --- APLICADO O HOVERTEMPLATE NAS LINHAS ---
        fig_dist_main.add_trace(go.Scatter(x=x_range, y=gaussian_kde(filtered_returns)(x_range), name=r'$\text{KDE}$', line=dict(color='#3498db', width=2.5),
                                           hovertemplate='Return: %{x:.2%}<br>Density: %{y:.4f}<extra>KDE</extra>'))
        fig_dist_main.add_trace(go.Scatter(x=x_range, y=norm.pdf(x_range, filtered_returns.mean(), filtered_returns.std()), name=r'$\text{Gaussian}$', line=dict(color='#777', dash='dash', width=1.5),
                                           hovertemplate='Return: %{x:.2%}<br>Density: %{y:.4f}<extra>Gaussian</extra>'))
        
        fig_dist_main.add_vline(x=var_limit, line_dash="dash", line_color="#e74c3c")
        fig_dist_main.add_annotation(x=var_limit, y=0.95, yref="paper", text=rf"$VaR_{{99\%}} = {var_limit*100:.2f}\%$", showarrow=False, font=dict(color="#e74c3c", size=16), bgcolor="rgba(0,0,0,0.5)")
        fig_dist_main.update_layout(
            title=rf"$\text{{Aggregated Return Distribution}}$", font=LATEX_FONT, 
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            margin=dict(l=40, r=20, t=50, b=10), xaxis_title=r"$\Delta \ln(P_t)$",
            xaxis=dict(tickformat='.0%')
        )

        fig_ridge = go.Figure()
        df_returns = pd.DataFrame({'return': filtered_returns})
        df_returns['Month'] = df_returns.index.to_period('M')
        unique_months = df_returns['Month'].unique()[-12:] 
        colors = sample_colorscale('Aggrnyl', np.linspace(0, 1, len(unique_months)))
        
        for i, month in enumerate(unique_months):
            month_data = df_returns[df_returns['Month'] == month]['return']
            if len(month_data) > 2:
                m_ret = month_data.mean()
                month_label = f"{month.strftime('%b %Y')}"
                fig_ridge.add_trace(go.Violin(x=month_data, y=[month_label] * len(month_data), name=month_label, line_color='white', line_width=1, fillcolor=colors[i], opacity=0.9, side='positive', width=3.5, orientation='h', points=False, showlegend=False, hoverinfo='skip'))
                fig_ridge.add_annotation(x=m_ret, y=month_label, text=f"μ: {m_ret*100:.2f}%", showarrow=False, yshift=18, bgcolor="rgba(0,0,0,0.7)", bordercolor=colors[i], font=dict(color="white", size=11, family="sans-serif"))
        
        fig_ridge.update_layout(
            title=rf"$\text{{Ridgeline Plot (Last 12 Months)}}$", xaxis_title=r"$\Delta \ln(P_t)$", font=LATEX_FONT, 
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            margin=dict(l=10, r=20, t=30, b=40), violingap=0, violingroupgap=0, violinmode='overlay',
            xaxis=dict(tickformat='.0%')
        )

        list_items = [html.Div([
            html.Span(d.strftime('%Y-%m-%d'), style={'color': '#eee'}), 
            html.Span(f" {extreme_days[d]:.2%}", style={'float':'right','color':'#e74c3c'})
        ], style={'padding':'4px 0','borderBottom':'1px solid #111'}) for d in extreme_days.sort_index(ascending=False).index]

        main_paths, sim_es = engine.run_monte_carlo(n_sims=80)

        # ========================================================
        # FASE 2: MODO HISTÓRIA (Fica SEMPRE preso na AAPL)
        # ========================================================
        engine.set_main_asset('AAPL')
        i_extreme_days, i_var_limit, i_filtered_returns = engine.get_extreme_events(months=12)
        
        i_counts, i_bin_edges = np.histogram(i_filtered_returns, bins=80, density=True)
        i_bin_centers = (i_bin_edges[:-1] + i_bin_edges[1:]) / 2
        
        fig_dist_intro = go.Figure()
        
        # --- APLICADO O HOVERTEMPLATE NAS BARRAS (STORY MODE) ---
        fig_dist_intro.add_trace(go.Bar(x=i_bin_centers[i_bin_centers > i_var_limit], y=i_counts[i_bin_centers > i_var_limit], marker_color='#333', name=r'$\text{Normal}$', showlegend=True,
                                        hovertemplate='Return: %{x:.2%}<br>Count: %{y:.1f}<extra>Normal</extra>'))        
        fig_dist_intro.add_trace(go.Bar(x=i_bin_centers[i_bin_centers <= i_var_limit], y=i_counts[i_bin_centers <= i_var_limit], marker_color='#c0392b', name=r'$\text{Tail Stress}$', showlegend=True,
                                        hovertemplate='Return: %{x:.2%}<br>Count: %{y:.1f}<extra>Tail Stress</extra>'))
        
        i_x_range = np.linspace(i_filtered_returns.min(), i_filtered_returns.max(), 250)
        
        # --- APLICADO O HOVERTEMPLATE NAS LINHAS (STORY MODE) ---
        fig_dist_intro.add_trace(go.Scatter(x=i_x_range, y=gaussian_kde(i_filtered_returns)(i_x_range), name=r'$\text{KDE}$', line=dict(color='#3498db', width=2.5),
                                            hovertemplate='Return: %{x:.2%}<br>Density: %{y:.4f}<extra>KDE</extra>'))
        fig_dist_intro.add_trace(go.Scatter(x=i_x_range, y=norm.pdf(i_x_range, i_filtered_returns.mean(), i_filtered_returns.std()), name=r'$\text{Gaussian}$', line=dict(color='#777', dash='dash', width=1.5),
                                            hovertemplate='Return: %{x:.2%}<br>Density: %{y:.4f}<extra>Gaussian</extra>'))
        
        fig_dist_intro.add_vline(x=i_var_limit, line_dash="dash", line_color="#e74c3c")
        fig_dist_intro.add_annotation(x=i_var_limit, y=0.95, yref="paper", text=rf"$VaR_{{99\%}} = {i_var_limit*100:.2f}\%$", showarrow=False, font=dict(color="#e74c3c", size=16), bgcolor="rgba(0,0,0,0.5)")
        
        orig_min = i_filtered_returns.min()
        orig_max = i_filtered_returns.max()
        pad = (orig_max - orig_min) * 0.05
        
        fig_dist_intro.update_layout(
            title=rf"$\text{{Aggregated Return Distribution: AAPL}}$", font=LATEX_FONT, 
            template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
            margin=dict(l=40, r=20, t=50, b=10), xaxis_title=r"$\Delta \ln(P_t)$",
            xaxis=dict(
                tickformat='.0%',
                range=[orig_min - pad, orig_max + pad], 
                autorange=False 
            ),
            yaxis=dict(
                range=[0, 65], 
                autorange=False
            )
        )
        
        intro_paths, _ = engine.run_monte_carlo(n_sims=80)
        
        fig_dist_intro.update_xaxes(fixedrange=True)
        fig_dist_intro.update_yaxes(fixedrange=True)
        fig_dist_intro.update_layout(dragmode=False)
        fig_dist_main.update_xaxes(fixedrange=True)
        fig_dist_main.update_yaxes(fixedrange=True)
        fig_dist_main.update_layout(dragmode=False)
        fig_ridge.update_xaxes(fixedrange=True)
        fig_ridge.update_yaxes(fixedrange=True)
        fig_ridge.update_layout(dragmode=False)
        
        return (
            fig_dist_intro, intro_paths.tolist(),  
            fig_dist_main, fig_ridge, list_items, main_paths.tolist(), sim_es, False, 0
        )
    
    @app.callback(
        [Output('container-distribution', 'style'),
        Output('container-ridgeline', 'style'),
        Output('toggle-risk-graphs-btn', 'children')],
        [Input('toggle-risk-graphs-btn', 'n_clicks')]
    )
    def toggle_risk_graphs(n_clicks):
        # O estilo quando a caixa deve aparecer
        estilo_visivel = {'display': 'flex', 'flexDirection': 'column', 'width': '100%'}
        # O estilo quando a caixa deve desaparecer completamente
        estilo_escondido = {'display': 'none'}
        
        # Se o número de cliques for par (ou 0 ao iniciar)
        if n_clicks % 2 == 0:
            texto_botao = "SHOW RIDGELINE PLOT"
            # Mostra o Distribution, esconde o Ridgeline
            return estilo_visivel, estilo_escondido, texto_botao
            
        # Se o número de cliques for ímpar
        else:
            texto_botao = "SHOW DISTRIBUTION PLOT"
            # Esconde o Distribution, mostra o Ridgeline
            return estilo_escondido, estilo_visivel, texto_botao
        

    @app.callback(
        [Output('intro-apple-dist', 'figure', allow_duplicate=True),
         Output('zoom-btn-intro', 'children', allow_duplicate=True)],
        [Input('zoom-btn-intro', 'n_clicks'),
         Input('focus-example-btn', 'n_clicks')],
        [State('intro-apple-dist', 'figure')],
        prevent_initial_call=True
    )
    def toggle_intro_graph_interactions(n_clicks_zoom, n_clicks_focus, fig):
        if fig is None: return no_update, no_update
        
        ctx = callback_context
        if not ctx.triggered:
            return no_update, no_update
            
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        new_fig = copy.deepcopy(fig)
        
        # 1. ATIVAR A ANIMAÇÃO SUAVE NOVAMENTE!
        if 'layout' not in new_fig: new_fig['layout'] = {}
        new_fig['layout']['transition'] = dict(duration=600, easing="cubic-in-out")
        
        btn_text = no_update
        
        # Limites exatos (o gráfico já foi gerado trancado no setup_analysis com estes valores)
        engine.set_main_asset('AAPL')
        _, _, i_filtered_returns = engine.get_extreme_events(months=12)
        pad = (i_filtered_returns.max() - i_filtered_returns.min()) * 0.05
        REAL_X_MIN = i_filtered_returns.min() - pad
        REAL_X_MAX = i_filtered_returns.max() + pad
        GLOBAL_Y_MAX = 65 
        
        ZOOM_X_MIN, ZOOM_X_MAX = -0.065, -0.015
        ZOOM_Y_MAX = 15 
        
        n_clicks_zoom = n_clicks_zoom or 0
        is_zoomed = (n_clicks_zoom % 2 == 1)
        
        # =========================================================
        # BOTÃO VERMELHO (ZOOM)
        # =========================================================
        if trigger_id == 'zoom-btn-intro':
            if is_zoomed:
                new_fig['layout']['xaxis']['range'] = [ZOOM_X_MIN, ZOOM_X_MAX]
                new_fig['layout']['yaxis']['range'] = [0, ZOOM_Y_MAX]
                new_fig['layout']['title'] = {'text': r"$\text{Left Tail Focus (Extreme Losses)}$"}
                btn_text = "WHOLE DISTRIBUTION"
            else:
                new_fig['layout']['xaxis']['range'] = [REAL_X_MIN, REAL_X_MAX]
                new_fig['layout']['yaxis']['range'] = [0, GLOBAL_Y_MAX]
                new_fig['layout']['title'] = {'text': r"$\text{Aggregated Return Distribution: AAPL}$"}
                btn_text = "ZOOM: LEFT TAIL"
                
        # =========================================================
        # BOTÃO VERDE (CASE STUDY)
        # =========================================================
        elif trigger_id == 'focus-example-btn':
            n_clicks_focus = n_clicks_focus or 0
            show_highlight = (n_clicks_focus % 2 == 1)
            
            new_fig['data'] = [t for t in new_fig.get('data', []) if t.get('name') != 'Case Study']
            
            if show_highlight:
                counts, bin_edges = np.histogram(i_filtered_returns, bins=80, density=True)
                bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
                
                target_val = -0.03513  
                idx = (np.abs(bin_centers - target_val)).argmin()
                target_x = bin_centers[idx]
                target_y = counts[idx]
                
                bar_width = bin_centers[1] - bin_centers[0]
                
                new_fig['data'].append({
                    'type': 'bar',
                    'x': [target_x],
                    'y': [target_y],
                    'width': [bar_width],
                    'name': 'Case Study',
                    'marker': {'color': '#39FF14'}
                })
                new_fig['layout']['barmode'] = 'overlay'

            # Respeitar os limites mantendo a animação intacta
            if is_zoomed:
                new_fig['layout']['xaxis']['range'] = [ZOOM_X_MIN, ZOOM_X_MAX]
                new_fig['layout']['yaxis']['range'] = [0, ZOOM_Y_MAX]
            else:
                new_fig['layout']['xaxis']['range'] = [REAL_X_MIN, REAL_X_MAX]
                new_fig['layout']['yaxis']['range'] = [0, GLOBAL_Y_MAX]

            new_fig['layout']['xaxis']['fixedrange'] = True
            new_fig['layout']['yaxis']['fixedrange'] = True
            new_fig['layout']['dragmode'] = False

        return new_fig, btn_text
    
    @app.callback(
        [Output('intro-contagion-map', 'figure'), 
         Output('asia-impact-table', 'children'),
         Output('zoom-asia-btn', 'children')],
        [Input('zoom-asia-btn', 'n_clicks')],         # <-- APAGAMOS O INPUT DA DROPDOWN
        [State('intro-contagion-map', 'figure')]
    )
    def update_intro_map_and_table(n_clicks, current_fig):

        main_ticker = 'AAPL'
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
            fig_map.add_trace(go.Scatter(x=cx, y=cy, fill='toself', fillcolor=colors[i], line=dict(color=colors[i], width=1.5), mode='lines', name=map_rows[i]['Country'], text=f"<b>{map_rows[i]['Country']}</b><br>Δρ: {c_vals[i]:.2f}", hoverinfo='text', showlegend=False))
            fig_map.add_trace(go.Scatter(x=[new_x[i]], y=[new_y[i]], mode='text', text=[map_rows[i]['Ticker']], textfont=dict(color='black', size=11, family="sans-serif"), hoverinfo='skip', showlegend=False))

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
        # O novo cabeçalho visualmente separado
        # Cabeçalho com linha horizontal mais subida e separador vertical
        table_header = html.Tr([
            html.Th("Country", style={
                'textAlign': 'center', 
                'color': '#ffffff',             
                'borderBottom': '2px solid #333333', 
                'borderRight': '1px solid #333333',  # <-- NOVA LINHA VERTICAL (Lado Direito)
                'paddingBottom': '4px',              # <-- DIMINUÍDO para subir a linha horizontal
                'paddingRight': '15px',              # Empurra o texto para não colar à linha vertical
                'textTransform': 'uppercase',   
                'fontSize': '0.85em',           
                'letterSpacing': '1px',
                'width': '50%',
                'fontWeight': 'bold'
            }),
            html.Th("Correlation Jump (Δρ)", style={
                'textAlign': 'center', 
                'color': '#ffffff', 
                'borderBottom': '2px solid #333333', 
                'paddingBottom': '4px',              # <-- DIMINUÍDO para subir a linha horizontal
                'paddingLeft': '15px',               # Afasta o texto da linha vertical
                'textTransform': 'uppercase',
                'fontSize': '0.85em',
                'letterSpacing': '1px',
                'width': '50%',
                'fontWeight': 'bold'
            })
        ])
        
        rows = []
        for d in sorted(table_data, key=lambda x: x['Jump'], reverse=True):
            display_value = f"{d['Jump']:+.4f}"
            intensity = min(abs(d['Jump']) + 0.3, 1.0) 
            
            if d['Jump'] < 0:
                text_color = f"rgba(52, 152, 219, {intensity})" # Azul
            else:
                text_color = f"rgba(231, 76, 60, {intensity})"  # Vermelho
            
            # Nota: Usa d['Country'] ou d['name'] dependendo de como chamaste a chave no teu dicionário table_data
            nome_pais = d.get('Country', d.get('name', 'N/A')) 

            rows.append(html.Tr([
                html.Td(nome_pais, style={
                    'textAlign': 'center',
                    'borderRight': '1px solid #333333', 
                    'padding': '8px 15px 8px 0',        
                    'fontSize': '1.1em',
                    'color': '#ffffff'  # Mantém o nome do país a branco para leitura clara
                }),
                html.Td(display_value, style={
                    'textAlign': 'center',
                    'padding': '8px 0 8px 15px',        
                    'fontSize': '1.1em',
                    'color': text_color, # <-- APLICA A COR DINÂMICA AQUI!
                    'fontWeight': 'bold' # Negrito nos números fica excelente com as cores
                })
            ]))

        table_body = html.Tbody(rows)
        
        impact_table = html.Table(
            [table_header, table_body], 
            className='intro-table', 
            style={'width': '100%', 'color': '#fff', 'borderCollapse': 'collapse', 'fontSize': '1.2em'}
        )
        
        fig_map.update_layout(dragmode=False)
        # 6. RETORNO CORRIGIDO (impact_table em vez de table_div)
        return fig_map, impact_table, btn_text

    # 1. Função que GERA OS BOTÕES do Mapa e pinta de roxo
    @app.callback(
        Output('extreme-dates-list-map', 'children'),
        [Input('main-asset-dropdown', 'value'),
         Input('selected-map-date', 'data')]
    )
    def update_map_dates_list(main_ticker, selected_date):
        engine.set_main_asset(main_ticker)
        extreme_days, _, _ = engine.get_extreme_events(months=12)
        
        if extreme_days.empty:
            return []
            
        if not selected_date:
            selected_date = extreme_days.sort_index(ascending=False).index[0].strftime('%Y-%m-%d')
            
        buttons = []
        for d in extreme_days.sort_index(ascending=False).index:
            date_str = d.strftime('%Y-%m-%d')
            
            # Lógica das Cores
            is_selected = (date_str == selected_date)
            bg_color = '#e74c3c' if is_selected else '#1e1e1e'
            border_color = '#e74c3c' if is_selected else '#444'
            
            btn = html.Button([
                html.Span(date_str, style={'fontWeight': 'bold', 'color': '#fff'}), 
                html.Span(f" {extreme_days[d]:.2%}", style={'float':'right','color': '#fff' if is_selected else '#ff6b6b'})
            ], 
            id={'type': 'map-date-btn', 'date': date_str}, # <-- ID específico para o mapa
            style={
                'width': '100%', 'backgroundColor': bg_color, 'border': f'1px solid {border_color}', 
                'borderRadius': '5px', 'textAlign': 'left', 'cursor': 'pointer', 
                'padding': '8px 10px', 'marginBottom': '6px', 'fontFamily': 'inherit', 'fontSize': '14px',
                'transition': 'background-color 0.3s'
            })
            buttons.append(btn)
            
        return buttons

    # 2. Função que ESCUTA O CLIQUE do Mapa (Agora com Reset automático)
    @app.callback(
        Output('selected-map-date', 'data'),
        [Input({'type': 'map-date-btn', 'date': ALL}, 'n_clicks'),
         Input('main-asset-dropdown', 'value')], # <-- LÊ AGORA A MUDANÇA DE EMPRESA!
        prevent_initial_call=True
    )
    def handle_map_date_click(n_clicks_list, main_ticker):
        ctx = callback_context
        if not ctx.triggered:
            return no_update
            
        prop_id = ctx.triggered[0]['prop_id']
        
        # O SEGREDO: Se o que disparou a função foi mudar a empresa, apaga a data!
        if 'main-asset-dropdown' in prop_id:
            return None
            
        # Se foi mesmo um clique num botão de data
        if "{" in prop_id:
            btn_id_dict = json.loads(prop_id.split('.')[0])
            return btn_id_dict['date']
            
        return no_update

    @app.callback(
        [Output('contagion-map', 'figure'), Output('safe-havens-list', 'children')],
        [Input('selected-map-date', 'data'), 
         Input('map-vis-type', 'value'), 
         Input('calm-period-selector', 'value'), 
         Input('main-asset-dropdown', 'value')]
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
            fig_map.add_trace(go.Scatter(x=cx, y=cy, fill='toself', fillcolor=colors[i], line=dict(color=colors[i], width=1.5), mode='lines', name=map_rows[i]['Country'], text=f"<b>{map_rows[i]['Country']}</b><br>Metric: {c_vals[i]:.2f}<br>Δ Volume: {v_vals[i]:.2%}", customdata=[map_rows[i]['Ticker']] * len(cx), hoverinfo='text', showlegend=False))
            fig_map.add_trace(go.Scatter(
                x=[new_x[i]], 
                y=[new_y[i]], 
                mode='text', 
                text=[map_rows[i]['Ticker']], 
                customdata=[map_rows[i]['Ticker']], # <--- A SOLUÇÃO ESTÁ AQUI
                textfont=dict(color='black', size=11, family="sans-serif"), 
                hoverinfo='skip', 
                showlegend=False
            ))

        # Traço invisível apenas para mostrar a barra de cores
        fig_map.add_trace(go.Scatter(
            x=[None], y=[None], 
            mode='markers', 
            marker=dict(
                colorscale='RdBu_r', 
                cmin=-1, 
                cmax=1, 
                showscale=True, 
                colorbar=dict(
                    title=dict(text="ρ scale", side="top"), # <--- O SEGREDO ESTÁ AQUI (move para o topo da barra)
                    thickness=15,
                    orientation="h",                  # Garante que é horizontal
                    y=-0.1,                           # Empurra a barra ligeiramente para baixo (opcional, ajusta se precisares)
                    yanchor="top",
                    len=0.6
                )
            ), 
            hoverinfo='none', 
            showlegend=False
        ))
        
        # --- CORREÇÃO AQUI: Margens ajustadas (b=80, t=60) para a barra de cor ter espaço e não ficar cortada ---
        fig_map.update_layout(title=rf"$\text{{Systemic Risk Cartogram - }} {target_date}$", font=LATEX_FONT, template="plotly_dark", xaxis=dict(visible=False, scaleanchor="y", scaleratio=1), yaxis=dict(visible=False), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=60, b=80))

        safe_havens = sorted([row for row in map_rows if row['Delta'] < 0 and row['Stress'] <= 0], key=lambda x: x['Stress'])
        
        safe_list_items = [
            html.Div([
                html.Span(sh['Country'], style={'color': '#eee'}), 
                html.Span("{:.2f}".format(sh['Delta']), style={'float':'right','color':'#2ecc71'})
            ], style={'padding':'6px 0','borderBottom':'1px solid #222'}) 
            for sh in safe_havens
        ]
        
        if not safe_list_items: 
            safe_list_items = [html.Div("No safe havens.", style={'color': '#777'})]

        fig_map.update_layout(dragmode=False)

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
        if frame > 30:
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
        str_min = rf"$\text{{Min: }} {min_val*100:+.2f}\%$"
        
        # 4. Construir a figura MUITO mais leve (sem fillgradient)
        fig_mc = go.Figure()
        fig_mc.add_trace(go.Scatter(x=x_vals, y=base_line, mode='lines', line=dict(width=0), showlegend=False))
        fig_mc.add_trace(go.Scatter(x=x_vals, y=lower_bound, mode='lines', fill='tonexty', fillcolor='rgba(231, 76, 60, 0.2)', line=dict(width=1, color='#FF0000', shape='spline'), showlegend=False))
        fig_mc.add_trace(go.Scatter(x=x_vals, y=base_line, mode='lines', line=dict(width=0), showlegend=False))
        fig_mc.add_trace(go.Scatter(x=x_vals, y=upper_bound, mode='lines', fill='tonexty', fillcolor='rgba(46, 204, 113, 0.2)', line=dict(width=1, color='#39FF14', shape='spline'), showlegend=False))
        fig_mc.add_trace(go.Scatter(x=x_vals, y=mean_path, mode='lines', line=dict(width=2, color='#f1c40f', shape='spline'), showlegend=False))

        # Congelar os eixos Y para não tremerem durante a animação
        y_min, y_max = np.min(paths) * 0.95, np.max(paths) * 1.05

        # --- APLICAR O BLOQUEIO A TODOS OS FRAMES (INCLUINDO O ÚLTIMO) ---
        fig_mc.update_xaxes(fixedrange=True)
        fig_mc.update_yaxes(fixedrange=True)
        fig_mc.update_layout(dragmode=False)
        fig_mc.update_traces(hoverinfo='skip')

        # Se for o último frame (Dia 30)
        if frame == 30: 
            final_es_ret = lower_bound[-1] - 1
            fig_mc.add_hline(y=lower_bound[-1], line_dash="dash", line_color="#FF0000", annotation_text=rf"$ES_{{1\%}} = {final_es_ret*100:.2f}\%$", annotation_position="bottom left", annotation_font=dict(color="#FF0000", size=16))
            fig_mc.update_layout(title=r"$\text{Simulated Paths: }$", font=LATEX_FONT, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=40, r=20, t=50, b=40), xaxis=dict(range=[0, 30]), yaxis=dict(range=[y_min, y_max]))
            
            # Devolvemos frame + 1, e metemos disabled=True para parar
            return fig_mc, frame + 1, True, str_max, str_mean, str_min
        
        # Frames do Dia 0 ao Dia 29
        fig_mc.update_layout(title=f"Monte Carlo Projection (Day {frame}/30)", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=LATEX_FONT, margin=dict(l=40, r=20, t=50, b=40), xaxis=dict(range=[0, 30]), yaxis=dict(range=[y_min, y_max]))
        
        return fig_mc, frame + 1, False, str_max, str_mean, str_min  

    @app.callback(
    [Output('intro-mc-sim', 'figure'),
     Output('mc-paths-btn', 'children'),
     Output('intro-stat-max', 'children'),  
     Output('intro-stat-mean', 'children'), 
     Output('intro-stat-min', 'children')], 
    [Input('mc-paths-btn', 'n_clicks'), Input('intro-mc-paths-store', 'data')] 
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
            fig.add_trace(go.Scatter(x=x_vals, y=mean_path, mode='lines', line=dict(width=3, color='#f1c40f'), showlegend=False))
            title = r"$\text{Aggregated Expected Shortfall (Risk Bands)}$"
            btn_text = "SHOW INDIVIDUAL PATHS" 
        
        fig.update_layout(
            title=title, title_x=0.5, font=LATEX_FONT, template="plotly_dark",
            xaxis_title="Days", yaxis_title=r"$\text{Price Multiplier } $",
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
        str_mean = rf"$\text{{Mean: }} {mean_val*100:+.2f}\%$"  # <-- Tira o \color{#f1c40f}
        str_min = rf"$\text{{Min: }} {min_val*100:+.2f}\%$"

        fig.update_xaxes(fixedrange=True)
        fig.update_yaxes(fixedrange=True)
        fig.update_layout(dragmode=False)
        fig.update_traces(hoverinfo='skip')

        return fig, btn_text, str_max, str_mean, str_min    

    @app.callback(
        [Output('intro-network-graph', 'figure'),
         Output('network-highlight-btn', 'children')],
        [Input('network-highlight-btn', 'n_clicks')] 
    )
    def update_intro_network(n_clicks):

        main_ticker = 'AAPL'   
        target_date = '2025-10-10'
        engine.set_main_asset(main_ticker)

        # 1. OBTER O NOME DA EMPRESA PRINCIPAL
        try:
            main_name = engine.assets_df.loc[engine.assets_df['ticker'] == main_ticker, 'name'].values[0]
        except:
            main_name = main_ticker

        top_pos, top_neg = engine.get_network_data(target_date, top_n=5)
        fig = go.Figure()

        top_pos = [node for node in top_pos if node['ticker'] != main_ticker][:4]
        top_neg = [node for node in top_neg if node['ticker'] != main_ticker][:4]

        if not top_pos:
            return go.Figure(), no_update

        show_safe = n_clicks % 2 == 1

        # =====================================================================
        # LÓGICA DE NORMALIZAÇÃO DO VOLUME (Tamanhos entre 20px e 55px)
        # =====================================================================
        # (O novo código perfeito)
        all_nodes = top_pos + top_neg
        vols = [n.get('volume', 0.0) for n in all_nodes] # O Motor já fez o trabalho difícil!
        min_v, max_v = (min(vols), max(vols)) if vols else (0, 0)
        
        def get_size(v):
            if max_v == min_v or max_v == 0: return 25
            return 20 + ((v - min_v) / (max_v - min_v)) * 35
        
        min_v, max_v = (min(vols), max(vols)) if vols else (0, 0)
        
        def get_size(v):
            if max_v == min_v or max_v == 0: return 25 # Tamanho base de segurança
            return 20 + ((v - min_v) / (max_v - min_v)) * 35 # Matemática de Escala

        # --- Lógica de desenho para o Modo História (COM highlight_mode) ---
        def add_nodes_edges(nodes, angles, color, is_top, highlight_mode):
            x_nodes, y_nodes, hover_texts = [], [], []
            custom_data = [] 
            node_sizes = [] # <--- NOVA LISTA PARA GUARDAR OS TAMANHOS DE CADA BOLA
            
            for i, node in enumerate(nodes):
                delta_val = node.get('delta', node['rho'])
                distance = max(0.4, 1.8 - (abs(delta_val) * 1.5))
                
                x, y = distance * np.cos(angles[i]), distance * np.sin(angles[i])
                x_nodes.append(x)
                y_nodes.append(y)
                
                edge_width = 1 + (abs(node['rho']) ** 2.5) * 20
                
                # --- CALCULAR O TAMANHO COM BASE NO VOLUME ---
                vol = node.get('volume', 0.0)
                node_sizes.append(get_size(vol))
                
                # Atualizar o hover para mostrar o volume formatado!
                vol_text = f"{vol:,.0f}" if vol > 0 else "N/A"
                hover_texts.append(f"Ticker: {node['ticker']}<br>Força (ρ): {node['rho']:.2f}<br>Salto (Δρ): {delta_val:.2f}<br>Volume: {vol_text}")
                custom_data.append(node['ticker']) 
                
                # --- OPACIDADE DA LINHA ---
                line_opacity = 0.05 if (highlight_mode and is_top) else 0.4
                
                fig.add_trace(go.Scatter(x=[0, x], y=[0, y], mode='lines', 
                                         line=dict(width=edge_width, color=color), 
                                         opacity=line_opacity, hoverinfo='none', showlegend=False))
                
                # --- ANOTAÇÕES DO TEXTO ---
                raw_name = node['name']
                wrapped_name = "<br>".join(textwrap.wrap(raw_name, width=13)) 
                
                # Aumentei as margens (22 e 30) para o texto não ficar colado às bolas gigantes
                if x > 0.15: shift_x = 22       
                elif x < -0.15: shift_x = -22   
                else: shift_x = 0
                
                shift_y = 30 if is_top else -30 
                
                # --- OPACIDADE DO TEXTO ---
                text_opacity = 0.15 if (highlight_mode and is_top) else 1.0
                
                fig.add_annotation(
                    x=x, y=y,
                    text=wrapped_name,
                    showarrow=False,
                    xshift=shift_x,
                    yshift=shift_y,
                    font=dict(color=f'rgba(255,255,255,{text_opacity})', size=11),
                    align="center"
                )
            
            # --- DESENHAR BOLAS COM TAMANHOS DINÂMICOS ---
            node_opacity = 0.15 if (highlight_mode and is_top) else 1.0
            
            fig.add_trace(go.Scatter(x=x_nodes, y=y_nodes, mode='markers', 
                                     customdata=custom_data, 
                                     marker=dict(size=node_sizes, color=color, opacity=node_opacity, 
                                                 line=dict(width=2, color=color)),
                                     hovertext=hover_texts, hoverinfo='text', showlegend=False,
                                     cliponaxis=False))

        # Adicionar os grupos
        pos_angles = np.linspace(np.pi/6, 5*np.pi/6, len(top_pos))
        add_nodes_edges(top_pos, pos_angles, '#e74c3c', is_top=True, highlight_mode=show_safe)

        neg_angles = np.linspace(7*np.pi/6, 11*np.pi/6, len(top_neg))
        add_nodes_edges(top_neg, neg_angles, '#2ecc71', is_top=False, highlight_mode=show_safe)

        # 3. NÓ CENTRAL AZUL (Tamanho fixo para não perder a importância)
        fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers+text', text=[f"<b>{main_name}</b>"],
                                 textposition="middle center", 
                                 textfont=dict(color='#ffffff', size=12), 
                                 marker=dict(size=65, color='#3498db', line=dict(width=2, color='#3498db')), 
                                 hoverinfo='text', name='Center', showlegend=False, cliponaxis=False))

        x_axis = dict(visible=False, range=[-1.9, 1.9], autorange=False)
        y_axis = dict(visible=False, range=[-1.9, 1.9], autorange=False, scaleanchor="x", scaleratio=1)

        fig.update_layout(
            title=f"Contagion Network - {target_date}", title_x=0.5,
            font=LATEX_FONT, template="plotly_dark",
            xaxis=x_axis,
            yaxis=y_axis,
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=20, r=20, t=50, b=40),
            uirevision='constant',
            dragmode=False
        )

        btn_text = "SHOW FULL NETWORK" if show_safe else "HIGHLIGHT SAFE HAVENS"
        fig.update_layout(dragmode=False)

        return fig, btn_text
    
    # 1. Função que GERA OS BOTÕES e pinta o selecionado de ROXO
    @app.callback(
        Output('extreme-dates-list-network', 'children'),
        [Input('main-asset-dropdown', 'value'),
         Input('selected-network-date', 'data')]
    )
    def update_network_dates_list(main_ticker, selected_date):
        engine.set_main_asset(main_ticker)
        extreme_days, _, _ = engine.get_extreme_events(months=12)
        
        if extreme_days.empty:
            return []
            
        # Se nenhuma data estiver selecionada ainda, assume a mais recente
        if not selected_date:
            selected_date = extreme_days.sort_index(ascending=False).index[0].strftime('%Y-%m-%d')
            
        buttons = []
        for d in extreme_days.sort_index(ascending=False).index:
            date_str = d.strftime('%Y-%m-%d')
            
            # Lógica das Cores: Verifica se este botão é o que está selecionado
            is_selected = (date_str == selected_date)
            bg_color = '#e74c3c' if is_selected else '#1e1e1e'     # Vermelho ou Cinza Escuro
            border_color = '#e74c3c' if is_selected else '#444'    # Borda Vermelha ou Cinza
            
            btn = html.Button([
                html.Span(date_str, style={'fontWeight': 'bold', 'color': '#fff'}), 
                html.Span(f" {extreme_days[d]:.2%}", style={'float':'right','color': '#fff' if is_selected else '#ff6b6b'})
            ], 
            id={'type': 'network-date-btn', 'date': date_str}, 
            style={
                'width': '100%', 'backgroundColor': bg_color, 'border': f'1px solid {border_color}', 
                'borderRadius': '5px', 'textAlign': 'left', 'cursor': 'pointer', 
                'padding': '8px 10px', 'marginBottom': '6px', 'fontFamily': 'inherit', 'fontSize': '14px',
                'transition': 'background-color 0.3s' # Animação suave na mudança de cor
            })
            buttons.append(btn)
            
        return buttons

    @app.callback(
        [Output('main-asset-dropdown', 'value'),
         Output('network-graph', 'clickData')], 
        [Input('network-graph', 'clickData')],
        prevent_initial_call=True
    )
    def apply_domino_effect(click_data):
        if not click_data:
            return no_update, no_update
            
        point = click_data['points'][0]
        
        if 'customdata' in point:
            clicked_ticker = point['customdata']
            if isinstance(clicked_ticker, list): 
                clicked_ticker = clicked_ticker[0]
                
            return clicked_ticker, None 
            
        return no_update, no_update
            
        
    @app.callback(
        Output('selected-network-date', 'data'),
        [Input({'type': 'network-date-btn', 'date': ALL}, 'n_clicks'),
         Input('main-asset-dropdown', 'value')],
        prevent_initial_call=True
    )
    def handle_network_date_click(n_clicks_list, main_ticker):
        from dash import callback_context 
        import json

        ctx = callback_context
        if not ctx.triggered:
            return no_update
            
        prop_id = ctx.triggered[0]['prop_id']
        
        # Se mudar a empresa, apaga a data selecionada para forçar a mais recente
        if 'main-asset-dropdown' in prop_id:
            return None
            
        # Se clicar no botão da data, extrai e devolve essa data
        if "{" in prop_id:
            btn_id_dict = json.loads(prop_id.split('.')[0])
            return btn_id_dict['date']
            
        return no_update
        
    @app.callback(
        Output('network-graph', 'figure'),
        [Input('selected-network-date', 'data'), 
         Input('main-asset-dropdown', 'value'),
         Input('node-click-memory', 'data')] 
    )
    def render_network(selected_date, main_ticker, clicked_node): 
        engine.set_main_asset(main_ticker)
        
        try:
            main_name = engine.assets_df.loc[engine.assets_df['ticker'] == main_ticker, 'name'].values[0]
        except:
            main_name = main_ticker
            
        extreme_days, _, _ = engine.get_extreme_events(months=12)
        
        target_date = selected_date if selected_date else (extreme_days.index[-1].strftime('%Y-%m-%d') if not extreme_days.empty else None)
        
        if not target_date:
            return go.Figure()

        top_pos, top_neg = engine.get_network_data(target_date, top_n=5)
        
        top_pos = [node for node in top_pos if node['ticker'] != main_ticker][:4]
        top_neg = [node for node in top_neg if node['ticker'] != main_ticker][:4]

        if not top_pos:
            return go.Figure() 

        fig = go.Figure()

        # =====================================================================
        # LÓGICA DE NORMALIZAÇÃO DO VOLUME PARA O DASHBOARD PRINCIPAL
        # =====================================================================
        # (O novo código perfeito)
        all_nodes = top_pos + top_neg
        vols = [n.get('volume', 0.0) for n in all_nodes] # O Motor já fez o trabalho difícil!
        min_v, max_v = (min(vols), max(vols)) if vols else (0, 0)
        
        def get_size(v):
            if max_v == min_v or max_v == 0: return 25
            return 20 + ((v - min_v) / (max_v - min_v)) * 35
        
        min_v, max_v = (min(vols), max(vols)) if vols else (0, 0)
        
        def get_size(v):
            if max_v == min_v or max_v == 0: return 25
            return 20 + ((v - min_v) / (max_v - min_v)) * 35 

        def add_nodes_edges(nodes, angles, color, is_top):
            x_nodes, y_nodes, hover_texts = [], [], []
            custom_data = [] 
            
            node_sizes = [] # <--- LISTA DE TAMANHOS
            border_colors = []
            border_widths = []
            
            for i, node in enumerate(nodes):
                delta_val = node.get('delta', node['rho'])
                distance = max(0.4, 1.8 - (abs(delta_val) * 1.5))
                
                x, y = distance * np.cos(angles[i]), distance * np.sin(angles[i])
                x_nodes.append(x)
                y_nodes.append(y)
                
                edge_width = 1 + (abs(node['rho']) ** 2.5) * 20
                
                # --- CALCULAR O TAMANHO E O TEXTO DO VOLUME ---
                vol = node.get('volume', 0.0)
                node_sizes.append(get_size(vol))
                vol_text = f"{vol:,.0f}" if vol > 0 else "N/A"
                
                hover_texts.append(f"Ticker: {node['ticker']}<br>Força (ρ): {node['rho']:.2f}<br>Salto (Δρ): {delta_val:.2f}<br>Volume: {vol_text}")
                custom_data.append(node['ticker']) 
                
                # --- LÓGICA DO PRIMEIRO CLIQUE (DESTAQUE VISUAL) ---
                is_clicked = (node['ticker'] == clicked_node)
                border_colors.append('#f1c40f' if is_clicked else color) 
                border_widths.append(4 if is_clicked else 2)             
                
                # Desenhar a Linha
                fig.add_trace(go.Scatter(x=[0, x], y=[0, y], mode='lines', 
                                         line=dict(width=edge_width, color=color), 
                                         opacity=0.4, hoverinfo='none', showlegend=False))
                
                raw_name = node['name']
                wrapped_name = "<br>".join(textwrap.wrap(raw_name, width=13)) 
                
                if x > 0.15: shift_x = 22       
                elif x < -0.15: shift_x = -22   
                else: shift_x = 0
                
                shift_y = 30 if is_top else -30 
                
                fig.add_annotation(
                    x=x, y=y,
                    text=wrapped_name,
                    showarrow=False,
                    xshift=shift_x,
                    yshift=shift_y,
                    font=dict(color='white', size=11),
                    align="center"
                )
            
            # Desenhar as Bolas
            fig.add_trace(go.Scatter(x=x_nodes, y=y_nodes, mode='markers', 
                                     customdata=custom_data, 
                                     marker=dict(size=node_sizes, color=color, opacity=1.0, 
                                                 line=dict(width=border_widths, color=border_colors)), 
                                     hovertext=hover_texts, hoverinfo='text', showlegend=False, cliponaxis=False))

        pos_angles = np.linspace(np.pi/6, 5*np.pi/6, len(top_pos))
        add_nodes_edges(top_pos, pos_angles, '#e74c3c', is_top=True)

        neg_angles = np.linspace(7*np.pi/6, 11*np.pi/6, len(top_neg))
        add_nodes_edges(top_neg, neg_angles, '#2ecc71', is_top=False)

        # NÓ CENTRAL AZUL COM TEXTO BRANCO E CUSTOMDATA
        fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers+text', text=[f"<b>{main_name}</b>"], 
                                 customdata=[main_ticker], 
                                 textposition="middle center", 
                                 textfont=dict(color='#ffffff', size=12), 
                                 marker=dict(size=65, color='#3498db', line=dict(width=3, color='#3498db')), 
                                 hoverinfo='text', name='Center', showlegend=False, cliponaxis=False))

        # --- UPDATE LAYOUT COM AUTO-SCALE DINÂMICO ---
        fig.update_layout(
            title=f"Contagion Network - {target_date}",
            font=LATEX_FONT, 
            template="plotly_dark",
            # Substituímos os ranges fixos [-1.9, 1.9] por autorange=True
            xaxis=dict(visible=False, autorange=True, scaleanchor="y", scaleratio=1),
            yaxis=dict(visible=False, autorange=True),
            plot_bgcolor='rgba(0,0,0,0)', 
            paper_bgcolor='rgba(0,0,0,0)',
            # AUMENTÁMOS AS MARGENS para que o Plotly não corte o texto quando fizer o zoom automático!
            margin=dict(l=70, r=70, t=70, b=70), 
            dragmode=False
        )

        # Trancar os eixos como combinámos antes para o utilizador não estragar o enquadramento
        fig.update_xaxes(fixedrange=True)
        fig.update_yaxes(fixedrange=True)

        return fig
    
    