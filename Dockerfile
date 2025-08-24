# 股票暴涨分析 MCP 服务 Docker 镜像
# Stock Surge Analysis MCP Service Docker Image

FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONIOENCODING=utf-8
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非 root 用户
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# 暴露端口（如果需要）
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import akshare; print('OK')" || exit 1

# 默认命令
CMD ["python", "surge_analysis_mcp_server.py"]

# 标签信息
LABEL maintainer="Stock Analysis Team <contact@example.com>"
LABEL version="1.1.0"
LABEL description="专业的股票暴涨分析 MCP 服务"
LABEL org.opencontainers.image.source="https://github.com/your-username/surge-analysis-mcp"
LABEL org.opencontainers.image.documentation="https://github.com/your-username/surge-analysis-mcp/blob/main/README.md"
LABEL org.opencontainers.image.licenses="MIT"