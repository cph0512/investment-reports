from pathlib import Path
import html
from datetime import datetime

ROOT = Path('/Users/cph/investment-reports')
OUT = ROOT / 'reports' / 'port-air-cargo' / '2026-08'
OUT.mkdir(parents=True, exist_ok=True)
HTML = OUT / 'report.html'

SOURCES = {
    'kel': ('TWPORT 基隆港', 'https://kl.twport.com.tw/statistics/ChartContainer?a=730&format=csv'),
    'khh': ('TWPORT 高雄港', 'https://kh.twport.com.tw/statistics/ChartContainer?a=999&format=csv'),
    'tpe': ('TWPORT 臺北港', 'https://kl.twport.com.tw/statistics/ChartContainer?a=736&format=csv'),
    'caa': ('CAA 民航統計月報', 'https://www.caa.gov.tw/StatisticsYearMonthFile.aspx?a=1091&lang=1'),
    'pola26': ('POLA 2026 統計', 'https://portoflosangeles.org/business/statistics/container-statistics/historical-teu-statistics-2026'),
    'pola25': ('POLA 2025 統計', 'https://portoflosangeles.org/business/statistics/container-statistics/historical-teu-statistics-2025'),
    'polb': ('POLB 2026年8月發布', 'https://polb.com/port-info/news-and-press/long-beach-reports-best-august-on-record-09-10-2026/'),
    'polbtable': ('POLB 官方月表', 'https://thehelm.polb.com/stellar_custom_table/table100'),
    'lax': ('LAWA LAX 貨量月報', 'https://www.lawa.org/lawa-investor-relations/statistics-for-lax/volume-of-air-traffic'),
    'sfo': ('SFO 2026年8月摘要', 'https://www.flysfo.com/sites/default/files/2026-10/Aug%202026%20and%20CYTD%20SFO%20Air%20Traffic%20Summary.pdf'),
    'smf': ('Sacramento 2026年8月月報', 'https://flysmf.gov/assets/august-2026-web-report-revised.pdf'),
}


def g(now, then):
    return None if then in (None, 0) or now is None else (now - then) / then * 100


def n(v, d=0):
    return 'N/A' if v is None else f'{v:,.{d}f}'


def p(v):
    if v is None:
        return 'N/A'
    return f"{'+' if v >= 0 else '−'}{abs(v):.2f}%"


def source(key):
    label, url = SOURCES[key]
    return f'<a href="{html.escape(url, quote=True)}">{html.escape(label)}</a>'


def cell(v, yoy=None, d=0, strong=False):
    text = n(v, d)
    if strong:
        text = f'<b>{text}</b>'
    if yoy is not None:
        text += f"<br><span class='sub'>YoY {p(yoy)}</span>"
    return text


def tbl(headers, rows, classes=''):
    head = ''.join(f'<th>{h}</th>' for h in headers)
    body = ''.join('<tr>' + ''.join(f'<td>{x}</td>' for x in row) + '</tr>' for row in rows)
    return f'<table class="{classes}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


