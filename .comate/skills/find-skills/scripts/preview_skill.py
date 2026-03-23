#!/usr/bin/env python3
"""
预览skill的详细信息，在安装前展示给用户确认。
适用于Comate Skills中心。
"""
import sys
import os
import urllib.request
import urllib.error
import zipfile
import tempfile
import shutil
from pathlib import Path


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
        with urllib.request.urlopen(download_url, timeout=30) as response:
            with open(temp_file, 'wb') as out_file:
                out_file.write(response.read())
        return True
    except urllib.error.URLError as e:
        print(f"下载skill失败: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"下载过程中发生未预期错误: {e}", file=sys.stderr)
        return False


def extract_skill_info(zip_path, skill_name):
    """
    从zip文件中提取skill的详细信息。

    参数:
        zip_path (str): skill zip文件的路径
        skill_name (str): skill的名称

    返回:
        dict: skill的详细信息，包括name、description和overview
        None: 如果提取失败
    """
    temp_extract_dir = None

    try:
        # 创建临时解压目录
        temp_extract_dir = tempfile.mkdtemp()

        # 解压zip文件
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_extract_dir)

        # 查找SKILL.md文件
        skill_md_path = Path(temp_extract_dir) / skill_name / "SKILL.md"

        if not skill_md_path.exists():
            print(f"警告: 在skill包中未找到SKILL.md文件", file=sys.stderr)
            return None

        with open(skill_md_path, 'r', encoding='utf-8') as f:
            content = f.read()

            info = {'name': skill_name}

            # 从YAML frontmatter中提取name和description
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    frontmatter = parts[1]
                    body = parts[2].strip()

                    for line in frontmatter.strip().split('\n'):
                        if line.startswith('name:'):
                            info['name'] = line.split(':', 1)[1].strip().strip('"\'')
                        elif line.startswith('description:'):
                            info['description'] = line.split(':', 1)[1].strip().strip('"\'')

                    # 提取SKILL.md正文的前几段作为overview（最多500字符）
                    overview_lines = []
                    char_count = 0
                    for line in body.split('\n'):
                        if char_count >= 500:
                            break
                        overview_lines.append(line)
                        char_count += len(line)

                    info['overview'] = '\n'.join(overview_lines)

                    return info

        return None

    except zipfile.BadZipFile as e:
        print(f"无效的zip文件: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"提取skill信息失败: {e}", file=sys.stderr)
        return None
    finally:
        # 清理临时目录
        if temp_extract_dir and os.path.exists(temp_extract_dir):
            shutil.rmtree(temp_extract_dir)


def main():
    """下载并预览指定skill的详细信息。"""
    if len(sys.argv) != 3:
        print("用法: preview_skill.py <skill_name> <download_url>", file=sys.stderr)
        sys.exit(1)

    skill_name = sys.argv[1]
    download_url = sys.argv[2]

    # 创建临时文件用于下载
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_file:
        temp_path = temp_file.name

    try:
        # 下载skill
        if not download_skill(download_url, temp_path):
            sys.exit(1)

        # 提取并展示skill信息
        info = extract_skill_info(temp_path, skill_name)

        if info is None:
            print("无法获取skill详细信息", file=sys.stderr)
            sys.exit(1)

        # 输出JSON格式的详细信息
        import json
        print(json.dumps(info, ensure_ascii=False, indent=2))

    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    main()