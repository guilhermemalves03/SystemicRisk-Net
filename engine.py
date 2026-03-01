import yfinance as yf
import pandas as pd
import numpy as np

class SystemicRiskEngine:
    def __init__(self, csv_path="assets.csv"):
        self.assets_df = pd.read_csv(csv_path)
        self.tickers = self.assets_df['ticker'].tolist()
        self.prices = None
        self.returns = None
        self.main_ticker = None
        self.main_returns = None

    def fetch_all_data(self, period="2y"):
        """Descarrega dados e calcula log returns: $r_{t}=\ln(P_{t}) - \ln(P_{t-1})$."""
        raw_data = yf.download(self.tickers, period=period, auto_adjust=True)
        if raw_data.empty: return None
        self.prices = raw_data['Close'].dropna(axis=1, how='all')
        self.returns = np.log(self.prices / self.prices.shift(1)).dropna()
        return self.returns

    def set_main_asset(self, ticker):
        if ticker in self.returns.columns:
            self.main_ticker = ticker
            self.main_returns = self.returns[ticker]
            return True
        return False

    def get_extreme_events(self, months=12, threshold=0.01):
        if self.main_returns is None: return pd.Series(), 0, pd.Series()
        filtered = self.main_returns.tail(int(months * 21)) 
        var_limit = filtered.quantile(threshold)
        extreme_days = filtered[filtered <= var_limit]
        return extreme_days, var_limit, filtered

    def get_contagion_metrics(self, other_ticker, extreme_index, filtered_index):
        """Calcula o salto de correlação: $\Delta \rho = \rho_{stress} - \rho_{calm}$."""
        if other_ticker not in self.returns.columns: return None
        stress_corr = self.main_returns.loc[extreme_index].corr(self.returns[other_ticker].loc[extreme_index])
        calm_corr = self.main_returns.loc[filtered_index].corr(self.returns[other_ticker].loc[filtered_index])
        if np.isnan(stress_corr) or np.isnan(calm_corr): return 0, 0, 0
        return stress_corr - calm_corr, stress_corr, calm_corr

    def calculate_expected_shortfall(self, returns_series, alpha=0.01):
        if returns_series.empty: return 0.0
        var_limit = returns_series.quantile(alpha)
        return returns_series[returns_series <= var_limit].mean()

    def run_monte_carlo(self, days=30, n_sims=80):
        """Executa bootstrapping garantindo o 'Dia 0' para a animação do Dash."""
        if self.main_returns is None: return None, None
        returns_vec = self.main_returns.dropna().values
        sim_returns = np.random.choice(returns_vec, size=(days, n_sims))
        initial_step = np.zeros((1, n_sims))
        # Adiciona ponto de partida em 1.0 (100%) para evitar erros de trace vazio
        paths = np.exp(np.cumsum(np.vstack([initial_step, sim_returns]), axis=0))
        final_returns = paths[-1] - 1
        sim_es = self.calculate_expected_shortfall(pd.Series(final_returns), alpha=0.01)
        return paths, sim_es