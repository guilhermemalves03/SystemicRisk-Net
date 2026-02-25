import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.colors as pc

# 1. DADOS (Baseados no teu projeto SystemicRisk-Net [cite: 1, 2])
# Ativos (Tabela I) 
df_assets = pd.DataFrame({
    'Ticker': ['Exxon Mobil', 'Goldman Sachs', 'Microsoft', 'JPMorgan', 'Chevron', 'SPY ETF', 'Alphabet'],
    'Stress_Corr': [0.8603, 0.9154, 0.9056, 0.8431, 0.8665, 0.9535, 0.8710],
    'Delta': [0.6076, 0.4976, 0.4383, 0.4369, 0.4340, 0.3051, 0.2506]
})

# Global (Tabela II) [cite: 81]
df_geo = pd.DataFrame({
    'Country': ['China', 'Hong Kong', 'Singapore', 'Netherlands', 'Brazil', 'France', 'Spain', 'Germany', 'Japan', 'USA'],
    'Delta': [0.9507, 0.8450, 0.7754, 0.6946, 0.6170, 0.3521, 0.3417, -0.0777, -0.5355, 0.0],
    'lat': [35.86, 22.31, 1.35, 52.13, -14.23, 46.22, 40.46, 51.16, 36.20, 38.89],
    'lon': [104.19, 114.16, 103.81, 5.29, -51.92, 2.21, -3.74, 10.45, 138.25, -77.03]
})

def get_color(val):
    normalized = (val + 1) / 2
    clamped = max(0, min(1, normalized))
    return pc.sample_colorscale('RdBu_r', clamped)[0]

# 2. VISUALIZAÇÕES
def create_network():
    dist = 1 - df_assets['Delta']
    angles = np.linspace(0, 2*np.pi, len(df_assets), endpoint=False)
    x, y = dist * np.cos(angles), dist * np.sin(angles)
    
    # Nomes flutuam BASTANTE ACIMA (offset aumentado)
    text_offset = 0.25 
    x_t, y_t = (dist + text_offset) * np.cos(angles), (dist + text_offset) * np.sin(angles)
    
    fig = go.Figure()
    
    for i, row in df_assets.iterrows():
        fig.add_trace(go.Scatter(x=[0, x[i]], y=[0, y[i]], mode='lines',
                                 line=dict(width=row['Delta']*45, color=get_color(row['Delta'])),
                                 opacity=0.7, hoverinfo='none'))
    
    fig.add_trace(go.Scatter(
        x=x, y=y, mode='markers+text',
        text=[f"{v:.2f}" for v in df_assets['Stress_Corr']],
        textposition="middle center",
        textfont=dict(color='white', size=11, family="Arial Black"),
        marker=dict(size=55, color='#111', line=dict(width=3, color=[get_color(d) for d in df_assets['Delta']]))
    ))
    
    fig.add_trace(go.Scatter(
        x=x_t, y=y_t, mode='text', text=df_assets['Ticker'],
        textfont=dict(size=14, color='white', family="Arial Black")
    ))
    
    # AAPL Central [cite: 46]
    fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers+text', text="1.00", textposition="middle center",
                             marker=dict(size=65, color='red', line=dict(width=3, color='white')),
                             textfont=dict(color='white', size=12, family="Arial Black")))
    
    fig.update_layout(
        showlegend=False, margin=dict(t=50, b=0, l=0, r=0),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.5, 1.5]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.5, 1.5]),
        paper_bgcolor='black', plot_bgcolor='black', font_color="white",
        title="Asset Contagion: Proximity/Thickness = Δρ"
    )
    return fig

def create_map():
    df_others = df_geo[df_geo['Country'] != 'USA'].copy()
    df_others['size'] = 14 + (df_others['Delta'].abs() * 60)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scattergeo(
        lat=df_others['lat'], lon=df_others['lon'], text=df_others['Country'],
        marker=dict(
            size=df_others['size'], color=df_others['Delta'], 
            colorscale='RdBu_r', cmin=-1, cmax=1, showscale=True, 
            colorbar=dict(title=dict(text="Δρ Jump", font=dict(color="white")), tickfont=dict(color="white")),
            line=dict(width=1.5, color='white')
        ),
        hovertemplate="<b>%{text}</b><br>Jump Δρ: %{marker.color:.4f}<extra></extra>"
    ))
    
    fig.add_trace(go.Scattergeo(
        lat=[38.89], lon=[-77.03], 
        marker=dict(size=35, color='limegreen', line=dict(width=2, color='white')),
        text="USA (Origin: AAPL)"
    ))
    
    # CORREÇÃO DA PARTE BRANCA AQUI
    fig.update_geos(
        projection_type="natural earth",
        showland=True, landcolor="#1a1a1a",
        showcountries=True, countrycolor="#444",
        showocean=True, oceancolor="black",
        bgcolor="black",     # Remove o fundo branco do "globo"
        showframe=False      # Remove a moldura branca exterior
    )
    
    fig.update_layout(
        title="Global Dorling Cartogram",
        margin=dict(t=50, b=0, l=0, r=0),
        paper_bgcolor='black', 
        font_color="white"
    )
    return fig

# 3. APP DASH
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H2("SystemicRisk-Net: Extreme Event Dashboard", 
                           className="text-center my-4", style={'color': 'red', 'fontWeight': 'bold'}))),
    
    dbc.Row([
        dbc.Col(dcc.Graph(figure=create_network(), id='net-graph'), width=6),
        dbc.Col(dcc.Graph(figure=create_map(), id='map-graph'), width=6)
    ]),
    
    dbc.Row(dbc.Col(html.P("Analysis of Extreme Value Events and Correlation Contagion", 
                           className="text-center mt-3", style={'color': '#888'})))
], fluid=True, style={'backgroundColor': 'black', 'minHeight': '100vh'})

if __name__ == '__main__':
    app.run(debug=True)