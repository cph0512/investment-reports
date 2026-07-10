from pathlib import Path
from datetime import datetime
import html

root = Path('/Users/cph/investment-reports')
outdir = root/'reports'/'port-air-cargo'/'2026-05'
outdir.mkdir(parents=True, exist_ok=True)
html_path = outdir/'report.html'
pdf_path = outdir/'report.pdf'

# Data compiled from upstream official-source research job on 2026-07-10.
research_dt = '2026-07-10 08:20 Asia/Taipei'
month = '2026-05'

def pct(x):
    return 'N/A' if x is None else f'{x:+.2f}%'

def fmt_num(x, decimals=0):
    if x is None: return 'N/A'
    return f'{x:,.{decimals}f}'

cards = [
    ('最新完整月份', '2026 年 5 月', '多數核心官方來源已公布至 5 月；6 月尚未形成跨來源完整月。'),
    ('台灣港口', '1,159,001 TEU', '全臺國際商港貨櫃裝卸量，MoM +5.94%、YoY -1.46%。'),
    ('桃園空運', '230,610.5 公噸', '表6總貨運量，MoM +4.21%、YoY +10.86%。'),
    ('POLA', '840,164.5 TEU', '5月總TEU，MoM -5.69%、YoY +17.24%。'),
    ('LAX', '200,341 tons', 'Air Cargo Total，MoM +3.55%、YoY +11.72%。'),
]

tw_ports = [
    ['全臺國際商港', '2026-05', '1,159,001.25', '+5.94%', '-1.46%', '2,252,974.75 / YoY -2.32%', '5,541,305.25 / YoY -2.29%', '臺灣港務公司'],
    ['基隆港群', '2026 1–5月累計', 'N/A', 'N/A', 'N/A', 'N/A', '670,716', '臺灣港務公司港群頁'],
    ['高雄港群', '2026 1–5月累計', 'N/A', 'N/A', 'N/A', 'N/A', '3,566,653', '臺灣港務公司港群頁'],
    ['臺北港', '2026 1–5月累計', 'N/A', 'N/A', 'N/A', 'N/A', '656,585', '臺灣港務公司港群頁'],
]

tpe_total = [
    ['總貨運量（表6）', '230,610.5', '+4.21%', '+10.86%', '451,900.4', '1,083,760.2', '公噸', '民航局統計月報表6'],
    ['進口／卸（表6）', '63,769.0', '+3.87%', '+17.68%', '125,161.7', '300,770.5', '公噸', '民航局統計月報表6'],
    ['出口／裝（表6）', '68,941.7', '+4.85%', '+17.88%', '134,696.2', '316,633.8', '公噸', '民航局統計月報表6'],
    ['轉口（表6）', '97,899.9', '+3.99%', '+2.68%', '192,042.6', '466,355.9', '公噸', '民航局統計月報表6'],
]

tpe_split = [
    ['表4合計（不含郵件）', '229,802.177', 'N/A', 'N/A', 'N/A', '1,079,750.166', '公噸', '民航局統計月報表4'],
    ['進口／卸', '63,355.904', 'N/A', 'N/A', 'N/A', '298,772.263', '公噸', '民航局統計月報表4'],
    ['出口／裝', '68,546.387', 'N/A', 'N/A', 'N/A', '314,621.986', '公噸', '民航局統計月報表4'],
    ['轉口', '97,899.886', 'N/A', 'N/A', 'N/A', '466,355.917', '公噸', '民航局統計月報表4'],
]

pola = [
    ['Loaded Imports', '449,370.25', '-2.27%', '+26.25%', '909,195.50 / YoY +14.34%', '2,145,334.00 / YoY +3.25%'],
    ['Loaded Exports', '107,656.75', '-15.71%', '-10.43%', '235,382.25 / YoY -5.31%', '588,441.50 / YoY -0.93%'],
    ['Empty Imports', '131.75', '+21.99%', '-68.15%', '239.75 / YoY -77.55%', '432.00 / YoY -81.27%'],
    ['Empty Exports', '283,005.75', '-6.66%', '+17.89%', '586,208.00 / YoY +13.92%', '1,385,661.00 / YoY -0.27%'],
    ['Total TEUs', '840,164.50', '-5.69%', '+17.24%', '1,731,025.50 / YoY +11.00%', '4,119,868.50 / YoY +1.39%'],
    ['POLB', '尚未取得', 'N/A', 'N/A', 'N/A', 'N/A'],
]

