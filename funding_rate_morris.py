import ccxt.async_support as ccxt
import asyncio
import pandas as pd
import datetime
import plotly.graph_objects as go

# Initialize dictionary to hold data
data = {}

# Function to convert seconds to 'hour:minute:second' format
def convert_seconds(seconds):
    if seconds is None:
        return None
    seconds = int(seconds)
    return f'{seconds // 3600}:{(seconds % 3600) // 60}:{seconds % 60}'

async def fetch_data(exchange, symbol):
    try:
        markets = await exchange.load_markets()  # get list of markets
        if symbol in markets:
            if 'fetchFundingRate' in dir(exchange):
                funding_rate = await exchange.fetch_funding_rate(symbol)
                if symbol not in data:
                    data[symbol] = {}
                data[symbol][exchange.id] = funding_rate['fundingRate']
            else:
                print(f'{exchange.id} does not support fetching funding rates')
        else:
            print(f'{symbol} is not available on {exchange.id}')
    except Exception as e:
        print(f'An error occurred: {str(e)}')

async def main():
    exchange_ids = ['binance', 'okex', 'bybit','gate','bitget']  # Use a simpler data to test
    # exchange_ids = ['binance', 'okex', 'bybit','gate','mexc','woo','bitget','kucoinfutures','bitmex']
    symbols = ['BTC/USDT:USDT', 'ETH/USDT:USDT', 'LOOM/USDT:USDT']  # Use a simpler data to test
    # symbols = ['BTC/USDT:USDT-230929', 'BTC/USDT:USDT', 'BTC/BUSD:BUSD', 'YFI/USDT:USDT', 'MKR/USDT:USDT', 'FOOTBALL/USDT:USDT', 'ETH/USDT:USDT-230929', 'ETH/USDT:USDT', 'ETH/BUSD:BUSD', 'BTCDOM/USDT:USDT', 'DEFI/USDT:USDT', 'BCH/USDT:USDT', 'COMP/USDT:USDT', 'GMX/USDT:USDT', 'QNT/USDT:USDT', 'BNB/USDT:USDT', 'BNB/BUSD:BUSD', 'LTC/USDT:USDT', 'LTC/BUSD:BUSD', 'AAVE/USDT:USDT', 'SOL/BUSD:BUSD', 'XMR/USDT:USDT', 'SOL/USDT:USDT', 'ZEC/USDT:USDT', 'DASH/USDT:USDT', 'NMR/USDT:USDT', 'TRB/USDT:USDT', 'ZEN/USDT:USDT', 'EGLD/USDT:USDT', 'OGN/USDT:USDT', 'SSV/USDT:USDT', 'KSM/USDT:USDT', 'APT/USDT:USDT', 'APT/BUSD:BUSD', 'INJ/USDT:USDT', 'KNC/USDT:USDT', 'ASTR/USDT:USDT', 'NEO/USDT:USDT', 'AR/USDT:USDT', 'FXS/USDT:USDT', 'AXS/USDT:USDT', 'ETC/USDT:USDT', 'ENS/USDT:USDT', 'LINK/USDT:USDT', 'CVX/USDT:USDT', 'AVAX/USDT:USDT', 'STMX/USDT:USDT', 'ICP/USDT:USDT', 'ATOM/USDT:USDT', 'SNX/USDT:USDT']
    
    # Fetch the funcding rate of each coin based on the order of exchange_ids
    for exchange_id in exchange_ids:
        exchange_class = getattr(ccxt, exchange_id)
        exchange = exchange_class({'enableRateLimit': True})
        tasks = [fetch_data(exchange, symbol) for symbol in symbols]
        await asyncio.gather(*tasks)
        await exchange.close()
        print("Finish fetching", exchange.id)

    # Convert data to DataFrame for easy tabulation and plotting
    df = pd.DataFrame(data)
    transposed_df = df.transpose()
    range_df = pd.DataFrame({"$Range(%)": [0 for exchange in range(len(transposed_df))]}, index=transposed_df.index)
    # print(transposed_df)
    

    # Define colors for highlighting & Create colors array for table
    default_color = 'lavender'
    highlight_color = 'hotpink'
    cell_colors = [[default_color]*(len(transposed_df)) for _ in range(len(transposed_df.columns) + 1)]

    for symbol in transposed_df.index:
        row = transposed_df.loc[symbol]
        max_fr = row.max()
        min_fr = row.min()
        max_exchange = row.idxmax()
        min_exchange = row.idxmin()
        arb_range = (max_fr-min_fr)*100
        print("=====================================================")
        print("Symbol:", symbol)
        print("Max Exchange:", max_exchange)
        print("Min Exchange:", min_exchange)
        print("$Range:", arb_range, "%")

        if max_exchange is not None and min_exchange is not None:
            range_df.loc[symbol] = arb_range
            cell_colors[transposed_df.columns.get_loc(max_exchange) + 1][transposed_df.index.get_loc(symbol)] = highlight_color
            cell_colors[transposed_df.columns.get_loc(min_exchange) + 1][transposed_df.index.get_loc(symbol)] = highlight_color
    print("=====================================================")
    print(range_df)

    # Show the funding rate table
    fig_highlighted_table = go.Figure(data=[go.Table(
        header = dict(values=["Symbol"]+list(transposed_df.columns)+list(range_df.columns), fill_color='paleturquoise', align='left'),
        cells = dict(values=[transposed_df.index]+[transposed_df[col] for col in transposed_df.columns]+[range_df[col] for col in range_df.columns], fill_color=cell_colors+[default_color, default_color, default_color], align='left'))
    ])
    fig_highlighted_table.show()

    # Transaction Executing 
    # To be finished


asyncio.run(main())
