#!/usr/bin/env python3
import json, urllib.request, html, pathlib, datetime, subprocess, os, re, shutil

REPORT_DATE='2026-07-01'
GENERATED='2026-07-01 08:20 Asia/Taipei'
OUT=pathlib.Path('/Users/cph/investment-reports/reports/shipping-logistics')/REPORT_DATE
OUT.mkdir(parents=True, exist_ok=True)
HTML=OUT/'report.html'
PDF=OUT/'report.pdf'
ALT=OUT/f'航運物流股日報_{REPORT_DATE}.pdf'
WATCH=['2603','2609','2615','2605','2606','2612','2617','2637','5608','2641','2607','2608','2611','2613','2636','2642','5601','5603','5604','5607','5609','1443','2610','2618','2646','2630','2645']
NAME={'2603':'長榮','2609':'陽明','2615':'萬海','2605':'新興','2606':'裕民','2612':'中航','2617':'台航','2637':'慧洋-KY','5608':'四維航','2641':'正德','2607':'榮運','2608':'嘉里大榮','2611':'志信','2613':'中櫃','2636':'台驊投控','2642':'宅配通','5601':'台聯櫃','5603':'陸海','5604':'中連','5607':'遠雄港','5609':'中菲行','1443':'立益物流','2610':'華航','2618':'長榮航','2646':'星宇航空','2630':'亞航','2645':'長榮航太'}
GROUPS=[('貨櫃航運',['2603','2609','2615']),('散裝 / 海運',['2605','2606','2612','2617','2637','5608','2641']),('港埠 / 物流 / 貨代',['2607','2608','2611','2613','2636','2642','5601','5603','5604','5607','5609','1443']),('航空 / 航太維修',['2610','2618','2646','2630','2645'])]
URLS={
 'twse_rev':'https://openapi.twse.com.tw/v1/opendata/t187ap05_L',
 'tpex_rev':'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O',
 'twse_mat':'https://openapi.twse.com.tw/v1/opendata/t187ap04_L',
 'tpex_mat':'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap04_O',
 'eva_dc':'https://www.evaair.com/zh-tw/about-eva-air/news/news-releases/2026-02-11-evaair-new-route-taipei-to-washington-dc.html',
 'airline_rating':'https://udn.com/news/story/7251/9585037',
 'ctee_airline':'https://www.ctee.com.tw/news/20260617700841-430201',
 'goodinfo_2603_div':'https://goodinfo.tw/tw/StockDividendSchedule.asp?STOCK_ID=2603',
 'goodinfo_2641_div':'https://goodinfo.tw/StockInfo/StockDividendSchedule.asp?STOCK_ID=2641',
 'scfi_udn':'https://udn.com/news/story/7251/9594874',
 'drewry':'https://www.drewry.co.uk/supply-chain-advisors/supply-chain-expertise/world-container-index-assessed-by-drewry',
 'baltic':'https://www.balticexchange.com/en/data-services/market-information0/dry-services.html',
 'hormuz':'https://www.eia.gov/todayinenergy/detail.php?id=65544',
 'fdx_8k':'https://www.sec.gov/Archives/edgar/data/0001048911/000104891126000050/fdx-20260623.htm',
 'fdx_earn':'https://www.sec.gov/Archives/edgar/data/1048911/000104891126000050/fdx-earningsreleasefy2026q4.htm',
 'fdxf':'https://www.sec.gov/Archives/edgar/data/0002082247/000162828026045515/fdxf-q4fy2026juneearningsr.htm',
 'ups_healthcare':'https://about.ups.com/us/en/newsroom/press-releases/customer-first/ups-extends-complex-healthcare-logistics-lead-with--48-million-i.html',
 'matx_div':'https://www.prnewswire.com/news-releases/matson-increases-quarterly-dividend-to-0-38-per-share-302811160.html',
 'gnk_629':'https://www.globenewswire.com/news-release/2026/06/29/3318793/',
 'gnk_617':'https://www.stocktitan.net/sec-filings/GNK/sc-to-t-a-genco-shipping-trading-ltd-amended-third-party-tender-offer-5494151630e5.html',
 'ups_ir':'https://investors.ups.com/','xpo_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001166003.json','chrw_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001043277.json','expd_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000746515.json','gxo_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001852244.json','jbh_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000728535.json','matx_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000003453.json','zim_ir':'https://www.zim.com/investors/press-releases','dac_sec':'https://www.sec.gov/edgar/browse/?CIK=1369241&owner=exclude','sblk_ir':'https://www.starbulk.com/gr/en/press-releases/','gogl_ir':'https://www.goldenocean.bm/category/press-releases/','gnk_ir':'https://investors.gencoshipping.com/','kex_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000056047.json'
}

