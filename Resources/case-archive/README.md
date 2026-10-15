# Case 留档（2026-10-12）

最终 PPT：C:/Users/Yuanyuan/Desktop/si/StressThermal.pptx。PPT 的图片等资源全部内嵌，无外部文件依赖。

## 顺序与入口

1. 01_Package_reliability.zip：两个阶段 thermal_bench.cmd → mechanics_bench.cmd；优先看 benchmark-golden/package 与 benchmark-golden/vm/formal-20261011-a，几何来源 original-case/dpack_struct_sis.cmd。原始 package 构建、热与热应力演示脚本保留在 original/performance-benchmark 和 from-archives。
2. 02_Submodelling.zip：global.cmd → unit-fine.cmd；优先看 benchmark-golden/pillar/inputs、vm/formal-pillar-recovered-a。geometry/unit-geometry 的生成方法在 original/flipchip-array-verification/prepare.py，完整原始几何输入为 vendor-original.cmd；材料、边界及细化脚本一并保留。
3. 03_Quasistatic_equilibrium.zip：quasistatic/frame-*/case.cmd，原说明中采用偶数帧；setup.py、refine.py、run-frames.sh 及渲染脚本保留。
4. 04_Linear_buckling.zip：linear-buckling/case.cmd；plate-buckling 是另一个变体，不应混为同一算例。
5. 05_Post_buckling.zip：post-buckling-supercritical/case.cmd 为原说明中的主要算例；post-buckling 为早期亚临界标定，arch-snap 为另一变体。
6. 06_Large_deformation.zip：geometric-off-v2/case.cmd、geometric-on-v2/case.cmd；成对比较，保留 setup-geometric.py 与比较说明。

## TDR 版本来源

不能把所有结果统一标成一个 binary。每个 ZIP 保留原始 identities.sha256 / binary.sha256、environment、运行日志与报告。README 列出输入和版本证据的路径。
- Flip-chip local-release 记录的 sinterconnect_run SHA256：a97a41e59aa4a5533fdc0645a5b11c837580fe11a9d12d5665adced18d931ea5。
- 早期 package/local replay manifest 记录 SHA256：05eb34c190aabd32b6d1e84b499bfbe8d70dff059420fdd415625d1a6ead3fd9；TDR_VERSION=16。这不是所有后续正式 benchmark 的版本，正式运行以各自 environment/日志为准。
- 力学动画原说明记录 vendor W-2024.09-SP1；后续本地 replay 与原动画不是一回事，应查对应 run 的 identities.sha256。没有逐次身份记录的输出，精确 binary 版本不能确认。

## 恢复方式与边界

ZIP 不含 TDR、图片、视频、二进制程序或大字段结果。先恢复输入与脚本，再配置历史 Linux 路径、求解器及授权，生成几何/网格，再执行 CMD，最后按需要重新后处理。这里没有重跑求解器，也不保证仅解压即可运行。

输入中的 mesh.tdr、assembled_bnd.tdr、unit_bnd.tdr、global_sis.tdr 等是需要重新生成的依赖，不能省略几何与前序求解阶段。按用户最终清理指示，benchmark-golden 和 converter-work 已从工作目录清理；本归档未做从零求解恢复验证。

完全相同的文件只保存一次；duplicate-path-map.json 记录原路径到实际保存路径。恢复原目录结构时按该映射复制回去。file-manifest.json 是保留文件的 SHA256 清单。

## Case 2 正式恢复运行的版本

formal-pillar-recovered-a/environment.json 记录 StressThermal SHA256 为 `6b14da5293db45767f9026e5599cc164e7ab654c8a091661610d8f76304f1781`，vendor 为 `6b5f30b801b08012dd846b339c4e4275502c5d1ee526420c4be315623d178464`。这是后续正式运行，区别于上文早期 local-release。恢复源码 .cpp/.h/.cmake 已补入 02_Submodelling.zip。记录 SHA 不等于保存了该求解器二进制。
