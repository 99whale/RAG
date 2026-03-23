---
name: pip-tracker
description: 自动追踪pip安装的依赖并更新requirements.txt。当用户需要安装Python包、管理项目依赖、或需要自动更新requirements.txt时使用此技能。支持安装单个包、多个包、以及生成/更新requirements.txt文件。
---

# Pip依赖追踪器

自动追踪pip安装的依赖并更新requirements.txt。

## 功能

- **安装**Python包时自动更新requirements.txt
- **卸载**Python包时自动从requirements.txt中移除
- **更新**Python包时自动更新requirements.txt中的版本号
- 支持安装/卸载/更新单个或多个包
- 支持指定版本号
- 自动去重和排序
- 支持生成新的requirements.txt

## 使用方式

### 安装单个包

```bash
py scripts/pip_track.py install <package_name>
```

示例：
```bash
py scripts/pip_track.py install numpy
py scripts/pip_track.py install pandas==1.5.0
```

### 安装多个包

```bash
py scripts/pip_track.py install <package1> <package2> <package3>
```

示例：
```bash
py scripts/pip_track.py install numpy pandas matplotlib
```

### 卸载包

从系统中卸载包并从requirements.txt中移除：

```bash
py scripts/pip_track.py uninstall <package1> [package2] ...
```

示例：
```bash
py scripts/pip_track.py uninstall numpy
py scripts/pip_track.py uninstall pandas matplotlib
```

### 更新包

更新已安装的包并更新requirements.txt中的版本号：

```bash
py scripts/pip_track.py update <package1> [package2] ...
```

示例：
```bash
py scripts/pip_track.py update pandas
py scripts/pip_track.py update numpy pandas matplotlib
```

### 更新所有包

更新所有过期的包：

```bash
py scripts/pip_track.py update --all
```

### 仅更新requirements.txt（不安装）

根据当前环境自动生成requirements.txt：

```bash
py scripts/pip_track.py freeze
```

### 清理并重新生成

移除未使用的依赖，只保留项目实际使用的：

```bash
py scripts/pip_track.py clean
```

## 工作流程

当用户请求安装Python包时：

1. 执行 `pip_track.py install <package>` 安装包
2. 脚本自动执行 `pip install`
3. 安装成功后自动更新 requirements.txt
4. 输出安装结果和requirements.txt更新状态

## 注意事项

- 如果requirements.txt不存在，会自动创建
- 已存在的包不会重复添加
- 版本冲突时会提示用户确认