def fetch_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 cph-investment-report/1.0'})
    with urllib.request.urlopen(req,timeout=25) as r:
        return json.loads(r.read().decode('utf-8-sig'))

def esc(x): return html.escape(str(x if x is not None else ''), quote=True)
def num(x):
    try: return int(str(x).replace(',','').strip())
    except Exception: return None
def pct(x):
    try:
        v=float(str(x).replace(',','').replace('%','').strip())
        return f'{v:+.2f}%'
    except Exception: return esc(x)
def pct_class(x):
    try: return 'pos' if float(str(x).replace(',','').replace('%',''))>=0 else 'neg'
    except Exception: return ''
def nt_100m(v):
    n=num(v)
    return '' if n is None else f'{n/100000:.2f} 億'
def roc_month(s):
    s=str(s)
    if len(s)>=5 and s[:3].isdigit(): return f'{int(s[:3])+1911}-{s[3:5]}'
    return s

def short_title(t):
    t=re.sub(r'\s+',' ',str(t)).strip()
    return t[:110]+('…' if len(t)>110 else '')

rev={}; mat=[]; fetch_notes=[]
for key in ['twse_rev','tpex_rev']:
    try:
        data=fetch_json(URLS[key]); fetch_notes.append(f'{key}:{len(data)}')
        for r in data:
            code=str(r.get('公司代號') or '').strip()
            if code in WATCH:
                r['_src']='TWSE 官方資料' if key=='twse_rev' else 'TPEx 官方資料'; r['_url']=URLS[key]
                rev[code]=r
    except Exception as e: fetch_notes.append(f'{key}:ERR {e}')
for key in ['twse_mat','tpex_mat']:
    try:
        data=fetch_json(URLS[key]); fetch_notes.append(f'{key}:{len(data)}')
        for r in data:
            code=str(r.get('公司代號') or r.get('SecuritiesCompanyCode') or '').strip()
            if code in WATCH:
                title=(r.get('主旨 ') or r.get('主旨') or r.get('Subject') or '').strip()
                date=r.get('發言日期') or r.get('Date') or r.get('出表日期') or ''
                mat.append({'code':code,'name':r.get('公司名稱') or r.get('CompanyName') or NAME.get(code,''),'date':date,'title':title,'src':'TWSE 官方資料' if key=='twse_mat' else 'TPEx 官方資料','url':URLS[key]})
    except Exception as e: fetch_notes.append(f'{key}:ERR {e}')

summary_cards=[
 ('risk','波灣風險仍是油輪/能源運輸主線','上游 deep research 今日 07:45、DR_STATUS=partial。荷姆茲海峽通行受限已列為最大地緣變數；油輪繞行與保險成本支撐油輪/能源運輸敘事，但航空燃油成本需反向留意。','上游深度研究 / 能源官方資料'),
 ('good','貨櫃運價續強，7 月 GRI 接棒','SCFI 6/27 收 3,239.64 點、月增約 26%；Drewry WCI 6/26 約 US$4,166/FEU、年增約 40%。7/1 起跨太平洋 GRI 題材延續，貨櫃三雄與貨代仍是短線焦點。','產業媒體 / Drewry'),
 ('warn','散裝與貨櫃分歧擴大','BDI 6/27 連 5 跌至約 2,524 點，Capesize 弱勢主導；散裝股雖有 5 月營收高成長與波灣油輪題材，但短線運價動能不如貨櫃。','Baltic Exchange / 產業媒體'),
 ('good','航空 5 月營收與北美線題材延續','華航、長榮航、星宇 5 月營收均創同期新高；長榮航桃園—華盛頓 6/26 開航、7 月訂位率高，航空貨運受 AI 伺服器北美需求支撐。','公司公告 / 產業媒體'),
 ('risk','FedEx 指引與分拆後口徑是美股焦點','FDX Q4 FY26 營收與調整 EPS 優於預期，但 CY2026 過渡期指引偏保守；FedEx Freight 分拆後首份業績與 FDX 股價序列技術性除權需分開解讀。','SEC 官方資料'),
 ('neutral','資料 QC 通過','上游日期為今日台北日期 2026-07-01，DR_STATUS=partial、非 failed/stale；本報再以 TWSE/TPEx 官方資料快速補查固定台股名單月營收與重大訊息。','TWSE / TPEx 官方資料')]

