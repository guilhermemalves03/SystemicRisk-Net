# SystemicRisk-Net 

An academic quantitative risk management terminal and interactive data visualization platform designed to diagnose cross-border asset contagion, evaluate portfolio vulnerabilities, and isolate structural safe havens during black-swan liquidations.

Built using **Python**, **Dash**, and **Plotly**, the architecture decouples a high-performance vector calculations backend from a reactive, modern visual interface executing purely in dark mode.

---

##  Key Architectural Features

* **Tail Risk Isolation:** Computes non-parametric empirical Value at Risk ($VaR_{99\%}$) to programmatically slice historical stress periods and extreme loss events.
* **Vectorized Contagion Modeling:** Tracks the structural shock transmission vector ($\Delta\rho$) across markets by evaluating raw global correlation matrices between calm and high-liquidation stress windows.
* **Predictive Risk Banding:** Deploys an asynchronous bootstrap Monte Carlo simulation engine to project 1,000 parallel random walk asset paths and extract the dynamic Expected Shortfall ($ES_{1\%}$) over a 30-day temporal horizon.
* **Occlusion-Free Macro-Cartography:** Implements an iterative, force-directed **Dorling Cartogram layout** to scale sovereign equity proxies (ETFs) by trading volume, preventing node overlap and label bleeding while maintaining global geographic placement.

---

##  Tech Stack & Dependencies

* **Core Engine:** Python 3.10+
* **Data Layer:** `yfinance` (Macro-data pipeline integration), `pandas`, `numpy` (Vectorized matrix scaling)
* **Frontend Analytics Terminal:** `dash` (Reactive callbacks), `plotly` (High-density web graphics)
* **Graph Topology:** `networkx` / Plotly layout structures

---

##  Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/SystemicRisk-Net.git](https://github.com/yourusername/SystemicRisk-Net.git)
   cd SystemicRisk-Net
