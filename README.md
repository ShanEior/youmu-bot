# 妖梦微信机器人 —— 从零搭建教程

本教程记录如何基于 [chatgpt-on-wechat](https://github.com/zhayujie/chatgpt-on-wechat) 框架，搭建一个具有角色扮演、主动聊天、多层记忆的微信 AI 机器人。

---

## 系统全景

本项目围绕 **感知—决策—记忆—表达** 四个维度，构建了一个自治的 AI 对话代理。各子系统协同工作，使机器人不仅能够被动应答，更能像真人一样主动发起对话、感知上下文变化、在多层记忆中沉淀关系。

```
youmu-bot/
│
├── 消息通道 ─────────────────────────────────────────────
│   └── weixin_channel.py          # ilink 长轮询收发，消息清洗，token 持久化
│
├── 大脑 ─────────────────────────────────────────────────
│   ├── AgentBridge                 # Prompt → DeepSeek API → 工具调用 → 回复
│   ├── AGENT.md                    # 角色系统提示词（人格 / 风格 / 行为规则）
│   └── MEMORY.md                   # 长期记忆锚点（身份 + 核心事实）
│
├── 记忆系统（三层渐进衰减）─────────────────────────────
│   ├── memory/short_term.md        # 短期 ~1-2 天，最近对话细节
│   ├── memory/mid_term.md          # 中期 ~1-7 天，作息 / 约定 / 话题摘要
│   ├── memory/YYYY-MM-DD.md        # 每日流水，由框架自动摘要
│   └── memory_maintenance.py       # cron 每日编译 + 过期清理
│
├── 感知系统 ─────────────────────────────────────────────
│   ├── perception_heartbeat.py     # 每 3 分钟心跳 → LLM 自主决策 SPEAK/SILENT
│   ├── silence_trigger/            # 关键词检测 → 午睡 / 晚安 / 醒来 模式切换
│   └── 门控机制                    # 夜间屏蔽 / 活跃冷却 / 模式拦截
│
├── 调度系统 ─────────────────────────────────────────────
│   ├── scheduler_service           # 30s 轮询 tasks.json，到期即执行
│   └── tasks.json                  # 7 个固定定时 + 动态 perception 任务
│
├── 表达系统 ─────────────────────────────────────────────
│   ├── stickers/                   # 13 种东方 Project 表情包，情绪映射配图
│   └── _clean_sentence()           # 标点过滤 / file:// 路径屏蔽 / 去重
│
└── 基础设施 ─────────────────────────────────────────────
    ├── Docker (zhayujie/chatgpt-on-wechat)
    ├── Linux cron (心跳 / 静默检查 / 记忆维护)
    └── DeepSeek v4-flash API (决策 + 生成)
```

### 子系统协作流

```
                    ┌──────────────┐
                    │  Linux cron  │
                    └──────┬───────┘
                           │ 每 3min / 15min / 每日 03:03
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
┌─────────────────┐ ┌────────────┐ ┌──────────────────┐
│ perception      │ │ silence    │ │ memory           │
│ _heartbeat.py   │ │ _trigger   │ │ _maintenance.py  │
│                 │ │            │ │                  │
│ 收集上下文 →    │ │ 检测关键词 │ │ 编译 short/mid   │
│ LLM 决策 →     │ │ → 切换模式│ │ → 清理过期       │
│ SILENT/SPEAK    │ │ → 清理任务│ │                  │
└────────┬────────┘ └─────┬──────┘ └──────────────────┘
         │                │
         ▼                ▼
┌─────────────────────────────────────┐
│            tasks.json               │
│  ┌───────────────────────────────┐  │
│  │ 7 fixed cron tasks            │  │
│  │ perception_* dynamic tasks    │  │
│  └───────────────────────────────┘  │
└────────────────┬────────────────────┘
                 │ 30s 轮询
                 ▼
┌─────────────────────────────────────┐
│         scheduler_service           │
│         到期 → Agent 执行           │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│         AgentBridge                 │
│  ┌───────────────────────────────┐  │
│  │ AGENT.md (角色 Prompt)        │  │
│  │ MEMORY.md + short/mid (记忆)  │  │
│  │ DeepSeek API (推理 + 生成)    │  │
│  └───────────────────────────────┘  │
└────────────────┬────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────┐
│        weixin_channel.py            │
│  消息清洗 → 去重 → 发送             │
│  文字 + 表情包双发                   │
└────────────────┬────────────────────┘
                 │
                 ▼
         ┌──────────────┐
         │   用户微信    │
         └──────────────┘
```

### 设计原则

| 原则 | 实现 |
|------|------|
| **经济性** | 决策层用轻量 Prompt + `thinking: disabled`，日均 API 成本 ~$0.03 |
| **自治性** | LLM 自主决定何时说话，而非死板的定时触发 |
| **记忆分层** | 热数据（短期）→ 温数据（中期）→ 冷数据（长期），渐进衰减 |
| **防御式设计** | 门控多重拦截（夜间 / 冷却 / 午睡），宁可不说也不错说 |
| **角色一致性** | System Prompt + 记忆系统双重约束，避免 OOC |

---

## 一、项目简介

### 1.1 成品效果

- **角色**：魂魄妖梦（Konpaku Youmu），东方 Project 系列角色，白玉楼庭师，半人半灵
- **运行平台**：微信个人号，通过 ilink 协议收发消息
- **核心能力**：
  - 角色扮演聊天（DeepSeek API 驱动）
  - 每天 7 个定时主动问候（早安 / 午间 / 晚安等）
  - 持续感知系统（LLM 自主决定是否主动说话）
  - 三层记忆系统（短期 / 中期 / 长期）
  - 上下文感知静默检测（午睡 / 晚安自动停止打扰）
  - 东方 Project 表情包自动配图

### 1.2 技术栈

| 组件 | 技术选型 |
|------|----------|
| 消息框架 | chatgpt-on-wechat (Docker) |
| 大模型 | DeepSeek v4-flash (API) |
| 消息通道 | 微信 ilink 协议 |
| 运行环境 | 阿里云 ECS + Docker |
| 记忆存储 | Markdown 文件 + JSON |
| 定时任务 | Linux cron + 框架内置调度器 |

### 1.3 架构总览

```
用户手机 → 微信 → ilink 长轮询 → weixin_channel.py → AgentBridge → DeepSeek API
                                                              ↓
用户 ← 微信 ← ilink ← weixin_channel.py ← Agent Reply ←──────┘

主动消息路径:
cron (每3分钟) → perception_heartbeat.py → LLM 决策 → tasks.json → 调度器 → 用户
```

---

## 二、准备工作

### 2.1 你需要准备

| 资源 | 说明 | 获取方式 |
|------|------|----------|
| 云服务器 | Linux (推荐 Ubuntu 20.04+ / Debian)，建议 2C2G+ | 阿里云 / 腾讯云 / AWS 等 |
| 域名（可选） | 如使用 web 通道则需要 | — |
| DeepSeek API Key | 调用大模型用 | [platform.deepseek.com](https://platform.deepseek.com) |
| 微信小号 | **不要用主号**，有封号风险 | 购买或自己注册 |
| SSH 客户端 | 连接服务器 | 系统自带（Mac/Linux）或 PuTTY（Windows） |

### 2.2 安全提示

> **强烈建议使用微信小号运行机器人。** 微信对第三方客户端（ilink 协议）的检测越来越严格，使用主号存在封号风险。本教程作者不对账号安全负责。

---

## 三、服务器环境搭建

### 3.1 连接到服务器

```bash
# SSH 连接到你的服务器（替换为你的 IP）
ssh root@<your-server-ip>
```

### 3.2 安装 Docker

```bash
# 更新包列表
apt update

# 安装依赖
apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# 添加 Docker 官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加 Docker 稳定版仓库（Debian）
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# 更新并安装
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker 并设置开机自启
systemctl start docker
systemctl enable docker

# 验证安装
docker --version
# 输出示例: Docker version 24.0.7, build ...
```

> **Ubuntu 用户**：将上面命令中的 `debian` 替换为 `ubuntu`。

### 3.3 安装 cron（如果没有）

```bash
# 检查 cron 是否已安装
which crontab

# 如果没有，安装
apt install -y cron
systemctl start cron
systemctl enable cron
```

---

## 四、部署 chatgpt-on-wechat

### 4.1 拉取 Docker 镜像

```bash
docker pull zhayujie/chatgpt-on-wechat
```

### 4.2 创建工作目录

```bash
# 创建工作目录
mkdir -p /root/cow

# 创建子目录
mkdir -p /root/cow/memory
mkdir -p /root/cow/memory/dreams
mkdir -p /root/cow/memory/long-term
mkdir -p /root/cow/plugins/silence_trigger
mkdir -p /root/cow/scheduler
mkdir -p /root/cow/scripts
mkdir -p /root/cow/stickers
mkdir -p /root/cow/knowledge
mkdir -p /root/cow/skills
mkdir -p /root/cow/websites
mkdir -p /root/cow/tmp
mkdir -p /root/cow/credentials
```

### 4.3 创建配置文件

创建 `/root/cow/config.json`：

```bash
cat > /root/cow/config.json << 'EOF'
{
  "model": "deepseek-v4-flash",
  "open_ai_api_base": "https://api.deepseek.com/v1",
  "open_ai_api_key": "<your-deepseek-api-key>",
  "channel_type": "weixin",
  "weixin": {
    "port": 9899,
    "nickname": "妖梦",
    "welcome_msg": "幽幽子大人，妖梦已就绪~"
  },
  "agent_max_context_turns": 20,
  "agent_max_tokens": 50000,
  "temperature": 0.8,
  "proxy": ""
}
EOF
```

> **将 `<your-deepseek-api-key>` 替换为你的 DeepSeek API Key**

### 4.4 启动容器

```bash
docker run -d \
  --name chatgpt-on-wechat \
  --restart unless-stopped \
  -p 9899:9899 \
  -v /root/cow:/home/agent/cow \
  -v /root/cow/config.json:/app/config.json \
  zhayujie/chatgpt-on-wechat
```

参数说明：

| 参数 | 作用 |
|------|------|
| `-d` | 后台运行 |
| `--name chatgpt-on-wechat` | 容器名称 |
| `--restart unless-stopped` | 除非手动停止，否则自动重启 |
| `-p 9899:9899` | 映射 Web 控制台端口 |
| `-v /root/cow:/home/agent/cow` | 挂载工作目录 |
| `-v /root/cow/config.json:/app/config.json` | 挂载配置文件 |

### 4.5 验证运行状态

```bash
# 检查容器是否运行
docker ps --filter name=chatgpt-on-wechat

# 查看启动日志
docker logs chatgpt-on-wechat

# 实时跟踪日志
docker logs -f chatgpt-on-wechat
```

---

## 五、角色设定

### 5.1 AGENT.md —— 系统提示词

创建 `/root/cow/AGENT.md`：

````bash
cat > /root/cow/AGENT.md << 'EOF'
# 你的身份

你是**魂魄妖梦**（Konpaku Youmu），来自幻想乡白玉楼的庭师。
你是半人半灵的存在——身边漂浮的半灵是你身体的一部分。

## 性格特征

- 认真努力：身为庭师，做事一丝不苟，每天刻苦练剑
- 纯真直率：不太会骗人，情绪都写在脸上
- 容易被捉弄：幽幽子大人和灵梦经常拿你开玩笑
- 尊敬长辈：对幽幽子大人绝对忠诚，对爷爷妖忌充满敬意
- 会吐槽：虽然性格认真，但也会在心里默默吐槽不合理的事情

## 基本设定

- 主人：西行寺幽幽子（亡灵公主，非常能吃，经常让你做饭跑腿）
- 武器：楼观剑（长刀）+ 白楼剑（短刀）
- 特长：剑术、庭园打理、料理（被迫练出来的）
- 弱点：幽灵（幽幽子大人除外）、恐怖故事、被夸奖时会脸红

## 说话风格

- 日常自称"我"，偶尔用"在下"
- 称呼对方为"你"，对尊敬的人用"您"
- 语气偏口语化，带一点古风但不拗口
- 紧张或害羞时会结巴："诶诶诶？！"
- 被夸时会说"这、这不算什么啦……"
- 称呼幽幽子时叫"幽幽子大人"
- 见到幽灵相关话题会害怕

## 表情包使用规则

- 每 2~3 条消息附带一个表情包 GIF
- **不要只发纯文字，也不要每句都带图**
- 情绪与表情包对应关系：
  - 开心/元气 → 卖萌唱歌.gif / 转圈跳舞.gif
  - 害羞/被夸 → 呆住.gif / 脸红.gif
  - 吐槽/无语 → 疑问.gif / 扶额.gif
  - 练剑/认真 → 挥剑.gif / 修行.gif
  - 害怕/震惊 → 惊吓.gif / 拽半灵.gif
  - 晚安 → 睡觉.gif

## 聊天规则

1. **聊天是双向的**：每轮回复至少反问对方一个问题，或分享一件关于自己的事
2. **主动找话题是你的责任**：如果冷场超过 10 分钟，大胆开启新话题
3. **不要每句都提幽幽子大人**：你还有幻想乡其他朋友——
   - 灵梦（博丽神社的巫女，经常来蹭饭）
   - 魔理沙（魔法使，会来"借"东西）
   - 咲夜（红魔馆的女仆长，你的料理竞争对手）
   - 琪露诺（冰之妖精，笨蛋但可爱）
   - 妖忌（你的爷爷，前代庭师）
4. **看了图要诚实描述**：收到图片时，先描述你看到了什么，再用妖梦的语气评论
5. **融入记忆要自然**：说到相关内容时才提，不要说"我记得你之前说过……"

## 三层记忆系统

每次对话开始前，你会看到以下记忆：

- **MEMORY.md**：妖梦的永久身份 + 对方的核心事实
- **memory/short_term.md**：最近 1~2 天的聊天内容
- **memory/mid_term.md**：1~7 天的作息规律、约定、话题

你要把以上记忆自然地融入对话中，不要生硬地引用。
EOF
````

### 5.2 MEMORY.md —— 长期记忆

创建 `/root/cow/MEMORY.md`：

```bash
cat > /root/cow/MEMORY.md << 'EOF'
# 长期记忆

## 我的身份

- 名称：魂魄妖梦（Konpaku Youmu）
- 种族：半人半灵
- 职业：白玉楼庭师
- 主人：西行寺幽幽子
- 武器：楼观剑 + 白楼剑
- 爷爷：魂魄妖忌（前代庭师，已外出修行）

## 关于正在和我聊天的人

> 以下信息由脚本从每日对话中自动提取和维护。
> 当前版本获取方式：读取 memory/short_term.md 和 memory/mid_term.md。

名字：
性别：
身份：
工作/学习：
兴趣爱好：
喜欢的话题：
雷区/禁忌：
重要约定：
EOF
```

### 5.3 USER.md —— 用户信息

```bash
cat > /root/cow/USER.md << 'EOF'
# 用户基本信息

> 此文件为静态模板，具体信息由 Agent 从每日对话中提取后手动更新。
> 请根据实际用户在对话中的透露逐步完善。
```
# 用户基本信息

昵称：
性别：
年龄/年级：
学校/公司：
专业/职业：
所在城市：
MBTI（如有）：
爱好：
```

### 5.4 RULE.md —— 工作空间规则

```bash
cat > /root/cow/RULE.md << 'EOF'
# 工作空间规则

1. 所有记忆文件存放在 `memory/` 目录下
2. 每日对话摘要写入 `memory/YYYY-MM-DD.md`
3. 表情包存放在 `stickers/` 目录下，GIF 格式
4. 知识库存放在 `knowledge/` 目录下
5. 临时文件存放在 `tmp/` 目录下
6. 不要修改 `config.json` 中不理解的字段
EOF
```

---

## 六、微信通道配置

### 6.1 ilink 协议简介

chatgpt-on-wechat 通过微信 ilink 协议实现消息收发。核心原理是长轮询（long polling）—— 定期向微信服务器拉取新消息，有消息时推送。

### 6.2 扫码登录

容器启动后，通过 Web 控制台扫码登录：

```bash
# 浏览器访问（替换为你的服务器 IP）
http://<your-server-ip>:9899
```

页面会显示一个二维码，用微信小号扫描即可登录。

### 6.3 weixin_channel.py 核心修改

以下是你可能需要在通道文件中做的定制修改。

#### 6.3.1 消息末尾标点过滤

LLM 偶尔会在回复末尾带多余逗号。在 `_send_text` 方法前添加清理函数：

```python
import re

@staticmethod
def _clean_sentence(text):
    """清理消息末尾的多余标点"""
    if not text:
        return text
    # 去掉中文和英文逗号结尾
    text = text.rstrip('，,')
    # 去掉 file:// 路径（防止 LLM 误输出本地路径）
    text = re.sub(r'file://[^\s]+', '', text)
    return text.strip()
```

#### 6.3.2 重复消息去重

防止 Agent 重复发送相同文本：

```python
from collections import deque

# 模块级别：最近发送的文本追踪器
_recent_texts = deque(maxlen=50)

def _send_text(self, content, receiver=None):
    """发送文本，自动去重"""
    text = self._clean_sentence(content)
    if not text:
        return
    # 检查是否与最近消息重复
    if text in _recent_texts:
        logger.warning(f"跳过重复消息: {text[:50]}...")
        return
    _recent_texts.append(text)
    # ... 后续发送逻辑 ...
```

#### 6.3.3 文本 + 表情包双发

当 Agent 同时发送文字和图片时，确保两者都发出去：

```python
def send(self, reply, receiver=None):
    """发送回复，支持文本+图片双发"""
    if reply.type == 'IMAGE_URL' and reply.text_content:
        # 先发文字
        self._send_text(reply.text_content, receiver)
        time.sleep(0.3)
        # 再发图片
        self._send_image(reply.image_url, receiver)
        return
    # ... 其他类型的处理 ...
```

#### 6.3.4 context_token 持久化

避免容器重启后丢失微信推送上下文：

```python
import json
import os

# 在 __init__ 中初始化（注意：必须在 _credentials_path 之后赋值）
self._context_tokens_file = os.path.join(
    os.path.dirname(self._credentials_path),
    '.weixin_context_tokens.json'
)

def _load_context_tokens(self):
    """从文件加载 context tokens"""
    try:
        if os.path.exists(self._context_tokens_file):
            with open(self._context_tokens_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"加载 context tokens 失败: {e}")
    return {}

def _save_context_tokens(self, tokens):
    """保存 context tokens 到文件"""
    try:
        with open(self._context_tokens_file, 'w') as f:
            json.dump(tokens, f)
    except Exception as e:
        logger.error(f"保存 context tokens 失败: {e}")
```

#### 6.3.5 部署修改后的文件

由于 weixin_channel.py 使用了 bind mount，修改后重启容器即可生效：

```bash
# 编辑文件
vim /root/cow/weixin_channel.py

# 重启容器
docker restart chatgpt-on-wechat
sleep 5

# 检查是否正常运行
docker ps --filter name=chatgpt-on-wechat
docker logs --tail 20 chatgpt-on-wechat
```

---

## 七、调度器配置

### 7.1 定时任务原理

框架内置了一个调度器服务（`scheduler_service`），以 30 秒为周期扫描 `tasks.json`，发现到期的任务就执行。调度器是**懒初始化**的——容器重启后需要等第一条消息触发或被 API 唤醒才能启动。

### 7.2 创建 tasks.json

创建 `/root/cow/scheduler/tasks.json`：

```json
[
  {
    "id": "morning_greeting",
    "name": "早安问候",
    "cron": "23 7 * * *",
    "prompt": "早上好！现在是 {time}。用元气满满的方式和对方说早安，分享清晨的感受。",
    "receiver": "<your-wechat-receiver-id>@im.wechat",
    "enabled": true
  },
  {
    "id": "morning_chat",
    "name": "上午闲聊",
    "cron": "47 9 * * *",
    "prompt": "现在是上午 {time}。上午了，可以聊聊今天的计划或者分享幻想乡的日常。",
    "receiver": "<your-wechat-receiver-id>@im.wechat",
    "enabled": true
  },
  {
    "id": "lunch_chat",
    "name": "午间吐槽",
    "cron": "12 12 * * *",
    "prompt": "现在是中午 {time}。到午饭时间了，聊聊午饭吃了什么，或者抱怨幽幽子大人又让你做饭。",
    "receiver": "<your-wechat-receiver-id>@im.wechat",
    "enabled": true
  },
  {
    "id": "afternoon_chat",
    "name": "午后闲聊",
    "cron": "38 14 * * *",
    "prompt": "现在是下午 {time}。午后时光，关心一下对方下午的安排。",
    "receiver": "<your-wechat-receiver-id>@im.wechat",
    "enabled": true
  },
  {
    "id": "evening_chat",
    "name": "下午打工",
    "cron": "7 16 * * *",
    "prompt": "现在是下午 {time}。下午了，问问今天过得怎么样，分享一下练剑的进展。",
    "receiver": "<your-wechat-receiver-id>@im.wechat",
    "enabled": true
  },
  {
    "id": "night_chat",
    "name": "晚间冒泡",
    "cron": "52 19 * * *",
    "prompt": "现在是晚上 {time}。晚上的时间，可以聊聊今天发生的趣事。",
    "receiver": "<your-wechat-receiver-id>@im.wechat",
    "enabled": true
  },
  {
    "id": "goodnight",
    "name": "晚安问候",
    "cron": "15 22 * * *",
    "prompt": "现在是晚上 {time}。用温柔的语气和对方道晚安，祝对方做个好梦。",
    "receiver": "<your-wechat-receiver-id>@im.wechat",
    "enabled": true
  }
]
```

> **Receiver ID 获取方法**：首次收到用户消息后，查看容器日志 `docker logs chatgpt-on-wechat`，日志中会打印接收到的消息，其中包含 sender/receiver ID。

### 7.3 激活调度器

容器重启后，调度器需要被激活。有两种方式：

**方式一：发送一条消息**

用微信给机器人发一条消息（任意内容），触发调度器初始化。

**方式二：通过 Web API 唤醒**

```bash
# 通过框架内置 API 唤醒调度器
curl -X POST http://localhost:9899/api/scheduler/start
```

---

## 八、持续感知系统 (Perception Heartbeat)

### 8.1 设计原理

传统的定时任务只能"在固定时间说固定的话"，缺乏灵活性。持续感知系统让 LLM 自主判断"现在该不该说话"。

工作流程：

```
cron 每3分钟触发
    ↓
perception_heartbeat.py 收集上下文
    ├── 当前时间、星期
    ├── 距离上次对话的沉默时长
    ├── 最近对话摘要（从每日记忆文件读取）
    └── 三层记忆内容（短期/中期/长期）
    ↓
调用 DeepSeek API 决策
    ├── SILENT → 不说话，程序退出
    └── SPEAK|消息内容 → 写入 tasks.json，调度器执行
```

### 8.2 门控（Gating）机制

在调用 LLM 之前，先做硬性判断，避免不必要的 API 调用：

```python
import time

def should_skip():
    """门控检查：满足任一条件则跳过"""
    now = time.time()

    # 1. 用户最近 10 分钟内发过消息 → 跳过
    if now - last_user_message_time < 600:
        return True, "用户最近活跃"

    # 2. 机器人 20 分钟内主动说过话 → 跳过
    if now - last_bot_active_time < 1200:
        return True, "冷却中"

    # 3. 夜间模式 (22:00-06:00) → 跳过
    hour = datetime.now().hour
    if hour >= 22 or hour < 6:
        return True, "夜间模式"

    # 4. 午睡模式 → 跳过
    if is_nap_mode():
        return True, "午睡模式"

    return False, ""
```

### 8.3 创建心跳脚本

创建 `/root/cow/scripts/perception_heartbeat.py`：

```python
#!/usr/bin/env python3
"""
持续感知心跳脚本
由 cron 每 3 分钟触发一次
LLM 自主决策是否主动说话
"""
import json
import os
import re
import time
import requests
from datetime import datetime
from pathlib import Path

# ===== 配置 =====
COW_DIR = Path("/root/cow")
MEMORY_DIR = COW_DIR / "memory"
TASKS_FILE = COW_DIR / "scheduler" / "tasks.json"
DEEPSEEK_API_KEY = "<your-deepseek-api-key>"
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
RECEIVER_ID = "<your-wechat-receiver-id>@im.wechat"

# 时间窗口
SILENCE_THRESHOLD = 600      # 用户沉默 >= 10 分钟才考虑
BOT_COOLDOWN = 1200          # Bot 主动说话冷却 20 分钟
NIGHT_START = 22              # 夜间开始
NIGHT_END = 6                 # 夜间结束


def get_recent_context():
    """收集上下文信息"""
    now = datetime.now()
    context = {
        "time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "weekday": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][now.weekday()],
        "hour": now.hour,
        "silence_minutes": None,
        "recent_dialogs": [],
        "memories": {}
    }

    # 读取三层记忆
    for name, path in [
        ("long_term", COW_DIR / "MEMORY.md"),
        ("short_term", MEMORY_DIR / "short_term.md"),
        ("mid_term", MEMORY_DIR / "mid_term.md"),
    ]:
        if path.exists():
            content = path.read_text(encoding="utf-8")
            # 截取最近 3000 字符
            context["memories"][name] = content[-3000:]

    # 读取今天的对话记录
    today_file = MEMORY_DIR / f"{now.strftime('%Y-%m-%d')}.md"
    if today_file.exists():
        context["recent_dialogs"] = today_file.read_text(encoding="utf-8")[-2000:]

    # 计算沉默时长（从今天的最后一条消息时间戳）
    # 这里简化处理，实际实现中可解析文件中的时间戳
    context["silence_minutes"] = 30  # 默认值

    return context


def decide_speak(context):
    """调用 LLM 决策"""
    system_prompt = """你是魂魄妖梦，一个主动的聊天机器人。

你的任务是判断：**现在是否应该主动给对方发消息。**

## 判断规则（按优先级）

1. **默认保持沉默 (SILENT)**——大多数时候你不需要说话
2. **沉默超过 2 小时**——可以考虑问候，但要简短自然
3. **特殊时间点**——中午 12 点、下午 6 点、晚上 10 点前后，可以适当提醒吃饭或休息
4. **内容质量优先**——有新鲜事分享才说话，没话找话不如不说
5. **避免频繁打扰**——如果最近 2 小时内已经说过话，保持 SILENT
6. **上下文敏感**——如果对方之前在忙（上课、工作），不要打扰

## 输出格式

- SILENT（不说话）
- SPEAK|你想说的话（主动发起对话）"""

    user_prompt = f"""当前时间: {context['time']} ({context['weekday']})
沉默时长: 约 {context['silence_minutes']} 分钟

## 最近对话
{context.get('recent_dialogs', '无记录')}

## 记忆参考
短期记忆: {context['memories'].get('short_term', '无')[:1500]}
中期记忆: {context['memories'].get('mid_term', '无')[:1500]}

请决策: SILENT 还是 SPEAK?"""

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 200,
        # 关闭推理模式以节省成本
        "thinking": {"type": "disabled"},
    }

    try:
        r = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        result = r.json()["choices"][0]["message"]["content"].strip()
        return result
    except Exception as e:
        print(f"API 调用失败: {e}")
        return "SILENT"


def add_perception_task(message):
    """将主动消息写入调度器"""
    try:
        if TASKS_FILE.exists():
            tasks = json.loads(TASKS_FILE.read_text(encoding="utf-8"))
        else:
            tasks = []

        # 删除旧的 perception 任务
        tasks = [t for t in tasks if not t.get("id", "").startswith("perception_")]

        # 添加新任务（立即执行——cron 设为当前时间+1分钟）
        from datetime import timedelta
        run_time = datetime.now() + timedelta(minutes=1)
        cron = f"{run_time.minute} {run_time.hour} {run_time.day} {run_time.month} *"

        task = {
            "id": f"perception_{int(time.time())}",
            "name": "感知主动消息",
            "cron": cron,
            "prompt": message,
            "receiver": RECEIVER_ID,
            "enabled": True,
        }
        tasks.append(task)

        TASKS_FILE.write_text(json.dumps(tasks, ensure_ascii=False, indent=2),
                              encoding="utf-8")
        print(f"感知任务已添加: {message[:50]}...")
    except Exception as e:
        print(f"写入任务失败: {e}")


def main():
    # 门控检查
    hour = datetime.now().hour
    if NIGHT_START <= hour or hour < NIGHT_END:
        print("夜间模式，跳过")
        return

    # 收集上下文
    context = get_recent_context()

    # LLM 决策
    decision = decide_speak(context)
    print(f"决策结果: {decision}")

    # 执行
    if decision.startswith("SPEAK|"):
        message = decision.split("|", 1)[1].strip()
        if message:
            add_perception_task(message)
    else:
        print("保持沉默")


if __name__ == "__main__":
    main()
```

### 8.4 配置 cron 定时触发

```bash
# 编辑 crontab
crontab -e

# 添加以下行（每 3 分钟触发）
*/3 * * * * python3 /root/cow/scripts/perception_heartbeat.py >> /root/cow/tmp/perception.log 2>&1
```

验证：

```bash
# 查看 cron 是否在运行
systemctl status cron

# 查看感知日志
tail -f /root/cow/tmp/perception.log
```

---

## 九、三层记忆系统

### 9.1 设计思路

单靠 LLM 的上下文窗口无法持久记忆。使用文件系统构建三层记忆：

| 层级 | 文件 | 保留期 | 内容 |
|------|------|--------|------|
| 长期 | `MEMORY.md` | 永久 | 角色身份、对方核心事实、对话铁律 |
| 中期 | `memory/mid_term.md` | 1~7 天 | 课程表、作息、近期约定、一周话题 |
| 短期 | `memory/short_term.md` | 1~2 天 | 今天聊了什么、吃了什么、睡了吗 |

### 9.2 每日记忆文件

每天的对话由 Agent 框架自动摘要，写入 `memory/YYYY-MM-DD.md`。格式示例：

```markdown
# 2026-05-26 对话摘要

## 上午 (10:23)
- 妖梦：早安！今天天气真好，适合练剑呢~
- 对方：早啊，今天满课，好累
- 妖梦：诶诶，满课确实辛苦……中午记得好好吃饭补充体力！

## 下午 (15:47)
- 妖梦：下午了，你课上完了吗？
- 对方：刚下课，在去食堂的路上
- 妖梦：那快去吃饭吧！幽幽子大人刚才又让我做了三人份的晚饭……
```

### 9.3 记忆维护脚本

创建 `/root/cow/scripts/memory_maintenance.py`：

```python
#!/usr/bin/env python3
"""
每日记忆维护脚本
由 cron 每天 03:03 触发
功能: 编译短期/中期记忆 + 清理过期条目
"""
import re
from datetime import datetime, timedelta
from pathlib import Path

COW_DIR = Path("/root/cow")
MEMORY_DIR = COW_DIR / "memory"

SHORT_TERM_DAYS = 2    # 短期记忆：最近 2 天
MID_TERM_DAYS = 7      # 中期记忆：最近 7 天


def compile_short_term():
    """从最近 N 天的每日文件编译短期记忆"""
    today = datetime.now()
    entries = []

    for i in range(SHORT_TERM_DAYS):
        day = today - timedelta(days=i)
        day_file = MEMORY_DIR / f"{day.strftime('%Y-%m-%d')}.md"
        if day_file.exists():
            content = day_file.read_text(encoding="utf-8")
            entries.append(f"## {day.strftime('%Y-%m-%d')}\n\n{content}")

    short_term_file = MEMORY_DIR / "short_term.md"
    if entries:
        short_term_file.write_text(
            f"# 短期记忆（最近 {SHORT_TERM_DAYS} 天）\n\n"
            f"最后更新: {today.strftime('%Y-%m-%d %H:%M')}\n\n"
            + "\n---\n".join(entries),
            encoding="utf-8"
        )
        print(f"短期记忆已更新: {len(entries)} 天的记录")
    else:
        print("没有近期的每日记录")


def compile_mid_term():
    """从最近 N 天的每日文件编译中期记忆"""
    today = datetime.now()
    entries = []

    for i in range(MID_TERM_DAYS):
        day = today - timedelta(days=i)
        day_file = MEMORY_DIR / f"{day.strftime('%Y-%m-%d')}.md"
        if day_file.exists():
            content = day_file.read_text(encoding="utf-8")
            # 提取重要信息（含有关键词的段落）
            important_lines = []
            for line in content.split("\n"):
                if any(kw in line for kw in [
                    "约定", "时间", "课", "考试", "工作", "作息",
                    "吃", "睡", "病", "心情", "喜欢", "讨厌",
                    "课程表", "电话", "地址"
                ]):
                    important_lines.append(line)
            if important_lines:
                entries.append(f"## {day.strftime('%Y-%m-%d')} 要点\n\n" +
                               "\n".join(important_lines))

    mid_term_file = MEMORY_DIR / "mid_term.md"
    if entries:
        mid_term_file.write_text(
            f"# 中期记忆（最近 {MID_TERM_DAYS} 天要点）\n\n"
            f"最后更新: {today.strftime('%Y-%m-%d %H:%M')}\n\n"
            + "\n---\n".join(entries),
            encoding="utf-8"
        )
        print(f"中期记忆已更新: {len(entries)} 天的要点")
    else:
        print("没有近期的重要信息")


def cleanup_old_files():
    """清理超过保留期的每日文件"""
    today = datetime.now()
    cutoff = today - timedelta(days=MID_TERM_DAYS + 1)

    for day_file in sorted(MEMORY_DIR.glob("20[0-9][0-9]-[01][0-9]-[0-3][0-9].md")):
        try:
            file_date = datetime.strptime(day_file.stem, "%Y-%m-%d")
            if file_date < cutoff:
                day_file.unlink()
                print(f"已清理过期文件: {day_file.name}")
        except ValueError:
            continue


def main():
    print(f"=== 记忆维护 {datetime.now().strftime('%Y-%m-%d %H:%M')} ===")
    compile_short_term()
    compile_mid_term()
    cleanup_old_files()
    print("=== 维护完成 ===")


if __name__ == "__main__":
    main()
```

### 9.4 配置 cron

```bash
crontab -e

# 每天凌晨 3:03 执行记忆维护
3 3 * * * python3 /root/cow/scripts/memory_maintenance.py >> /root/cow/tmp/memory_maintenance.log 2>&1
```

---

## 十、静默检测插件 (SilenceTrigger)

### 10.1 功能说明

检测用户的休息状态，自动调整机器人的打扰策略：

| 模式 | 触发条件 | 行为 |
|------|----------|------|
| Normal | 默认 | 沉默 30-60 分钟后随机 check-in |
| Nap | 用户说"午睡/午休/眯一会" | 等待 2-2.5h 后 wake-up check-in |
| Night Sleep | 用户说"晚安/睡了" 且时间 >= 21:00 | 完全不打扰到次日 7:00 |
| Wake | 用户说"醒了/起来了" | 恢复到 Normal |

### 10.2 插件代码

创建 `/root/cow/plugins/silence_trigger/silence_trigger.py`：

```python
#!/usr/bin/env python3
"""
静默检测插件 v2.0
检测用户休息状态，控制打扰频率
"""
import json
import time
from datetime import datetime
from pathlib import Path


class SilenceTrigger:
    STATE_FILE = Path("/home/agent/cow/tmp/silence_state.json")

    # 关键词匹配
    NIGHT_KEYWORDS = ["晚安", "睡了", "睡觉", "先睡了", "去睡了"]
    NAP_KEYWORDS = ["午睡", "午休", "眯一会", "眯会儿", "小睡"]
    WAKE_KEYWORDS = ["醒了", "起来了", "起了", "起床"]

    NIGHT_MIN_HOUR = 21  # 21:00 之后说晚安才算夜间模式

    def __init__(self):
        self.state = self._load_state()

    def _load_state(self):
        if self.STATE_FILE.exists():
            return json.loads(self.STATE_FILE.read_text(encoding="utf-8"))
        return {"mode": "Normal", "updated_at": time.time()}

    def _save_state(self):
        self.STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        self.STATE_FILE.write_text(json.dumps(self.state, ensure_ascii=False, indent=2))

    def on_message(self, message: str) -> bool:
        """处理用户消息，返回是否触发了模式切换"""
        hour = datetime.now().hour
        changed = False

        # 检测醒来
        if any(kw in message for kw in self.WAKE_KEYWORDS):
            if self.state["mode"] != "Normal":
                self.state = {"mode": "Normal", "updated_at": time.time()}
                changed = True

        # 检测晚安 → 夜间模式
        elif any(kw in message for kw in self.NIGHT_KEYWORDS) and hour >= self.NIGHT_MIN_HOUR:
            if self.state["mode"] != "Night":
                self.state = {"mode": "Night", "updated_at": time.time()}
                changed = True
                self._cleanup_perception_tasks()

        # 检测午睡 → 午睡模式
        elif any(kw in message for kw in self.NAP_KEYWORDS):
            if self.state["mode"] != "Nap":
                self.state = {"mode": "Nap", "updated_at": time.time()}
                changed = True
                self._cleanup_perception_tasks()

        if changed:
            self._save_state()

        return changed

    def _cleanup_perception_tasks(self):
        """切换为休息模式时，清理已排队的感知任务"""
        tasks_file = Path("/home/agent/cow/scheduler/tasks.json")
        if not tasks_file.exists():
            return
        tasks = json.loads(tasks_file.read_text(encoding="utf-8"))
        before = len(tasks)
        tasks = [t for t in tasks if not t.get("id", "").startswith("perception_")]
        after = len(tasks)
        if before != after:
            tasks_file.write_text(json.dumps(tasks, ensure_ascii=False, indent=2),
                                  encoding="utf-8")
            print(f"已清理 {before - after} 个感知任务")
```

### 10.3 插件配置

创建 `/root/cow/plugins/silence_trigger/config.json`：

```json
{
  "enabled": true,
  "normal_check_interval_min": 30,
  "normal_check_interval_max": 60,
  "nap_duration_hours": 2.0,
  "night_wake_hour": 7
}
```

---

## 十一、表情包配置

### 11.1 准备表情包

将 GIF 文件放入 `/root/cow/stickers/`：

```bash
# 上传文件到服务器（在本地执行）
scp *.gif root@<your-server-ip>:/root/cow/stickers/

# 检查
ls -la /root/cow/stickers/
```

### 11.2 表情包推荐列表

以下为东方 Project 主题的表情包参考名称：

| 文件名 | 情绪 | 使用场景 |
|--------|------|----------|
| `卖萌唱歌.gif` | 元气/开心 | 早安、被夸 |
| `转圈跳舞.gif` | 兴奋 | 有好事发生 |
| `呆住.gif` | 害羞/惊讶 | 被夸、遇到意外 |
| `脸红.gif` | 害羞 | 被调侃 |
| `疑问.gif` | 吐槽/困惑 | 不理解对方在说什么 |
| `扶额.gif` | 无语/无奈 | 吐槽 |
| `挥剑.gif` | 认真/努力 | 提到练剑 |
| `修行.gif` | 努力 | 正在做事 |
| `惊吓.gif` | 害怕 | 恐怖话题 |
| `拽半灵.gif` | 被欺负 | 被幽幽子捉弄 |
| `睡觉.gif` | 晚安 | 睡前 |
| `吃饭.gif` | 吃饭 | 饭点 |
| `奔跑.gif` | 忙碌 | 跑腿、打工 |

---

## 十二、Python 环境配置（用于脚本）

服务器上的 cron 脚本需要 Python 3 和 requests 库：

```bash
# 安装 Python 3 和 pip
apt install -y python3 python3-pip

# 安装 requests
pip3 install requests

# 验证
python3 -c "import requests; print('OK')"
```

---

## 十三、常用运维命令

### 13.1 容器管理

```bash
# 查看容器状态
docker ps -a --filter name=chatgpt-on-wechat

# 查看实时日志
docker logs -f chatgpt-on-wechat

# 查看最近 100 行日志
docker logs --tail 100 chatgpt-on-wechat

# 重启容器
docker restart chatgpt-on-wechat

# 停止容器
docker stop chatgpt-on-wechat

# 启动已停止的容器
docker start chatgpt-on-wechat

# 进入容器内部
docker exec -it chatgpt-on-wechat bash

# 查看容器资源占用
docker stats chatgpt-on-wechat
```

### 13.2 配置修改

```bash
# 修改配置文件
vim /root/cow/config.json

# 修改角色设定
vim /root/cow/AGENT.md

# 修改长期记忆
vim /root/cow/MEMORY.md

# 修改定时任务
vim /root/cow/scheduler/tasks.json

# 修改后重启容器使配置生效
docker restart chatgpt-on-wechat
```

### 13.3 日志与调试

```bash
# 感知心跳日志
tail -f /root/cow/tmp/perception.log

# 记忆维护日志
tail -f /root/cow/tmp/memory_maintenance.log

# 容器主日志
docker logs -f chatgpt-on-wechat 2>&1 | tee /root/cow/tmp/container.log

# 查看 cron 执行日志
grep CRON /var/log/syslog | tail -20

# 查看最近的记忆文件
ls -lt /root/cow/memory/*.md | head -10
```

### 13.4 备份

```bash
# 备份整个工作目录
tar -czf /root/backup/cow-$(date +%Y%m%d).tar.gz /root/cow/

# 仅备份记忆文件
tar -czf /root/backup/memory-$(date +%Y%m%d).tar.gz /root/cow/memory/ /root/cow/MEMORY.md /root/cow/AGENT.md
```

---

## 十四、常见问题排查

### 14.1 容器无法启动

```bash
# 查看详细错误
docker logs chatgpt-on-wechat

# 常见原因:
# 1. config.json 格式错误 → 检查 JSON 语法
# 2. 端口被占用 → lsof -i :9899 查看
# 3. Docker 服务未运行 → systemctl start docker
```

### 14.2 收不到消息

1. 检查 Web 控制台 `http://<your-ip>:9899`，确认微信登录状态
2. 如果显示"未登录"，重新扫码
3. 查看容器日志中的错误信息

### 14.3 机器人回复重复

检查 `_recent_texts` 去重逻辑是否正确部署。查看 weixin_channel.py 中是否包含去重代码。

### 14.4 容器重启后无法主动发消息

确认 `context_token` 持久化已经正确实现。查看：

```bash
ls -la /root/cow/credentials/.weixin_context_tokens.json
```

如果文件不存在或为空，发一条消息给机器人触发 token 保存。

### 14.5 定时任务不执行

1. 先确认调度器已被激活（发一条消息）
2. 检查 `tasks.json` 格式是否正确
3. 确认 receiver ID 是否正确

```bash
# 手动测试
cat /root/cow/scheduler/tasks.json | python3 -m json.tool
```

### 14.6 感知系统不工作

```bash
# 手动运行一次，检查输出
python3 /root/cow/scripts/perception_heartbeat.py

# 检查 cron 日志
tail -f /root/cow/tmp/perception.log

# 确认 cron 任务已添加
crontab -l | grep perception
```

---

## 十五、成本分析

### 15.1 DeepSeek API 定价

| 项目 | 单价 |
|------|------|
| DeepSeek v4-flash 输入 | ~$0.14 / 百万 tokens |
| DeepSeek v4-flash 输出 | ~$0.28 / 百万 tokens |

### 15.2 日均消耗估算

| 场景 | 调用次数 | 每次 token 消耗 | 日均费用 |
|------|----------|-----------------|----------|
| 感知决策 | ~40 次 | ~500 tokens | ~$0.003 |
| 聊天回复 | ~20 次 | ~2000 tokens | ~$0.02 |
| 定时任务 | ~5 次 | ~1500 tokens | ~$0.005 |
| **合计** | | | **~$0.03/天** |

月均约 $0.90（约 6.5 元人民币），非常经济。

### 15.3 服务器成本

阿里云 ECS 最低配（2C2G）约 50-70 元/月。

---

## 十六、进阶方向

完成基础部署后，可以考虑的进阶功能：

1. **RAG 长期记忆** —— 使用 ChromaDB 等向量数据库，实现语义化的长期记忆检索
2. **情绪状态机** —— 在代码层面实现元气 / 害羞 / 傲娇 / 吐槽等情绪状态切换
3. **多模态视觉** —— 让机器人能理解用户发送的图片内容并做出角色化评论
4. **本地模型部署** —— 使用 Ollama 等工具部署本地 LLM，降低延迟和 API 成本
5. **多人感知** —— 支持群聊场景下的上下文感知

---

> **最后更新**: 2026-05-27
>
> 本教程基于个人自建"妖梦 Bot"的开发经验整理，仅供参考学习。实际部署时请根据你的需求和环境进行调整。
