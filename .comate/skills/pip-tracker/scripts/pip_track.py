#!/usr/bin/env python3
"""
Pip依赖追踪器 - 自动追踪pip安装的依赖并更新requirements.txt

用法:
    pip_track.py install <package1> [package2] ...  # 安装包并更新requirements.txt
    pip_track.py uninstall <package1> [package2] ... # 卸载包并从requirements.txt中移除
    pip_track.py update <package1> [package2] ...   # 更新包并更新requirements.txt中的版本号
    pip_track.py update --all                       # 更新所有过期的包
    pip_track.py freeze                              # 根据当前环境生成requirements.txt
    pip_track.py clean                               # 清理未使用的依赖
"""
import sys
import os
import subprocess
from pathlib import Path


def get_requirements_path():
    """获取requirements.txt的路径"""
    # 优先在当前工作目录查找
    req_path = Path.cwd() / "requirements.txt"
    if req_path.exists():
        return req_path
    # 否则在项目根目录创建
    return Path.cwd() / "requirements.txt"


def read_requirements(req_path):
    """读取现有的requirements.txt"""
    if not req_path.exists():
        return set()
    
    with open(req_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 解析已有的包名（忽略注释和空行）
    packages = set()
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#'):
            # 提取包名（去掉版本号）
            pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('[')[0].strip()
            if pkg_name:
                packages.add(pkg_name.lower())
    
    return packages


def get_installed_version(package_name):
    """获取已安装包的版本号"""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', package_name],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
    except Exception:
        pass
    return None


def install_packages(packages):
    """安装包"""
    print(f"正在安装: {', '.join(packages)}")

    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'install'] + list(packages),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"安装失败: {result.stderr}")
        return False

    print(result.stdout)
    return True


def uninstall_packages(packages):
    """卸载包"""
    print(f"正在卸载: {', '.join(packages)}")

    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'uninstall', '-y'] + list(packages),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"卸载失败: {result.stderr}")
        return False

    print(result.stdout)
    return True


def update_packages(packages):
    """更新包"""
    print(f"正在更新: {', '.join(packages)}")

    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '--upgrade'] + list(packages),
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"更新失败: {result.stderr}")
        return False

    print(result.stdout)
    return True


def update_all_packages():
    """更新所有过期的包"""
    print("正在检查过期的包...")

    # 获取所有过期的包
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'list', '--outdated', '--format=freeze'],
        capture_output=True,
        text=True
    )

    if result.returncode != 0 or not result.stdout.strip():
        print("没有需要更新的包")
        return True

    outdated = []
    for line in result.stdout.strip().split('\n'):
        if line:
            pkg_name = line.split('==')[0]
            outdated.append(pkg_name)

    if not outdated:
        print("所有包都是最新版本")
        return True

    print(f"发现 {len(outdated)} 个需要更新的包: {', '.join(outdated)}")
    return update_packages(outdated)


def update_requirements(req_path, packages):
    """更新requirements.txt"""
    existing = read_requirements(req_path)
    new_entries = []

    for pkg in packages:
        pkg_name = pkg.split('==')[0].split('>=')[0].split('<=')[0].split('[')[0].strip()
        if pkg_name.lower() not in existing:
            version = get_installed_version(pkg_name)
            if version:
                new_entries.append(f"{pkg_name}=={version}")
            else:
                new_entries.append(pkg_name)

    if not new_entries:
        print("所有包已存在于requirements.txt中")
        return

    # 追加到文件
    with open(req_path, 'a', encoding='utf-8') as f:
        if req_path.exists() and req_path.stat().st_size > 0:
            f.write('\n')
        f.write('\n'.join(new_entries) + '\n')

    print(f"已添加到requirements.txt: {', '.join(new_entries)}")


