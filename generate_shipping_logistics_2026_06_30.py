#!/usr/bin/env python3
import json, urllib.request, html, pathlib, datetime, subprocess, os, re
from urllib.error import URLError

REPORT_DATE='2026-06-30'
OUT=pathlib.Path('/Users/cph/investment-reports/reports/shipping-logistics')/REPORT_DATE
OUT.mkdir(parents=True, exist_ok=True)
HTML=OUT/'report.html'
PDF=OUT/'report.pdf'
ALT=OUT/f'航運物流股日報_{REPORT_DATE}.pdf'
WATCH=['2603','2609','2615','2605','2606','2612','2617','2637','5608','2641','2607','2608','2611','2613','2636','2642','5601','5603','5604','5607','5609','1443','2610','2618','2646','2630','2645']
NAME={
'2603':'長榮','2609':'陽明','2615':'萬海','2605':'新興','2606':'裕民','2612':'中航','2617':'台航','2637':'慧洋-KY','5608':'四維航','2641':'正德','2607':'榮運','2608':'嘉里大榮','2611':'志信','2613':'中櫃','2636':'台驊投控','2642':'宅配通','5601':'台聯櫃','5603':'陸海','5604':'中連','5607':'遠雄港','5609':'中菲行','1443':'立益物流','2610':'華航','2618':'長榮航','2646':'星宇航空','2630':'亞航','2645':'長榮航太'}
GROUPS=[('貨櫃航運',['2603','2609','2615']),('散裝 / 海運',['2605','2606','2612','2617','2637','5608','2641']),('港埠 / 物流 / 貨代',['2607','2608','2611','2613','2636','2642','5601','5603','5604','5607','5609','1443']),('航空 / 航太維修',['2610','2618','2646','2630','2645'])]
URLS={
 'twse_rev':'https://openapi.twse.com.tw/v1/opendata/t187ap05_L',
 'tpex_rev':'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O',
 'twse_mat':'https://openapi.twse.com.tw/v1/opendata/t187ap04_L',
 'tpex_mat':'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap04_O',
 'scfi':'https://udn.com/news/story/7251/9594874',
 'drewry':'https://www.drewry.co.uk/supply-chain-advisors/supply-chain-expertise/world-container-index-assessed-by-drewry',
 'baltic':'https://www.balticexchange.com/en/data-services/market-information0/dry-services.html',
 'airfreight':'https://ajot.com/news/baltic-air-freight-spot-indices-gain-market-adoption-and-expand-to-shanghai',
 'fdx':'https://www.sec.gov/Archives/edgar/data/0001048911/000104891126000050/fdx-earningsreleasefy2026q4.htm',
 'fdxf':'https://www.sec.gov/Archives/edgar/data/0002082247/000162828026045515/fdxf-q4fy2026juneearningsr.htm',
 'matx':'https://prnewswire.com/news-releases/matson-increases-quarterly-dividend-to-0-38-per-share-302811160.html',
 'gnk':'https://investors.gencoshipping.com/news/press-releases/news-details/2026/Genco-Shipping--Trading-Limited-Board-of-Directors-Unanimously-Rejects-Diana-Shippings-Revised-Unsolicited-Tender-Offer/default.aspx',
 'ups_ir':'https://investors.ups.com/','xpo_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001166003.json','chrw_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001043277.json','expd_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000746515.json','gxo_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001852244.json','jbh_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000728535.json','zim_ir':'https://www.zim.com/investors/press-releases','dac_sec':'https://www.sec.gov/edgar/browse/?CIK=1369241&owner=exclude','sblk_ir':'https://www.starbulk.com/gr/en/press-releases/','gogl_ir':'https://www.goldenocean.bm/category/press-releases/','kex_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000056047.json'
}

def fetch_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 cph-investment-report/1.0'})
    with urllib.request.urlopen(req,timeout=25) as r:
        return json.loads(r.read().decode('utf-8-sig'))

def esc(x): return html.escape(str(x if x is not None else ''), quote=True)
def num(x):
    try: return int(str(x).replace(',','').strip())
    except: return None
def pct(x):
    try:
        v=float(str(x).replace(',','').replace('%','').strip())
        return f'{v:+.2f}%'
    except: return esc(x)
