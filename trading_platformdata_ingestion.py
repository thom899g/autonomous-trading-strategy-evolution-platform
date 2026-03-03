"""
Market Data Ingestion Module
Handles real-time and historical data collection from exchanges
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import ccxt
import pandas as pd
import numpy as np
from .config import config

class MarketDataFetcher:
    """Fetches and processes market data from exchanges"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.exchange = None
        self._initialize_exchange()
        
    def _initialize_exchange(self):
        """Initialize exchange connection with error handling"""
        try:
            exchange_class = getattr(ccxt, config.exchange_config.exchange_id)
            exchange_params = {
                'apiKey': config.exchange_config.api_key,
                'secret': config.exchange_config.api_secret,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'spot'
                }
            }
            
            if config.exchange_config.testnet:
                exchange_params['urls'] = {'api': 'https://testnet.binance.vision/api'}
                
            self.exchange = exchange_class(exchange_params)
            self.exchange.load_markets()
            self.logger.info(f"Initialized {config