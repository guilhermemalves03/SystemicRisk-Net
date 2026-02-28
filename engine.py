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
        raw_data = yf.download(self.tickers, period=period)
        
       
        if raw_data.empty:
            print("Erro crítico: Nenhum dado foi descarregado.")
            return None

        self.prices = raw_data['Close'].dropna(axis=1, how='all')
        self.volumes = raw_data['Volume'].dropna(axis=1, how='all')
        
        self.returns = np.log(self.prices / self.prices.shift(1)).dropna()
        return self.returns

    

    def set_main_asset(self, ticker):
    
        if ticker in self.returns.columns:
            self.main_ticker = ticker
            self.main_returns = self.returns[ticker]
            return True
        return False

    def get_extreme_events(self, months=12, threshold=0.01):
    
        if self.main_returns is None or self.main_returns.empty:
            print(f"Erro: Sem dados para o ativo {self.main_ticker}")
            return pd.Series(), None, pd.Series()
            
        end_date = self.main_returns.index[-1]
        start_date = end_date - pd.DateOffset(months=months)
        
        filtered = self.main_returns[start_date:end_date]
        
        if filtered.empty:
            return pd.Series(), None, filtered
            
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
      
        if self.main_returns is None: return None, None
        
        
        sim_returns = np.random.choice(self.main_returns, size=(days, n_sims))
        
        
        paths = np.exp(np.cumsum(sim_returns, axis=0))
        
        
        final_returns = paths[-1] - 1
        
        
        sim_es = self.calculate_expected_shortfall(pd.Series(final_returns), alpha=0.01)
        
        return paths, sim_es
    
if __name__ == "__main__":
    engine = SystemicRiskEngine()
    print("A descarregar dados...")
    engine.fetch_all_data(period="2y")
    engine.set_main_asset('AAPL')
    
    
    extreme_days, var_limit, filtered_data = engine.get_extreme_events(months=12)
    es_hist = engine.calculate_expected_shortfall(filtered_data)
    
    
    paths, es_sim = engine.run_monte_carlo(days=30, n_sims=1000) 

 
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Gráfico 1: Histograma de Retornos (Foco na Cauda Esquerda)
    ax1.hist(filtered_data, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    ax1.axvline(var_limit, color='red', linestyle='--', label=f'VaR 99% ({var_limit:.2%})')
    ax1.axvline(es_hist, color='darkred', linestyle='-', label=f'Exp. Shortfall ({es_hist:.2%})')
    ax1.set_title(f"Distribuição de Retornos: {engine.main_ticker}")
    ax1.legend()

    ax2.plot(paths, color='blue', alpha=0.1) 
    ax2.plot(paths.mean(axis=1), color='cyan', linewidth=2, label='Média')
    ax2.axhline(1 + es_sim, color='red', linewidth=2, label=f'ES Simulado ({es_sim:.2%})')
    ax2.set_title(f"Monte Carlo: Projeção 30 Dias ({engine.main_ticker})")
    ax2.set_xlabel("Dias Úteis")
    ax2.set_ylabel("Valor Relativo (1.0 = Hoje)")
    ax2.legend()

    plt.tight_layout()
    plt.show() 