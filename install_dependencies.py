#!/usr/bin/env python3
"""智能依赖安装脚本

检测已安装的依赖，只安装未安装的包，避免重复安装
保持requirements.txt中的安装顺序
"""

import subprocess
import sys
import re


def read_requirements(file_path):
    """读取requirements.txt文件，返回依赖列表
    
    Args:
        file_path: requirements.txt文件路径
    
    Returns:
        list: 依赖包列表
    """
    packages = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith('#'):
                continue
            # 移除版本号和其他附加信息，只保留包名
            # 处理各种格式：package, package==version, package>=version等
            package_name = re.split('[=<>~]', line)[0].strip()
            packages.append(package_name)
    return packages


def check_installed_packages():
    """检查已安装的包
    
    Returns:
        set: 已安装的包名集合
    """
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--format=freeze'],
            capture_output=True,
            text=True,
            check=True
        )
        installed = set()
        for line in result.stdout.strip().split('\n'):
            if line:
                package_name = line.split('==')[0].strip()
                installed.add(package_name)
        return installed
    except subprocess.CalledProcessError as e:
        print(f"检查已安装包时出错: {e}")
        return set()


def install_packages(packages, requirements_file):
    """安装包
    
    Args:
        packages: 要安装的包列表
        requirements_file: requirements.txt文件路径
    """
    if not packages:
        print("所有依赖已安装，无需操作")
        return
    
    print(f"需要安装 {len(packages)} 个依赖包...")
    
    # 从requirements.txt中获取完整的包规格（包括版本号）
    full_specs = {}
    with open(requirements_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            package_name = re.split('[=<>~]', line)[0].strip()
            full_specs[package_name] = line
    
    # 安装包
    for package in packages:
        spec = full_specs.get(package, package)
        print(f"安装: {spec}")
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', spec],
                check=True
            )
            print(f"✓ 安装成功: {spec}")
        except subprocess.CalledProcessError as e:
            print(f"✗ 安装失败: {spec}")
            print(f"  错误信息: {e}")


def main():
    """主函数"""
    requirements_file = 'requirements.txt'
    
    # 读取依赖列表
    required_packages = read_requirements(requirements_file)
    print(f"从 {requirements_file} 中读取到 {len(required_packages)} 个依赖包")
    
    # 检查已安装的包
    installed_packages = check_installed_packages()
    print(f"已安装 {len(installed_packages)} 个包")
    
    # 确定需要安装的包
    packages_to_install = [pkg for pkg in required_packages if pkg not in installed_packages]
    print(f"需要安装 {len(packages_to_install)} 个包")
    
    if packages_to_install:
        print("\n需要安装的包:")
        for pkg in packages_to_install:
            print(f"  - {pkg}")
        print()
        
        # 安装包
        install_packages(packages_to_install, requirements_file)
    else:
        print("所有依赖包已安装，无需操作！")


if __name__ == "__main__":
    main()
