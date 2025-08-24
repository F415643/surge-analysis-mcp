#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clean MCP Server for Stock Surge Analysis
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import json
from typing import Any, Dict, List, Optional
import pandas as pd
import akshare as ak

# 设置编码
os.environ['PYTHONIOENCODING'] = 'utf-8'

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# 创建服务器实例
server = Server("surge-analysis-server")

# 预设股票列表
POPULAR_STOCKS = [
    ["000001", "平安银行"],
    ["000002", "万科A"],
    ["000858", "五粮液"],
    ["600036", "招商银行"],
    ["600519", "贵州茅台"]
]

TECH_STOCKS = [
    ["000002", "万科A"],
    ["002415", "海康威视"],
    ["000725", "京东方A"],
    ["002230", "科大讯飞"],
    ["300059", "东方财富"]
]


class CleanSurgeAnalyzer:
    """Clean surge analyzer without emoji characters"""
    
    def __init__(self):
        self.surge_threshold = 5.0
        self.volume_threshold = 2.0
        
    async def analyze_stock(self, symbol: str, name: str = None, days: int = 180):
        """Analyze stock surge patterns"""
        try:
            # Get stock data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            hist_df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily", 
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                adjust="qfq"
            )
            
            if hist_df.empty:
                return None
            
            # Data preprocessing
            hist_df['日期'] = pd.to_datetime(hist_df['日期'])
            hist_df = hist_df.sort_values('日期')
            hist_df['涨跌幅'] = hist_df['收盘'].pct_change() * 100
            
            # Basic statistics
            basic_stats = {
                'current_price': float(hist_df['收盘'].iloc[-1]),
                'total_return': float(((hist_df['收盘'].iloc[-1] / hist_df['收盘'].iloc[0]) - 1) * 100),
                'volatility': float(hist_df['涨跌幅'].std()),
                'min_price': float(hist_df['收盘'].min()),
                'max_price': float(hist_df['收盘'].max())
            }
            
            # Surge analysis
            surge_days = hist_df[hist_df['涨跌幅'] > self.surge_threshold].copy()
            surges = []
            for _, row in surge_days.iterrows():
                surges.append({
                    'date': row['日期'].strftime('%Y-%m-%d'),
                    'return': float(row['涨跌幅']),
                    'volume': int(row['成交量']),
                    'price': float(row['收盘'])
                })
            
            # Sort by date descending
            surges = sorted(surges, key=lambda x: x['date'], reverse=True)
            
            # Volume analysis
            avg_volume = hist_df['成交量'].mean()
            volume_spikes = hist_df[hist_df['成交量'] > avg_volume * self.volume_threshold]
            
            volume_stats = {
                'avg_volume': int(avg_volume),
                'max_volume': int(hist_df['成交量'].max()),
                'spikes': len(volume_spikes)
            }
            
            # Company info
            try:
                company_info = ak.stock_individual_info_em(symbol=symbol)
                company_data = {}
                if not company_info.empty:
                    for _, row in company_info.iterrows():
                        key = str(row['item']).strip()
                        value = str(row['value']).strip()
                        if key and value and key != 'nan' and value != 'nan':
                            company_data[key] = value
            except:
                company_data = {}
            
            return {
                'basic': basic_stats,
                'surges': surges,
                'volume': volume_stats,
                'company': company_data
            }
            
        except Exception as e:
            return None


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="analyze_single_stock",
            description="分析单只股票的暴涨逻辑和技术指标",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "股票代码，如 000158"
                    },
                    "name": {
                        "type": "string",
                        "description": "股票名称（可选）"
                    },
                    "days": {
                        "type": "integer",
                        "description": "分析天数，默认180天",
                        "default": 180
                    }
                },
                "required": ["symbol"]
            }
        ),
        types.Tool(
            name="get_surge_summary",
            description="获取股票暴涨事件摘要信息",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "股票代码"
                    },
                    "name": {
                        "type": "string",
                        "description": "股票名称（可选）"
                    },
                    "surge_threshold": {
                        "type": "number",
                        "description": "暴涨阈值（百分比），默认5.0",
                        "default": 5.0
                    }
                },
                "required": ["symbol"]
            }
        ),
        types.Tool(
            name="compare_stocks",
            description="对比分析两只或多只股票的表现",
            inputSchema={
                "type": "object",
                "properties": {
                    "stocks": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 2,
                            "maxItems": 2
                        },
                        "description": "股票列表，格式：[["代码", "名称"], ...]",
                        "minItems": 2
                    },
                    "days": {
                        "type": "integer",
                        "description": "分析天数，默认180天",
                        "default": 180
                    }
                },
                "required": ["stocks"]
            }
        ),
        types.Tool(
            name="batch_analyze_stocks",
            description="批量分析股票组合",
            inputSchema={
                "type": "object",
                "properties": {
                    "preset": {
                        "type": "string",
                        "description": "预设组合：popular（热门股）或 tech（科技股）",
                        "enum": ["popular", "tech"]
                    },
                    "stocks": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 2,
                            "maxItems": 2
                        },
                        "description": "自定义股票列表"
                    },
                    "days": {
                        "type": "integer",
                        "description": "分析天数，默认180天",
                        "default": 180
                    }
                }
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls"""
    analyzer = CleanSurgeAnalyzer()
    
    if name == "analyze_single_stock":
        symbol = arguments.get("symbol")
        name = arguments.get("name", symbol)
        days = arguments.get("days", 180)
        
        result = await analyzer.analyze_stock(symbol, name, days)
        if result:
            report = f"股票分析：{name} ({symbol})\n"
            report += "=" * 50 + "\n"
            report += f"当前价格：{result['basic']['current_price']:.2f}\n"
            report += f"总回报率：{result['basic']['total_return']:.2f}%\n"
            report += f"波动率：{result['basic']['volatility']:.2f}%\n"
            report += f"价格区间：{result['basic']['min_price']:.2f} - {result['basic']['max_price']:.2f}\n"
            report += f"暴涨次数：{len(result['surges'])}\n"
            
            if result['surges']:
                report += "\n最近暴涨事件：\n"
                for surge in result['surges'][:3]:
                    report += f"  {surge['date']}: {surge['return']:.2f}% (成交量: {surge['volume']})\n"
            
            return [types.TextContent(type="text", text=report)]
        else:
            return [types.TextContent(type="text", text=f"无法获取 {symbol} 的数据，请检查股票代码是否正确")]
    
    elif name == "get_surge_summary":
        symbol = arguments.get("symbol")
        name = arguments.get("name", symbol)
        threshold = arguments.get("surge_threshold", 5.0)
        
        # 使用分析器获取数据
        result = await analyzer.analyze_stock(symbol, name, 360)  # 1年数据
        if result:
            surges = [s for s in result['surges'] if s['return'] >= threshold]
            
            report = f"暴涨摘要：{name} ({symbol})\n"
            report += "=" * 40 + "\n"
            report += f"暴涨阈值：{threshold}%\n"
            report += f"暴涨次数：{len(surges)}\n"
            
            if surges:
                report += f"最大单日涨幅：{max(s['return'] for s in surges):.2f}%\n"
                report += f"平均暴涨幅度：{sum(s['return'] for s in surges)/len(surges):.2f}%\n"
                
                report += "\n最近暴涨事件：\n"
                for surge in surges[:5]:
                    report += f"  {surge['date']}: {surge['return']:.2f}%\n"
            
            return [types.TextContent(type="text", text=report)]
        else:
            return [types.TextContent(type="text", text=f"无法获取 {symbol} 的数据")]
    
    elif name == "compare_stocks":
        stocks = arguments.get("stocks", [])
        days = arguments.get("days", 180)
        
        comparison = []
        for stock in stocks:
            symbol, name = stock[0], stock[1]
            result = await analyzer.analyze_stock(symbol, name, days)
            if result:
                comparison.append({
                    'symbol': symbol,
                    'name': name,
                    'data': result
                })
        
        if comparison:
            report = "股票对比分析\n"
            report += "=" * 50 + "\n"
            
            for item in comparison:
                data = item['data']
                report += f"\n{item['name']} ({item['symbol']}):\n"
                report += f"  总回报率：{data['basic']['total_return']:.2f}%\n"
                report += f"  波动率：{data['basic']['volatility']:.2f}%\n"
                report += f"  暴涨次数：{len(data['surges'])}\n"
            
            return [types.TextContent(type="text", text=report)]
        else:
            return [types.TextContent(type="text", text="无法获取对比数据")]
    
    elif name == "batch_analyze_stocks":
        preset = arguments.get("preset")
        custom_stocks = arguments.get("stocks", [])
        days = arguments.get("days", 180)
        
        if preset == "popular":
            stocks = POPULAR_STOCKS
        elif preset == "tech":
            stocks = TECH_STOCKS
        else:
            stocks = custom_stocks
        
        results = []
        for stock in stocks:
            symbol, name = stock[0], stock[1]
            result = await analyzer.analyze_stock(symbol, name, days)
            if result:
                results.append({
                    'symbol': symbol,
                    'name': name,
                    'data': result
                })
        
        if results:
            report = f"批量分析结果 ({preset or '自定义'})\n"
            report += "=" * 50 + "\n"
            
            for item in results:
                data = item['data']
                report += f"\n{item['name']} ({item['symbol']}):\n"
                report += f"  总回报率：{data['basic']['total_return']:.2f}%\n"
                report += f"  波动率：{data['basic']['volatility']:.2f}%\n"
                report += f"  暴涨次数：{len(data['surges'])}\n"
            
            return [types.TextContent(type="text", text=report)]
        else:
            return [types.TextContent(type="text", text="批量分析失败")]
    
    return [types.TextContent(type="text", text="未知工具")]


async def main():
    """Main function"""
    # Run server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="surge-analysis-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities()
            )
        )


if __name__ == "__main__":
    asyncio.run(main())