# 公开数据结构

网站数据封装在 `index.html` 的 `basis-report-data` JSON 节点中。

## 产品信息

- `symbol`：IM、IC、IH、IF
- `future_name`：股指期货名称
- `spot_code`、`spot_name`：对应指数
- `tenors`：近月、次近月、次远月、最远月

## 每日处理结果

- `date`：交易日
- `spot_price`：对应指数价格
- `contracts`：当日按期限排序选出的实际期货合约
- `contract`：合约代码
- `price`：期货价格
- `expiry_date`：到期日
- `days_to_expiry`：剩余自然日

浏览器基于以上处理后价格面板计算直接价差、年化升贴水、对数升贴水、年化对数升贴水、期限对比、双基差差额和一年窗口分位数。

公开文件不包含开高低收全量面板、成交量、持仓量、买卖盘、结算价、数据库主键、数据源凭证或本地缓存结构。

