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
            description="批量分析多只股票并生成对比报告",
            inputSchema={
                "type": "object",
                "properties": {
                    "preset": {
                        "type": "string",
                        "enum": ["popular", "tech", "custom"],
                        "description": "预设股票列表：popular(热门股票), tech(科技股票), custom(自定义)"
                    },
                    "custom_stocks": {
                        "type": "array",
                        "items": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 2,
                            "maxItems": 2
                        },
                        "description": "自定义股票列表，格式：[["代码", "名称"], ...]"
                    },
                    "days": {
                        "type": "integer",
                        "description": "分析天数，默认180天",
                        "default": 180
                    }
                },
                "required": ["preset"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""
    
    if name == "analyze_single_stock":
        return await _analyze_single_stock(arguments or {})
    elif name == "get_surge_summary":
        return await _get_surge_summary(arguments or {})
    elif name == "compare_stocks":
        return await _compare_stocks(arguments or {})
    elif name == "batch_analyze_stocks":
        return await _batch_analyze_stocks(arguments or {})
    else:
        raise ValueError(f"Unknown tool: {name}")


async def _analyze_single_stock(args: Dict[str, Any]) -> List[types.TextContent]:
    """Analyze single stock"""
    symbol = args.get("symbol")
    name = args.get("name")
    days = args.get("days", 180)
    
    if not symbol:
        return [types.TextContent(type="text", text="Error: Missing stock symbol")]
    
    try:
        analyzer = CleanSurgeAnalyzer()
        result = await analyzer.analyze_stock(symbol, name, days)
        
        if not result:
            return [types.TextContent(type="text", text=f"Failed to get data for stock {symbol}")]
        
        # Format result
        output = _format_single_analysis(symbol, name or symbol, result)
        
        return [types.TextContent(type="text", text=output)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Analysis failed: {str(e)}")]


async def _get_surge_summary(args: Dict[str, Any]) -> List[types.TextContent]:
    """Get surge summary"""
    symbol = args.get("symbol")
    name = args.get("name")
    surge_threshold = args.get("surge_threshold", 5.0)
    
    if not symbol:
        return [types.TextContent(type="text", text="Error: Missing stock symbol")]
    
    try:
        analyzer = CleanSurgeAnalyzer()
        analyzer.surge_threshold = surge_threshold
        
        result = await analyzer.analyze_stock(symbol, name, 180)
        
        if not result:
            return [types.TextContent(type="text", text=f"Failed to get data for stock {symbol}")]
        
        # Generate summary
        output = _format_surge_summary(symbol, name or symbol, result, surge_threshold)
        
        return [types.TextContent(type="text", text=output)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Summary failed: {str(e)}")]


async def _compare_stocks(args: Dict[str, Any]) -> List[types.TextContent]:
    """Compare stocks"""
    stocks = args.get("stocks", [])
    days = args.get("days", 180)
    
    if len(stocks) < 2:
        return [types.TextContent(type="text", text="Error: Need at least 2 stocks for comparison")]
    
    try:
        analyzer = CleanSurgeAnalyzer()
        results = []
        
        for symbol, name in stocks:
            result = await analyzer.analyze_stock(symbol, name, days)
            if result:
                results.append({
                    'symbol': symbol,
                    'name': name,
                    'data': result
                })
        
        if len(results) < 2:
            return [types.TextContent(type="text", text="Comparison failed: Insufficient valid data")]
        
        # Format comparison result
        output = _format_comparison(results)
        
        return [types.TextContent(type="text", text=output)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Comparison failed: {str(e)}")]


async def _batch_analyze_stocks(args: Dict[str, Any]) -> List[types.TextContent]:
    """Batch analyze stocks"""
    preset = args.get("preset")
    custom_stocks = args.get("custom_stocks", [])
    days = args.get("days", 180)
    
    # Determine stock list
    if preset == "popular":
        stock_list = POPULAR_STOCKS
    elif preset == "tech":
        stock_list = TECH_STOCKS
    elif preset == "custom":
        if not custom_stocks:
            return [types.TextContent(type="text", text="Error: Custom mode requires stock list")]
        stock_list = custom_stocks
    else:
        return [types.TextContent(type="text", text="Error: Invalid preset type")]
    
    try:
        analyzer = CleanSurgeAnalyzer()
        results = []
        
        for symbol, name in stock_list:
            result = await analyzer.analyze_stock(symbol, name, days)
            if result:
                results.append({
                    'symbol': symbol,
                    'name': name,
                    'surge_count': len(result['surges']),
                    'total_return': result['basic']['total_return'],
                    'volatility': result['basic']['volatility']
                })
        
        if not results:
            return [types.TextContent(type="text", text="Batch analysis failed")]
        
        # Format result
        output = _format_batch_analysis(results, preset)
        
        return [types.TextContent(type="text", text=output)]
        
    except Exception as e:
        return [types.TextContent(type="text", text=f"Batch analysis failed: {str(e)}")]


def _format_single_analysis(symbol: str, name: str, result: Dict) -> str:
    """Format single stock analysis result"""
    basic = result['basic']
    surges = result['surges']
    volume = result['volume']
    company = result['company']
    
    output = f"Stock Analysis Report: {name}({symbol})\n"
    output += "=" * 50 + "\n\n"
    
    # Basic info
    output += f"Basic Performance:\n"
    output += f"  Current Price: ${basic['current_price']:.2f}\n"
    output += f"  Total Return: {basic['total_return']:+.2f}%\n"
    output += f"  Volatility: {basic['volatility']:.2f}%\n"
    output += f"  Price Range: ${basic['min_price']:.2f} - ${basic['max_price']:.2f}\n\n"
    
    # Surge analysis
    output += f"Surge Analysis:\n"
    output += f"  Surge Count: {len(surges)} times\n"
    if surges:
        max_surge = max(s['return'] for s in surges)
        output += f"  Max Surge: +{max_surge:.2f}%\n"
        output += f"  Recent Surge: {surges[0]['date']} (+{surges[0]['return']:.2f}%)\n"
    output += "\n"
    
    # Volume analysis
    output += f"Volume Analysis:\n"
    output += f"  Average Volume: {volume['avg_volume']:,.0f}\n"
    output += f"  Volume Spikes: {volume['spikes']} times\n"
    output += f"  Max Volume: {volume['max_volume']:,.0f}\n\n"
    
    # Company info
    if company:
        output += f"Company Info:\n"
        for key, value in list(company.items())[:5]:  # Show first 5 items
            output += f"  {key}: {value}\n"
    
    return output


def _format_surge_summary(symbol: str, name: str, result: Dict, threshold: float) -> str:
    """Format surge summary"""
    basic = result['basic']
    surges = result['surges']
    
    output = f"Surge Summary: {name}({symbol})\n"
    output += "-" * 30 + "\n"
    
    output += f"Current Price: ${basic['current_price']:.2f}\n"
    output += f"Total Return: {basic['total_return']:+.2f}%\n"
    output += f"Surge Count: {len(surges)} times (>{threshold}%)\n"
    
    if surges:
        recent_surge = surges[0]
        max_surge = max(s['return'] for s in surges)
        output += f"Max Surge: +{max_surge:.2f}%\n"
        output += f"Recent Surge: {recent_surge['date']} (+{recent_surge['return']:.2f}%)\n"
    
    # Surge frequency rating
    surge_count = len(surges)
    if surge_count >= 10:
        rating = "Very High"
    elif surge_count >= 5:
        rating = "High"
    elif surge_count >= 2:
        rating = "Medium"
    else:
        rating = "Low"
    
    output += f"Surge Frequency: {rating}\n"
    
    return output


def _format_comparison(results: List[Dict]) -> str:
    """Format comparison result"""
    output = "Stock Comparison Analysis\n"
    output += "=" * 40 + "\n\n"
    
    # Table header
    output += f"{'Stock':8s} {'Symbol':8s} {'Return':8s} {'Surges':7s} {'Volatility':10s}\n"
    output += "-" * 50 + "\n"
    
    # Data rows
    for item in results:
        symbol = item['symbol']
        name = item['name']
        basic = item['data']['basic']
        surges = item['data']['surges']
        
        output += f"{name[:6]:8s} {symbol:8s} {basic['total_return']:+6.1f}% {len(surges):5d} {basic['volatility']:8.1f}%\n"
    
    # Analysis conclusion
    best_return = max(results, key=lambda x: x['data']['basic']['total_return'])
    most_surges = max(results, key=lambda x: len(x['data']['surges']))
    
    output += f"\nBest Performance: {best_return['name']} (Return: {best_return['data']['basic']['total_return']:+.1f}%)\n"
    output += f"Most Surges: {most_surges['name']} ({len(most_surges['data']['surges'])} times)\n"
    
    return output


def _format_batch_analysis(results: List[Dict], preset: str) -> str:
    """Format batch analysis result"""
    output = f"Batch Stock Analysis Report ({preset})\n"
    output += "=" * 50 + "\n\n"
    
    # Sort and show top 5
    surge_ranking = sorted(results, key=lambda x: x['surge_count'], reverse=True)
    return_ranking = sorted(results, key=lambda x: x['total_return'], reverse=True)
    
    output += "Top 5 by Surge Frequency:\n"
    for i, stock in enumerate(surge_ranking[:5], 1):
        output += f"  {i}. {stock['name']} ({stock['symbol']}): {stock['surge_count']} times, {stock['total_return']:+.1f}%\n"
    
    output += "\nTop 5 by Return:\n"
    for i, stock in enumerate(return_ranking[:5], 1):
        output += f"  {i}. {stock['name']} ({stock['symbol']}): {stock['total_return']:+.1f}%, {stock['surge_count']} surges\n"
    
    # Statistics
    total_stocks = len(results)
    avg_return = sum(s['total_return'] for s in results) / total_stocks
    total_surges = sum(s['surge_count'] for s in results)
    
    output += f"\nStatistics Summary:\n"
    output += f"  Analyzed Stocks: {total_stocks}\n"
    output += f"  Average Return: {avg_return:+.1f}%\n"
    output += f"  Total Surges: {total_surges}\n"
    output += f"  Average Surges: {total_surges/total_stocks:.1f} per stock\n"
    
    return output


async def main():
    """Main function"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="surge-analysis-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())