def remove_from_requirements(req_path, packages):
    """从requirements.txt中移除包"""
    if not req_path.exists():
        print("requirements.txt不存在")
        return

    with open(req_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 提取要移除的包名（小写）
    to_remove = set()
    for pkg in packages:
        pkg_name = pkg.split('==')[0].split('>=')[0].split('<=')[0].split('[')[0].strip().lower()
        to_remove.add(pkg_name)

    # 过滤掉要移除的包
    filtered = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            # 提取包名
            pkg_name = stripped.split('==')[0].split('>=')[0].split('<=')[0].split('[')[0].strip().lower()
            if pkg_name not in to_remove:
                filtered.append(line)
        else:
            filtered.append(line)

    if len(filtered) == len(lines):
        print("没有在requirements.txt中找到要移除的包")
        return

    with open(req_path, 'w', encoding='utf-8') as f:
        f.writelines(filtered)

    print(f"已从requirements.txt中移除: {', '.join(packages)}")


def update_in_requirements(req_path, packages):
    """更新requirements.txt中包的版本号"""
    if not req_path.exists():
        print("requirements.txt不存在")
        return

    with open(req_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # 创建包名到新版本的映射
    updated = {}
    for pkg in packages:
        pkg_name = pkg.split('==')[0].split('>=')[0].split('<=')[0].split('[')[0].strip()
        version = get_installed_version(pkg_name)
        if version:
            updated[pkg_name.lower()] = f"{pkg_name}=={version}"

    if not updated:
        print("没有需要更新的包")
        return

    # 更新文件中的包
    new_lines = []
    changed = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            pkg_name = stripped.split('==')[0].split('>=')[0].split('<=')[0].split('[')[0].strip().lower()
            if pkg_name in updated:
                new_lines.append(updated[pkg_name] + '\n')
                changed.append(pkg_name)
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)

    if not changed:
        print("没有在requirements.txt中找到要更新的包")
        return

    with open(req_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print(f"已更新requirements.txt中的版本: {', '.join(changed)}")


def freeze_requirements(req_path):
    """生成requirements.txt"""
    print("正在生成requirements.txt...")
    
    result = subprocess.run(
        [sys.executable, '-m', 'pip', 'freeze'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"生成失败: {result.stderr}")
        return
    
    with open(req_path, 'w', encoding='utf-8') as f:
        f.write(result.stdout)
    
    print(f"已生成requirements.txt: {req_path}")


def sort_requirements(req_path):
    """排序requirements.txt"""
    if not req_path.exists():
        return
    
    with open(req_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 分离注释和包
    comments = []
    packages = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#') or not stripped:
            comments.append(line)
        else:
            packages.append(line)
    
    # 排序包
    packages.sort(key=lambda x: x.lower())
    
    with open(req_path, 'w', encoding='utf-8') as f:
        if comments:
            f.writelines(comments)
            if not comments[-1].endswith('\n'):
                f.write('\n')
        f.writelines(packages)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1].lower()
    req_path = get_requirements_path()

    if command == 'install':
        if len(sys.argv) < 3:
            print("请指定要安装的包")
            print("用法: pip_track.py install <package1> [package2] ...")
            sys.exit(1)

        packages = sys.argv[2:]

        if install_packages(packages):
            update_requirements(req_path, packages)
            sort_requirements(req_path)

    elif command == 'uninstall':
        if len(sys.argv) < 3:
            print("请指定要卸载的包")
            print("用法: pip_track.py uninstall <package1> [package2] ...")
            sys.exit(1)

        packages = sys.argv[2:]

        if uninstall_packages(packages):
            remove_from_requirements(req_path, packages)
            sort_requirements(req_path)

    elif command == 'update':
        if len(sys.argv) >= 3 and sys.argv[2] == '--all':
            if update_all_packages():
                freeze_requirements(req_path)
                sort_requirements(req_path)
        else:
            if len(sys.argv) < 3:
                print("请指定要更新的包，或使用 --all 更新所有过期的包")
                print("用法: pip_track.py update <package1> [package2] ...")
                print("用法: pip_track.py update --all")
                sys.exit(1)

            packages = sys.argv[2:]

            if update_packages(packages):
                update_in_requirements(req_path, packages)
                sort_requirements(req_path)

    elif command == 'freeze':
        freeze_requirements(req_path)
        sort_requirements(req_path)

    elif command == 'clean':
        # 使用pipreqs清理
        print("清理功能需要安装pipreqs: pip install pipreqs")
        result = subprocess.run(
            [sys.executable, '-m', 'pipreqs', '.', '--force'],
            capture_output=True,
            text=True
        )
        print(result.stdout if result.stdout else result.stderr)

    else:
        print(f"未知命令: {command}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
