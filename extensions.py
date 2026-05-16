from core.database import DatabaseManager
from core.prediction_engine import PredictionEngine
from core.history_manager import HistoryManager

db_manager = DatabaseManager()
prediction_engine = PredictionEngine()
history_manager = HistoryManager(db_manager)
