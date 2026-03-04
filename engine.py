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

    def fetch_all_data(self, period="1y"):
        # auto_adjust=False para bater certo com a EDA
        raw_data = yf.download(self.tickers, period=period, auto_adjust=False)
        if raw_data.empty: return None
        
        self.prices = raw_data['Close']
        # Sem dropna() aqui para não apagar datas partilhadas
        self.returns = np.log(self.prices / self.prices.shift(1))
        return self.returns

    def set_main_asset(self, ticker):
        if ticker in self.returns.columns:
            self.main_ticker = ticker
            self.main_returns = self.returns[ticker]
            return True
        return False

    def get_extreme_events(self, months=12, threshold=0.01):
        if self.main_returns is None: 
            return pd.Series(), 0, pd.Series()
        
        # Isolar e limpar NaNs APENAS do ativo principal (Exato à EDA)
        filtered = self.main_returns.dropna()
        if filtered.empty: return pd.Series(), 0, pd.Series()
        
        var_limit = np.percentile(filtered, threshold * 100)
        extreme_days = filtered[filtered < var_limit]
        
        return extreme_days, var_limit, filtered

    def get_contagion_metrics(self, other_ticker, extreme_index, filtered_index):
        if other_ticker not in self.returns.columns: return 0, 0, 0
        
        # Limpar NaNs apenas entre o ativo principal e o secundário na correlação
        df_corr = pd.concat([self.main_returns, self.returns[other_ticker]], axis=1).dropna()
        
        valid_extreme = extreme_index.intersection(df_corr.index)
        if len(valid_extreme) < 2: return 0, 0, 0
        stress_corr = df_corr.iloc[:, 0].loc[valid_extreme].corr(df_corr.iloc[:, 1].loc[valid_extreme])
        
        valid_calm = filtered_index.intersection(df_corr.index)
        if len(valid_calm) < 2: return 0, 0, 0
        calm_corr = df_corr.iloc[:, 0].loc[valid_calm].corr(df_corr.iloc[:, 1].loc[valid_calm])
        
        if pd.isna(stress_corr) or pd.isna(calm_corr): return 0, 0, 0
        return stress_corr - calm_corr, stress_corr, calm_corr

    def calculate_expected_shortfall(self, returns_series, alpha=0.01):
        if returns_series.empty: return 0.0
        var_limit = returns_series.quantile(alpha)
        return returns_series[returns_series <= var_limit].mean()

    def run_monte_carlo(self, days=30, n_sims=80):
        if self.main_returns is None: return None, None
        
        clean_returns = self.main_returns.replace([np.inf, -np.inf], np.nan).dropna()
        if clean_returns.empty: return None, None
        
        returns_vec = clean_returns.values
        sim_returns = np.random.choice(returns_vec, size=(days, n_sims))
        initial_step = np.zeros((1, n_sims))
        
        paths = np.exp(np.cumsum(np.vstack([initial_step, sim_returns]), axis=0))
        final_returns = paths[-1] - 1
        sim_es = self.calculate_expected_shortfall(pd.Series(final_returns), alpha=0.01)
        
        return paths, sim_es
    
    def get_event_contagion(self, other_ticker, stress_date, calm_period='3M'):
        if other_ticker not in self.returns.columns or self.main_returns is None:
            return None
        
        stress_date = pd.to_datetime(stress_date)
        if stress_date not in self.returns.index: 
            # Fallback para o dia mais próximo caso a data exata falhe no index
            idx = self.returns.index.get_indexer([stress_date], method='nearest')[0]
        else:
            idx = self.returns.index.get_loc(stress_date)
        
        # Janela de Stress: +/- 15 dias de negociação (~1.5 meses no total)
        start_stress = max(0, idx - 15)
        end_stress = min(len(self.returns) - 1, idx + 15)
        
        stress_returns_main = self.main_returns.iloc[start_stress:end_stress+1]
        stress_returns_other = self.returns[other_ticker].iloc[start_stress:end_stress+1]
        
        # Janela Calma (Dias de negociação aproximados)
        calm_days = 21 if calm_period == '1M' else (63 if calm_period == '3M' else 252)
        end_calm = max(0, start_stress - 1)
        start_calm = max(0, end_calm - calm_days)
        
        calm_returns_main = self.main_returns.iloc[start_calm:end_calm+1]
        calm_returns_other = self.returns[other_ticker].iloc[start_calm:end_calm+1]
        
        if len(stress_returns_main) < 3 or len(calm_returns_main) < 3: return None
        
        stress_corr = stress_returns_main.corr(stress_returns_other)
        calm_corr = calm_returns_main.corr(calm_returns_other)
        
        if pd.isna(stress_corr) or pd.isna(calm_corr): return None
        return stress_corr - calm_corr, stress_corr, calm_corr