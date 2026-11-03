# 子平八字 · Web 项目模板

一个可自行部署的中文八字 Web 项目。输入出生资料后，程序计算真太阳时、四柱、大运与流年，生成十二章报告。报告提供白话、专业两种阅读方式及判断依据。子平大师提供可选的深度解读和互动问答。

- [GitHub Pages 互动预览](https://mountainlost.github.io/ziping-bazi-template/)由原站前端直接构建。首页、排盘表单、子平大师和报告页沿用原布局，可打开一份虚构示例体验报告。
- 完整排盘、保存报告、发签和 AI 问答需要运行 Next.js 与 FastAPI。基础排盘与完整规则报告无需 API 密钥。
- AI 启用后读取已确认的命盘。深度解读和问答单独保存，后端会校验锁定命盘在请求前后一致。

## 本地运行

需要 Python 3.10+、Node.js 20.9+ 和 npm。以下为 Windows PowerShell 操作。

```powershell
.\setup.ps1
.\start.ps1
```

打开 [本地网站](http://127.0.0.1:3000) 或 [API 文档](http://127.0.0.1:8000/docs)。Windows 启动器沿用本机的 CodexToolData 虚拟环境目录。其他环境可在仓库根目录自行建立虚拟环境，安装 `apps/api/requirements.lock.txt`，再在两个终端分别运行：

```sh
python -m uvicorn app.main:app --app-dir apps/api --host 127.0.0.1 --port 8000
```

```sh
cd apps/web
npm ci
npm run dev
```

如需指定 SQLite 文件，启动 API 前设置 `BAZI_DB_PATH` 为自己实例的绝对路径。

## 启用子平大师

1. 复制 `deploy/magpie.example.json` 到仓库外，填写自己网关的 URL、模型 ID 和密钥。
2. 在启动后端的环境设置 `MAGPIE_CONFIG_FILE` 为上述私密 JSON 的绝对路径。
3. 生成并确认基础报告后，用同一环境运行以下命令，签发访问当前实例的大师签：

   ```sh
   python scripts/issue_master_pass.py --database /absolute/path/charts.access.sqlite
   ```

4. 在子平大师页面输入签子，再开始解盘或提问。网关的联网能力取决于所配置的模型与网关。

更多见 [AI 接入](docs/API_CONNECTIONS.md) 和 [服务器部署](docs/SERVER_DEPLOYMENT.md)。

## 测试与资料

Windows PowerShell 下先设置 `$env:PYTHONUTF8="1"` 与 `$env:PYTHONIOENCODING="utf-8"`，再从仓库根目录运行 `python -m pytest -q`。前端在 `apps/web` 下运行 `npm run lint`、`npm run typecheck` 和 `npm run build`。测试覆盖无密钥生成报告、时辰边界与 AI 请求前后的命盘一致性。

- [架构说明](docs/ARCHITECTURE.md)
- [数据与典籍来源](docs/DATA_SOURCES.md)
- [第三方声明](THIRD_PARTY_NOTICES.md)
- [发布文案](RELEASE.md)

传统命理解读仅供参考。

如需重建 Pages 预览，请在已安装后端依赖的环境运行：

```sh
python scripts/build_pages_preview.py pages-output --base-path /ziping-bazi-template
```

将输出目录发布到 GitHub Pages。部署到其他仓库时，将路径改为对应仓库名。
