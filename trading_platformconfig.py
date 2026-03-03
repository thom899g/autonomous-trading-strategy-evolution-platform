"""
Platform Configuration Module
Centralized configuration management for the Autonomous Trading Platform
Uses environment variables with Firebase as primary state store
"""
import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
load_dotenv()

@dataclass
class DatabaseConfig:
    """Firebase database configuration"""
    project_id: str = os.getenv("FIREBASE_PROJECT_ID", "trading-platform-dev")
    collection_strategies: str = "trading_strategies"
    collection_backtests: str = "backtest_results"
    collection_market_data: str = "market_data_snapshots"
    collection_execution_logs: str = "execution_logs"

@dataclass
class ExchangeConfig:
    """Exchange API configuration"""
    exchange_id: str = "binance"
    api_key: str = os.getenv("EXCHANGE_API_KEY", "")
    api_secret: str = os.getenv("EXCHANGE_API_SECRET", "")
    testnet: bool = True
    rate_limit: int = 100  # requests per minute

@dataclass
class RLConfig:
    """Reinforcement Learning configuration"""
    learning_rate: float = 0.001
    gamma: float = 0.99
    epsilon_start: float = 1.0
    epsilon_end: float = 0.01
    epsilon_decay: float = 0.995
    memory_size: int = 10000
    batch_size: int = 64
    target_update: int = 100

@dataclass
class ModelConfig:
    """Neural network model configuration"""
    hidden_layers: tuple = (256, 128, 64)
    dropout_rate: float = 0.2
    activation: str = "relu"
    optimizer: str = "adam"

class ConfigManager:
    """Manages platform configuration with Firebase integration"""
    
    def __init__(self):
        self.db_config = DatabaseConfig()
        self.exchange_config = ExchangeConfig()
        self.rl_config = RLConfig()
        self.model_config = ModelConfig()
        self._firebase_app = None
        self._db = None
        
        # Setup logging
        self.setup_logging()
        
    def setup_logging(self):
        """Configure structured logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('trading_platform.log')
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def initialize_firebase(self) -> bool:
        """Initialize Firebase connection with error handling"""
        try:
            if not firebase_admin._apps:
                # Use service account if available, otherwise use default
                cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
                if cred_path and os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                else:
                    cred = credentials.ApplicationDefault()
                    
                self._firebase_app = firebase_admin.initialize_app(cred, {
                    'projectId': self.db_config.project_id
                })
                self._db = firestore.client()
                self.logger.info("Firebase initialized successfully")
                return True
            else:
                self.logger.warning("Firebase already initialized")
                return False
        except Exception as e:
            self.logger.error(f"Failed to initialize Firebase: {e}")
            return False
            
    @property
    def db(self) -> Optional[firestore.Client]:
        """Get Firestore database client"""
        if not self._db:
            self.initialize_firebase()
        return self._db
        
    def validate_config(self) -> bool:
        """Validate all configuration parameters"""
        errors = []
        
        # Validate exchange credentials
        if not self.exchange_config.api_key or not self.exchange_config.api_secret:
            errors.append("Exchange API credentials not configured")
            
        # Validate Firebase connection
        if not self._db:
            self.logger.warning("Firebase not initialized, attempting connection...")
            if not self.initialize_firebase():
                errors.append("Failed to connect to Firebase")
                
        if errors:
            self.logger.error(f"Configuration validation failed: {errors}")
            return False
        return True
        
    def get_config_dict(self) -> Dict[str, Any]:
        """Return all configuration as dictionary"""
        return {
            'database': asdict(self.db_config),
            'exchange': asdict(self.exchange_config),
            'rl': asdict(self.rl_config),
            'model': asdict(self.model_config)
        }

# Global configuration instance
config = ConfigManager()