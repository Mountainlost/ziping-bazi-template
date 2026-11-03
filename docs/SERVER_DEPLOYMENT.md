# 服务器部署

应用需要一个运行 Next.js 和 FastAPI 的环境。GitHub Pages 发布由原站前端导出的静态预览，构建方式见 README。

1. 按 README 安装依赖并跑通本地站点。将 SQLite 数据和日志放在源码以外的持久目录。
2. Windows 生产部署可运行 `deploy/prepare-server.ps1`，生成 Next.js standalone 构建。复制 `deploy/server.example.json` 为仓库外的配置，填写自己的路径、端口与站点地址。
3. 运行 `python deploy/run_server.py --config <配置文件> --check` 验证，再去掉 `--check` 启动。Next 和 API 默认只监听本机。
4. 如需公开访问，用自己的反向代理提供 HTTPS，将流量指向 Next 端口。示例见 `deploy/Caddyfile.snippet`。API 和模型网关可维持回环访问。
5. 如有需要，从 `deploy/magpie.example.json` 创建私密配置，在部署配置中指定 `magpieConfigFile`。

先备份实例数据，再替换部署版本。可用 `deploy/backup_data.py` 制作 SQLite 一致性备份。