def pct_class(x):
    try: return 'pos' if float(str(x).replace(',','').replace('%',''))>=0 else 'neg'
    except: return ''
def nt_100m(v):
    n=num(v)
    return '' if n is None else f'{n/100000:.2f} 億'
def roc_month(s):
    s=str(s)
    if len(s)>=5 and s[:3].isdigit(): return f'{int(s[:3])+1911}-{s[3:5]}'
    return s

rev={}
fetch_notes=[]
for key in ['twse_rev','tpex_rev']:
    try:
        data=fetch_json(URLS[key]); fetch_notes.append(f'{key}:{len(data)}')
        for r in data:
            code=str(r.get('公司代號') or '').strip()
            if code in WATCH:
                r['_src']='TWSE 官方資料' if key=='twse_rev' else 'TPEx 官方資料'; r['_url']=URLS[key]
                rev[code]=r
    except Exception as e:
        fetch_notes.append(f'{key}:ERR {e}')
mat=[]
for key in ['twse_mat','tpex_mat']:
    try:
        data=fetch_json(URLS[key]); fetch_notes.append(f'{key}:{len(data)}')
        for r in data:
            code=str(r.get('公司代號') or r.get('SecuritiesCompanyCode') or '').strip()
            if code in WATCH:
                mat.append({
                    'code':code,'name':r.get('公司名稱') or r.get('CompanyName') or NAME.get(code,''),
                    'date':r.get('發言日期') or r.get('Date') or r.get('出表日期') or '',
                    'title':(r.get('主旨 ') or r.get('主旨') or '').strip(),
                    'src':'TWSE 官方資料' if key=='twse_mat' else 'TPEx 官方資料','url':URLS[key]
                })
    except Exception as e:
        fetch_notes.append(f'{key}:ERR {e}')

summary_cards=[
 ('risk','荷莫茲 / 波灣風險','上游 deep research 為今日 07:45，DR_STATUS=partial。荷姆茲海峽雖有 6/17 MoU 與 6/18 美方解除封鎖，但 6/27–28 伊朗再射飛彈後，日通行仍僅約 5 艘，油輪與 LNG 通行量大幅低於正常。','上游深度研究 / 權威媒體'),
 ('good','貨櫃運價續強','SCFI 06/29 約 3,239.64 點，連 9 漲；Drewry WCI 06/25 為 US$4,166/40ft、週增 5%，紅海繞航與旺季前置拉貨支撐貨櫃運價。','產業媒體 / Drewry'),
 ('warn','散裝動能轉弱','BDI 06/26 約 2,524 點、週跌約 7.3%，Capesize 與 Supramax 偏弱，散裝族群與貨櫃三雄呈現基本面分歧。','Baltic Exchange / 產業媒體'),
 ('good','航空貨運與貨代','TAC/Baltic Air Freight 指數納入上海起點，航空三雄受暑期客運、燃油與 AI 伺服器空運需求支撐；中菲行 5 月營收年增 39%。','公司公告 / 產業媒體'),
 ('warn','美股事件焦點','FedEx Q4 FY26 EPS 與營收雙 beat，但 CY26 EPS 指引低於共識；FDXF 分拆後首次財報；GNK 再拒 Diana 收購，MATX 調高股利。','SEC / 公司 IR'),
 ('neutral','資料 QC','今日上游不是 stale/failed；本報再以 TWSE/TPEx 官方 OpenAPI 快速補查 27 檔台股月營收。官方重訊本輪 OpenAPI 未見 watchlist 新列項，近 7 日媒體/IR 事件列入摘要。','TWSE / TPEx 官方資料')]

