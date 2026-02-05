"""
統一的異常定義模組
集中導入 MongoDB 相關異常，避免循環導入和導入順序問題
"""
from pymongo.errors import (
    ConnectionFailure,
    ServerSelectionTimeoutError,
    OperationFailure,
    ConfigurationError
)

__all__ = [
    'ConnectionFailure',
    'ServerSelectionTimeoutError',
    'OperationFailure',
    'ConfigurationError'
]