cal_air = [
    ['LAX', 'Air Cargo Total（Mail + Freight）', '200,341', '+3.55%', '+11.72%', '393,807', 'Fiscal YTD 2,142,602 / YoY +1.12%', 'tons', 'LAWA 官方 FTCOM PDF'],
    ['LAX', 'Freight', '195,008', 'N/A', 'N/A', 'N/A', 'N/A', 'tons', 'LAWA 官方 FTCOM PDF'],
    ['LAX', 'Mail', '5,333', 'N/A', 'N/A', 'N/A', 'N/A', 'tons', 'LAWA 官方 FTCOM PDF'],
    ['SFO', '貨運月報', '尚未穩定取得', 'N/A', 'N/A', 'N/A', 'N/A', 'tons', '官方頁未穩定解析'],
    ['SMF', '官方 reports', '已見6月PDF但未抽取', 'N/A', 'N/A', 'N/A', 'N/A', 'tons', 'Sacramento 官方 reports'],
]

key_changes = [
    '台灣港口貨櫃量 5 月月增但年減：全臺國際商港 115.9 萬 TEU，MoM +5.94%、YoY -1.46%，1–5 月累計 YoY -2.29%。',
    '桃園空運維持雙位數年增：表6總貨運量 230,610.5 公噸，MoM +4.21%、YoY +10.86%。',
    '桃園進出口貨是成長主軸：表6進口／卸與出口／裝分別 YoY +17.68%、+17.88%，轉口僅 +2.68%。',
    'POLA 5 月總TEU年增 +17.24%，但月減 -5.69%；進口 YoY +26.25%，出口 YoY -10.43%，顯示進口補貨強於出口。',
    'LAX 5 月 Air Cargo Total 200,341 tons，MoM +3.55%、YoY +11.72%，加州空運延續年增動能。',
    'POLB、SFO等來源本次未能穩定取得官方可驗證數字，正式判讀以已驗證來源為主。',
]

sources = [
    ['臺灣港務公司貨櫃裝卸量', 'https://www.twport.com.tw/statistics/ChartContainer?a=132&format=csv'],
    ['臺灣港務公司各港群營運實績', 'https://www.twport.com.tw/statistics/Articles?a=134'],
    ['交通部民航局民航統計月報', 'https://www.caa.gov.tw/Article.aspx?a=1091&lang=1'],
    ['民航局 115年5月（上）ODS', 'https://www.caa.gov.tw/FileAtt.ashx?lang=1&id=41032'],
    ['Port of Los Angeles Container Statistics', 'https://portoflosangeles.org/business/statistics/container-statistics'],
    ['Port of Los Angeles Historical TEU 2026', 'https://portoflosangeles.org/Business/statistics/Container-Statistics/Historical-TEU-Statistics-2026'],
    ['LAWA LAX Volume of Air Traffic', 'https://www.lawa.org/lawa-investor-relations/statistics-for-lax/volume-of-air-traffic'],
    ['LAX May 2026 FTCOM PDF', 'https://www.lawa.org/sites/lawa/files/2026-06/FTCOM%200526.pdf'],
    ['Sacramento Airport Reports', 'https://sacramento.aero/about/reports'],
]

def table(headers, rows):
    th = ''.join(f'<th>{html.escape(h)}</th>' for h in headers)
    body = ''
    for r in rows:
        body += '<tr>' + ''.join(f'<td>{html.escape(str(c))}</td>' for c in r) + '</tr>'
    return f'<table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>'

card_html = ''.join(f'<div class="card"><div class="k">{html.escape(k)}</div><div class="v">{html.escape(v)}</div><p>{html.escape(d)}</p></div>' for k,v,d in cards)
changes_html = ''.join(f'<li>{html.escape(x)}</li>' for x in key_changes)
sources_html = ''.join(f'<li><b>{html.escape(a)}</b><br><span>{html.escape(u)}</span></li>' for a,u in sources)

content = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><title>港口與空運貨量 2026-05</title>
<style>
@page {{ size: A4; margin: 14mm 12mm; }}
* {{ box-sizing: border-box; }}
body {{ font-family: "PingFang TC", "Heiti TC", "Noto Sans TC", "Microsoft JhengHei", sans-serif; color:#172033; margin:0; line-height:1.45; font-size:10.2px; }}
.cover {{ background:linear-gradient(135deg,#0f2a4a,#145ea8); color:white; padding:26px 28px; border-radius:18px; margin-bottom:14px; }}
h1 {{ margin:0 0 8px; font-size:28px; letter-spacing:.5px; }}
.subtitle {{ font-size:13px; opacity:.92; }}
.notice {{ margin-top:10px; padding:8px 10px; border-radius:9px; background:rgba(255,255,255,.12); font-size:10.5px; }}
.grid {{ display:grid; grid-template-columns: repeat(5, 1fr); gap:8px; margin:12px 0 16px; }}
.card {{ border:1px solid #dbe4f0; border-radius:12px; padding:10px; background:#f8fbff; min-height:92px; }}
.card .k {{ color:#5a6b82; font-size:10px; }}
.card .v {{ color:#0f3f75; font-size:16px; font-weight:700; margin:4px 0; }}
.card p {{ margin:0; color:#3d4b5f; font-size:9.2px; }}
h2 {{ font-size:16px; color:#0f2a4a; border-left:5px solid #1a73e8; padding-left:8px; margin:18px 0 8px; break-after:avoid; }}
h3 {{ font-size:12px; color:#243b55; margin:10px 0 6px; }}
table {{ width:100%; border-collapse:collapse; margin:6px 0 10px; break-inside:auto; }}
th {{ background:#153e6f; color:white; font-weight:600; padding:6px 5px; font-size:8.8px; text-align:left; }}
td {{ border-bottom:1px solid #e2e8f0; padding:5px; vertical-align:top; font-size:8.7px; }}
tr:nth-child(even) td {{ background:#f8fafc; }}
ul {{ margin:6px 0 10px 18px; padding:0; }}
li {{ margin:4px 0; }}
.note {{ background:#fff8e6; border:1px solid #f1d18a; border-radius:10px; padding:10px 12px; margin:10px 0; }}
.sources li span {{ color:#345; font-size:8.5px; word-break:break-all; }}
.footer {{ margin-top:16px; color:#667085; font-size:8.5px; border-top:1px solid #e5e7eb; padding-top:8px; }}
.badge {{ display:inline-block; padding:2px 7px; border-radius:99px; background:#e7f0ff; color:#145ea8; font-weight:700; }}
</style></head><body>
<section class="cover">
  <h1>港口與空運貨量月報</h1>
  <div class="subtitle">資料月份：2026 年 5 月｜月／季／年累計｜YoY / MoM｜研究時間：{research_dt}</div>
  <div class="notice">⚠️ Skill(s) not found and skipped: logistics-volume-official-stats。本文僅使用官方資料或明確標示官方來源；未穩定取得者列為缺口，不以非官方數字補值。</div>
</section>
<div class="grid">{card_html}</div>
<h2>重點結論</h2><ol>{changes_html}</ol>
<div class="note"><b>最新完整月份判斷：</b>截至 2026-07-10 08:20 Asia/Taipei，臺灣港務、民航局／桃園機場、POLA、LAX 可取得 2026 年 5 月官方完整月資料；2026 年 6 月多數核心來源尚未完整公布或未穩定取得，因此本報告採 2026 年 5 月為最新完整月份。</div>
<h2>台灣港口貨櫃裝卸量（單位：TEU）</h2>
{table(['項目','月份/期間','月值','MoM','YoY','QTD','YTD','來源'], tw_ports)}
<p>說明：基隆港群、高雄港群、臺北港官方港群頁本次穩定取得 115 年 1–5 月累計值；未取得逐月可驗證序列，因此月、MoM、YoY、QTD 標示 N/A。</p>
<h2>桃園機場空運總量：表6（單位：公噸）</h2>
{table(['項目','2026-05','MoM','YoY','QTD','YTD','單位','來源'], tpe_total)}
<h2>桃園機場國際及兩岸貨物分拆：表4（單位：公噸）</h2>
{table(['項目','2026-05','MoM','YoY','QTD','YTD','單位','來源'], tpe_split)}
<p>說明：表4口徑為國際及兩岸航線貨物運量，不含郵件；表6為桃園機場運輸概況貨運噸數，含郵件及貨物，兩者不可直接混同。</p>
<h2>美國港口：POLA / POLB（單位：TEU）</h2>
{table(['項目','2026-05','MoM','YoY','QTD','YTD'], pola)}
<p>POLB：官方統計頁本次讀取逾時或被追蹤資源阻擋，未取得穩定可驗證數據；未用非官方資料補值。</p>
<h2>加州主要機場空運</h2>
{table(['機場','口徑','2026-05','MoM','YoY','QTD','YTD','單位','來源'], cal_air)}
<p>說明：LAX PDF 使用 tons；LAWA 同頁提供 Fiscal YTD（Jul 2025–May 2026），不是 calendar YTD，避免與其他來源直接相加。</p>
<h2>資料限制與缺口</h2>
<ul>
<li>POLB 官方統計頁／新聞稿本次未穩定取得可解析官方數字，列為缺口。</li>
<li>SFO 官方統計頁本次未穩定取得貨運月報數字；SMF 已見官方月報 PDF 連結但未完成貨運表格抽取。</li>
<li>OAK、ONT、SAN 未確認可穩定取得官方貨運月序列，未納入。</li>
<li>不同來源單位與口徑不同：TEU、公噸、tons、含郵件／不含郵件、calendar YTD／fiscal YTD 不可直接相加。</li>
<li>ROC 115 年已換算為西元 2026 年。</li>
</ul>
<h2>官方來源 URL</h2><ul class="sources">{sources_html}</ul>
<div class="footer">產製：每月港口／空運貨量主報告 agent。所有百分比公式：(本期 - 比較期) / 比較期；比較期為 0 或缺資料時標 N/A。</div>
</body></html>'''
html_path.write_text(content, encoding='utf-8')
print(html_path)
print(pdf_path)
