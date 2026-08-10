# GitHub Pages 全流程

## 1. 创建仓库

1. 登录 GitHub。
2. 点击右上角 `+`，选择 `New repository`。
3. Repository name 填写 `QuantScope_Basis_Web`。
4. Description 可填写：`QuantScope 股指期货升贴水研究与交互式可视化网站`。
5. 免费使用 GitHub Pages 时选择 `Public`。
6. 不勾选自动创建 README、`.gitignore` 或 License，避免与本目录文件冲突。
7. 点击 `Create repository`。

## 2. 发布前检查

在本目录打开 PowerShell：

```powershell
py -3 tools\validate_public_site.py index.html
```

只有看到“检查通过”后再上传。检查会确认：

- 页面是完整的自包含交互 HTML；
- 处理后的数据结构可读取；
- 四个股指期货品种及其序列存在；
- 没有外部脚本、外部样式、本机地址或 API 地址；
- 数据中没有密码、密钥、Token 或凭证字段；
- 没有 OHLC、成交量、持仓量等原始全量行情字段。

## 3. 首次上传

### 网页方式

1. 进入新建仓库。
2. 点击 `uploading an existing file` 或 `Add file → Upload files`。
3. 将本目录中的所有文件和文件夹拖入上传区域。
4. Commit message 填写 `Initial QuantScope Basis Web release`。
5. 点击 `Commit changes`。

必须确认 `index.html` 位于仓库根目录，不能变成 `QuantScope_Basis_Web/index.html`。

### Git 命令方式

在本目录打开 PowerShell，将 `你的GitHub用户名` 替换为实际用户名：

```powershell
git init
git branch -M main
git add index.html .nojekyll .gitignore README.md DEPLOY_TO_GITHUB.md SECURITY.md ECHARTS_LICENSE.txt PUBLIC_DATA_SCHEMA.md CHANGELOG.md VERSION tools 发布前检查.bat 更新网站.bat
git commit -m "Initial QuantScope Basis Web release"
git remote add origin https://github.com/你的GitHub用户名/QuantScope_Basis_Web.git
git push -u origin main
```

## 4. 开启 GitHub Pages

1. 打开仓库的 `Settings`。
2. 左侧点击 `Pages`。
3. `Source` 选择 `Deploy from a branch`。
4. Branch 选择 `main`。
5. Folder 选择 `/ (root)`。
6. 点击 `Save`。

通常等待 1—10 分钟后，页面会显示网站地址：

```text
https://你的GitHub用户名.github.io/QuantScope_Basis_Web/
```

## 5. 检查线上网站

打开网站后依次检查：

1. IM、IC、IH、IF 是否都能切换；
2. 单一构造、四期限和基差对比是否正常；
3. 构造方法、S/F 来源和计算形式是否可切换；
4. 图例、换月标记、构造明细、悬停卡片是否可交互；
5. 时间轴是否可缩放和拖动；
6. 合约构造区间和每日计算明细是否可展开；
7. 浏览器 `F12 → Console` 中是否没有红色错误。

## 6. 后续更新

1. 在本地 QuantScope r13 中运行最新升贴水分析；
2. 点击“导出升贴水 HTML”；
3. 用更新脚本验证并替换网站首页：

```powershell
powershell -ExecutionPolicy Bypass -File tools\update_site.ps1 -HtmlPath "导出的HTML完整路径"
```

4. 再运行一次检查：

```powershell
py -3 tools\validate_public_site.py index.html
```

5. 提交更新：

```powershell
git add index.html
git commit -m "Update processed basis data"
git push
```

GitHub Pages 会在提交后自动重新部署，不需要一直打开本地运行窗口。

## 7. 不要上传

- `QuantScope_RQAlpha_v*.zip`
- `.venv`、`instance`、`cache`、`market_cache`
- `.env`、账号配置、RQData凭证
- SQLite、CSV、Parquet、Pickle原始文件
- 回测策略、后台代码和任务日志