# Official TWPORT CSV snapshots; tuple is total, inbound containers, outbound containers.
ports = {
    '基隆港': {
        'source': 'kel',
        '2025': [(128813.75,65700.75,63113), (104992.75,54443,50549.75), (136081.75,73179.25,62902.5), (139028.75,74049.75,64979), (141255.5,73639,67616.5), (136769.5,72155.5,64614), (135946.75,72840.5,63106.25), (139112,74251.5,64860.5)],
        '2026': [(146288.5,77232.5,69056), (107376.25,54725.75,52650.5), (132320.5,71978.25,60342.25), (140271.5,75813.75,64457.75), (144459.5,74473.25,69986.25), (137019,73564.75,63454.25), (133564.25,71663,61901.25), (134859.5,71998.5,62861)],
    },
    '高雄港': {
        'source': 'khh',
        '2025': [(780706.5,384941.25,395765.25), (693319.75,341070.75,352249), (791883.25,399838.25,392045), (736143,367257,368886), (760686.5,382245.5,378441), (754069,373178,380891), (731295.5,361265.5,370030), (762628,378047,384581)],
        '2026': [(754113.25,371286.5,382826.75), (616873,297258,319615), (760028.75,388974.75,371054), (697903,345271.75,352631.25), (737735,371738.75,365996.25), (708466,352935.25,355530.75), (750947,370836.75,380110.25), (712521.5,357924.25,354597.25)],
    },
    '臺北港': {
        'source': 'tpe',
        '2025': [(117935,54489,63446), (100157.25,48789.5,51367.75), (131944.25,65495,66449.25), (120731.25,59963.5,60767.75), (130724.75,65127.75,65597), (129791.5,63536,66255.5), (123743.75,59354,64389.75), (117768.5,57409.25,60359.25)],
        '2026': [(137826.25,66206.25,71620), (108763.25,50832.5,57930.75), (147455.5,70758.5,76697), (126127.75,60771.25,65356.5), (136412.75,66934.5,69478.25), (133576.5,66574.5,67002), (130918.25,62903.25,68015), (134633.75,64494.25,70139.5)],
    },
}
port_rows = []
for name, d in ports.items():
    for metric_index, metric in enumerate(['總計', '進港櫃', '出港櫃']):
        current = d['2026'][7][metric_index]
        previous = d['2026'][6][metric_index]
        prior = d['2025'][7][metric_index]
        qtd = sum(x[metric_index] for x in d['2026'][6:8])
        qtd_prior = sum(x[metric_index] for x in d['2025'][6:8])
        ytd = sum(x[metric_index] for x in d['2026'])
        ytd_prior = sum(x[metric_index] for x in d['2025'])
        port_rows.append([
            f'<b>{name}</b>' if metric_index == 0 else '',
            f'<b>{metric}</b>' if metric_index == 0 else metric,
            cell(current, None, 2, metric_index == 0),
            p(g(current, previous)),
            p(g(current, prior)),
            cell(qtd, g(qtd, qtd_prior), 2),
            cell(ytd, g(ytd, ytd_prior), 2),
            source(d['source']),
        ])

# CAA Table 6: total air cargo includes freight and mail, metric tonnes.
t6 = {'current': 224625.055, 'previous': 232233.958, 'prior': 215889.322, 'qtd': 456859.013, 'qtd_prior': 439028.759, 'ytd': 1775531.839, 'ytd_prior': 1620803.677}
t6_rows = [[
    '<b>總貨運量（貨物＋郵件）</b>', cell(t6['current'], None, 3, True), p(g(t6['current'],t6['previous'])), p(g(t6['current'],t6['prior'])), cell(t6['qtd'],g(t6['qtd'],t6['qtd_prior']),3), cell(t6['ytd'],g(t6['ytd'],t6['ytd_prior']),3), source('caa')
]]
# CAA Table 4: international/cross-strait freight only; source values kg converted to metric tonnes.
ty_split = [
    ('進口／卸', 64407.981, 68912.620, 58726.421, 133320.601, 120749.706, 497543.225, 435303.419),
    ('出口／裝', 67868.791, 71261.742, 62643.364, 139130.533, 125059.759, 520605.280, 441778.394),
    ('轉口', 91567.688, 91254.853, 93652.058, 182822.541, 191472.940, 751024.542, 736558.546),
    ('表4合計', 223844.460, 231429.215, 215021.843, 455273.675, 437282.405, 1769173.047, 1613640.359),
]
ty_rows = []
for label, cur, prev, prior, qtd, qtd_prior, ytd, ytd_prior in ty_split:
    bold = label == '表4合計'
    ty_rows.append([
        f'<b>{label}</b>' if bold else label, cell(cur,None,3,bold), p(g(cur,prev)), p(g(cur,prior)), cell(qtd,g(qtd,qtd_prior),3), cell(ytd,g(ytd,ytd_prior),3), source('caa')
    ])

# POLA: tuple loaded imports, empty imports, loaded exports, empty exports, all official monthly table values.
pola_2026 = [
 (421593.75,115,104297,285994.5),(433812.25,17.25,116633.25,273860.5),(380732.5,60,132129,239598),(459825.25,108,127725.5,303202.25),(449370.25,131.75,107656.75,283005.75),(530557.5,201,126365.25,345610.25),(499551.5,446,111775.5,348691.25),(500301.5,358,115561.25,339685.75),(545695.6,1487.7,125750.75,369718.25)
]
pola_2025 = [
 (483831.25,144,113270.75,326999),(413236.25,33,109156.25,278972.5),(385530.5,1062.25,122974.75,268836.2),(439230,654.15,128394,274528.5),(355950.25,413.6,120196,240058.75),(470449.75,148,126144.25,295597.75),(543727.8,503,121507,354099.5),(504514.25,456.65,127378.75,326005.5),(460043.75,276,114693,308040.5)
]

