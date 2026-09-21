**AI Editor** 将复杂的视频创作转化为自然直观的对话体验。兼顾易用性和企业级可靠性，让视频创作对初学者和创意爱好者都变得简单友好。

## ✨ 核心特性
- 🌐 **智能素材搜索与整理**： 自动在线搜索并下载符合你需求的图片和视频片段。基于用户主题素材进行片段拆分与内容理解。
- ✍️ **智能文案生成**： 结合用户主题、画面理解与情绪识别，自动构建故事线及契合的旁白。内置少样本（Few-shot）仿写能力，支持通过输入参考文本（如种草测评、日常碎碎念等）定义文案风格，实现语感、节奏与句式的精准复刻。
- 🎵 **智能推荐音乐、配音与字体**：支持导入私有歌单，根据视频内容和情绪自动推荐背景音乐并智能卡点。只需描述"克制一点","偏情绪化","像纪录片旁白"等风格，系统即可匹配合适的配音与字体，保证整体风格协调统一。
- 💬 **对话式精修**：支持快速删减、替换或重组片段；修改任意字幕文案；调整文字颜色、字体、描边、位置等视觉元素——所有操作均通过自然语言完成，即改即得。
- ⚡ **剪辑技能沉淀**： 可一键保存为专属剪辑Skill，记录完整的剪辑逻辑。下次只需更换素材并选择对应Skill，即可快速复刻同款风格，实现高效批量生产。

## ✨ 演示案例

<table align="center">
  <tr>
    <td align="center"><b>种草视频</b></td>
    <td align="center"><b>幽默有趣</b></td>
    <td align="center"><b>好物分享</b></td>
    <td align="center"><b>文艺风格</b></td>
  </tr>
  <tr>
    <td align="center"><video src="https://github.com/user-attachments/assets/28043813-1fda-4077-80d4-c6f540d7c7cb" controls width="220"></video></td>
    <td align="center"><video src="https://github.com/user-attachments/assets/a1e33da2-a799-4398-a1bb-b25bb5143d7c" controls width="220"></video></td>
    <td align="center"><video src="https://github.com/user-attachments/assets/444fd0fb-8824-4c25-b449-9309b0fcfd85" controls width="220"></video></td>
    <td align="center"><video src="https://github.com/user-attachments/assets/2e69fa0d-b693-4d4f-b4d2-45146254f9e8" controls width="220"></video></td>
  </tr>
  </tr>

  <tr>
    <td align="center"><b>开箱视频</b></td>
    <td align="center"><b>宠物说话</b></td>
    <td align="center"><b>旅行Vlog</b></td>
    <td align="center"><b>年终总结</b></td>
  </tr>
  <tr>
    <td align="center"><video src="https://github.com/user-attachments/assets/ff1d669b-1d27-4cf8-b0be-1b141c717466" controls width="220"></video></td>
    <td align="center"><video src="https://github.com/user-attachments/assets/063608bb-7fbd-4841-a08f-032ae459499f" controls width="220"></video></td>
    <td align="center"><video src="https://github.com/user-attachments/assets/bc441dfa-e995-4575-8401-ecefa269e57b" controls width="220"></video></td>
    <td align="center"><video src="https://github.com/user-attachments/assets/533ef5c3-bb76-4416-bff7-825e88b00b7d" controls width="220"></video></td>
  </tr>
  </tr>
</table>

> <sub>
> ⚠️ <b>画质注：</b>受限于README展示空间，演示视频经过极限压缩。实际运行默认保持原分辨率输出，支持自定义尺寸。<br>
> ⚖️ <b>免责声明：</b>演示中包含的用户自摄素材及品牌标识仅作技术能力展示，版权归原作者所有。如有侵权请联系删除。
> </sub>

## 📦 安装

### 1. 克隆仓库
```bash
# 如果没有安装git，参考官方网站进行安装：https://git-scm.com/install/
# 或手动打包下载，并解压
git clone https://github.com/ninghan11111-ai/ai-editor.git
cd ai-editor
```

### 2. 创建虚拟环境

按照官方指南安装 Conda（推荐Miniforge，安装过程中建议勾选上自动配置环境变量）：https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html

