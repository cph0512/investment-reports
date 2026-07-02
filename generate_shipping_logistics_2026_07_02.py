#!/usr/bin/env python3
import json, urllib.request, html, pathlib, datetime, re, subprocess, shutil, os
TZ=datetime.timezone(datetime.timedelta(hours=8))
now=datetime.datetime.now(TZ)
REPORT_DATE=now.strftime('%Y-%m-%d')
GENERATED=now.strftime('%Y-%m-%d %H:%M Asia/Taipei')
PREV_TW='2026-07-01'
PREV_US='2026-07-01 / 最新公告日'
OUT=pathlib.Path('/Users/cph/investment-reports/reports/shipping-logistics')/REPORT_DATE
OUT.mkdir(parents=True, exist_ok=True)
HTML=OUT/'report.html'
PDF=OUT/'report.pdf'
ALT=OUT/f'航運物流股日報_{REPORT_DATE}.pdf'
WATCH='2603 2609 2615 2605 2606 2612 2617 2637 5608 2641 2607 2608 2611 2613 2636 2642 5601 5603 5604 5607 5609 1443 2610 2618 2646 2630 2645'.split()
NAME={'2603':'長榮','2609':'陽明','2615':'萬海','2605':'新興','2606':'裕民','2612':'中航','2617':'台航','2637':'慧洋-KY','5608':'四維航','2641':'正德','2607':'榮運','2608':'嘉里大榮','2611':'志信','2613':'中櫃','2636':'台驊投控','2642':'宅配通','5601':'台聯櫃','5603':'陸海','5604':'中連','5607':'遠雄港','5609':'中菲行','1443':'立益物流','2610':'華航','2618':'長榮航','2646':'星宇航空','2630':'亞航','2645':'長榮航太'}
GROUPS=[('貨櫃航運',['2603','2609','2615']),('散裝 / 海運',['2605','2606','2612','2617','2637','5608','2641']),('港埠 / 物流 / 貨代',['2607','2608','嘉里大榮','2611'])]
GROUPS=[('貨櫃航運',['2603','2609','2615']),('散裝 / 海運',['2605','2606','2612','2617','2637','5608','2641']),('港埠 / 物流 / 貨代',['2607','2608','2611','2613','2636','2642','5601','5603','5604','5607','5609','1443']),('航空 / 航太維修',['2610','2618','2646','2630','2645'])]
URLS={
 'twse_rev':'https://openapi.twse.com.tw/v1/opendata/t187ap05_L','tpex_rev':'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O','twse_mat':'https://openapi.twse.com.tw/v1/opendata/t187ap04_L','tpex_mat':'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap04_O',
 'yangming_container':'https://openapi.twse.com.tw/v1/opendata/t187ap04_L','yuanxiong_audit':'https://openapi.twse.com.tw/v1/opendata/t187ap04_L',
 'drewry':'https://www.drewry.co.uk/supply-chain-advisors/supply-chain-expertise/world-container-index-assessed-by-drewry','scfi_te':'https://tradingeconomics.com/commodity/containerized-freight-index','baltic':'https://www.balticexchange.com/en/data-services/market-information0/dry-services.html','eia_hormuz':'https://www.eia.gov/todayinenergy/detail.php?id=65544',
 'ups_8k':'https://www.sec.gov/Archives/edgar/data/1090727/000162828026043196/ups-20260613.htm','ups_healthcare':'https://about.ups.com/us/en/newsroom/press-releases/customer-first/ups-extends-complex-healthcare-logistics-lead-with--48-million-i.html','ups_ir':'https://investors.ups.com/sec-filings/all-sec-filings',
 'fdx_8k':'https://www.sec.gov/Archives/edgar/data/0001048911/000104891126000050/fdx-20260623.htm','fdx_earn':'https://www.sec.gov/Archives/edgar/data/1048911/000104891126000050/fdx-earningsreleasefy2026q4.htm','fdxf':'https://www.sec.gov/Archives/edgar/data/0002082247/000162828026045515/fdxf-q4fy2026juneearningsr.htm',
 'matx_div':'https://www.prnewswire.com/news-releases/matson-increases-quarterly-dividend-to-0-38-per-share-302811160.html','gnk_629':'https://www.globenewswire.com/news-release/2026/06/29/3318793/','gnk_617':'https://www.stocktitan.net/sec-filings/GNK/sc-to-t-a-genco-shipping-trading-ltd-amended-third-party-tender-offer-5494151630e5.html',
 'xpo_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001166003.json','chrw_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001043277.json','expd_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000746515.json','gxo_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001852244.json','jbh_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000728535.json','matx_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000003453.json','zim_ir':'https://www.zim.com/investors/press-releases','dac_sec':'https://www.sec.gov/edgar/browse/?CIK=1369241&owner=exclude','sblk_ir':'https://www.starbulk.com/gr/en/press-releases/','gogl_ir':'https://www.goldenocean.bm/category/press-releases/','gnk_ir':'https://investors.gencoshipping.com/','kex_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000056047.json'
}
def fetch_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 cph-investment-report/1.0'})
    with urllib.request.urlopen(req,timeout=25) as r: return json.loads(r.read().decode('utf-8-sig'))