def pola_norm(x): return (x[0], x[2], x[1], x[3])

def make_port_rows(current, prior, labels, source_key, current_month, quarter_start, total_override=None):
    current = [tuple(x) for x in current]
    prior = [tuple(x) for x in prior]
    rows = []
    for i, label in enumerate(labels):
        now = current[-1][i]
        prev = current[-2][i]
        old = prior[-1][i]
        q = sum(x[i] for x in current[quarter_start:])
        qold = sum(x[i] for x in prior[quarter_start:])
        y = sum(x[i] for x in current)
        yold = sum(x[i] for x in prior)
        rows.append([label, cell(now,None,2,label=='總計'),p(g(now,prev)),p(g(now,old)),cell(q,g(q,qold),2),cell(y,g(y,yold),2),source(source_key)])
    return rows

pola_cur = [pola_norm(x) for x in pola_2026]
pola_old = [pola_norm(x) for x in pola_2025]
for collection in (pola_cur, pola_old):
    for x in collection:
        pass
pola_extended_cur = [(x[0],x[1],x[2],x[3],x[2]+x[3],sum(x)) for x in pola_cur]
pola_extended_old = [(x[0],x[1],x[2],x[3],x[2]+x[3],sum(x)) for x in pola_old]
pola_rows = make_port_rows(pola_extended_cur, pola_extended_old, ['Loaded Imports','Loaded Exports','Empty Imports','Empty Exports','Empty Total','總計'], 'pola26', '2026-09', 6)

# POLB: 2026 Jul/Aug components are confirmed by official releases; exact total uses release aggregate.
polb_components_2026 = [
 (409818,99478,16273,322197),(368060,97422,15618,286426),(374412,104554,14794,281176),(389835,118901,17553,291704),(418851,109168,16094,297918),(387025,86446,14476,291384),(467461,104843,14399,341806),(456100,99754,17375,346763)
]
polb_components_2025 = [
 (471649,98655,13225,369205),(368669,90026,14397,292293),(380562,104063,17213,315619),(419828,93842,17368,336456),(299116,82149,15424,242471),(348681,87627,13098,254997),(468081,91328,13474,371350),(440318,95960,15007,350560)
]
polb_totals_2026 = [847765,767525,774935,817992,842030,779331,928508,919992]
polb_totals_2025 = [952733,765385,817457,867493,639160,704403,944232,901846]
polb_rows = []
polb_labels = ['Imports（Loaded）','Exports（Loaded）','Empty Total','總計']
for idx, label in enumerate(polb_labels):
    if idx == 0:
        values = [x[0] for x in polb_components_2026]; old = [x[0] for x in polb_components_2025]
    elif idx == 1:
        values = [x[1] for x in polb_components_2026]; old = [x[1] for x in polb_components_2025]
    elif idx == 2:
        values = [x[2]+x[3] for x in polb_components_2026]; old = [x[2]+x[3] for x in polb_components_2025]
    else:
        values = polb_totals_2026; old = polb_totals_2025
    cur, prev, prior = values[-1], values[-2], old[-1]
    qtd, qtd_prior = sum(values[6:]), sum(old[6:])
    ytd, ytd_prior = sum(values), sum(old)
    polb_rows.append([
        f'<b>{label}</b>' if idx == 3 else label, cell(cur,None,0,idx==3),p(g(cur,prev)),p(g(cur,prior)),cell(qtd,g(qtd,qtd_prior),0),cell(ytd,g(ytd,ytd_prior),0),source('polb')
    ])

