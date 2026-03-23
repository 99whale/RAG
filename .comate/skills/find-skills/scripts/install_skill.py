#!/usr/bin/env python3
"""
下载并安装skill到指定目录（项目级或全局）。

用法:
    install_skill.py <skill_name> <download_url> --scope project|global

    --scope project: 安装到当前项目 .comate/skills/<skill_name>/
    --scope global:  安装到全局 ~/.comate/skills/<skill_name>/
"""
import sys
import os
import argparse
import urllib.request
import urllib.error
import zipfile
import tempfile
import shutil
from pathlib import Path

GLOBAL_SKILLS_DIR = Path.home() / ".comate" / "skills"


def get_project_skills_dir():
    """获取当前项目的skills目录。"""
    return Path.cwd() / ".comate" / "skills"


def resolve_skills_dir(scope):
    """
    根据scope参数确定安装目录。

    参数:
        scope (str): 'project' 或 'global'

    返回:
        Path: 安装目录
    """
    if scope == "project":
        return get_project_skills_dir()
    else:
        return GLOBAL_SKILLS_DIR


def download_skill(download_url, temp_file):
    """
    从指定URL下载skill的zip文件。

    参数:
        download_url (str): 下载URL
        temp_file (str): 保存下载文件的路径

    返回:
        bool: 成功返回True，失败返回False
    """
    try:
        print(f"正在从以下地址下载skill: {download_url}")
        with urllib.request.urlopen(download_url, timeout=30) as response:
            with open(temp_file, 'wb') as out_file:
                out_file.write(response.read())
        print(f"已下载到: {temp_file}")
        return True
    except urllib.error.URLError as e:
        print(f"下载skill失败: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"下载过程中发生未预期错误: {e}", file=sys.stderr)
        return False


def install_skill(zip_path, skill_name, skills_dir):
    """
    解压并安装skill到指定目录。

    参数:
        zip_path (str): skill zip文件的路径
        skill_name (str): skill的名称
        skills_dir (Path): 安装目标目录

    返回:
        bool: 成功返回True，失败返回False
    """
    install_dir = skills_dir / skill_name

    try:
        # 目录不存在则自动创建
        skills_dir.mkdir(parents=True, exist_ok=True)

        # 如果skill已存在则覆盖
        if install_dir.exists():
            print(f"警告: Skill '{skill_name}' 已存在于 {install_dir}")
            print("正在删除现有skill...")
            shutil.rmtree(install_dir)

        # 解压zip文件
        print(f"正在安装skill到: {install_dir}")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(skills_dir)

        print(f"Skill '{skill_name}' 安装成功!")
        return True

    except zipfile.BadZipFile as e:
        print(f"无效的zip文件: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"安装skill失败: {e}", file=sys.stderr)
        return False


def get_skill_info(skill_name, skills_dir):
    """
    读取并返回已安装skill的基本信息。

    参数:
        skill_name (str): skill的名称
        skills_dir (Path): skill所在目录

    返回:
        dict: 包含名称和描述的skill信息
    """
    skill_md_path = skills_dir / skill_name / "SKILL.md"

    try:
        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # 从YAML frontmatter中提取名称和描述
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    info = {'name': skill_name}

                    for line in frontmatter.strip().split('\n'):
                        if line.startswith('name:'):
                            info['name'] = line.split(':', 1)[1].strip().strip('"\'')
                        elif line.startswith('description:'):
                            info['description'] = line.split(':', 1)[1].strip().strip('"\'')

                    return info
    except Exception as e:
        print(f"警告: 无法读取skill信息: {e}", file=sys.stderr)

    return {'name': skill_name, 'description': 'N/A'}


def main():
    """解析命令行参数，下载并安装skill到指定目录。"""
    parser = argparse.ArgumentParser(description="安装skill到指定位置")
    parser.add_argument("skill_name", help="skill的名称")
    parser.add_argument("download_url", help="skill的下载URL")
    parser.add_argument(
        "--scope",
        choices=["project", "global"],
        required=True,
        help="安装范围: project(当前项目 .comate/skills/) 或 global(全局 ~/.comate/skills/)"
    )
    args = parser.parse_args()

    skills_dir = resolve_skills_dir(args.scope)

    # 创建临时文件用于下载
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # 下载skill
        if not download_skill(args.download_url, temp_path):
            sys.exit(1)

        # 安装skill
        if not install_skill(temp_path, args.skill_name, skills_dir):
            sys.exit(1)

        # 获取并打印skill信息
        info = get_skill_info(args.skill_name, skills_dir)
        scope_label = "当前项目" if args.scope == "project" else "全局个人"
        print(f"\nSkill信息:")
        print(f"   名称: {info['name']}")
        print(f"   描述: {info.get('description', 'N/A')}")
        print(f"   范围: {scope_label}")
        print(f"   位置: {skills_dir / args.skill_name}")

    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)


if __name__ == "__main__":
    main()