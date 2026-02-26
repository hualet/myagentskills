# My Agent Skills

个人收集/编写的 Claude Code Agent 技能库。

## 技能列表

### pdf-toc-extractor
从PDF文档中提取目录（书签/大纲）结构，支持文本和JSON格式输出。

### deepin-mail
通过 D-Bus 与 deepin-mail 邮件客户端交互，支持读取、发送、搜索和管理邮件。

## 项目结构

```
.
├── .claude-plugin/
│   └── marketplace.json    # 插件配置文件
├── pdf-toc-extractor/      # PDF目录提取技能
│   ├── SKILL.md
│   ├── scripts/
│   └── references/
├── deepin-mail/            # Deepin Mail 邮件操作技能
│   ├── SKILL.md
│   └── scripts/
└── README.md
```
