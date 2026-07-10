# 安全配置与素材合规

本文说明密钥管理、secret scanning、素材来源追踪和 license report。

## 使用 config.local.toml 保存密钥

`config.toml` 应保持可提交状态，不要写入真实 API key。

复制示例文件：

```bash
cp config.local.toml.example config.local.toml
```

把真实密钥写入 `config.local.toml`。该文件已加入 `.gitignore`，不会被 Git 跟踪。

运行时加载顺序：

1. `config.toml`
2. `config.local.toml`
3. 环境变量覆盖

可用环境变量示例：

```bash
export OPENSTORYLINE_LLM_API_KEY="..."
export OPENSTORYLINE_VLM_API_KEY="..."
export PEXELS_API_KEY="..."
export TTS_MINIMAX_API_KEY="..."
export AI_TRANSITION_MINIMAX_API_KEY="..."
```

也可以指定本地配置路径：

```bash
export OPENSTORYLINE_CONFIG_LOCAL=/path/to/config.local.toml
```

## 本地 secret 检查

手动扫描当前已跟踪文件：

```bash
python scripts/check_secrets.py
```

扫描整个工作区：

```bash
python scripts/check_secrets.py --all
```

启用 pre-commit：

```bash
pip install pre-commit
pre-commit install
```

仓库已提供 `.pre-commit-config.yaml`，提交前会运行 `scripts/check_secrets.py`。

如果使用 GitHub，请在仓库安全设置中开启：

- Secret scanning
- Push protection
- Dependabot alerts

## License Report

最终渲染成功后，系统会生成：

```text
outputs/<session_id>/license_report.json
outputs/<session_id>/license_report.md
```

报告会尽量记录：

- 用户上传/本地素材
- Pexels 搜索素材
- 内置 BGM
- 内置字体
- AI 生成转场

报告不是法律意见。商用前仍需要人工确认人物肖像、商标、品牌、音乐、字体、AI 生成内容和上传素材授权。

## 内置资源 license 元数据

下载的资源目录 `resource/` 默认不进入 Git。运行下面命令可给资源元数据补齐合规字段：

```bash
python scripts/annotate_resource_licenses.py
```

新增字段：

```json
{
  "license": "unknown",
  "license_url": "",
  "commercial_allowed": false,
  "attribution_required": true,
  "compliance_notes": "License metadata was not provided with the bundled resource. Verify rights before commercial use."
}
```

没有明确授权的资源默认视为不可商用，避免误用。