industry_cards=[
 ('good','SCFI / WCI','Asia→US 貨櫃運價多指標齊揚：SCFI 6/27 約 3,239.64；Drewry WCI 6/26 約 US$4,166/FEU。短線核心是紅海繞航、旺季前置拉貨與 7 月漲價。',URLS['drewry'],'產業數據'),
 ('warn','BDI','BDI 6/27 約 2,524、週跌約 7.3%，Capesize 拖累；散裝族群宜與貨櫃族群分開看待。',URLS['baltic'],'產業數據'),
 ('risk','荷姆茲海峽','上游回報 6/30 僅約 5 艘通行、遠低於正常水準；因全球原油與 LNG 供應占比高，油輪、能源與航空燃油成本同時受影響。',URLS['hormuz'],'能源官方資料'),
 ('neutral','航空貨運','北美 AI 伺服器空運需求使航空貨運單價維持高檔；華航 5 月貨運營收 YoY +53.5%，長榮航貨運 YoY +41.54%。',URLS['airline_rating'],'產業媒體')]

tw_events=[
 ('2026-06-26','2618 長榮航','桃園—華盛頓 DC 直飛開航','每週四班、B787-9 執飛；北美航點增至 10 個，每週 98 班，7 月平均訂位率約 90%。',URLS['eva_dc'],'公司公告'),
 ('2026-06-25','2610/2618/2646 航空族群','法人/外資升評與買超','本土法人上調航空族群目標價；外資 6/17 起連日買超航空股，焦點在暑期客運、油價與貨運。',URLS['airline_rating'],'產業媒體'),
 ('2026-06-23','2641 正德','現金股利 0.5 元除息基準日','2026 第 1 次除息基準日；屬股利時程事項，非營運基本面變動。',URLS['goodinfo_2641_div'],'公開資訊彙整'),
 ('2026-06-22','2603 長榮','子公司 Evergreen Marine (Asia) 購置新建造貨櫃','配合船隊與貨櫃配置；需以 MOPS 公告與後續資本支出口徑追蹤。',URLS['twse_mat'],'TWSE 官方資料'),
 ('2026-06-17','2603 長榮','現金股利 16 元除息','除息交易日 6/17、基準日 6/26、發放日 7/17；填息進度與貨櫃運價同步觀察。',URLS['goodinfo_2603_div'],'公開資訊彙整'),
 ('2026-06-17','2610/2618/2646 航空族群','油價回落與美伊談判題材推升航空股','航空三雄齊揚，長榮航量價表現突出；後續仍需觀察波灣風險對燃油的反向衝擊。',URLS['ctee_airline'],'產業媒體')]

us_events=[
 ('GNK','2026-06-29','Diana 延長 tender 至 7/10 17:00 ET；Genco 重申拒絕。至 6/26 已 tender 約 10.58M 股、占 28.4%。','公司公告',URLS['gnk_629']),
 ('FDXF','2026-06-25','FedEx Freight 分拆後首份季報：Q4 FY26 營收 US$2.4B（+4.8%）、調整營業利益 US$363M（-23.9%）。','SEC 官方資料',URLS['fdxf']),
 ('MATX','2026-06-25','Q3 季股利調升至 US$0.38/股（QoQ +5.6%），連續 14 年年增；9/3 支付、8/6 record。','公司公告',URLS['matx_div']),
 ('FDX','2026-06-23','Q4 FY26 營收 US$25.0B、調整 EPS US$6.31；CY2026 過渡期指引調整 EPS US$16.90–18.10，市場解讀偏保守。','SEC 官方資料',URLS['fdx_8k']),
 ('UPS','2026-06-22','宣布投資 US$48M 建置/強化 27 個全球溫控冷鏈 cross-dock，聚焦 GLP-1、生物製劑等醫療物流。','公司公告',URLS['ups_healthcare']),
 ('GNK','2026-06-17','Diana 將 Genco 收購提案提高至 implied US$27.34/股，GNK 董事會仍反對。','SEC / 公司公告',URLS['gnk_617'])]

