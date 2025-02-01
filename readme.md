# **Dash Stock Analysis App**

This Dash-based web application fetches stock market data using **Polygon.io** and **Yahoo Finance (`yfinance`)**, performs technical analysis with **pandas_ta**, and visualizes the results using **Plotly**.

## **Features**

- Fetches real-time and historical stock price data.
- Supports multiple timeframes (1m, 5m, etc.).
- Computes **SMA (Simple Moving Average)** and **RSI (Relative Strength Index)**.
- Interactive graphs for better visualization.
- Dash-powered web UI.

---

## **Installation & Setup**

### **1. Clone the Repository**

### **2. Create a Virtual Environment (Optional but Recommended)**

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### **3. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **4. Set Your Polygon.io API Key**

- Open the Python file and replace `POLYGON_API_KEY` with your actual API key.

---

## **Running the Application**

```bash
python main.py
```

- Open your browser and go to `http://127.0.0.1:8050/`

---

## **Troubleshooting**

- **Graphs not displaying?**
  - Ensure that the fetched data is properly formatted.
  - Print the DataFrame (`df.head()`) to debug.
- **API Key Issues?**
  - Ensure you have an active API key from [Polygon.io](https://polygon.io/).
  - Check if the API key is correctly set in the script.

---

## **Future Enhancements**

- Add more technical indicators (MACD, Bollinger Bands).
- Support for user-defined tickers and timeframes.
- Implement database storage for historical data.
