
def price_message(stock: dict):
    return f"{stock['info']['name']}\n目前價格: {stock['realtime']['latest_trade_price']}"

def ma31(ma_31: list, days: str):
    return f"31 日內的 {days}MA:\n{ma_31}"