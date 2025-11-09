from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return [
  { "id": "bitcoin", "symbol": "BTC", "name": "Bitcoin" },
  { "id": "ethereum", "symbol": "ETH", "name": "Ethereum" },
  { "id": "tether", "symbol": "USDT", "name": "Tether" },
  { "id": "binancecoin", "symbol": "BNB", "name": "Binance Coin" },
  { "id": "solana", "symbol": "SOL", "name": "Solana" },
  { "id": "ripple", "symbol": "XRP", "name": "XRP" },
  { "id": "cardano", "symbol": "ADA", "name": "Cardano" },
  { "id": "dogecoin", "symbol": "DOGE", "name": "Dogecoin" },
  { "id": "tron", "symbol": "TRX", "name": "TRON" },
  { "id": "matic-network", "symbol": "MATIC", "name": "Polygon" },
  { "id": "polkadot", "symbol": "DOT", "name": "Polkadot" },
  { "id": "litecoin", "symbol": "LTC", "name": "Litecoin" },
  { "id": "avalanche-2", "symbol": "AVAX", "name": "Avalanche" },
  { "id": "shiba-inu", "symbol": "SHIB", "name": "Shiba Inu" },
  { "id": "chainlink", "symbol": "LINK", "name": "Chainlink" },
  { "id": "stellar", "symbol": "XLM", "name": "Stellar" },
  { "id": "uniswap", "symbol": "UNI", "name": "Uniswap" },
  { "id": "internet-computer", "symbol": "ICP", "name": "Internet Computer" },
  { "id": "cosmos", "symbol": "ATOM", "name": "Cosmos" },
  { "id": "monero", "symbol": "XMR", "name": "Monero" },
  { "id": "bitcoin-cash", "symbol": "BCH", "name": "Bitcoin Cash" },
  { "id": "near", "symbol": "NEAR", "name": "Near Protocol" },
  { "id": "aptos", "symbol": "APT", "name": "Aptos" },
  { "id": "pepe", "symbol": "PEPE", "name": "Pepe" },
  { "id": "render-token", "symbol": "RNDR", "name": "Render" },
  { "id": "arbitrum", "symbol": "ARB", "name": "Arbitrum" },
  { "id": "optimism", "symbol": "OP", "name": "Optimism" }
]
