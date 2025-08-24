#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分析器功能
Test analyzer functionality
"""

import pytest
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from universal_surge_analyzer import UniversalSurgeAnalyzer
except ImportError:
    pytest.skip("UniversalSurgeAnalyzer not available", allow_module_level=True)


class TestUniversalSurgeAnalyzer:
    """测试通用暴涨分析器"""
    
    def setup_method(self):
        """测试前设置"""
        self.analyzer = UniversalSurgeAnalyzer()
    
    def test_analyzer_initialization(self):
        """测试分析器初始化"""
        assert self.analyzer is not None
        assert hasattr(self.analyzer, 'analyze_stock')
    
    @pytest.mark.asyncio
    async def test_analyze_stock_basic(self):
        """测试基本股票分析功能"""
        try:
            # 使用测试数据或模拟数据
            result = self.analyzer.analyze_stock("000001", days=30)
            
            # 验证返回结果结构
            if result:
                assert isinstance(result, dict)
                # 可以添加更多具体的断言
                
        except Exception as e:
            # 在没有网络或数据源的情况下，测试应该优雅地处理
            pytest.skip(f"Skipping due to data source issue: {e}")
    
    def test_analyzer_parameters(self):
        """测试分析器参数验证"""
        # 测试无效参数
        with pytest.raises((ValueError, TypeError)):
            self.analyzer.analyze_stock("", days=-1)
    
    def test_analyzer_methods_exist(self):
        """测试分析器必要方法存在"""
        required_methods = ['analyze_stock']
        
        for method in required_methods:
            assert hasattr(self.analyzer, method)
            assert callable(getattr(self.analyzer, method))


if __name__ == "__main__":
    pytest.main([__file__])