import json
import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import joblib

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

PAPER_TRADES_FILE = "paper_trades.json"
MODEL_FILE = "ml_trade_model.pkl"
REGIME_FILE = "ml_regime.json"

def compute_rsi(data, window=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def extract_features():
    if not os.path.exists(PAPER_TRADES_FILE):
        return None
    
    with open(PAPER_TRADES_FILE, 'r') as f:
        trades = json.load(f)
        
    closed_trades = [t for t in trades if t.get('status') == 'CLOSED' and t.get('pnl_pct') is not None]
    if len(closed_trades) < 10:
        print("[ML AGENT] Not enough closed trades to train a model (need at least 10).")
        return None
        
    dataset = []
    
    # Group trades by asset to batch yfinance calls
    assets = set(t['pair'] for t in closed_trades)
    
    for asset in assets:
        asset_trades = [t for t in closed_trades if t['pair'] == asset]
        try:
            # Map forex/crypto tickers
            yf_ticker = asset
            if "/" in asset:
                yf_ticker = asset.replace("/", "") + "=X"
                if "BTC" in asset or "ETH" in asset or "SOL" in asset:
                    yf_ticker = asset.replace("/", "-")
            elif asset == "NIFTY":
                yf_ticker = "^NSEI"
            else:
                yf_ticker = asset + ".NS"
                
            hist = yf.download(yf_ticker, period="3mo", interval="1d", progress=False)
            if hist.empty:
                continue
                
            hist['RSI'] = compute_rsi(hist)
            hist['Volatility'] = hist['Close'].pct_change().rolling(window=14).std()
            hist['SMA_20'] = hist['Close'].rolling(window=20).mean()
            
            for t in asset_trades:
                trade_date = pd.to_datetime(t['opened_at']).tz_localize(None).normalize()
                if trade_date in hist.index:
                    row = hist.loc[trade_date]
                    
                    target = 1 if t['pnl_pct'] > 0 else 0
                    
                    dataset.append({
                        "asset": asset,
                        "direction": 1 if t['direction'] == "BUY" else 0,
                        "rsi": float(row['RSI'].iloc[0]) if isinstance(row['RSI'], pd.Series) else float(row['RSI']),
                        "volatility": float(row['Volatility'].iloc[0]) if isinstance(row['Volatility'], pd.Series) else float(row['Volatility']),
                        "price_above_sma": 1 if float(row['Close'].iloc[0] if isinstance(row['Close'], pd.Series) else row['Close']) > float(row['SMA_20'].iloc[0] if isinstance(row['SMA_20'], pd.Series) else row['SMA_20']) else 0,
                        "target": target
                    })
        except Exception as e:
            print(f"Error processing {asset}: {e}")
            
    df = pd.DataFrame(dataset).dropna()
    return df

def train_and_evaluate():
    if not SKLEARN_AVAILABLE:
        print("[ML AGENT] scikit-learn is not installed. Skipping ML training.")
        return
        
    print("[ML AGENT] Starting self-improvement cycle...")
    df = extract_features()
    
    if df is None or len(df) < 10:
        print("[ML AGENT] Insufficient data for machine learning training.")
        return
        
    features = ['direction', 'rsi', 'volatility', 'price_above_sma']
    X = df[features]
    y = df['target']
    
    # Train Random Forest
    rf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    rf.fit(X, y)
    
    # Calculate overall win probability base rate
    win_rate = y.mean()
    
    print(f"[ML AGENT] Training complete. Historical Win Rate: {win_rate*100:.1f}%")
    
    # Save the model
    joblib.dump(rf, MODEL_FILE)
    
    # Save a JSON manifest for the main bot to know ML is active
    regime = {
        "last_trained": datetime.now().isoformat(),
        "samples": len(df),
        "historical_win_rate": float(win_rate),
        "features": features
    }
    with open(REGIME_FILE, "w") as f:
        json.dump(regime, f)
        
    print("[ML AGENT] Self-improvement model updated successfully!")

if __name__ == "__main__":
    train_and_evaluate()
