# settings.py

# Kraken API Credentials
KRAKEN_API_KEY = "QbKj+kbW+g2FERPllj7B54IIQJz4m1gR714i5EpizHwa4fzDZylfijpH"
KRAKEN_API_SECRET = "em5Kv0AY0dYwljWXPCRJOAEX/CIC+rW4hV9WfxFGRcomC2Qs1NRX3MO/AhjrIzQFjNgQ7VokY/RD9a65FJbqj/fV"

# Kraken API URLs
BASE_URL = "https://demo-futures.kraken.com/derivatives/api/v3"
WS_URL = "wss://demo-futures.kraken.com/ws/v1"

SYMBOL = "PI_XBTUSD"
STREAM_NAME = "ticker"

PRODUCTION_MODE = False

DEFAULT_BRAIN = "heuristic"

MAX_LOSS_PERCENT = 10.0
TICK_SIZE = 0.5
QUANTITY_PRECISION = 2

ENABLE_SENTIMENT_ANALYSIS = False
ENABLE_RAG_VECTOR_SEARCH = False
ENABLE_ALF_GRAPH_MODE = False