def e(x): return html.escape(str(x if x is not None else ''), quote=True)
def num(x):
    try: return int(str(x).replace(',','').strip())
    except Exception: return None
def pct(x):
    try: return f"{float(str(x).replace(',','').replace('%','').strip()):+.2f}%"
    except Exception: return e(x)
def pct_class(x):
    try: return 'pos' if float(str(x).replace(',','').replace('%',''))>=0 else 'neg'
    except Exception: return ''
def nt_100m(v):
    n=num(v); return '' if n is None else f'{n/100000:.2f} 億'
def roc_month(s):
    s=str(s)
    return f'{int(s[:3])+1911}-{s[3:5]}' if len(s)>=5 and s[:3].isdigit() else s
def roc_date(s):
    s=str(s).strip()
    if len(s)==7 and s[:3].isdigit(): return f'{int(s[:3])+1911}-{s[3:5]}-{s[5:7]}'
    if len(s)==8 and s.isdigit(): return f'{s[:4]}-{s[4:6]}-{s[6:8]}'
    return s
def short(t,n=115):
    t=re.sub(r'\s+',' ',str(t)).strip(); return t[:n]+('…' if len(t)>n else '')
def src(label,url): return f'<span class="source">來源：<a href="{e(url)}">{e(label)}</a></span>'
rev={}; mat=[]; fetch_notes=[]
for key,label in [('twse_rev','TWSE 官方資料'),('tpex_rev','TPEx 官方資料')]:
    try:
        data=fetch_json(URLS[key]); fetch_notes.append(f'{key}:{len(data)}')
        for r in data:
            c=str(r.get('公司代號') or '').strip()
            if c in WATCH: r['_src']=label; r['_url']=URLS[key]; rev[c]=r
    except Exception as ex: fetch_notes.append(f'{key}:ERR {type(ex).__name__}')
for key,label in [('twse_mat','TWSE 官方資料'),('tpex_mat','TPEx 官方資料')]:
    try:
        data=fetch_json(URLS[key]); fetch_notes.append(f'{key}:{len(data)}')
        for r in data:
            c=str(r.get('公司代號') or r.get('SecuritiesCompanyCode') or '').strip()
            if c in WATCH:
                mat.append({'code':c,'name':r.get('公司名稱') or r.get('CompanyName') or NAME.get(c,''),'date':roc_date(r.get('發言日期') or r.get('Date') or r.get('出表日期') or ''),'title':(r.get('主旨 ') or r.get('主旨') or r.get('Subject') or '').strip(),'fact':roc_date(r.get('事實發生日') or ''),'src':label,'url':URLS[key]})
    except Exception as ex: fetch_notes.append(f'{key}:ERR {type(ex).__name__}')
