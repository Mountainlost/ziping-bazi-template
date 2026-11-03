# 第三方声明

## 📋 bazi-skill

名称：jinchenma94/bazi-skill。来源：https://github.com/jinchenma94/bazi-skill 。许可证：MIT License。

本地副本：`third_party/bazi-skill/`，原始许可证见 `third_party/bazi-skill/LICENSE`，保留完整版权声明。

固定提交：`112a5d84cd1a001a0038cafca3be68d93e4c0cc9`。以隔离适配器导入原排盘函数，未改动第三方核心代码。

## 📋 地点数据

GeoNames：中国行政地名及WGS84坐标，快照2026-11-02。来源：https://download.geonames.org/export/dump/CN.zip 。采用CC BY 4.0：https://creativecommons.org/licenses/by/4.0/ 。项目：https://www.geonames.org/ 。本项目筛选行政中心记录，与区划层级匹配、规范化并压缩，未匹配项不补造。

Administrative-divisions-of-China：省市区层级，来源：https://github.com/modood/Administrative-divisions-of-China ，原始LICENSE：https://github.com/modood/Administrative-divisions-of-China/blob/master/LICENSE 。许可证原文如下：

```text
        DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
                    Version 2, December 2004

 Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>

 Everyone is permitted to copy and distribute verbatim or modified
 copies of this license document, and changing it is allowed as long
 as the name is changed.

            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION

  0. You just DO WHAT THE FUCK YOU WANT TO.
```

scripts/build_locations.py记录源文件SHA256、筛选与打包过程；源快照及许可证说明随项目保留。

## 📋 视觉素材

人物配图为本项目生成的古代学者意象，非历史人物传世肖像。书封为本项目DOM/CSS设计，不复制出版社书籍封面。已批准参考图保存在docs目录，运行配图位于apps/web/public/images。

## 📋 应用依赖

`@phosphor-icons/react`（Phosphor Icons）：MIT License，Copyright (c) 2020 Phosphor Icons。用于统一导航、附件、问答与操作图标；项目：https://github.com/phosphor-icons/react 。原许可证保留在依赖包中，通过npm安装，无付费图标或远程图像接口。

Next.js / React / Tailwind CSS / TypeScript / ESLint、FastAPI / Pydantic / uvicorn / httpx / pytest / tzdata 均通过标准包管理器安装；具体版本由 `apps/web/package-lock.json` 和 `apps/api/requirements.lock.txt` 记录，许可证遵循各包自带声明。