# Major California airport traffic: each source retains its published unit and coverage.
airport_data = [
    ('LAX','2026-08','貨物＋郵件／LAWA tons',202357,207272,188761,409629,369614,1554542,1441696,'lax'),
    ('SFO','2026-08','貨物＋郵件／公噸',46576,47501,46021,94077,92592,353133,357710,'sfo'),
    ('SMF','2026-08','Freight＋Airmail／short tons',8910.0,8331.414,9525.481,17241.414,19163.624,76325.101,68144.722,'smf'),
]
airport_rows = []
for airport, month, unit, cur, prev, prior, qtd, qtd_prior, ytd, ytd_prior, skey in airport_data:
    d = 1 if airport == 'SMF' else 0
    airport_rows.append([airport,month,unit,cell(cur,None,d,True),p(g(cur,prev)),p(g(cur,prior)),cell(qtd,g(qtd,qtd_prior),d),cell(ytd,g(ytd,ytd_prior),d),source(skey)])

# Key figures used in narrative, calculated from the same values rendered below.
khh_aug = ports['高雄港']['2026'][7][0]
khh_mom = g(khh_aug, ports['高雄港']['2026'][6][0])
khh_yoy = g(khh_aug, ports['高雄港']['2025'][7][0])
tpe_aug = ports['臺北港']['2026'][7][0]
tpe_yoy = g(tpe_aug, ports['臺北港']['2025'][7][0])
kel_aug = ports['基隆港']['2026'][7][0]
kel_yoy = g(kel_aug, ports['基隆港']['2025'][7][0])
pola_total = pola_extended_cur[-1][-1]
pola_mom = g(pola_total, pola_extended_cur[-2][-1])
pola_yoy = g(pola_total, pola_extended_old[-1][-1])
polb_total = polb_totals_2026[-1]
polb_mom = g(polb_total, polb_totals_2026[-2])
polb_yoy = g(polb_total, polb_totals_2025[-1])

