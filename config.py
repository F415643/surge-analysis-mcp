"""
配置管理模块
Configuration Management for Technical Indicator MCP Service
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class CacheConfig:
    """缓存配置"""
    # 内存缓存TTL (秒)
    hot_data_ttl: int = 900  # 15分钟
    indicator_result_ttl: int = 300  # 5分钟
    screen_result_ttl: int = 600  # 10分钟
    
    # 文件缓存TTL (秒)
    historical_data_ttl: int = 86400  # 24小时
    stock_list_ttl: int = 604800  # 1周
    
    # 缓存大小限制
    max_memory_cache_size: int = 1000  # 最大缓存条目数
    max_file_cache_size_mb: int = 500  # 最大文件缓存大小(MB)
    
    # 缓存目录
    cache_directory: str = "./cache"


@dataclass
class APIConfig:
    """API配置"""
    # 数据源配置
    primary_data_source: str = "yahoo"
    backup_data_sources: List[str] = None
    
    # API密钥配置
    yahoo_finance_api_key: Optional[str] = None  # Yahoo Finance Pro (可选)
    alpha_vantage_api_key: Optional[str] = None  # Alpha Vantage API密钥
    finnhub_api_key: Optional[str] = None        # Finnhub API密钥
    polygon_api_key: Optional[str] = None        # Polygon.io API密钥
    quandl_api_key: Optional[str] = None         # Quandl API密钥
    
    # API限制
    requests_per_minute: int = 100
    requests_per_hour: int = 2000
    max_concurrent_requests: int = 10
    
    # 超时设置
    request_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    
    def __post_init__(self):
        if self.backup_data_sources is None:
            self.backup_data_sources = ["alpha_vantage", "finnhub"]


@dataclass
class MarketConfig:
    """市场配置"""
    # 支持的市场
    supported_markets: List[str] = None
    
    # 默认股票池
    default_stock_pools: Dict[str, List[str]] = None
    
    # 市场交易时间 (UTC)
    market_hours: Dict[str, Dict[str, str]] = None
    
    def __post_init__(self):
        if self.supported_markets is None:
            self.supported_markets = ["US", "CN", "HK"]
        
        if self.default_stock_pools is None:
            self.default_stock_pools = {
                "SP500": [],  # 将在运行时加载
                "HSI": [],    # 恒生指数成分股
                "CSI300": []  # 沪深300成分股
            }
        
        if self.market_hours is None:
            self.market_hours = {
                "US": {"open": "14:30", "close": "21:00"},  # UTC时间
                "CN": {"open": "01:30", "close": "07:00"},  # UTC时间
                "HK": {"open": "01:30", "close": "08:00"}   # UTC时间
            }


@dataclass
class IndicatorConfig:
    """技术指标配置"""
    # 默认参数
    default_ma_periods: List[int] = None
    default_rsi_period: int = 14
    default_macd_params: Dict[str, int] = None
    default_bb_period: int = 20
    default_bb_std: float = 2.0
    default_kdj_period: int = 9
    default_williams_period: int = 14
    
    # 计算限制
    max_data_points: int = 10000
    min_data_points_for_calculation: int = 50
    
    def __post_init__(self):
        if self.default_ma_periods is None:
            self.default_ma_periods = [5, 10, 20, 50, 200]
        
        if self.default_macd_params is None:
            self.default_macd_params = {"fast": 12, "slow": 26, "signal": 9}


@dataclass
class ScreeningConfig:
    """筛选配置"""
    # 结果限制
    max_screen_results: int = 100
    default_screen_limit: int = 50
    
    # 评分权重
    default_condition_weight: float = 1.0
    max_conditions_per_screen: int = 10
    
    # 超时设置
    screen_timeout_seconds: int = 60
    scan_timeout_seconds: int = 30


@dataclass
class AlertConfig:
    """预警配置"""
    # 预警限制
    max_alerts_per_user: int = 50
    max_total_alerts: int = 1000
    
    # 检查频率
    alert_check_interval: int = 60  # 秒
    
    # 预警保留时间
    alert_history_days: int = 30


@dataclass
class BacktestConfig:
    """回测配置"""
    # 时间限制
    max_backtest_years: int = 5
    min_backtest_days: int = 30
    
    # 复杂度限制
    max_strategy_conditions: int = 5
    max_concurrent_backtests: int = 3
    
    # 性能设置
    backtest_timeout_minutes: int = 10


@dataclass
class SurgeAnalysisConfig:
    """暴涨分析配置"""
    # 暴涨检测参数
    default_surge_threshold: float = 20.0  # 默认暴涨阈值(%)
    min_surge_duration: int = 1           # 最小持续天数
    max_surge_duration: int = 30          # 最大持续天数
    volume_surge_threshold: float = 1.5   # 成交量放大阈值
    
    # 分析窗口配置
    pre_surge_analysis_window: int = 30   # 暴涨前分析窗口
    pattern_analysis_window: int = 60     # 形态分析窗口
    momentum_analysis_window: int = 20    # 动量分析窗口
    
    # 技术指标阈值
    rsi_oversold_threshold: float = 30
    rsi_overbought_threshold: float = 70
    mfi_oversold_threshold: float = 20
    mfi_overbought_threshold: float = 80
    
    # 形态识别参数
    consolidation_threshold: float = 0.05  # 整理形态阈值
    breakout_threshold: float = 0.02       # 突破阈值
    pattern_confidence_threshold: float = 60  # 形态置信度阈值
    
    # 相似度分析参数
    similarity_threshold: float = 0.7      # 相似度阈值
    max_similar_patterns: int = 5          # 最大相似模式数量
    
    # 预测参数
    prediction_confidence_threshold: float = 60  # 预测置信度阈值
    high_probability_threshold: float = 70       # 高概率阈值
    medium_probability_threshold: float = 40     # 中等概率阈值


@dataclass
class SystemConfig:
    """系统配置"""
    # 日志配置
    log_level: str = "INFO"
    log_file: str = "technical_indicator_mcp.log"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_max_size: int = 10485760  # 10MB
    log_backup_count: int = 5
    
    # 性能配置
    max_workers: int = 4
    max_memory_usage_mb: int = 512
    
    # 安全配置
    enable_rate_limiting: bool = True
    enable_caching: bool = True
    
    # 开发配置
    debug_mode: bool = False
    test_mode: bool = False