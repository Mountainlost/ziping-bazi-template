# AI 接入

基础排盘、十二章报告、命盘附件和地点匹配由本地服务完成。可选问答使用 Magpie 的 Responses 接口。

将 `deploy/magpie.example.json` 复制到源码之外，填入自己的网关配置。开发运行时使用环境变量 `MAGPIE_CONFIG_FILE` 指向文件。Windows 生产部署可设置配置中的 `magpieConfigFile`。密钥只由后端读取。

确认命盘后，`POST /api/v1/charts/{chartId}/ask` 提供两种模式。普通提问按主题检索现有报告证据。使用 `mode=rederive` 时，根据锁定四柱、命局证据和已计算的运年生成独立解读。联网查证依赖网关和模型支持的 `web_search`。

后端校验引用的证据编号，并在请求前后比较锁定命盘。请求不包含姓名或完整出生资料。发签通过 `scripts/issue_master_pass.py` 在服务器本地完成，默认每日全站最多 50 次，按北京时间重置。