```
# 要求python>=3.11
conda create -n storyline python=3.11
conda activate storyline
```

### 3. 资源下载与依赖安装
#### 3.1 一键安装（仅支持Linux和MacOS）
```
sh build_env.sh
```

#### 3.2 手动安装
##### A. MacOS 或 Linux
  - Step 1: 安装 wget（如果尚未安装）
    
    ```
    # MacOS: 如果你还没有安装 Homebrew，请先安装：https://brew.sh/
    brew install wget
    
    # Ubuntu/Debian
    sudo apt-get install wget
    
    # CentOS
    sudo yum install wget
    ```

  - Step 2: 下载资源
  
    ```bash
    chmod +x download.sh
    AI_EDITOR_ASSET_BASE_URL=https://your-asset-host.example/path ./download.sh
    ```
  
  - Step 3: 安装依赖

    ```bash
    pip install -r requirements.txt
    ```
    如果你计划使用 `storyline.local_asr`，请确认当前环境已安装 `torchaudio`。

###### B. Windows
  - Step 1: 准备目录：在项目根目录下新建目录 `resource`。

  - Step 2: 下载并解压：

    *   下载模型包 `models.zip` -> 解压至 `.storyline` 目录。
  
    *   下载资源包 `resource.zip` -> 解压至 `resource` 目录。
  - Step 3:  **安装依赖**：
    ```bash
    pip install -r requirements.txt
    ```
    如果你计划使用 `storyline.local_asr`，请确认当前环境已安装 `torchaudio`。


## 🚀 快速开始
注意：在开始之前，您需要先在 config.toml 中配置 API-Key。详细信息请参阅文档 [API-Key 配置](docs/source/zh/api-key.md)

### 1. 启动 MCP 服务器

#### MacOS or Linux
  ```bash
  PYTHONPATH=src python -m ai_editor.mcp.server
  ```

#### Windows
  ```
  $env:PYTHONPATH="src"; python -m ai_editor.mcp.server
  ```


### 2. 启动对话界面

- 方式 1：命令行界面

  ```bash
  python cli.py
  ```

- 方式 2：Web 界面

  ```bash
  uvicorn agent_fastapi:app --host 127.0.0.1 --port 7860
  ```

## 📁 项目结构
```
AI Editor/
├── 🎯 src/ai_editor/           核心应用
│   ├── mcp/                         🔌 模型上下文协议
│   ├── nodes/                       🎬 视频处理节点
│   ├── skills/                      🛠️ Agent 技能库
│   ├── storage/                     💾 Agent 记忆系统
│   ├── utils/                       🧰 工具函数
│   ├── agent.py                     🤖 Agent 构建
│   └── config.py                    ⚙️ 配置管理
├── 📚 docs/                         文档
├── 🐳 Dockerfile                    Docker 配置
├── 💬 prompts/                      LLM 提示词模板
├── 🎨 resource/                     静态资源
│   ├── bgms/                        背景音乐库
│   ├── fonts/                       字体文件
│   ├── script_templates/            视频脚本模板
│   └── unicode_emojis.json          Emoji 列表
├── 🔧 scripts/                      工具脚本
├── 🌐 web/                          Web 界面
├── 🚀 agent_fastapi.py              FastAPI 服务器
├── 🖥️ cli.py                        命令行界面
├── ⚙️ config.toml                   主配置文件
├── 🚀 build_env.sh                  环境构建脚本
├── 📥 download.sh                   资源下载脚本
├── 📦 requirements.txt              运行时依赖
└── ▶️ run.sh                        启动脚本

```

## 📚 文档

### 📖 教程索引

- [API申请与配置](docs/source/zh/api-key.md) - 如何申请和配置 API 密钥
- [使用教程](docs/source/zh/guide.md) - 常见用例和基本操作
- [常见问题](docs/source/zh/faq.md) - 常见问题解答

## TODO

- [ ] 添加口播类型视频剪辑功能
- [ ] 添加音色克隆功能
- [ ] 添加更多的转场/滤镜/特效功能
- [ ] 添加图像/视频生成和编辑能力
- [ ] 支持GPU渲染和高光裁切

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
