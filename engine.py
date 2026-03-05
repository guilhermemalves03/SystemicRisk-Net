import yfinance as yf
import pandas as pd
import numpy as np

class SystemicRiskEngine:
    def __init__(self, csv_path="assets.csv"):
        self.assets_df = pd.read_csv(csv_path)
        self.tickers = self.assets_df['ticker'].tolist()
        self.prices = None
        self.returns = None
        self.volume = None
        self.main_ticker = None
        self.main_returns = None

    def fetch_all_data(self, period="2y"):
        raw_data = yf.download(self.tickers, period=period, auto_adjust=True)
        if raw_data.empty: return None
        
        if isinstance(raw_data.columns, pd.MultiIndex):
            self.prices = raw_data['Close'].dropna(axis=1, how='all')
            self.volume = raw_data['Volume'].dropna(axis=1, how='all')
        else:
            self.prices = raw_data[['Close']].rename(columns={'Close': self.tickers[0]})
            self.volume = raw_data[['Volume']].rename(columns={'Volume': self.tickers[0]})
            
        # CORREÇÃO: Propagar o último preço válido para preencher feriados locais (ffill)
        self.prices = self.prices.ffill()
        
        # CORREÇÃO: Apenas dropar a linha se TODOS os ativos estiverem NaN nesse dia
        self.returns = np.log(self.prices / self.prices.shift(1)).dropna(how='all')
        return self.returns
            
        self.returns = np.log(self.prices / self.prices.shift(1)).dropna()
        return self.returns

    def set_main_asset(self, ticker):
        if ticker in self.returns.columns:
            self.main_ticker = ticker
            self.main_returns = self.returns[ticker]
            return True
        return False

    

    def get_extreme_events(self, months=12, threshold=0.01): # Mudei para 0.05 (VaR 95%) para teres mais eventos, muda para 0.01 se quiseres manter 99%
        if self.main_returns is None: return pd.Series(), 0, pd.Series()
        
        # Filtrar valores NaN apenas do ativo principal para não falhar os quantis
        main_clean = self.main_returns.dropna() 
        filtered = main_clean.tail(int(months * 21)) 
        
        if filtered.empty: return pd.Series(), 0, pd.Series()
        
        var_limit = filtered.quantile(threshold)
        extreme_days = filtered[filtered <= var_limit]
        return extreme_days, var_limit, filtered

    def get_event_contagion(self, other_ticker, stress_date, calm_period='3M'):
        if other_ticker not in self.returns.columns or self.main_returns is None:
            return None
        
        stress_date = pd.to_datetime(stress_date)
        if stress_date not in self.returns.index: 
            idx = self.returns.index.get_indexer([stress_date], method='nearest')[0]
        else:
            idx = self.returns.index.get_loc(stress_date)
        
        start_stress = max(0, idx - 15)
        end_stress = min(len(self.returns) - 1, idx + 15)
        
        stress_returns_main = self.main_returns.iloc[start_stress:end_stress+1]
        stress_returns_other = self.returns[other_ticker].iloc[start_stress:end_stress+1]
        
        if self.volume is not None and other_ticker in self.volume.columns:
            stress_vol_other = self.volume[other_ticker].iloc[start_stress:end_stress+1].mean()
        else:
            stress_vol_other = 1
        
        calm_days = 21 if calm_period == '1M' else (63 if calm_period == '3M' else 252)
        end_calm = max(0, start_stress - 1)
        start_calm = max(0, end_calm - calm_days)
        
        calm_returns_main = self.main_returns.iloc[start_calm:end_calm+1]
        calm_returns_other = self.returns[other_ticker].iloc[start_calm:end_calm+1]
        
        if self.volume is not None and other_ticker in self.volume.columns:
            calm_vol_other = self.volume[other_ticker].iloc[start_calm:end_calm+1].mean()
        else:
            calm_vol_other = 1
        
        if len(stress_returns_main) < 3 or len(calm_returns_main) < 3: return None
        
        stress_corr = stress_returns_main.corr(stress_returns_other)
        calm_corr = calm_returns_main.corr(calm_returns_other)
        if pd.isna(stress_corr) or pd.isna(calm_corr): return None
        
        delta_vol = (stress_vol_other / calm_vol_other) - 1 if calm_vol_other > 0 else 0
        
        # Agora devolve 2 blocos separados: (Métricas de Correlação) e (Métricas de Volume)
        return (stress_corr - calm_corr, stress_corr, calm_corr), (delta_vol, stress_vol_other, calm_vol_other)

    def calculate_expected_shortfall(self, returns_series, alpha=0.01):
        if returns_series.empty: return 0.0
        var_limit = returns_series.quantile(alpha)
        return returns_series[returns_series <= var_limit].mean()

    def run_monte_carlo(self, days=30, n_sims=80):
        if self.main_returns is None: return None, None
        returns_vec = self.main_returns.dropna().values
        sim_returns = np.random.choice(returns_vec, size=(days, n_sims))
        initial_step = np.zeros((1, n_sims))
        paths = np.exp(np.cumsum(np.vstack([initial_step, sim_returns]), axis=0))
        final_returns = paths[-1] - 1
        sim_es = self.calculate_expected_shortfall(pd.Series(final_returns), alpha=0.01)
        return paths, sim_es
    
    def get_realized_volatility(self, ticker, window=21):
        if self.returns is None or ticker not in self.returns.columns:
            return None
        return self.returns[ticker].rolling(window=window).std() * np.sqrt(252)