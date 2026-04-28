import dash
from engine import SystemicRiskEngine
from layout import get_layout
from callbacks import register_callbacks

external_stylesheets = ['https://fonts.googleapis.com/css2?family=EB+Garamond:wght@400;700&display=swap']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Systemic Risk-Net"

engine = SystemicRiskEngine()
engine.fetch_all_data(period="2y")

app.layout = get_layout(engine)
register_callbacks(app, engine)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)