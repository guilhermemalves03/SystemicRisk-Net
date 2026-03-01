import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from scipy.stats import kurtosis, skew

class SystemicRiskEngine:
    def __init__(self, csv_path="assets.csv"):
        
        self.assets_df = pd.read_csv(csv_path)
        self.tickers = self.assets_df['ticker'].tolist()
        
        
        self.prices = None
        self.volumes = None
        self.returns = None
        
        
        self.main_ticker = None
        self.main_returns = None

    def fetch_all_data(self, period="2y"):
        """Descarrega dados e calcula log returns: $r_{t}=ln(P_{t}) - ln(P_{t-1})$."""
        raw_data = yf.download(self.tickers, period=period, auto_adjust=True)
        
        if raw_data.empty:
            return None

        # Remove colunas que falharam no download 
        self.prices = raw_data['Close'].dropna(axis=1, how='all')
        self.volumes = raw_data['Volume'].dropna(axis=1, how='all')
        
        # Cálculo de log returns 
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
        
        main_clean = self.main_returns.dropna()
        end_date = main_clean.index[-1]
        start_date = end_date - pd.DateOffset(months=months)
        filtered = main_clean[start_date:end_date]
        
        if filtered.empty: return pd.Series(), 0, filtered
            
        # REVERSÃO: Voltamos ao Quantile fixo (o que dava sempre os 3 valores)
        var_limit = filtered.quantile(threshold)
        extreme_days = filtered[filtered <= var_limit]
        
        return extreme_days, var_limit, filtered
    
    def get_contagion_metrics(self, other_ticker, extreme_index, filtered_index):
        
        if other_ticker not in self.returns.columns:
            return None
            
        stress_corr = self.main_returns.loc[extreme_index].corr(self.returns[other_ticker].loc[extreme_index])
        
        calm_corr = self.main_returns.loc[filtered_index].corr(self.returns[other_ticker].loc[filtered_index])
        
        delta_rho = stress_corr - calm_corr
        return delta_rho, stress_corr, calm_corr
    
    def calculate_expected_shortfall(self, returns_series, alpha=0.01):
       
        if returns_series.empty: return 0.0
        
        var_limit = returns_series.quantile(alpha)
        
        es_value = returns_series[returns_series <= var_limit].mean()
        
        return es_value

    def run_monte_carlo(self, days=30, n_sims=10000):
        """
        Executa Simulação de Monte Carlo via Bootstrapping.
        Retorna: (trajetórias, ES_simulado)
        """
        if self.main_returns is None: return None, None
        
        # Bootstrapping: Escolhe retornos reais aleatórios para o futuro
        # Isto preserva a Kurtosis (Fat Tails) que encontraste nos dados
        sim_returns = np.random.choice(self.main_returns, size=(days, n_sims))
        
        # Gera trajetórias de preço (acumulando os retornos)
        # Partimos de 1.0 (100% do valor atual)
        paths = np.exp(np.cumsum(sim_returns, axis=0))
        
        # Calcula o retorno final de cada simulação (última linha da matriz)
        final_returns = paths[-1] - 1
        
        # Calcula o ES para o cenário simulado a 30 dias
        sim_es = self.calculate_expected_shortfall(pd.Series(final_returns), alpha=0.01)
        
        return paths, sim_es
    
        
    
