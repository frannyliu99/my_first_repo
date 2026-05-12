# 俄罗斯方块 (Tetris)

一个使用 Python + pygame 编写的经典俄罗斯方块小游戏。

## 功能特性

- 7 种经典方块 (I / O / T / S / Z / J / L)
- 左右移动、顺时针 / 逆时针旋转
- 软降 (↓) 与硬降 (空格)
- 落点提示影子方块 (ghost piece)
- 消行计分、等级提升、速度递增
- 暂停 / 继续、游戏结束后一键重开
- 右侧信息面板显示分数、等级、消行数、下一个方块

## 环境要求

- Python 3.10+
- 依赖见 `requirements.txt`（主要是 `pygame`）

## 运行方法

### 1. 进入项目目录

```bash
cd new_demo
```

### 2. 激活虚拟环境

macOS / Linux：

```bash
source venv/bin/activate
```

Windows (PowerShell)：

```powershell
venv\Scripts\Activate.ps1
```

### 3. （首次使用时）安装依赖

```bash
pip install -r requirements.txt
```

### 4. 启动游戏

```bash
python tetris.py
```

退出虚拟环境：

```bash
deactivate
```

## 操作说明

| 按键 | 功能 |
| --- | --- |
| ← / → | 左右移动 |
| ↓ | 加速下落（软降，每格 +1 分） |
| 空格 | 直接落底（硬降，每格 +2 分） |
| ↑ 或 X | 顺时针旋转 |
| Z | 逆时针旋转 |
| P | 暂停 / 继续 |
| R | 游戏结束后重新开始 |
| ESC | 退出游戏 |

## 计分规则

- 一次消除 1 行：100 × 等级
- 一次消除 2 行：300 × 等级
- 一次消除 3 行：500 × 等级
- 一次消除 4 行 (Tetris)：800 × 等级
- 每累计消除 10 行升 1 级，下落速度递增

## 项目结构

```
new_demo/
├── tetris.py          # 游戏主程序
├── requirements.txt   # Python 依赖列表
├── README.md          # 项目说明（本文件）
└── venv/              # 虚拟环境（已通过 python3 -m venv venv 创建）
```
