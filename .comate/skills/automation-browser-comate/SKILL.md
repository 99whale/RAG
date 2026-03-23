---
name: comate-automation-browser
description: |
    浏览器自动化，用于网页浏览、UI 测试、截图验证和网页内容抓取。
    在以下场景使用此 skill：
    - 需要浏览网站、导航网页或与网页 UI 交互
    - 需要截图进行视觉验证
    - 需要测试 Web 应用的 UI 行为
    - 需要抓取或提取网页内容
    - 需要点击按钮或在网页中输入文本
hidden: true
---

# Comate Automation Browser

通过 `run_command` 工具加 `comate-automation-browser` 前缀来调用浏览器自动化能力。

## 调用方式

```json
{ "command": "comate-automation-browser <子命令> [参数]" }
```

**重要**：必须通过 `run_command` 加 `comate-automation-browser` 前缀调用。不要将 `browser_use` 作为独立工具直接调用，也不要将 `comate-automation-browser` 作为 shell 命令执行。

## 可用命令

### 导航

| 命令 | 参数 | 说明 |
|------|------|------|
| `navigate <url>` | `url`（必填） | 导航到指定 URL |
| `back` | — | 浏览器后退 |
| `forward` | — | 浏览器前进 |
| `reload` | — | 重新加载当前页面 |

### 页面检查

| 命令 | 参数 | 说明 |
|------|------|------|
| `snapshot` | — | 获取无障碍快照（包含元素 UID 的 YAML 树） |
| `html [selector]` | `selector`（可选，CSS 选择器） | 获取页面 HTML，可通过选择器过滤 |
| `screenshot` | 见下方选项 | 对当前页面截图 |
| `status` | — | 显示浏览器状态和所有打开的标签页 |
| `console` | — | 获取浏览器控制台消息 |

**`screenshot` 选项**（均为可选）：
- 位置参数：`filePath` — 截图保存路径
- `--format <png|jpeg|webp>` — 图片格式
- `--full-page` — 截取整个可滚动页面
- `--uid <uid>` — 截取指定 UID 的元素

### 交互

| 命令 | 参数 | 说明 |
|------|------|------|
| `click <uid>` | `uid`（必填，来自 snapshot） | 通过 UID 点击元素 |
| `type <text>` | 见下方选项 | 在页面或聚焦元素中输入文本 |
| `scroll <direction>` | `up` 或 `down`（默认 `down`） | 滚动页面 |

**`type` 选项**：
- `<text>`（必填）— 要输入的文本，多词文本用 `"` 包裹
- `--uid <uid>` — 输入前先聚焦该元素
- `--submit` — 输入后按回车
- `--slowly` — 逐字符输入

### 标签页管理

| 命令 | 参数 | 说明 |
|------|------|------|
| `new_page [url]` | `url`（可选） | 打开新标签页，可选导航到指定 URL |
| `select_page <index>` | `index`（整数） | 按索引切换标签页 |
| `close_page <index>` | `index`（整数） | 按索引关闭标签页 |

### 高级

| 命令 | 参数 | 说明 |
|------|------|------|
| `evaluate <script>` | `script`（剩余参数拼接为一个字符串） | 在页面上下文中执行 JavaScript |

## 执行行为

- **自动执行模式**（默认）：命令立即执行，无需用户确认。
- **保护模式**：当设置中启用 `browserProtection` 时，每条命令进入 `pending` 状态，等待用户确认。
- **状态流转**：`pending` -> `running` -> `success` / `failed` / `aborted` / `rejected`

## 标准工作流

```
1. run_command: "comate-automation-browser navigate https://example.com"
2. run_command: "comate-automation-browser snapshot"
   -> 读取 YAML 输出获取元素 UID
3. run_command: "comate-automation-browser click 15"
   -> 点击 UID 为 15 的元素
4. run_command: "comate-automation-browser snapshot"
   -> 获取更新后的页面状态和新的 UID
5. run_command: "comate-automation-browser screenshot"
   -> 视觉验证
```

## 关键规则

- **UID 来自 `snapshot`**：在使用 `click` 或 `type --uid` 前，必须先执行 `snapshot` 获取当前元素的 UID。
- **交互后重新 snapshot**：点击和导航后 UID 会变化，必须重新获取。
- **`snapshot` 为主要视图**：使用 `snapshot` 了解页面结构，`screenshot` 仅用于视觉验证。
- **会话自动管理**：浏览器会话按对话自动管理，无需手动管理。
- **不暴露缓存路径**：在回复中不得描述截图、文件等的缓存地址或本地临时路径（如 `/tmp/...`、`~/.cache/...` 等），仅描述操作结果或展示图片内容。
- **需要用户手动操作时暂停**：当遇到需要用户手动操作的场景时（如：
  - 图形验证码、滑块验证、人机验证（CAPTCHA）
  - 短信/邮箱验证码
  - 扫码登录
  - 用户专属的敏感凭证（如密码、OTP、安全令牌）
  - 需要用户主观判断或选择的复杂交互
  ），暂停自动化执行，等待用户 10 秒并提示用户需要进行操作。用户完成操作后，继续执行后续自动化流程。
  **注意**：普通表单填写、文本输入、按钮点击等可自动化的操作由 agent 自行处理，不在此列。