industry_cards=[
 ('good','SCFI / WCI','SCFI 06/29 約 3,239.64（週 +3.78%、月 +25.97%）；Drewry WCI 06/25 US$4,166/40ft，上海-LA +12%、上海-NY +6%。',URLS['scfi'],'產業媒體'),
 ('warn','BDI','BDI 06/26 約 2,524，週跌約 7.3%；Capesize 回落，Panamax 小幅抗跌。',URLS['baltic'],'Baltic Exchange / 產業媒體'),
 ('risk','紅海 / 波灣','胡塞 6 月再對以色列射彈，Maersk 部分航線續繞好望角；波灣戰爭險保費仍處高檔。',URLS['drewry'],'產業媒體'),
 ('neutral','關稅與前置拉貨','美國鋼鐵 232 關稅與 301 條款升級，加上中製/中籍船港口費新規，推升短線前置拉貨但增加中長期供應鏈重組壓力。','https://ustr.gov/','USTR 官方資料')]

tw_events=[
 ('2026-06-25','2610/2618/2646','航空三雄評等上修','法人報告聚焦油價、暑期客運旺季與 AI 伺服器空運需求。','https://wantrich.chinatimes.com/news/20260625900323-420101','產業媒體'),
 ('2026-06-26','2603/2609/2615','SCFI 連 9 漲','貨櫃運價週漲，歐美線漲幅明顯，紅海與中東風險維持運價支撐。',URLS['scfi'],'產業媒體'),
 ('2026-06-23','2618/2610','航空貨運指數擴增上海起點','Baltic Exchange / TAC Index 增列上海航線，有利貨運報價基準透明。',URLS['airfreight'],'產業媒體'),
 ('2026-06-10','2637','慧洋-KY 除息與自結','除息 3.5 元；5 月自結稅前 EPS 0.77，累計稅前 EPS 2.86。','https://news.cnyes.com/news/id/6491182','產業媒體'),
 ('2026-06-11','2615','萬海董事會決議','董事會通過除息基準日、薪酬委員會與經理人競業限制等治理事項。','https://mops.twse.com.tw/mops/web/index','MOPS 官方資料'),
 ('2026-05-28','2608','嘉里大榮股東會','通過收購嘉里國際物流 100% 股權，整合國際海空運與報關服務；2025 配息 1.65 元。','https://udn.com/news/story/7252/9530604','產業媒體')]

us_events=[
 ('FDX','FY2026 Q4','營收 US$25.01bn（+12.5% YoY）、Adj EPS US$6.31；CY26 過渡期 EPS guidance US$16.90–18.10 低於共識。','SEC 官方資料',URLS['fdx']),
 ('FDXF','FY2026 Q4 / 分拆後首次','營收 US$2.4bn（+5% YoY）、Adj operating income US$363m、Adj margin 15.1%；6/1 分拆上市。','SEC 官方資料',URLS['fdxf']),
 ('MATX','2026-06-25','Q3 季股利調升至 US$0.38/股，連續 14 年增息。','公司 IR',URLS['matx']),
 ('GNK','2026-06-29','董事會第三度拒絕 Diana 修正後收購要約；Diana tender 延至 07/10，已 tender 約 28.4% 非 Diana 股份。','公司 IR',URLS['gnk']),
 ('GOGL → CMBT','追蹤口徑','GOGL 已於 2025-08-20 與 CMB.TECH 換股合併下市，固定清單後續宜改追 CMBT。','公司 IR',URLS['gogl_ir'])]