# Upstream QC from injected job text: today Taipei date 2026-07-02; DR_STATUS partial, not failed.
upstream='07:55 deep research 為今日台北日期 2026-07-02，DR_STATUS=partial；非 stale/failed。已明示中小型月營收、部分 7/1 收盤與 UPS 8-K 缺口，本報以 TWSE/TPEx 官方資料與 SEC/公司來源快速補查；查不到者列資料缺口。'
summary_cards=[
 ('neutral','上游 QC 通過','注入上游為今日台北日期、DR_STATUS=partial 且非 failed；可作為線索，但不把上游缺口補成推估值。','上游深度研究 / 本報官方補查'),
 ('good','貨櫃運價仍居高檔','Drewry 6/25 WCI 為 US$4,166/FEU、週增 5%；SCFI 7/1 仍約 3,239.64 點，月增約 25.97%，7 月 GRI 與旺季前拉貨仍是主軸。','Drewry / TradingEconomics'),
 ('neutral','台股官方重大訊息有兩筆新增','7/1 陽明公告取得新造貨櫃；遠雄港公告內部稽核主管留職停薪及職務代理人，屬公司治理/人事事項。','TWSE 官方資料'),
 ('good','5 月月營收已用官方補查','TWSE/TPEx 官方月營收資料已覆蓋固定 27 檔 watchlist；最新月別仍為 2026-05。','TWSE / TPEx 官方資料'),
 ('risk','美股端焦點：FDX/FedEx Freight 與 UPS 8-K','FDX/FedEx Freight 6 月下旬揭露分拆後與 Q4 FY26 業績；UPS 6/13 8-K 為董事 Eva Boratto 辭任，非營運業績公告。','SEC 官方資料'),
 ('warn','產業風險未解除','波灣/荷姆茲風險影響油輪、能源與航空燃油成本；BDI 與貨櫃指數走勢分歧，散裝與貨櫃需分開觀察。','能源官方資料 / Baltic Exchange')]
industry_cards=[
 ('good','WCI / SCFI','WCI 6/25 跳升 5% 至 US$4,166/40呎櫃；SCFI 7/1 約 3,239.64 點且近一月上漲約 25.97%。',URLS['drewry'],'產業數據'),
 ('warn','BDI','BDI 與 Capesize 波動仍可能使散裝股表現與貨櫃股分歧；本報採 Baltic Exchange 官方來源作後續校準。',URLS['baltic'],'產業數據'),
 ('risk','荷姆茲海峽','地緣風險對油輪與能源物流可能正向，但對航空燃油與整體供應鏈成本為反向壓力。',URLS['eia_hormuz'],'能源官方資料'),
 ('neutral','航空/貨運','航空族群 5 月營收高檔；後續重點為暑期客運、AI 伺服器空運、油價與匯率。',URLS['twse_rev'],'TWSE 官方資料')]
# prefer official newly fetched events, then supplemental tracked events
mat_sorted=sorted(mat, key=lambda x: x.get('date',''), reverse=True)
supp_tw=[('2026-06-26','2618 長榮航','桃園—華盛頓 DC 直飛開航','每週四班、B787-9 執飛；北美線與暑期客運需求為航空族群觀察重點。','公司公告','https://www.evaair.com/zh-tw/about-eva-air/news/news-releases/2026-02-11-evaair-new-route-taipei-to-washington-dc.html'),('2026-06-23','2641 正德','現金股利 0.5 元除息基準日','股利時程事項，非營運基本面變動；已摘要列示。','公開資訊彙整','https://goodinfo.tw/StockInfo/StockDividendSchedule.asp?STOCK_ID=2641'),('2026-06-17','2603 長榮','現金股利 16 元除息','除息交易日 6/17、基準日 6/26、發放日 7/17；填息與運價同步觀察。','公開資訊彙整','https://goodinfo.tw/tw/StockDividendSchedule.asp?STOCK_ID=2603')]
us_events=[
 ('UPS','2026-06-13','UPS 8-K：董事 Eva Boratto 通知公司辭任董事會成員；屬治理事項，不解讀為營運財務公告。','SEC 官方資料',URLS['ups_8k']),
 ('UPS','2026-06-22','投資 US$48M 強化 27 個全球溫控冷鏈 cross-dock，聚焦 GLP-1、生物製劑等醫療物流。','公司公告',URLS['ups_healthcare']),
 ('FDX','2026-06-23','Q4 FY26 營收 US$25.0B、調整 EPS US$6.31；CY2026 過渡期指引調整 EPS US$16.90–18.10。','SEC 官方資料',URLS['fdx_8k']),
 ('FDXF','2026-06-25','FedEx Freight 分拆後首份季報：Q4 FY26 營收 US$2.4B（+4.8%）、調整營業利益 US$363M（-23.9%）。','SEC 官方資料',URLS['fdxf']),
 ('MATX','2026-06-25','Q3 季股利調升至 US$0.38/股（QoQ +5.6%）；9/3 支付、8/6 record。','公司公告',URLS['matx_div']),
 ('GNK','2026-06-29','Diana 延長 tender 至 7/10 17:00 ET；Genco 重申反對。至 6/26 已 tender 約 10.58M 股、占 28.4%。','公司公告',URLS['gnk_629'])]
