#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pytest 配置文件
pytest configuration file
"""

import pytest
import sys
import os
import asyncio

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 设置环境变量
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['TESTING'] = 'true'


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于异步测试"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_stock_data():
    """提供示例股票数据用于测试"""
    import pandas as pd
    import numpy as np
    from datetime import datetime, timedelta
    
    # 生成模拟股票数据
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=100),
        end=datetime.now(),
        freq='D'
    )
    
    # 模拟价格数据
    np.random.seed(42)  # 确保可重现性
    base_price = 10.0
    returns = np.random.normal(0, 0.02, len(dates))
    prices = [base_price]
    
    for ret in returns[1:]:
        prices.append(prices[-1] * (1 + ret))
    
    data = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * (1 + abs(np.random.normal(0, 0.01))) for p in prices],
        'low': [p * (1 - abs(np.random.normal(0, 0.01))) for p in prices],
        'close': prices,
        'volume': np.random.randint(1000000, 10000000, len(dates)),
        'amount': [p * v for p, v in zip(prices, np.random.randint(1000000, 10000000, len(dates)))]
    })
    
    return data


@pytest.fixture
def mock_analyzer():
    """提供模拟分析器用于测试"""
    class MockAnalyzer:
        def __init__(self):
            self.surge_threshold = 5.0
            self.volume_threshold = 2.0
        
        def analyze_stock(self, symbol, name=None, days=180):
            """模拟股票分析"""
            return {
                "symbol": symbol,
                "name": name or f"Stock {symbol}",
                "analysis_period": days,
                "basic_info": {
                    "current_price": 10.50,
                    "price_change": 0.25,
                    "price_change_pct": 2.44
                },
                "surge_analysis": {
                    "surge_count": 3,
                    "surge_frequency": 0.15,
                    "avg_surge_magnitude": 7.2
                },
                "technical_indicators": {
                    "rsi": 65.4,
                    "macd": 0.12,
                    "volume_ratio": 1.8
                },
                "risk_assessment": {
                    "volatility": 0.25,
                    "risk_level": "Medium"
                }
            }
    
    return MockAnalyzer()


@pytest.fixture
def sample_stock_symbols():
    """提供示例股票代码用于测试"""
    return [
        ("000001", "平安银行"),
        ("000002", "万科A"),
        ("600036", "招商银行"),
        ("600519", "贵州茅台")
    ]


def pytest_configure(config):
    """pytest 配置"""
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """修改测试项目收集"""
    # 为没有标记的测试添加 unit 标记
    for item in items:
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.unit)