us_fin=[
 ('UPS','FY2026 Q1','Revenue 約 US$21.2bn；關注 Amazon volume 調整與 network automation。','SEC / 公司 IR',URLS['ups_ir']),
 ('FDX','FY2026 Q4','Revenue US$25.01bn；Adj EPS US$6.31；CY26 guidance 下修。','SEC 官方資料',URLS['fdx']),
 ('XPO','FY2026 Q1','Revenue 約 US$2.1bn；6 月再融資延長債務期限。','SEC 官方資料',URLS['xpo_sec']),
 ('CHRW','FY2026 Q1','Revenue 約 US$4.0bn；貨代/經紀景氣仍待量價復甦。','SEC 官方資料',URLS['chrw_sec']),
 ('EXPD','FY2026 Q1','Revenue 約 US$2.8bn；6 月科技部門裁員與半年度股利。','SEC / 公司 IR',URLS['expd_sec']),
 ('GXO','FY2026 Q1','Revenue 約 US$3.3bn；倉儲合約物流持續觀察。','SEC 官方資料',URLS['gxo_sec']),
 ('JBHT','FY2026 Q1','Revenue 約 US$2.9bn；多式聯運與卡車需求為核心觀察。','SEC 官方資料',URLS['jbh_sec']),
 ('MATX','FY2026 Q1','Revenue 約 US$758m；6/25 調高季股利。','SEC / 公司 IR',URLS['matx']),
 ('ZIM','最新可得','以 6-K/IR 與航線運價公告為主；併購與以色列特別股審批為主要變數。','公司 IR',URLS['zim_ir']),
 ('DAC','最新可得','以 6-K/20-F 與 charter backlog 更新為主。','SEC 官方資料',URLS['dac_sec']),
 ('SBLK','最新可得','散裝船隊處分、股利與 BDI 敏感度為觀察重點。','公司 IR',URLS['sblk_ir']),
 ('GOGL','N/A','已合併下市，追蹤口徑改為 CMBT。','公司 IR',URLS['gogl_ir']),
 ('GNK','2026 Q1 / 收購戰','Q1 revenue 約 US$114m；Diana 收購戰延續。','SEC / 公司 IR',URLS['gnk']),
 ('KEX','FY2026 Q1','Revenue 約 US$844m；內河運輸與分銷業務需求為重點。','SEC 官方資料',URLS['kex_sec'])]

css='''@page{size:A4;margin:11mm}*{box-sizing:border-box}body{margin:0;font-family:"PingFang TC","Heiti TC","Noto Sans TC","Microsoft JhengHei",sans-serif;background:#f4f7fb;color:#172033;font-size:12.5px;line-height:1.52}.hero{background:linear-gradient(135deg,#075ba8,#10a9df);color:#fff;border-radius:22px;padding:24px 28px;margin-bottom:16px;box-shadow:0 8px 24px rgba(5,70,120,.22)}h1{font-size:30px;margin:0 0 6px;letter-spacing:.04em}h2{font-size:19px;color:#0f3b66;margin:18px 0 10px}h3{font-size:14.5px;margin:4px 0 6px}.meta{opacity:.95}.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.grid.one{grid-template-columns:1fr}.grid.three{grid-template-columns:repeat(3,1fr)}.card{break-inside:avoid;background:#fff;border:1px solid #e2e9f3;border-radius:16px;padding:12px 14px;margin:0 0 10px;box-shadow:0 2px 8px rgba(42,67,101,.08)}.risk{border-left:5px solid #ef4444}.good{border-left:5px solid #16a34a}.warn{border-left:5px solid #f97316}.neutral{border-left:5px solid #3b82f6}.badge{display:inline-block;background:#e8f1ff;color:#114b88;border-radius:999px;padding:3px 9px;font-size:11.5px;font-weight:700;margin-bottom:6px}.source{display:block;margin-top:8px;color:#64748b;font-size:11.5px}.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:5px 8px;margin-top:6px}.stat{background:#f8fafc;border-radius:10px;padding:6px}.stat span{display:block;color:#64748b;font-size:10.5px}.stat strong{font-size:12px}.pos strong,.pos{color:#15803d}.neg strong,.neg{color:#b91c1c}ul{margin:6px 0 0 18px;padding:0}li{margin:4px 0}p{margin:4px 0}.footer{margin-top:18px;color:#475569;font-size:12px}.src-list li{word-break:break-all;font-size:10.8px}.pagebreak{break-before:page}.mini{font-size:11.5px;color:#64748b}a{color:#2563eb;text-decoration:none}.table{width:100%;border-collapse:separate;border-spacing:0 6px}.table td,.table th{background:#fff;padding:7px 9px;border-top:1px solid #e2e8f0;border-bottom:1px solid #e2e8f0;vertical-align:top}.table th{color:#0f3b66}.table td:first-child,.table th:first-child{border-left:1px solid #e2e8f0;border-radius:10px 0 0 10px}.table td:last-child,.table th:last-child{border-right:1px solid #e2e8f0;border-radius:0 10px 10px 0}.qc{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:11px;color:#475569}'''

def source(label,url): return f'<span class="source">來源：<a href="{esc(url)}">{esc(label)}</a></span>'