us_fin=[
 ('UPS','FY2026 Q1','Revenue US$21.2B（+1% YoY）；Adj EPS US$1.07；重申 FY26 revenue US$89.7B、Adj OI margin 9.6%。','公司 IR',URLS['ups_ir']),
 ('FDX','FY2026 Q4','Revenue US$25.0B（+13% YoY）；Adj EPS US$6.31；FY26 Adj EPS US$20.24；CY2026 guidance US$16.90–18.10。','SEC 官方資料',URLS['fdx_earn']),
 ('XPO','FY2026 Q1','Revenue 約 US$2.10B（+7.3%）；Adj EPS US$1.01；Adj EBITDA US$319M。','SEC 官方資料',URLS['xpo_sec']),
 ('CHRW','FY2026 Q1','Revenue 約 US$4.01B；Adj EPS 約 US$1.35，貨代/經紀景氣仍待量價復甦。','SEC 官方資料',URLS['chrw_sec']),
 ('EXPD','FY2026 Q1','Revenue 約 US$2.78B；國際貨代需求與費率口徑續追。','SEC 官方資料',URLS['expd_sec']),
 ('GXO','FY2026 Q1','Revenue 約 US$3.30B；合約物流新約與自動化效率為核心。','SEC 官方資料',URLS['gxo_sec']),
 ('JBHT','FY2026 Q1','Revenue 約 US$2.92B；多式聯運、Dedicated 與卡車需求為核心觀察。','SEC 官方資料',URLS['jbh_sec']),
 ('MATX','FY2026 Q1','Revenue 約 US$758M；6/25 調高季股利。','SEC / 公司 IR',URLS['matx_sec']),
 ('ZIM','FY2026 Q1 / 併購','上游回報 Q1 轉虧，且 Hapag-Lloyd 收購案以 US$35/股現金推進；後續以公司 IR/監管審批為準。','公司 IR',URLS['zim_ir']),
 ('DAC','最新可得','以 20-F/6-K、charter backlog 與貨櫃船租金為主；受貨櫃景氣與船舶資產價格影響。','SEC 官方資料',URLS['dac_sec']),
 ('SBLK','最新可得','散裝船隊處分、股利政策與 BDI 敏感度為觀察重點。','公司 IR',URLS['sblk_ir']),
 ('GOGL','最新可得','固定追蹤清單仍保留；需注意合併/上市口徑與公司 IR 更新。','公司 IR',URLS['gogl_ir']),
 ('GNK','2026 Q1 / 收購戰','Q1 revenue 約 US$114M；Diana 收購戰與 tender 比例為短線主軸。','公司 IR',URLS['gnk_ir']),
 ('KEX','FY2026 Q1','Revenue 約 US$844M；內河運輸、分銷與能源/農產品物流需求為重點。','SEC 官方資料',URLS['kex_sec'])]

css='''@page{size:A4;margin:11mm}*{box-sizing:border-box}body{margin:0;font-family:"PingFang TC","Heiti TC","Noto Sans TC","Microsoft JhengHei",sans-serif;background:#f4f7fb;color:#172033;font-size:12.5px;line-height:1.52}.hero{background:linear-gradient(135deg,#075ba8,#10a9df);color:#fff;border-radius:22px;padding:24px 28px;margin-bottom:16px;box-shadow:0 8px 24px rgba(5,70,120,.22)}h1{font-size:30px;margin:0 0 6px;letter-spacing:.04em}h2{font-size:19px;color:#0f3b66;margin:18px 0 10px}h3{font-size:14.5px;margin:4px 0 6px}.meta{opacity:.95}.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.grid.one{grid-template-columns:1fr}.grid.three{grid-template-columns:repeat(3,1fr)}.card{break-inside:avoid;background:#fff;border:1px solid #e2e9f3;border-radius:16px;padding:12px 14px;margin:0 0 10px;box-shadow:0 2px 8px rgba(42,67,101,.08)}.risk{border-left:5px solid #ef4444}.good{border-left:5px solid #16a34a}.warn{border-left:5px solid #f97316}.neutral{border-left:5px solid #3b82f6}.badge{display:inline-block;background:#e8f1ff;color:#114b88;border-radius:999px;padding:3px 9px;font-size:11.5px;font-weight:700;margin-bottom:6px}.source{display:block;margin-top:8px;color:#64748b;font-size:11.5px}.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:5px 8px;margin-top:6px}.stat{background:#f8fafc;border-radius:10px;padding:6px}.stat span{display:block;color:#64748b;font-size:10.5px}.stat strong{font-size:12px}.stat small{display:block;color:#64748b}.pos strong,.pos{color:#15803d}.neg strong,.neg{color:#b91c1c}ul{margin:6px 0 0 18px;padding:0}li{margin:4px 0}p{margin:4px 0}.footer{margin-top:18px;color:#475569;font-size:12px}.src-list li{word-break:break-all;font-size:10.8px}.pagebreak{break-before:page}.mini{font-size:11.5px;color:#64748b}a{color:#2563eb;text-decoration:none}.table{width:100%;border-collapse:separate;border-spacing:0 6px}.table td,.table th{background:#fff;padding:7px 9px;border-top:1px solid #e2e8f0;border-bottom:1px solid #e2e8f0;vertical-align:top}.table th{color:#0f3b66;background:#e8f1ff}.table td:first-child,.table th:first-child{border-left:1px solid #e2e8f0;border-radius:10px 0 0 10px}.table td:last-child,.table th:last-child{border-right:1px solid #e2e8f0;border-radius:0 10px 10px 0}.notice{background:#fff7ed;border:1px solid #fed7aa;border-radius:14px;padding:10px 12px;color:#9a3412}.toc{display:flex;gap:8px;flex-wrap:wrap}.toc span{background:#e8f1ff;border-radius:999px;padding:4px 10px;color:#114b88;font-weight:700;font-size:11.5px}'''

