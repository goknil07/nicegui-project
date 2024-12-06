from nicegui import ui
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

 


def calculate_dates(time_range):
    """
    Function to calculate dates based on the selected time range
    """
    today = datetime.today()
    if time_range == "Son 6 Ay":
        start_date = (today - timedelta(days=182)).strftime("%Y-%m-%d")             
    elif time_range == "Son 1 Yıl":
        start_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")
    elif time_range == "Son 2 Yıl":
        start_date = (today - timedelta(days=730)).strftime("%Y-%m-%d")
    elif time_range == "Son 5 Yıl":
        start_date = (today - timedelta(days=1825)).strftime("%Y-%m-%d")
    else:
        start_date = ""
    end_date = today.strftime("%Y-%m-%d")
    return start_date, end_date

# Function to identify Buy/Sell points
def identify_signals(closing_prices, short_term_ma, long_term_ma):
    signals = pd.DataFrame(index=closing_prices.index)
    signals['Buy'] = (short_term_ma > long_term_ma) & (short_term_ma.shift(1) <= long_term_ma.shift(1))
    signals['Sell'] = (short_term_ma < long_term_ma) & (short_term_ma.shift(1) >= long_term_ma.shift(1))
    return signals

# Function to process data and create a graph based on user inputs
def handle_inputs(time_range, start_date, end_date, stock_symbol):
    if time_range != "Manuel":
        start_date, end_date = calculate_dates(time_range)

    try:
        t1 = datetime.strptime(start_date, "%Y-%m-%d")
        t2 = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return "Lütfen tarih formatını (YYYY-MM-DD) doğru girin.", None

    if t1 > t2:
        return "Başlangıç tarihi bitiş tarihinden büyük olamaz.", None

    if stock_symbol.strip():
        try:
            stock = yf.Ticker(stock_symbol)
            hist = stock.history(start=start_date, end=end_date)
            closing_prices = hist['Close']
        except Exception as e:
            return f"Veri çekilirken hata oluştu: {str(e)}", None
    else:
        return "Lütfen geçerli bir hisse senedi sembolü girin.", None

    if closing_prices.empty:
        return "Belirtilen tarih aralığında veri bulunamadı.", None

    # Calculate moving averages
    short_term_ma = closing_prices.rolling(window=20).mean()
    long_term_ma = closing_prices.rolling(window=50).mean()

    # Identify Buy/Sell signals
    signals = identify_signals(closing_prices, short_term_ma, long_term_ma)

    # Create the graph
    plt.figure(figsize=(30, 20))  # Updated graph size
    plt.plot(closing_prices, label=f'{stock_symbol} Closing Prices', color='blue')
    plt.plot(short_term_ma, label='20-Day Moving Average', color='orange')
    plt.plot(long_term_ma, label='50-Day Moving Average', color='green')

    # Mark Buy/Sell points
    buy_signals = closing_prices[signals['Buy']]
    sell_signals = closing_prices[signals['Sell']]
    plt.scatter(buy_signals.index, buy_signals, label='Buy Signal', marker='^', color='green', s=100)
    plt.scatter(sell_signals.index, sell_signals, label='Sell Signal', marker='v', color='red', s=100)

    plt.title(f'{stock_symbol} Closing Prices with Buy/Sell Signals')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid()

    # Save the graph with a unique name for each analysis
    grafik_dosyasi = f"grafik_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    plt.savefig(grafik_dosyasi)
    plt.close()

    return f"Başlangıç Tarihi: {start_date}\nBitiş Tarihi: {end_date}", grafik_dosyasi

# Create the interface
with ui.column().classes('space-y-4'):
    # Header Section
    with ui.row().classes('bg-gray-800 text-white p-4 rounded-lg shadow-lg'):
        ui.label("Hisse Senedi Analiz Uygulaması").classes('text-2xl font-bold')

    # Stock symbol input
    with ui.row().classes('bg-gray-100 p-4 rounded-lg shadow-lg'):
        stock_symbol_input = ui.input(
            label="Hisse Senedi Sembolü (Örn: MSFT, AAPL)"
        ).classes('p-2 border rounded-lg')

    # Other inputs
    time_range = ui.radio(
        options=["Son 6 Ay", "Son 1 Yıl", "Son 2 Yıl", "Manuel"],
        value="Son 6 Ay"
    ).classes('p-2')

    start_date = ui.input(label="Başlangıç Tarihi (YYYY-MM-DD)").classes('p-2 border rounded-lg')
    end_date = ui.input(label="Bitiş Tarihi (YYYY-MM-DD)").classes('p-2 border rounded-lg')

    result = ui.label("").classes('text-lg mt-4')
    grafik = ui.image().style('max-height: 600px;').classes('rounded-lg shadow-lg')

    def run_analysis():
        result_text, grafik_dosyasi = handle_inputs(
            time_range.value, start_date.value, end_date.value, stock_symbol_input.value
        )
        result.set_text(result_text)
        if grafik_dosyasi:
            grafik.set_source(grafik_dosyasi)

    ui.button("Analizi Çalıştır", on_click=run_analysis).classes('mt-4 bg-blue-500 text-white p-2 rounded-lg hover:bg-blue-700')

ui.run()