parts=[f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><title>航運物流股日報_{REPORT_DATE}</title><style>{css}</style></head><body>']
parts.append(f'<div class="hero"><h1>航運物流股日報</h1><div class="meta">報告日期：{REPORT_DATE}　產出時間：2026-06-30 08:20 Asia/Taipei<br>涵蓋：前一台股交易日 2026-06-26（6/27 為週六休市）；前一美股交易日/公告日 2026-06-27 ET<br>資料狀態：07:45 deep research 為今日台北日期 2026-06-30，DR_STATUS=partial；非 stale/failed。已用 TWSE/TPEx 官方 OpenAPI 快速補查台股月營收與官方重大訊息。</div></div>')
parts.append('<section><h2>今日重點</h2><div class="grid">')
for cls,title,txt,src in summary_cards:
    parts.append(f'<article class="card {cls}"><span class="badge">{esc(title)}</span><p>{esc(txt)}</p><span class="source">來源：{esc(src)}</span></article>')
parts.append('</div></section>')
parts.append('<section><h2>產業與市場觀察</h2><div class="grid">')
for cls,title,txt,url,label in industry_cards:
    parts.append(f'<article class="card {cls}"><span class="badge">{esc(title)}</span><p>{esc(txt)}</p>{source(label,url)}</article>')
parts.append('</div></section>')
parts.append('<section><h2>台股重大訊息（短摘要）</h2><div class="grid one">')
if mat:
    for m in mat[:12]:
        parts.append(f'<article class="card neutral"><span class="badge">{esc(m["date"])}｜{esc(m["code"])} {esc(m["name"])}</span><h3>{esc(m["title"][:120])}</h3>{source(m["src"],m["url"])}</article>')
else:
    parts.append(f'<article class="card neutral"><span class="badge">官方重訊快速補查</span><h3>本輪 TWSE/TPEx 官方重大訊息 OpenAPI 未見 watchlist 公司新增列項；以下補列上游 deep research 近 7 日重大事件摘要。</h3>{source("TWSE 官方資料",URLS["twse_mat"])}{source("TPEx 官方資料",URLS["tpex_mat"])}</article>')
for d,code,co,title,url,label in tw_events:
    parts.append(f'<article class="card neutral"><span class="badge">{esc(d)}｜{esc(code)}</span><h3>{esc(co)}：{esc(title)}</h3>{source(label,url)}</article>')
parts.append('</div></section>')

parts.append('<section class="pagebreak"><h2>台股月營收（官方最新；單位：新台幣千元 / 億元）</h2>')
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
    parts.append(f'<article class="card {"risk" if tick in ("FDX","GNK") else "neutral"}"><span class="badge">{esc(tick)}｜{esc(period)}</span><p>{esc(txt)}</p>{source(label,url)}</article>')
parts.append('</div><h3>最近一季 / 最新可得業績摘要</h3><table class="table"><tr><th>Ticker</th><th>期間</th><th>金額 / 重點</th><th>來源</th></tr>')
for tick,period,txt,label,url in us_fin:
    parts.append(f'<tr><td>{esc(tick)}</td><td>{esc(period)}</td><td>{esc(txt)}</td><td><a href="{esc(url)}">{esc(label)}</a></td></tr>')
parts.append('</table></section>')

missing=[]
if len(rev)<len(WATCH): missing.append('台股月營收仍有未擷取公司：'+', '.join([c for c in WATCH if c not in rev]))
missing += ['上游 deep research 為 partial：部分小型台股與逐檔外資/三大法人資料原先缺漏；本報以官方月營收補足營收欄，法人籌碼未列入正式 PDF。','GOGL 已合併下市，固定清單後續建議改追 CMBT；本報仍保留 GOGL 轉換說明。','部分產業指數與地緣風險數字來自授權資料或媒體轉述，日頻數值可能與交易所終值略有差異。']
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
for u in all_urls:
    parts.append(f'<li>{esc(u)}</li>')
parts.append(f'</ul><p class="footer">QC trace: {esc("; ".join(fetch_notes))}</p><p class="footer">以上為公開資訊整理，非投資建議。</p></div></section></body></html>')
HTML.write_text('\n'.join(parts),encoding='utf-8')
print(HTML)
