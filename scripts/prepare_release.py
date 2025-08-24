#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
发布准备脚本
Release preparation script
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


def get_project_root():
    """获取项目根目录"""
    return Path(__file__).parent.parent


def update_version_info(version, changes):
    """更新版本信息"""
    project_root = get_project_root()
    version_file = project_root / "VERSION_INFO.json"
    
    version_info = {
        "version": version,
        "release_date": datetime.now().strftime("%Y-%m-%d"),
        "changes": changes,
        "compatibility": {
            "windows": True,
            "macos": True,
            "linux": True,
            "python_versions": [
                "3.8+", "3.9+", "3.10+", "3.11+", "3.12+"
            ]
        }
    }
    
    with open(version_file, 'w', encoding='utf-8') as f:
        json.dump(version_info, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Updated version info to {version}")


def run_tests():
    """运行测试"""
    project_root = get_project_root()
    os.chdir(project_root)
    
    print("Running tests...")
    try:
        # 运行基本测试
        result = subprocess.run([
            sys.executable, "-m", "pytest", "tests/", "-v"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✓ All tests passed")
            return True
        else:
            print(f"✗ Tests failed:\n{result.stdout}\n{result.stderr}")
            return False
            
    except FileNotFoundError:
        print("⚠ pytest not found, skipping tests")
        return True


def check_dependencies():
    """检查依赖包"""
    project_root = get_project_root()
    requirements_file = project_root / "requirements.txt"
    
    if not requirements_file.exists():
        print("✗ requirements.txt not found")
        return False
    
    print("✓ requirements.txt exists")
    
    # 检查核心依赖
    with open(requirements_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    required_packages = ['mcp', 'akshare', 'pandas', 'numpy']
    missing_packages = []
    
    for package in required_packages:
        if package not in content:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"⚠ Missing packages in requirements.txt: {missing_packages}")
    else:
        print("✓ All core dependencies present")
    
    return True


def validate_mcp_config():
    """验证 MCP 配置"""
    project_root = get_project_root()
    mcp_file = project_root / "mcp.json"
    
    if not mcp_file.exists():
        print("✗ mcp.json not found")
        return False
    
    try:
        with open(mcp_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 检查配置结构
        if "mcpServers" not in config:
            print("✗ Invalid MCP configuration structure")
            return False
        
        print("✓ MCP configuration is valid")
        return True
        
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in mcp.json: {e}")
        return False


def create_release_archive():
    """创建发布归档"""
    project_root = get_project_root()
    
    # 创建 release 目录
    release_dir = project_root / "release"
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()
    
    # 要包含的文件和目录
    include_items = [
        "*.py",
        "requirements.txt",
        "README.md",
        "LICENSE",
        "mcp.json",
        "pyproject.toml",
        "scripts/",
        "tests/"
    ]
    
    # 复制文件
    for item in include_items:
        if item.endswith('/'):
            # 目录
            src_dir = project_root / item.rstrip('/')
            if src_dir.exists():
                dst_dir = release_dir / item.rstrip('/')
                shutil.copytree(src_dir, dst_dir)
                print(f"✓ Copied directory: {item}")
        else:
            # 文件或通配符
            if '*' in item:
                import glob
                for file_path in glob.glob(str(project_root / item)):
                    file_name = os.path.basename(file_path)
                    shutil.copy2(file_path, release_dir / file_name)
                    print(f"✓ Copied file: {file_name}")
            else:
                src_file = project_root / item
                if src_file.exists():
                    shutil.copy2(src_file, release_dir / item)
                    print(f"✓ Copied file: {item}")
    
    # 创建 ZIP 归档
    archive_name = f"surge-analysis-mcp-v{get_current_version()}"
    shutil.make_archive(
        str(project_root / archive_name),
        'zip',
        str(release_dir)
    )
    
    print(f"✓ Created release archive: {archive_name}.zip")
    return f"{archive_name}.zip"


def get_current_version():
    """获取当前版本"""
    project_root = get_project_root()
    version_file = project_root / "VERSION_INFO.json"
    
    if version_file.exists():
        with open(version_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("version", "1.0.0")
    
    return "1.0.0"


def prepare_release(version, changes):
    """完整的发布准备流程"""
    print(f"🚀 Preparing release v{version}")
    print("=" * 50)
    
    # 更新版本信息
    update_version_info(version, changes)
    
    # 运行测试
    if not run_tests():
        return False
    
    # 检查依赖
    if not check_dependencies():
        return False
    
    # 验证配置
    if not validate_mcp_config():
        return False
    
    # 创建归档
    archive_name = create_release_archive()
    
    print("=" * 50)
    print(f"✅ Release preparation completed!")
    print(f"📦 Archive: {archive_name}")
    print("📝 Next steps:")
    print("   1. Upload the archive to GitHub releases")
    print("   2. Update documentation")
    print("   3. Announce the release")
    
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python prepare_release.py <version> <changes>")
        print("Example: python prepare_release.py 1.1.0 'Added new analysis features'")
        sys.exit(1)
    
    version = sys.argv[1]
    changes = sys.argv[2]
    
    success = prepare_release(version, changes)
    if not success:
        sys.exit(1)