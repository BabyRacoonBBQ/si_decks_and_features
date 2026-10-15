# StressThermal

本仓库维护两部分：**StressThermal 功能介绍网页**和 **StressThermal 案例库**。Xiaodong 的 presentation 是重要参考资料，来自截图 OCR 转写，不属于本仓库持续维护的演示内容。

## 阅读入口

| 部分 | 入口 | 内容 |
| --- | --- | --- |
| 功能介绍 | [Features](sinterconnect-catalog/index.html) | 功能分类、开发状态、命令说明及关联案例 |
| 案例库 | [Application cases](sinterconnect-catalog/application-cases.html) | 应用背景、输入、网格、物理场、结果和 GT-A 对比状态 |
| 功能测试 | [Feature tests](sinterconnect-catalog/feature-tests.html) | 独立功能案例及验证状态 |
| 配套演示 | [StressThermal / packaging / hybrid bonding](hybrid-bonding/hybrid-bonding.html) | 功能介绍、封装演进、真实器件、hybrid bonding 和 trace mapping |
| 进度 | [维护日志](sinterconnect-catalog/progress.html) | 案例与功能维护记录 |
| 参考资料 | [Xiaodong presentation 的 HTML 转写](芯片与封装仿真_HTML幻灯片.html) | 保留的截图 OCR 参考版本 |

克隆后用浏览器打开上述 HTML 即可。网页、案例图片、下载文件及本地 VTK viewer 随仓库保留；外部参考链接需要联网。也可在仓库根目录运行 `python -m http.server 8000 --bind 127.0.0.1`，访问本地网页。

## 目录与维护边界

- `sinterconnect-catalog/`：两部分共用的网页、数据、生成脚本和必要案例资源。`feature-*.html` 是功能详情；`case-*.html` 是案例详情。
- `hybrid-bonding/`：我们维护的配套 HTML 演示。当前修改以 HTML 为准，目录中的 PPTX 是历史导出，不与 HTML 自动同步。
- `Resources/case-archive/`：六项历史案例的精简恢复归档、命令和版本证据，见[归档说明](Resources/case-archive/README.md)。ZIP 完整不等于已完成从零求解恢复验证。
- `Resources/xiaodong-originals/`：12 张原始截图，用于核对 OCR、图示和批注。HTML 转写未完整覆盖所有原图，因此同时保留。
- `StressThermal.pptx`：保留的演示文件；不作为当前网页修改的生成源。

备份目录、临时 Python 运行库、缓存及独立项目 `rea-review/` 不纳入本仓库。保留在案例目录里的 TDR、GT-A 脚本、网格和运行日志是已有报告的具体证据，不应按临时文件批量清理。

## 维护与检查

网页、数据和生成入口见 [catalog 维护说明](sinterconnect-catalog/README.md)。提交前在仓库根目录执行：

```powershell
python sinterconnect-catalog/check_catalog_links.py
```

修改交互图或演示页时，还需用浏览器查看改动页面，确认导航、图片、放大窗口和本地资源正常。案例的历史结果、当前回归验证和 GT-A 数值对比要分别记录；没有执行求解时，不更新为已通过。

Xiaodong 参考 presentation 及原始截图保持原样。修订功能或案例时，将内容写入我们维护的网页；OCR 内容需要以原图、输入文件或权威资料核对后再采用。第三方图像和 viewer 的来源、署名及许可随内容保留。
