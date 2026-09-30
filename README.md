# 渡海 · 中国品牌出海情报

一个为产品经理设计的中国品牌全球化情报站。它不追求堆新闻，而是把公开信息整理成「发生了什么、为什么重要、产品经理能验证什么」。

## 网站提供什么

- 覆盖品牌扩张、产品与包装、营销内容、渠道电商、物流履约、支付金融、政策合规、市场消费八个情报域。
- 每条信号同时展示业务价值分与来源可信度，明确区分机会、风险和混合信号。
- 支持按关键词、市场、时间、情报域与影响类型筛选。
- 首页直接给出 PM Takeaway 和下一步验证动作，适合每天 5–10 分钟扫描。
- 保留原文链接；站内摘要只做索引，不转载全文。

## 自动回查节奏

工作流按 `Asia/Shanghai` 时区运行：

| 时间 | 回查范围 | 目的 |
| --- | --- | --- |
| 每天 11:00 | 最近 3 个自然日 | 捕获新事件与迟到稿件 |
| 每周日 11:00 | 当月 1 日至当天 | 补齐漏抓、更新与跨来源证据 |
| 每月 1 日 11:00 | 完整上月 | 固化月度复盘 |

`data/state/schedule.json` 记录最后完成日期。若 GitHub 定时任务延迟或漏跑，下一次会补算遗漏日期；自动补跑最多 62 天。

## 数据原则

来源按可信度分层：

1. A：监管机构、交易所、公司财务披露。
2. B：公司官网、平台公告、产品更新。
3. C：通讯社、行业媒体与新闻发现源。
4. D：社交与论坛线索（默认不自动发布）。

自动采集只接入公开 RSS/API。监管与官方来源作为事实依据；Google News 与 GDELT 只作为发现层。网站不会自动抓取禁止批量查询的服务，也不会保存整篇受版权保护的正文。

## 本地运行

```bash
npm install
npm run build:pages
```

校验数据和日期逻辑：

```bash
python3 -m unittest discover -s tests -p "test_*.py"
python3 scripts/validate_data.py --data data/intel.json
```

手动执行一次日常核查：

```bash
python3 scripts/plan_windows.py \
  --mode daily \
  --state data/state/schedule.json \
  --output work/plan.json

python3 scripts/collect.py \
  --plan work/plan.json \
  --sources config/sources.json \
  --data data/intel.json \
  --state data/state/schedule.json
```

也可以在 GitHub 的 **Actions → Collect and publish intelligence → Run workflow** 中选择 `daily`、`weekly` 或 `monthly` 手动回查。

## 目录

```text
app/                    Sites 版本入口与元数据
components/radar-app.tsx  情报站主界面
config/sources.json     公开数据源配置
data/intel.json         网站读取的标准化情报
data/state/             运行账本
scripts/                日期规划、采集、清洗与校验
tests/                  核心规则测试
.github/workflows/      每日采集与 GitHub Pages 发布
```

## 边界

网站内容来自公开信息并包含编辑判断，不构成投资、法律或经营建议。重要决策请回到原始文件，并由对应领域的专业人士复核。

## License

[MIT](LICENSE)
