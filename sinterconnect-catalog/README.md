# StressThermal features and cases

本目录同时承载功能介绍和案例库，通过相关功能、应用案例及功能测试链接互相连接。入口为 `index.html`、`application-cases.html` 和 `feature-tests.html`。提交已生成的 HTML 和必要资源，阅读者无需安装 Python、Node 或求解器。

## 数据与生成入口

| 文件 | 用途 |
| --- | --- |
| `catalog-data.json` / `features-data.json` | 原有案例与功能记录 |
| `source-table-data.json` / `screenshots/` | 原表转写和原始截图；保留来源与原始状态 |
| `catalog-crosslinks.json` | 原有记录和来源记录之间的关联 |
| `gt-a-cases.json` / `assets/gt-a/` | GT-A 转换产物、下载文件和验证状态 |
| `feature_content.py` / `case_result_content.py` | 功能说明与案例结果内容 |
| `cantilever_case_report.py` / `damascene_case_report.py` | 详细案例报告内容 |
| `render_english_catalog.py` | 当前统一页面渲染入口 |
| `catalog-merged.json` | 渲染后统一的数据视图 |

修改相应数据或内容模块后，在仓库根目录运行：

```powershell
python sinterconnect-catalog/render_english_catalog.py
python sinterconnect-catalog/check_catalog_links.py
```

这些命令使用 Python 标准库，不执行求解器。渲染会更新多份 HTML 和统一数据，应审查差异，避免覆盖其他人的修改。`build_catalog.py`、`build_source_catalog.py` 和 `import_screenshot_data.py` 包含原始导入流程；不要为了常规文字修订重新导入整套来源记录。

`check_catalog_links.py` 检查原表行覆盖、功能与案例关联、状态标签及本地导航。目前包含 104 项功能、59 条原表明细和 25 个案例。页面链接检查不能代替求解验证。

## 案例资源与再生成

- `assets/case-reports/`：具体案例的图、输入、保留数据和证据记录。
- `assets/svisual/`：历史结果图、数据清单和验证记录。
- `assets/gt-a/`：转换脚本、模型、日志和对应清单。
- `../Resources/case-archive/`：精简历史案例 ZIP，以及输入执行顺序、版本和恢复边界。

保留的 Cantilever 和 Damascene 数据可用于重新生成已有报告图，不代表运行了新仿真。需要 Python 的 `numpy`、`h5py`、`matplotlib` 和 `Pillow`：

```powershell
python sinterconnect-catalog/prepare_cantilever_report.py
python sinterconnect-catalog/prepare_damascene_report.py
python sinterconnect-catalog/export_damascene_vtk.py
python sinterconnect-catalog/render_english_catalog.py
python sinterconnect-catalog/check_catalog_links.py
```

上述后处理以已保留的数据文件为前提。历史 `prepare_svisual.py`、`prepare_tsv_results.py` 和 `maintain_gt_a.py` 引用原 Linux / converter 环境，应先按文件内容配置路径；它们不是跨机器一键恢复入口。求解器、授权和 converter 的开发源码不由本网页仓库提供。

## 本地三维查看器

浏览页面使用已提交的 `assets/vtk-viewer/vtk-model-viewer.js`，无需 CDN。修改 viewer 源码后，在其目录执行：

```powershell
npm ci
npm run build
```

同时提交生成的 bundle、`build-info.json`、许可文件和锁文件；不提交 `node_modules/`。第三方许可见 `assets/vtk-viewer/THIRD_PARTY_LICENSES.txt`。

## 参考资料边界

仓库根目录的 Xiaodong HTML presentation 是截图 OCR 转写的参考资料。它及 `Resources/xiaodong-originals/` 中的截图不属于本目录的自动生成目标，不随功能、案例更新而改写。