html_doc = f'''<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8"><title>港口與空運貨量｜2026年8月</title>
<style>
@page {{ size:A4; margin:10mm 10mm 12mm; }}
* {{ box-sizing:border-box; }} html {{ -webkit-print-color-adjust:exact; print-color-adjust:exact; }}
body {{ margin:0; color:#1f2937; font-family:"PingFang TC","Heiti TC","Noto Sans TC","Microsoft JhengHei",sans-serif; font-size:9px; line-height:1.45; }}
a {{ color:#146b88; text-decoration:none; border-bottom:1px solid #bddbe5; }}
.hero {{ min-height:222px; padding:25px 27px; border-radius:20px; color:#fff; background:linear-gradient(133deg,#092b3d 0%,#0c5a6e 59%,#25928b 100%); position:relative; overflow:hidden; }}
.hero:after {{ content:""; position:absolute; width:230px; height:230px; border:39px solid rgba(255,255,255,.09); border-radius:50%; right:-59px; top:-78px; }}
.eyebrow {{ letter-spacing:2px; opacity:.77; font-size:8.5px; }} h1 {{ margin:10px 0 7px; font-size:27px; letter-spacing:.5px; }}
.subtitle {{ font-size:12px; opacity:.95; }} .cover-note {{ margin-top:31px; border-left:3px solid #9bf2db; padding-left:10px; width:84%; font-size:9px; opacity:.93; }}
.cards {{ display:grid; grid-template-columns:repeat(4,1fr); gap:8px; margin:10px 0 12px; }} .card {{ border:1px solid #d7e6ea; border-radius:11px; background:#f6fafb; padding:8px 10px; min-height:78px; }}
.card .k {{ color:#68788a; font-size:8px; }} .card .v {{ color:#0d5b70; font-size:14px; font-weight:700; margin:3px 0; }} .card .d {{ color:#506173; font-size:7.8px; }}
h2 {{ margin:14px 0 7px; color:#103f52; font-size:14px; border-left:4px solid #2aa79a; padding-left:7px; break-after:avoid; }} h3 {{ margin:9px 0 5px; color:#34586a; font-size:10.5px; break-after:avoid; }}
.lead {{ background:#edf8f6; border:1px solid #cbe8e3; border-radius:11px; padding:8px 12px; margin:7px 0; }} .lead ol {{ margin:0 0 0 17px; padding:0; }} .lead li {{ margin:3px 0; }}
.note {{ background:#fff7e8; border:1px solid #efd89f; border-radius:9px; padding:7px 9px; margin:7px 0; }} .sub,.muted {{ color:#68788a; font-size:7.1px; }}
table {{ width:100%; border-collapse:collapse; margin:5px 0 8px; break-inside:auto; }} thead {{ display:table-header-group; }} tr {{ break-inside:avoid; }} th {{ background:#17495d; color:#fff; text-align:left; padding:4px 4px; font-size:7.4px; font-weight:600; }} td {{ padding:4px 4px; border-bottom:1px solid #dde7eb; vertical-align:top; font-size:7.55px; }} tr:nth-child(even) td {{ background:#f7fafb; }}
.sources {{ columns:2; column-gap:22px; margin:5px 0 0 17px; padding:0; }} .sources li {{ break-inside:avoid; margin:3px 0; }} .page-break {{ break-before:page; }} .footer {{ margin-top:11px; border-top:1px solid #dce5e9; padding-top:7px; color:#6a7885; font-size:7.2px; }}
</style></head><body>
<section class="hero"><div class="eyebrow">MONTHLY LOGISTICS VOLUME MONITOR</div><h1>港口與空運貨量月報</h1><div class="subtitle">2026 年 8 月基準｜第三季截至目前｜YoY / MoM</div><div class="cover-note">研究日：2026-10-10（Asia/Taipei）<br>最新共同完整月份為 2026 年 8 月；Port of Los Angeles 已公布至 9 月，於美國港口段另列。所有數字採官方統計或官方月報；缺口不以非官方資料補值。</div></section>
<div class="cards"><div class="card"><div class="k">桃園機場 8月總貨運</div><div class="v">{n(t6['current'],1)}</div><div class="d">公噸｜YoY {p(g(t6['current'],t6['prior']))}｜MoM {p(g(t6['current'],t6['previous']))}</div></div><div class="card"><div class="k">高雄港 8月總計</div><div class="v">{n(khh_aug,0)}</div><div class="d">TEU｜YoY {p(khh_yoy)}｜MoM {p(khh_mom)}</div></div><div class="card"><div class="k">POLA 9月總計</div><div class="v">{n(pola_total,0)}</div><div class="d">TEU｜YoY {p(pola_yoy)}｜MoM {p(pola_mom)}</div></div><div class="card"><div class="k">POLB 8月總計</div><div class="v">{n(polb_total,0)}</div><div class="d">TEU｜YoY {p(polb_yoy)}｜MoM {p(polb_mom)}</div></div></div>
<h2>重點結論</h2><div class="lead"><ol>
<li><b>桃園空運 8 月回落但仍年增：</b>表6總貨運量 {n(t6['current'],1)} 公噸，MoM {p(g(t6['current'],t6['previous']))}、YoY {p(g(t6['current'],t6['prior']))}；1–8 月累計 YoY {p(g(t6['ytd'],t6['ytd_prior']))}。</li>
<li><b>桃園貨流呈現進出口增、轉口降：</b>表4進口 YoY {p(g(64407.981,58726.421))}、出口 {p(g(67868.791,62643.364))}，轉口 {p(g(91567.688,93652.058))}；不含郵件。</li>
<li><b>臺灣港口 8 月同步放緩：</b>高雄港 {n(khh_aug,0)} TEU，MoM {p(khh_mom)}、YoY {p(khh_yoy)}；臺北港 YoY {p(tpe_yoy)}，基隆港 YoY {p(kel_yoy)}。</li>
<li><b>POLA 9 月明顯反彈：</b>總量 {n(pola_total,0)} TEU，MoM {p(pola_mom)}、YoY {p(pola_yoy)}；POLB 可核對最新為 8 月，總量 {n(polb_total,0)} TEU、YoY {p(polb_yoy)}。</li>
<li><b>加州空運恢復不均：</b>LAX 8月貨物＋郵件 YoY {p(g(202357,188761))}；SFO YoY {p(g(46576,46021))}；SMF（Freight＋Airmail）YoY {p(g(8910.0,9525.481))}。</li>
</ol></div>
<div class="note"><b>判讀與風險：</b>臺灣海空運 8 月的月減不等於需求趨勢反轉，受季節、出貨排程與天數影響。南加州兩港資料月份不同，不能把 POLA 9 月與 POLB 8 月直接相減或合併判讀。TEU、公噸、LAWA tons、short tons 亦不可相加。</div>
<h2>臺灣主要港口｜貨櫃裝卸量（TEU，2026-08）</h2>{tbl(['港口','項目','最新月','MoM','YoY','Q3截至8月','1–8月／YTD','官方來源'], port_rows)}
<p class="muted">進港櫃／出港櫃為港務公司裝卸方向，不等同海關進口／出口。Q3截至8月＝7–8月。</p>
<h2>桃園機場空運總量｜CAA 表6（公噸，2026-08）</h2>{tbl(['項目','最新月','MoM','YoY','Q3截至8月','1–8月／YTD','官方來源'], t6_rows)}
<p class="muted">表6按 ACI 定義含貨物與郵件、不含行李；不可與表4的純 freight 拆項直接勾稽。</p>
<h2>桃園機場進口／出口／轉口｜CAA 表4（公噸，2026-08）</h2>{tbl(['項目','最新月','MoM','YoY','Q3截至8月','1–8月／YTD','官方來源'], ty_rows)}
<div class="note">表4僅含國際及兩岸航線 freight，不含郵件；原表以公斤列示，本報除以1,000換算公噸。進口／出口涵蓋一般、機放與快遞專區；轉口含進倉、出倉與機下直轉。</div>
<div class="page-break"></div>
<h2>美國港口｜Port of Los Angeles（TEU，2026-09）</h2>{tbl(['項目','最新月','MoM','YoY','Q3截至9月','1–9月／YTD','官方來源'], pola_rows)}
<p class="muted">POLA 的 Imports／Exports 指 loaded containers；Empty Total＝empty imports＋empty exports。Q3截至9月＝7–9月。</p>
<h2>美國港口｜Port of Long Beach（TEU，2026-08）</h2>{tbl(['項目','最新月','MoM','YoY','Q3截至8月','1–8月／YTD','官方來源'], polb_rows)}
<div class="note"><b>POLB 資料狀態：</b>2026年8月官方新聞稿確認總計 919,992 TEU、進口 456,100、出口 99,754、空櫃 364,138；9月完整官方月度資料在本次截點未能穩定取得，故不推估。7月分項加總與官方總計相差 1 TEU、1–8月分項加總與官方總計相差 6 TEU，總計欄優先採官方發布總數。</div>
<h2>加州主要機場空運｜各來源最新完整月份</h2>{tbl(['機場','資料月','單位／口徑','最新月','MoM','YoY','Q3截至最新月','YTD','官方來源'], airport_rows)}
<div class="note"><b>單位與口徑：</b>LAX 依 LAWA 原表「Tons」呈現，官方未明示公噸或短噸；SFO 為 metric tons；SMF 原始資料為 pounds，本報以 2,000 lb＝1 short ton 換算。三者皆以來源表列的貨物＋郵件／Airmail口徑呈現。</div>
<h2>資料完整性與限制</h2><ul>
<li>臺灣港口與桃園機場最新完整月為2026年8月。POLA已公布至9月；POLB、LAX、SFO與SMF最新可驗證月為8月。</li>
<li>POLB官方統計頁面當次擷取僅穩定顯示至6月，7–8月改採港方官方月度新聞稿；9月不以第三方或未驗證搜尋摘要補值。</li>
<li>OAK、ONT、SAN未納入：本次無法在相同官方快照中同時取得最新月、前月、同期、QTD與YTD的完整可稽核貨量，故明確留白。</li>
<li>所有百分比按（本期－比較期）／比較期計算；比較期為零或缺值標N/A。原始發布數的四捨五入可能造成分項加總尾差。</li>
</ul>
<h2>官方來源</h2><ul class="sources"><li>{source('kel')}</li><li>{source('khh')}</li><li>{source('tpe')}</li><li>{source('caa')}</li><li>{source('pola26')}</li><li>{source('pola25')}</li><li>{source('polb')}</li><li>{source('polbtable')}</li><li>{source('lax')}</li><li>{source('sfo')}</li><li>{source('smf')}</li></ul>
<div class="footer">產製：每月港口／空運貨量主報告｜研究日：2026-10-10｜僅採官方來源；所有引用均內嵌至來源標籤。</div>
</body></html>'''
HTML.write_text(html_doc, encoding='utf-8')
print(HTML)
