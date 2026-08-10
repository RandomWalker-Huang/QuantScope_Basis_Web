# QuantScope Basis Web

QuantScope 股指期货升贴水研究网站，从 `QuantScope_RQAlpha v2.2.4-r13` 的 07 升贴水分析模块独立发布。

网站采用单文件静态结构：图表运行时、交互程序和处理后的行情结果均封装在 `index.html` 中。部署到 GitHub Pages 后，无需启动 QuantScope、Python、RQData 或本地服务即可访问。

## 当前数据

- 数据区间：2023-01-03 至 2026-07-06
- 品种：IM、IC、IH、IF
- 每个品种：847 个有效交易日
- 保留字段：日期、指数价格、期货价格、实际合约、到期日、剩余期限
- 可交互口径：单一 S/F、四期限同时对比、基差对比；支持数值差、年化、对数及年化对数口径
- 图表功能：悬停、缩放、拖动、换月断点、换月标记、构造明细、一年窗口分位数

## 未发布内容

本仓库不包含 QuantScope 完整源码、Python 后台、策略代码、RQData 账号、密码、Token、本地数据库、缓存文件或原始全量行情文件。

## 发布

完整步骤参见 [DEPLOY_TO_GITHUB.md](DEPLOY_TO_GITHUB.md)。最简流程为：

1. 在 GitHub 创建仓库 `QuantScope_Basis_Web`；
2. 上传本目录全部内容；
3. 在 `Settings → Pages` 中选择 `Deploy from a branch`；
4. 选择 `main` 和 `/ (root)` 后保存。

发布前建议运行：

```powershell
py -3 tools\validate_public_site.py index.html
```

## 更新数据

在本地 r13 平台重新运行“独立升贴水分析”，点击“导出升贴水 HTML”，然后使用：

```powershell
powershell -ExecutionPolicy Bypass -File tools\update_site.ps1 -HtmlPath "C:\下载目录\QuantScope_Basis_Interactive_日期时间.html"
```

脚本会先验证新报告，再替换 `index.html`。之后提交并推送到 GitHub，Pages 会自动更新。

## 权限说明

GitHub Pages 免费版网站是公开网页。仓库外部用户不能直接修改本仓库，但网页内容可被访问者查看。若需要仅限指定同事访问，应在固定域名前增加身份访问控制。

## 第三方组件

图表使用 Apache License 2.0 授权的 Apache ECharts，许可文本见 `ECHARTS_LICENSE.txt`。