def source(label,url): return f'<span class="source">來源：<a href="{esc(url)}">{esc(label)}</a></span>'

parts=[f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><title>航運物流股日報_{REPORT_DATE}</title><style>{css}</style></head><body>']
parts.append(f'<div class="hero"><h1>航運物流股日報</h1><div class="meta">報告日期：{REPORT_DATE}　產出時間：{GENERATED}<br>涵蓋：前一台股交易日/公告日 2026-06-30；前一美股交易日/公告日 2026-06-30<br>資料狀態：07:45 deep research 為今日台北日期 2026-07-01，DR_STATUS=partial；非 stale/failed。已用 TWSE/TPEx 官方資料快速補查台股月營收與重大訊息。</div></div>')
parts.append('<div class="toc"><span>今日重點</span><span>產業指標</span><span>台股重大訊息</span><span>月營收</span><span>美股公告</span><span>資料缺口</span></div>')
parts.append('<section><h2>今日重點</h2><div class="grid">')
for cls,title,txt,src in summary_cards:
    parts.append(f'<article class="card {cls}"><span class="badge">{esc(title)}</span><p>{esc(txt)}</p><span class="source">來源：{esc(src)}</span></article>')
parts.append('</div></section>')
parts.append('<section><h2>產業與市場觀察</h2><div class="grid">')
for cls,title,txt,url,label in industry_cards:
    parts.append(f'<article class="card {cls}"><span class="badge">{esc(title)}</span><p>{esc(txt)}</p>{source(label,url)}</article>')
parts.append('</div></section>')

parts.append('<section><h2>台股重大訊息（短摘要）</h2><div class="grid one">')
recent_mat=[m for m in mat if str(m.get('date','')) >= '20260617' or str(m.get('date','')) >= '2026/06/17']
if recent_mat:
    for m in recent_mat[:8]:
        parts.append(f'<article class="card neutral"><span class="badge">{esc(m["date"])}｜{esc(m["code"])} {esc(m["name"])}</span><h3>{esc(short_title(m["title"]))}</h3>{source(m["src"],m["url"])}</article>')
else:
    parts.append(f'<article class="card neutral"><span class="badge">官方重大訊息快速補查</span><h3>本輪 TWSE/TPEx 官方重大訊息資料未擷取到固定名單新增列項；以下補列上游 deep research 近 14 日重大事件摘要。</h3>{source("TWSE 官方資料",URLS["twse_mat"])}{source("TPEx 官方資料",URLS["tpex_mat"])}</article>')
for d,code,title,txt,url,label in tw_events:
    parts.append(f'<article class="card neutral"><span class="badge">{esc(d)}｜{esc(code)}</span><h3>{esc(title)}</h3><p>{esc(txt)}</p>{source(label,url)}</article>')
parts.append('</div></section>')

parts.append('<section class="pagebreak"><h2>台股月營收（官方最新；單位：新台幣千元 / 億元）</h2><p class="mini">最新月營收公布期為 2026/05；若官方資料未擷取到則明列缺口，不以推估值補列。</p>')
for g,codes in GROUPS:
    parts.append(f'<h3>{esc(g)}</h3><div class="grid three">')
    for code in codes:
        r=rev.get(code)
        if r:
            month=roc_month(r.get('資料年月',''))
            mon=r.get('營業收入-當月營收','')
            cum=r.get('累計營業收入-當月累計營收','')
            mom=r.get('營業收入-上月比較增減(%)','')
            yoy=r.get('營業收入-去年同月增減(%)','')
            cyoy=r.get('累計營業收入-前期比較增減(%)','')
            ccls='good' if (pct_class(yoy)=='pos' and pct_class(cyoy)=='pos') else 'warn'
            parts.append(f'''<article class="card {ccls}"><span class="badge">{code} {esc(NAME.get(code,''))}</span><h3>{esc(month)}</h3><div class="stats"><div class="stat"><span>單月營收</span><strong>{esc(mon)}</strong><small>（{esc(nt_100m(mon))}）</small></div><div class="stat {pct_class(mom)}"><span>MoM</span><strong>{pct(mom)}</strong></div><div class="stat {pct_class(yoy)}"><span>YoY</span><strong>{pct(yoy)}</strong></div><div class="stat"><span>累計營收</span><strong>{esc(cum)}</strong><small>（{esc(nt_100m(cum))}）</small></div><div class="stat {pct_class(cyoy)}"><span>累計 YoY</span><strong>{pct(cyoy)}</strong></div></div>{source(r['_src'],r['_url'])}</article>''')
        else:
            parts.append(f'<article class="card neutral"><span class="badge">{code} {esc(NAME.get(code,""))}</span><h3>尚未公布 / 本次官方資料未擷取到</h3><p>不以推估值補列。</p>{source("TWSE/TPEx 官方資料",URLS["twse_rev"])}</article>')
    parts.append('</div>')
parts.append('</section>')

parts.append('<section><h2>美股重大公告 / 最新可得業績</h2><div class="grid">')
for tick,period,txt,label,url in us_events:
    parts.append(f'<article class="card {"risk" if tick in ("FDX","GNK") else "neutral"}"><span class="badge">{esc(period)}｜{esc(tick)}</span><p>{esc(txt)}</p>{source(label,url)}</article>')
parts.append('</div><h3>最近一季 / 最新可得業績摘要</h3><table class="table"><tr><th>Ticker</th><th>期間</th><th>金額 / 重點</th><th>來源</th></tr>')
for tick,period,txt,label,url in us_fin:
    parts.append(f'<tr><td>{esc(tick)}</td><td>{esc(period)}</td><td>{esc(txt)}</td><td><a href="{esc(url)}">{esc(label)}</a></td></tr>')
parts.append('</table></section>')

missing=[]
if len(rev)<len(WATCH): missing.append('台股月營收仍有未擷取公司：'+', '.join([c for c in WATCH if c not in rev]))
missing += ['上游 deep research 為 partial：產業指數、地緣風險與部分併購細節仍需以後續官方/交易所公告滾動校正。','ZIM 收購案、GNK tender 與 GOGL/CMBT 口徑屬跨市場事件，本報列公開來源與資料缺口，不作交易建議。','市場日頻指數（SCFI/WCI/BDI/燃油）可能因來源發布時間與結算口徑存在差異。']
parts.append('<section><h2>資料缺口與注意事項</h2><div class="grid">')
for m in missing:
    parts.append(f'<article class="card neutral"><span class="badge">注意</span><p>{esc(m)}</p></article>')
parts.append('<article class="card neutral"><span class="badge">非投資建議</span><p>以上為公開資訊整理，非投資建議。</p></article></div></section>')
all_urls=[]
for u in URLS.values(): all_urls.append(u)
for _,_,_,_,u,_ in tw_events: all_urls.append(u)
for _,_,_,_,u in us_events: all_urls.append(u)
for _,_,_,_,u in us_fin: all_urls.append(u)
all_urls=sorted(set(all_urls))
parts.append('<section><h2>來源清單（完整 URL）</h2><div class="card"><ul class="src-list">')
for u in all_urls: parts.append(f'<li>{esc(u)}</li>')
parts.append(f'</ul><p class="footer">QC trace: {esc("; ".join(fetch_notes))}</p><p class="footer">以上為公開資訊整理，非投資建議。</p></div></section></body></html>')
HTML.write_text('\n'.join(parts),encoding='utf-8')
print(str(HTML))
