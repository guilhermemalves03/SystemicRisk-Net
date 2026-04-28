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
        fig_dist.add_trace(go.Bar(x=bin_centers[bin_centers > var_limit], y=counts[bin_centers > var_limit], marker_color='#333', name='Normal', showlegend=False))
        fig_dist.add_trace(go.Bar(x=bin_centers[bin_centers <= var_limit], y=counts[bin_centers <= var_limit], marker_color='#c0392b', name='Tail Stress', showlegend=False))
        
        x_range = np.linspace(filtered_returns.min(), filtered_returns.max(), 250)
        fig_dist.add_trace(go.Scatter(x=x_range, y=gaussian_kde(filtered_returns)(x_range), name='KDE', line=dict(color='#3498db', width=2.5)))
        fig_dist.add_trace(go.Scatter(x=x_range, y=norm.pdf(x_range, filtered_returns.mean(), filtered_returns.std()), name='Gaussian', line=dict(color='#777', dash='dash', width=1.5)))
        
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
        Output('intro-apple-dist', 'figure', allow_duplicate=True),
        [Input('zoom-btn-intro', 'n_clicks')],
        [State('intro-apple-dist', 'figure')],
        prevent_initial_call=True
    )
    def toggle_intro_zoom(n_clicks, fig):
        if fig is None: return no_update
        
        patched_fig = go.Figure(fig)
        patched_fig.update_layout(transition=dict(duration=500, easing="cubic-in-out"))
        
        if n_clicks % 2 == 1:
            x_min, x_max = -0.10, -0.02
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
        else:
            patched_fig.update_xaxes(autorange=True)
            patched_fig.update_yaxes(autorange=True)
            patched_fig.update_layout(title_text=r"$\text{Aggregated Return Distribution: AAPL}$")
            
        return patched_fig

    @app.callback(
        [Output('intro-contagion-map', 'figure'), Output('asia-impact-table', 'children')],
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
            return fig, html.Div()
            
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

        fig_map.add_trace(go.Scatter(x=[None], y=[None], mode='markers', marker=dict(colorscale='RdBu_r', cmin=-1, cmax=1, showscale=False)))
        fig_map.update_layout(title=rf"$\text{{Shock (}} \Delta\rho \text{{) - {target_date} (Calm: 1M)}}$", font=LATEX_FONT, template="plotly_dark", xaxis=dict(visible=False, scaleanchor="y", scaleratio=1), yaxis=dict(visible=False), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=50, b=10))

        fig_map.update_layout(transition=dict(duration=500, easing="cubic-in-out"))
        if n_clicks and n_clicks % 2 == 1:
            fig_map.update_xaxes(range=[70, 150], autorange=False)
            fig_map.update_yaxes(range=[-10, 50], autorange=False)
        else:
            fig_map.update_xaxes(autorange=True)
            fig_map.update_yaxes(autorange=True)

        table_header = html.Thead(html.Tr([html.Th("Country"), html.Th("Correlation Jump (Δρ)")]))
        table_body = html.Tbody([
            html.Tr([
                html.Td(d['Country']), 
                html.Td(f"+{d['Jump']:.4f}", style={'color': '#2ecc71' if d['Jump'] > 0 else '#e74c3c', 'fontWeight': 'bold'})
            ]) for d in sorted(table_data, key=lambda x: x['Jump'], reverse=True)
        ])
        
        impact_table = html.Table([table_header, table_body], className='intro-table', style={'width': '100%', 'color': '#fff', 'borderCollapse': 'collapse', 'fontSize': '1.2em'})

        return fig_map, impact_table

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
        paths = np.array(paths)
        current_paths = paths[:frame+1, :]
        mean_path = np.mean(current_paths, axis=1)
        
        lower_bound = np.zeros(frame + 1)
        upper_bound = np.zeros(frame + 1)
        for t in range(frame + 1):
            step_vals = current_paths[t, :]
            lower_bound[t] = np.mean(step_vals[step_vals <= np.percentile(step_vals, 1)])
            upper_bound[t] = np.mean(step_vals[step_vals >= np.percentile(step_vals, 99)])
            
        x_vals = np.arange(frame + 1)
        base_line = np.ones_like(x_vals) 
        
        current_vals = current_paths[-1, :] - 1
        max_val, mean_val, min_val = np.max(current_vals), np.mean(current_vals), np.min(current_vals)
        
        str_max = rf"$\text{{Max: }} {max_val*100:+.2f}\%$"
        str_mean = rf"$\text{{Mean: }} {mean_val*100:+.2f}\%$"
        str_min = rf"$\text{{Worst: }} {min_val*100:+.2f}\%$"
        
        fig_mc = go.Figure()
        fig_mc.add_trace(go.Scatter(x=x_vals, y=base_line, mode='lines', line=dict(width=0), showlegend=False))
        fig_mc.add_trace(go.Scatter(x=x_vals, y=lower_bound, mode='lines', fill='tonexty', fillgradient=dict(type='vertical', colorscale=[[0, '#FF0000'], [1, 'rgba(0,0,0,0)']]), line=dict(width=1, color='#FF0000', shape='spline'), showlegend=False))
        fig_mc.add_trace(go.Scatter(x=x_vals, y=base_line, mode='lines', line=dict(width=0), showlegend=False))
        fig_mc.add_trace(go.Scatter(x=x_vals, y=upper_bound, mode='lines', fill='tonexty', fillgradient=dict(type='vertical', colorscale=[[0, 'rgba(0,0,0,0)'], [1, '#39FF14']]), line=dict(width=1, color='#39FF14', shape='spline'), showlegend=False))
        fig_mc.add_trace(go.Scatter(x=x_vals, y=mean_path, mode='lines', line=dict(width=2, color='#FFFFFF', shape='spline'), showlegend=False))

        if frame >= 30:
            final_es_ret = lower_bound[-1] - 1
            fig_mc.add_hline(y=lower_bound[-1], line_dash="dash", line_color="#FF0000", annotation_text=rf"$ES_{{1\%}} = {final_es_ret*100:.2f}\%$", annotation_position="bottom left", annotation_font=dict(color="#FF0000", size=16))
            fig_mc.update_layout(title=r"$\text{Simulated Paths: } S_t = S_0 \exp\left(\sum r_i\right)$", font=LATEX_FONT, template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=40, r=20, t=50, b=40))
            return fig_mc, frame, True, str_max, str_mean, str_min
        
        fig_mc.update_layout(title=f"Monte Carlo Projection (Day {frame}/30)", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=LATEX_FONT, margin=dict(l=40, r=20, t=50, b=40), xaxis=dict(range=[0, 30]), yaxis=dict(range=[np.min(paths)*0.95, np.max(paths)*1.05]))
        return fig_mc, frame + 1, False, str_max, str_mean, str_min