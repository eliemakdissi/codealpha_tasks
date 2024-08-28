import tkinter as tk
from tkinter import ttk
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StockPortfolio:
    def __init__(self, master):
        self.master = master
        self.master.title("Stock Portfolio Tracker")
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.stocks = {}
        self.plotted_lines = {}
        self.company_to_symbol = {
            "Amazon": "AMZN",
            "Nvidia": "NVDA",
            "Apple": "AAPL",
            "Microsoft": "MSFT",
            "Google": "GOOGL",
            "Facebook": "META",
            "Tesla": "TSLA",
            "Netflix": "NFLX",
            "Intel": "INTC",
            "IBM": "IBM",
            "Cisco": "CSCO",
            "Oracle": "ORCL",
            "Adobe": "ADBE",
            "Salesforce": "CRM",
            "PayPal": "PYPL",
            "Shopify": "SHOP",
            "Square": "SQ",
            "Twitter": "TWTR",
            "Uber": "UBER",
            "Lyft": "LYFT",
            "Snap": "SNAP",
            "Spotify": "SPOT",
            "Zoom": "ZM",
            "Slack": "WORK",
            "Pinterest": "PINS",
            "Dropbox": "DBX",
            "Airbnb": "ABNB",
            "Palantir": "PLTR",
            "Snowflake": "SNOW",
            "Coinbase": "COIN",
            "Robinhood": "HOOD",
            "Roku": "ROKU",
            "Peloton": "PTON",
            "Beyond Meat": "BYND",
            "Chewy": "CHWY",
            "Etsy": "ETSY",
            "DoorDash": "DASH",
            "Zillow": "Z",
            "Redfin": "RDFN",
            "Wayfair": "W",
            "Carvana": "CVNA",
            "DraftKings": "DKNG",
            "Bumble": "BMBL",
            "Match Group": "MTCH",
            "Okta": "OKTA",
            "CrowdStrike": "CRWD",
            "Datadog": "DDOG",
            "Atlassian": "TEAM",
            "ServiceNow": "NOW",
            "Twilio": "TWLO",
            "Cloudflare": "NET",
            "Fastly": "FSLY",
            "DocuSign": "DOCU",
            "RingCentral": "RNG",
            "ZoomInfo": "ZI",
            "Asana": "ASAN",
            "Smartsheet": "SMAR",
            "Monday.com": "MNDY",
            "HubSpot": "HUBS",
            "Zendesk": "ZEN",
            "Alteryx": "AYX",
            "Splunk": "SPLK"
        }
        self.company_to_symbol = {k.upper(): v for k, v in self.company_to_symbol.items()}

        self.symbol_label = tk.Label(master, text="Stock Symbol or Company Name:")
        self.symbol_label.grid(row=0, column=0)
        self.symbol_entry = tk.Entry(master)
        self.symbol_entry.grid(row=0, column=1)

        self.add_button = tk.Button(master, text="Add Stock", command=self.add_stock)
        self.add_button.grid(row=0, column=2)

        self.stock_listbox = tk.Listbox(master, width=40)
        self.stock_listbox.grid(row=1, columnspan=3)

        self.remove_button = tk.Button(master, text="Remove Stock", command=self.remove_stock)
        self.remove_button.grid(row=2, column=2)

        self.refresh_button = tk.Button(master, text="Refresh Prices", command=self.refresh_prices)
        self.refresh_button.grid(row=2, column=3)

        self.plot_button = tk.Button(master, text="Plot Stock", command=self.plot_stock)
        self.plot_button.grid(row=2, column=0)

        self.remove_plot_button = tk.Button(master, text="Remove Plot", command=self.remove_plot)
        self.remove_plot_button.grid(row=2, column=1)

        self.message_label = tk.Label(master, text="")
        self.message_label.grid(row=3, columnspan=3)

        self.period_label = tk.Label(master, text="Select Period:")
        self.period_label.grid(row=4, column=0)
        self.period_var = tk.StringVar(value="1d")
        self.period_menu = ttk.Combobox(master, textvariable=self.period_var, values=["1d", "1mo", "1y"], state="readonly")
        self.period_menu.grid(row=4, column=1)

        self.interval_label = tk.Label(master, text="Select Interval:")
        self.interval_label.grid(row=5, column=0)
        self.interval_var = tk.StringVar(value="1m")
        self.interval_menu = ttk.Combobox(master, textvariable=self.interval_var, values=["1m", "5m", "15m", "1h", "1d", "1wk", "1mo"], state="readonly")
        self.interval_menu.grid(row=5, column=1)

        self.fig = None
        self.ax = None
        self.canvas = None

    def add_stock(self):
        name_or_symbol = self.symbol_entry.get().upper()
        symbol = self.company_to_symbol.get(name_or_symbol, name_or_symbol)
        
        if not self.is_valid_symbol(symbol):
            self.message_label.config(text="Invalid stock symbol or company name.")
            return

        if symbol in self.stocks:
            self.message_label.config(text="Stock already exists in the portfolio.")
            return

        try:
            price = self.get_stock_price(symbol)
            self.stocks[symbol] = price
            self.stock_listbox.insert(tk.END, f"{symbol}: ${price:.2f}")
            self.message_label.config(text="Stock added successfully.")
        except Exception as e:
            self.message_label.config(text=f"Failed to add stock: {e}")

    def remove_stock(self):
        selected_index = self.stock_listbox.curselection()
        if not selected_index:
            self.message_label.config(text="Please select a stock to remove.")
            return

        symbol = self.stock_listbox.get(selected_index[0]).split(":")[0].strip()
        del self.stocks[symbol]
        self.stock_listbox.delete(selected_index)
        self.message_label.config(text="Stock removed successfully.")
        
        if symbol in self.plotted_lines:
            self.remove_plot_by_symbol(symbol)

    def refresh_prices(self):
        for i, symbol in enumerate(self.stocks.keys()):
            try:
                price = self.get_stock_price(symbol)
                self.stocks[symbol] = price
                self.stock_listbox.delete(i)
                self.stock_listbox.insert(i, f"{symbol}: ${price:.2f}")
            except Exception as e:
                self.message_label.config(text=f"Failed to refresh prices: {e}")

    def get_stock_price(self, symbol):
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d", interval="1m")
        if not data.empty:
            return data['Close'].iloc[-1]
        else:
            self.message_label.config(text="Invalid response from Yahoo Finance API")

    def is_valid_symbol(self, symbol):
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")
        return not data.empty

    def plot_stock(self):
        selected_index = self.stock_listbox.curselection()
        if not selected_index:
            self.message_label.config(text="Please select a stock to plot.")
            return

        period = self.period_var.get()
        interval = self.interval_var.get()
        symbol = self.stock_listbox.get(selected_index[0]).split(":")[0].strip()
        
        if symbol in self.plotted_lines:
            self.message_label.config(text="Stock is already plotted.")
            return

        stock = yf.Ticker(symbol)
        data = stock.history(period=period, interval=interval)

        if data.empty:
            self.message_label.config(text=f"No data available to plot for {symbol}.")
            return

        if self.fig is None or self.ax is None or self.canvas is None:
            self.fig, self.ax = plt.subplots(figsize=(10, 4))
            self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
            self.canvas.get_tk_widget().grid(row=6, columnspan=3)

        line, = self.ax.plot(data.index, data['Close'], label=f'{symbol} Close Price')
        self.plotted_lines[symbol] = line
        self.ax.set_title("Stock Prices")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Price")
        self.ax.legend()

        for label in self.ax.get_xticklabels():
            label.set_fontsize(8)

        self.canvas.draw()

    def remove_plot(self):
        selected_index = self.stock_listbox.curselection()
        if not selected_index:
            self.message_label.config(text="Please select a stock to remove its plot.")
            return

        symbol = self.stock_listbox.get(selected_index[0]).split(":")[0].strip()
        self.remove_plot_by_symbol(symbol)

    def remove_plot_by_symbol(self, symbol):
        if symbol in self.plotted_lines:
            line = self.plotted_lines.pop(symbol)
            line.remove()

            self.ax.clear()
            for remaining_symbol in self.plotted_lines.keys():
                stock = yf.Ticker(remaining_symbol)
                data = stock.history(period=self.period_var.get(), interval=self.interval_var.get())
                self.ax.plot(data.index, data['Close'], label=f'{remaining_symbol} Close Price')

            if self.plotted_lines:
                self.ax.set_title("Stock Prices Comparison")
                self.ax.set_xlabel("Time")
                self.ax.set_ylabel("Price")
                self.ax.legend()
                for label in self.ax.get_xticklabels():
                    label.set_fontsize(8)
            else:
                self.canvas.get_tk_widget().grid_remove()
                self.fig = None
                self.ax = None
                self.canvas = None

            if self.canvas:
                self.canvas.draw()
            self.message_label.config(text=f"Plot for {symbol} removed successfully.")
        else:
            self.message_label.config(text=f"No plot found for {symbol}.")

    def on_closing(self):
        self.master.destroy()
        self.master.quit()

def main():
    root = tk.Tk()
    app = StockPortfolio(root)
    root.mainloop()

main()