us_fin=[('UPS','FY2026 Q1 / 最新 8-K','Revenue US$21.2B；Adj EPS US$1.07；6/13 8-K 為董事辭任。','公司 IR / SEC',URLS['ups_ir']),('FDX','FY2026 Q4','Revenue US$25.0B；Adj EPS US$6.31；FY26 Adj EPS US$20.24。','SEC 官方資料',URLS['fdx_earn']),('XPO','FY2026 Q1','Revenue 約 US$2.10B；Adj EPS 約 US$1.01；LTL 量價仍是觀察重點。','SEC 官方資料',URLS['xpo_sec']),('CHRW','FY2026 Q1','Revenue 約 US$4.01B；貨代/經紀景氣仍待量價復甦。','SEC 官方資料',URLS['chrw_sec']),('EXPD','FY2026 Q1','Revenue 約 US$2.78B；國際貨代需求與費率口徑續追。','SEC 官方資料',URLS['expd_sec']),('GXO','FY2026 Q1','Revenue 約 US$3.30B；合約物流新約與自動化效率為核心。','SEC 官方資料',URLS['gxo_sec']),('JBHT','FY2026 Q1','Revenue 約 US$2.92B；多式聯運與 Dedicated 需求為核心。','SEC 官方資料',URLS['jbh_sec']),('MATX','FY2026 Q1 / 股利','Revenue 約 US$758M；6/25 宣布調高季股利。','SEC / 公司 IR',URLS['matx_sec']),('ZIM','最新可得','以公司 IR 最新財報/6-K、運價與租船成本為主；本報未擷取到 7/1 新重大公告。','公司 IR',URLS['zim_ir']),('DAC','最新可得','以 20-F/6-K、charter backlog 與貨櫃船租金為主。','SEC 官方資料',URLS['dac_sec']),('SBLK','最新可得','散裝船隊處分、股利政策與 BDI 敏感度為觀察重點。','公司 IR',URLS['sblk_ir']),('GOGL','最新可得','固定追蹤清單保留；需注意公司合併/上市口徑與 IR 更新。','公司 IR',URLS['gogl_ir']),('GNK','2026 Q1 / 收購戰','Q1 revenue 約 US$114M；Diana tender/董事會反對為短線公告主軸。','公司 IR',URLS['gnk_ir']),('KEX','FY2026 Q1','Revenue 約 US$844M；內河運輸與能源/農產品物流需求為重點。','SEC 官方資料',URLS['kex_sec'])]
css='''@page{size:A4;margin:11mm}*{box-sizing:border-box}body{margin:0;font-family:"PingFang TC","Heiti TC","Noto Sans TC","Microsoft JhengHei",sans-serif;background:#f4f7fb;color:#172033;font-size:12.5px;line-height:1.52}.hero{background:linear-gradient(135deg,#075ba8,#10a9df);color:#fff;border-radius:22px;padding:24px 28px;margin-bottom:16px;box-shadow:0 8px 24px rgba(5,70,120,.22)}h1{font-size:30px;margin:0 0 6px;letter-spacing:.04em}h2{font-size:19px;color:#0f3b66;margin:18px 0 10px}h3{font-size:14.5px;margin:4px 0 6px}.meta{opacity:.95}.toc{display:flex;flex-wrap:wrap;gap:7px;margin:0 0 12px}.toc span{background:#fff;border:1px solid #dbe7f5;border-radius:999px;padding:5px 10px;color:#195a91;font-weight:700}.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.grid.one{grid-template-columns:1fr}.grid.three{grid-template-columns:repeat(3,1fr)}.card{break-inside:avoid;background:#fff;border:1px solid #e2e9f3;border-radius:16px;padding:12px 14px;margin:0 0 10px;box-shadow:0 2px 8px rgba(42,67,101,.08)}.risk{border-left:5px solid #ef4444}.good{border-left:5px solid #16a34a}.warn{border-left:5px solid #f97316}.neutral{border-left:5px solid #3b82f6}.badge{display:inline-block;background:#e8f1ff;color:#114b88;border-radius:999px;padding:3px 9px;font-size:11.5px;font-weight:700;margin-bottom:6px}.source{display:block;margin-top:8px;color:#64748b;font-size:11.5px}.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:5px 8px;margin-top:6px}.stat{background:#f8fafc;border-radius:10px;padding:6px}.stat span{display:block;color:#64748b;font-size:10.5px}.stat strong{font-size:12px}.stat small{display:block;color:#64748b}.pos strong,.pos{color:#15803d}.neg strong,.neg{color:#b91c1c}ul{margin:6px 0 0 18px;padding:0}li{margin:4px 0}p{margin:4px 0}.footer{margin-top:18px;color:#475569;font-size:12px}.src-list li{word-break:break-all;font-size:10.8px}.pagebreak{break-before:page}.mini{font-size:11.5px;color:#64748b}a{color:#2563eb;text-decoration:none}.fin-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}.fin{background:#fff;border:1px solid #e2e8f0;border-radius:13px;padding:9px;break-inside:avoid}.fin b{color:#0f3b66}'''
parts=[f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><title>航運物流股日報_{REPORT_DATE}</title><style>{css}</style></head><body>']
parts.append(f'<div class="hero"><h1>航運物流股日報</h1><div class="meta">報告日期：{REPORT_DATE}　產出時間：{GENERATED}<br>涵蓋：前一台股交易日/公告日 {PREV_TW}；前一美股交易日/公告日 {PREV_US}<br>資料狀態：{e(upstream)}</div></div>')
parts.append('<div class="toc"><span>今日重點</span><span>產業指標</span><span>台股重大訊息</span><span>月營收</span><span>美股公告</span><span>資料缺口</span></div>')
parts.append('<section><h2>今日重點</h2><div class="grid">')
for cls,t,txt,s in summary_cards: parts.append(f'<article class="card {cls}"><span class="badge">{e(t)}</span><p>{e(txt)}</p><span class="source">來源：{e(s)}</span></article>')
parts.append('</div></section><section><h2>產業與市場觀察</h2><div class="grid">')
for cls,t,txt,u,l in industry_cards: parts.append(f'<article class="card {cls}"><span class="badge">{e(t)}</span><p>{e(txt)}</p>{src(l,u)}</article>')
parts.append('</div></section><section><h2>台股重大訊息（短摘要）</h2><div class="grid one">')
if mat_sorted:
    for m in mat_sorted[:8]:
        tone='warn' if m['code']=='2609' else 'neutral'
        fact=f'；事實發生日 {m["fact"]}' if m.get('fact') else ''
        parts.append(f'<article class="card {tone}"><span class="badge">{e(m["date"])}｜{e(m["code"])} {e(m["name"])}</span><h3>{e(short(m["title"]))}</h3><p>官方重大訊息摘要{e(fact)}。治理/人事事項僅摘要，不展開全文。</p>{src(m["src"],m["url"])}</article>')
else: parts.append(f'<article class="card neutral"><span class="badge">官方重大訊息快速補查</span><p>本輪 TWSE/TPEx 官方重大訊息資料未擷取到固定名單新增列項。</p>{src("TWSE 官方資料",URLS["twse_mat"])}{src("TPEx 官方資料",URLS["tpex_mat"])}</article>')
for d,c,t,txt,l,u in supp_tw: parts.append(f'<article class="card neutral"><span class="badge">{e(d)}｜{e(c)}</span><h3>{e(t)}</h3><p>{e(txt)}</p>{src(l,u)}</article>')
parts.append('</div></section>')
parts.append('<section class="pagebreak"><h2>台股月營收（官方最新；單位：新台幣千元 / 億元）</h2><p class="mini">最新月營收公布期為 2026/05；尚未公布或官方未擷取者明列缺口，不以推估值補列。</p>')
for g,codes in GROUPS:
    parts.append(f'<h3>{e(g)}</h3><div class="grid three">')
    for code in codes:
        r=rev.get(code)
        if r:
            mon=r.get('營業收入-當月營收',''); cum=r.get('累計營業收入-當月累計營收',''); mom=r.get('營業收入-上月比較增減(%)',''); yoy=r.get('營業收入-去年同月增減(%)',''); cyoy=r.get('累計營業收入-前期比較增減(%)','')
            ccls='good' if (pct_class(yoy)=='pos' and pct_class(cyoy)=='pos') else 'warn'
            parts.append(f'''<article class="card {ccls}"><span class="badge">{code} {e(NAME.get(code,''))}</span><h3>{e(roc_month(r.get('資料年月','')))}</h3><div class="stats"><div class="stat"><span>單月營收</span><strong>{e(mon)}</strong><small>（{e(nt_100m(mon))}）</small></div><div class="stat {pct_class(mom)}"><span>MoM</span><strong>{pct(mom)}</strong></div><div class="stat {pct_class(yoy)}"><span>YoY</span><strong>{pct(yoy)}</strong></div><div class="stat"><span>累計營收</span><strong>{e(cum)}</strong><small>（{e(nt_100m(cum))}）</small></div><div class="stat {pct_class(cyoy)}"><span>累計 YoY</span><strong>{pct(cyoy)}</strong></div></div>{src(r['_src'],r['_url'])}</article>''')
        else: parts.append(f'<article class="card neutral"><span class="badge">{code} {e(NAME.get(code,""))}</span><h3>尚未公布 / 本次官方資料未擷取到</h3><p>不以推估值補列。</p>{src("TWSE/TPEx 官方資料",URLS["twse_rev"])}</article>')
    parts.append('</div>')
parts.append('</section><section><h2>美股重大公告 / 最新可得業績</h2><div class="grid">')
for tick,d,txt,l,u in us_events: parts.append(f'<article class="card {"risk" if tick in ("FDX","GNK") else "neutral"}"><span class="badge">{e(d)}｜{e(tick)}</span><p>{e(txt)}</p>{src(l,u)}</article>')
parts.append('</div><h3>最近一季 / 最新可得業績摘要</h3><div class="fin-grid">')
for tick,period,txt,l,u in us_fin: parts.append(f'<div class="fin"><b>{e(tick)}</b>｜{e(period)}<p>{e(txt)}</p>{src(l,u)}</div>')
parts.append('</div></section>')
missing=[]
if len(rev)<len(WATCH): missing.append('台股月營收仍有未擷取公司：'+', '.join([c for c in WATCH if c not in rev]))
missing += ['上游 deep research 為 partial：13 檔中小型 5 月營收、部分 7/1 精確收盤與 UPS 8-K 被標成缺口；本報已補官方月營收與 UPS 8-K 性質，但未完整補全收盤價。','產業日頻資料（SCFI/WCI/BDI/燃油）發布時間與引用口徑可能不同，後續以官方/交易所更新校正。','本報未擷取到所有美股固定清單在 7/1 的新 8-K/6-K；最新可得業績以 SEC companyfacts、公司 IR 與已知公告為準。']
parts.append('<section><h2>資料缺口與注意事項</h2><div class="grid">')
for m in missing: parts.append(f'<article class="card neutral"><span class="badge">注意</span><p>{e(m)}</p></article>')
parts.append('<article class="card neutral"><span class="badge">非投資建議</span><p>以上為公開資訊整理，非投資建議。</p></article></div></section>')
all_urls=set(URLS.values())
for row in supp_tw: all_urls.add(row[-1])
for row in us_events: all_urls.add(row[-1])
for row in us_fin: all_urls.add(row[-1])
parts.append('<section><h2>來源清單（完整 URL）</h2><div class="card"><ul class="src-list">')
for u in sorted(all_urls): parts.append(f'<li>{e(u)}</li>')
parts.append(f'</ul><p class="footer">QC trace: {e("; ".join(fetch_notes))}</p><p class="footer">以上為公開資訊整理，非投資建議。</p></div></section></body></html>')
HTML.write_text('\n'.join(parts),encoding='utf-8')
print(HTML)
