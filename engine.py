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
            
        self.prices = self.prices.ffill()
        
       
        self.returns = np.log(self.prices / self.prices.shift(1)).dropna(how='all')
        return self.returns

    def get_network_data(self, target_date, top_n=4):
        correlations = []
        empresas_df = self.assets_df[~self.assets_df['sector'].isin(['Country', 'Index', 'ETF'])]
        valid_tickers = empresas_df['ticker'].tolist()

        
        stress_corrs, calm_corrs = self.get_bulk_contagion(target_date, '1M')
        if stress_corrs is None or calm_corrs is None: return [], []

        for ticker in valid_tickers:
            if ticker == self.main_ticker or ticker not in stress_corrs: 
                continue
            
            stress_rho = stress_corrs[ticker]
           
            calm_rho = calm_corrs[ticker] if ticker in calm_corrs else 0.0
            
            if not pd.isna(stress_rho):
                name_match = self.assets_df[self.assets_df['ticker'] == ticker]['name'].values
                name = name_match[0] if len(name_match) > 0 else ticker
                
                
                vol = 0.0
                if self.volume is not None and ticker in self.volume.columns:
                    try:
                        dt = pd.to_datetime(target_date)
                        if dt in self.volume.index:
                            vol = float(self.volume.loc[dt, ticker])
                        else:
                            idx = self.volume.index.get_indexer([dt], method='nearest')[0]
                            vol = float(self.volume.iloc[idx][ticker])
                            
                        if pd.isna(vol):  
                            vol = 0.0
                            
                    except:
                        vol = 0.0 
                
                
                delta_rho = stress_rho - calm_rho if not pd.isna(calm_rho) else stress_rho
                    
                
                correlations.append({'ticker': ticker, 'name': name, 'rho': stress_rho, 'delta': delta_rho, 'volume': vol})
        
        df = pd.DataFrame(correlations).sort_values('rho', ascending=False)
        if len(df) < top_n * 2: return [], []
        
        return df.head(top_n).to_dict('records'), df.tail(top_n).to_dict('records')

    def set_main_asset(self, ticker):
        if ticker in self.returns.columns:
            self.main_ticker = ticker
            self.main_returns = self.returns[ticker]
            return True
        return False

    

    def get_extreme_events(self, months=12, threshold=0.01): 
        if self.main_returns is None: return pd.Series(), 0, pd.Series()
        
        
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
        
        
        return (stress_corr - calm_corr, stress_corr, calm_corr), (delta_vol, stress_vol_other, calm_vol_other)

    def get_bulk_contagion(self, target_date, calm_period='3M'):
        if self.main_returns is None: return None, None
        
        stress_date = pd.to_datetime(target_date)
        if stress_date not in self.returns.index: 
            idx = self.returns.index.get_indexer([stress_date], method='nearest')[0]
        else:
            idx = self.returns.index.get_loc(stress_date)
            
        start_stress = max(0, idx - 15)
        end_stress = min(len(self.returns) - 1, idx + 15)
        
        calm_days = 21 if calm_period == '1M' else (63 if calm_period == '3M' else 252)
        end_calm = max(0, start_stress - 1)
        start_calm = max(0, end_calm - calm_days)
        
        
        stress_df = self.returns.iloc[start_stress:end_stress+1]
        calm_df = self.returns.iloc[start_calm:end_calm+1]
        
        if len(stress_df) < 3 or len(calm_df) < 3: 
            return None, None
            
        
        stress_corrs = stress_df.corrwith(self.main_returns.iloc[start_stress:end_stress+1])
        calm_corrs = calm_df.corrwith(self.main_returns.iloc[start_calm:end_calm+1])
        
        return stress_corrs, calm_corrs

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
    