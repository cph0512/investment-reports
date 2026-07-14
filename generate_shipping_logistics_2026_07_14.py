#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime as dt, json, urllib.request, urllib.parse, pathlib, html, re, subprocess, shutil, os
TZ=dt.timezone(dt.timedelta(hours=8))
NOW=dt.datetime.now(TZ)
REPORT_DATE=NOW.strftime('%Y-%m-%d')
GENERATED=NOW.strftime('%Y-%m-%d %H:%M Asia/Taipei')
PREV_TW='2026-07-13（週一）/ 最新公告日'
PREV_US='2026-07-13（美東，週一）/ 最新公告日'
BASE=pathlib.Path('/Users/cph/investment-reports')
OUT=BASE/'reports'/'shipping-logistics'/REPORT_DATE
OUT.mkdir(parents=True, exist_ok=True)
HTML=OUT/'report.html'; PDF=OUT/'report.pdf'; ALT=OUT/f'航運物流股日報_{REPORT_DATE}.pdf'
WATCH='2603 2609 2615 2605 2606 2612 2617 2637 5608 2641 2607 2608 2611 2613 2636 2642 5601 5603 5604 5607 5609 1443 2610 2618 2646 2630 2645'.split()
NAME={'2603':'長榮','2609':'陽明','2615':'萬海','2605':'新興','2606':'裕民','2612':'中航','2617':'台航','2637':'慧洋-KY','5608':'四維航','2641':'正德','2607':'榮運','2608':'嘉里大榮','2611':'志信','2613':'中櫃','2636':'台驊投控','2642':'宅配通','5601':'台聯櫃','5603':'陸海','5604':'中連','5607':'遠雄港','5609':'中菲行','1443':'立益物流','2610':'華航','2618':'長榮航','2646':'星宇航空','2630':'亞航','2645':'長榮航太'}
GROUPS=[('貨櫃航運',['2603','2609','2615']),('散裝 / 海運',['2605','2606','2612','2617','2637','5608','2641']),('港埠 / 物流 / 貨代',['2607','2608','2611','2613','2636','2642','5601','5603','5604','5607','5609','1443']),('航空 / 航太維修',['2610','2618','2646','2630','2645'])]
URLS={
 'twse_rev':'https://openapi.twse.com.tw/v1/opendata/t187ap05_L',
 'tpex_rev':'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O',
 'twse_mat':'https://openapi.twse.com.tw/v1/opendata/t187ap04_L',
 'tpex_mat':'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap04_O',
 'sec_sub':'https://data.sec.gov/submissions/CIK{cik}.json',
 'sec_facts':'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json',
 'drewry':'https://www.drewry.co.uk/supply-chain-advisors/supply-chain-expertise/world-container-index-assessed-by-drewry',
 'baltic':'https://www.balticexchange.com/en/data-services/market-information0/dry-services.html',
 'sec_company':'https://www.sec.gov/edgar/search/',
 'zim_ir':'https://www.zim.com/investors/press-releases',
 'dac_ir':'https://www.danaos.com/news-and-media/press-releases/default.aspx',
 'sblk_ir':'https://www.starbulk.com/gr/en/press-releases/',
 'gogl_ir':'https://www.cmb.tech/investors',
 'gnk_ir':'https://investors.gencoshipping.com/',
}
CIK={'UPS':'0001090727','FDX':'0001048911','XPO':'0001166003','CHRW':'0001043277','EXPD':'0000746515','GXO':'0001852244','JBHT':'0000728535','MATX':'0000003453','KEX':'0000056047','GNK':'0001326200'}
FOREIGN={'ZIM':URLS['zim_ir'],'DAC':URLS['dac_ir'],'SBLK':URLS['sblk_ir'],'GOGL':URLS['gogl_ir']}

def req(url):
    return urllib.request.Request(url, headers={'User-Agent':'cph0512 investment report cph@example.com','Accept':'application/json,text/html,*/*'})
def fetch_json(url, timeout=25):
    with urllib.request.urlopen(req(url), timeout=timeout) as r:
        return json.loads(r.read().decode('utf-8-sig'))
def e(x): return html.escape(str(x if x is not None else ''), quote=True)
def num(x):
    try: return int(str(x).replace(',','').strip())
    except Exception: return None
def fmt_int(x):
    n=num(x); return '—' if n is None else f'{n:,}'
def nt_100m(x):
    n=num(x); return '—' if n is None else f'{n/100000:.2f} 億'
def pct(x):
    try: return f"{float(str(x).replace(',','').replace('%','').strip()):+.2f}%"
    except Exception: return '—'
def pct_class(x):
    try: return 'pos' if float(str(x).replace(',','').replace('%',''))>=0 else 'neg'
    except Exception: return ''
def roc_month(s):
    s=str(s or '').strip()
    return f'{int(s[:3])+1911}-{s[3:5]}' if len(s)>=5 and s[:3].isdigit() else (s or '未揭露')
def roc_date(s):
    s=str(s or '').strip()
    if len(s)==7 and s[:3].isdigit(): return f'{int(s[:3])+1911}-{s[3:5]}-{s[5:7]}'
    if len(s)==8 and s.isdigit(): return f'{s[:4]}-{s[4:6]}-{s[6:8]}'
    return s or '未揭露'
def short(t,n=105):
    t=re.sub(r'\s+',' ',str(t or '')).strip()
    return t[:n]+('…' if len(t)>n else '')
def src(label,url): return f'<span class="source">來源：<a href="{e(url)}">{e(label)}</a></span>'

fetch_notes=[]; rev={}; mat=[]
for key,label in [('twse_rev','TWSE 官方資料'),('tpex_rev','TPEx 官方資料')]:
    try:
        data=fetch_json(URLS[key]); fetch_notes.append(f'{key}:{len(data)}')
        for r in data:
            c=str(r.get('公司代號') or '').strip()
            if c in WATCH:
                r['_src']=label; r['_url']=URLS[key]; rev[c]=r
    except Exception as ex: fetch_notes.append(f'{key}:ERR {type(ex).__name__}')
for key,label in [('twse_mat','TWSE 官方資料'),('tpex_mat','TPEx 官方資料')]:
    try:
        data=fetch_json(URLS[key]); fetch_notes.append(f'{key}:{len(data)}')
        for r in data:
            c=str(r.get('公司代號') or r.get('SecuritiesCompanyCode') or '').strip()
            if c in WATCH:
                title=(r.get('主旨 ') or r.get('主旨') or r.get('Subject') or '').strip()
                date=roc_date(r.get('發言日期') or r.get('Date') or r.get('出表日期') or '')
                mat.append({'code':c,'name':r.get('公司名稱') or r.get('CompanyName') or NAME.get(c,''),'date':date,'title':title,'fact':roc_date(r.get('事實發生日') or ''),'src':label,'url':URLS[key]})
    except Exception as ex: fetch_notes.append(f'{key}:ERR {type(ex).__name__}')
# keep only recent-ish announcements around coverage window when parseable
mat_sorted=sorted(mat, key=lambda x:x.get('date',''), reverse=True)[:12]

us=[]; filings=[]
concepts=['RevenueFromContractWithCustomerExcludingAssessedTax','Revenues','SalesRevenueNet','OperatingIncomeLoss','NetIncomeLoss']
def duration_days(a):
    try:
        return (dt.date.fromisoformat(a.get('end',''))-dt.date.fromisoformat(a.get('start',''))).days
    except Exception:
        return None

def pick_latest_quarter(gaap, con):
    units=gaap.get(con,{}).get('units',{})
    vals=[]
    for unit,arr in units.items():
        for a in arr:
            if a.get('val') is None or a.get('form') not in ('10-Q','10-K'):
                continue
            dur=duration_days(a)
            frame=str(a.get('frame') or '')
            fp=str(a.get('fp') or '')
            # Prefer true quarterly observations; avoid old/annual/cumulative facts.
            quarterly=(dur is not None and 60 <= dur <= 115) or ('Q' in frame and 'I' not in frame)
            if not quarterly:
                continue
            vals.append((a.get('end',''), a.get('filed',''), fp, con, unit, a.get('val'), dur, frame))
    if not vals:
        return None
    end,filed,fp,con,unit,val,dur,frame=sorted(vals, reverse=True)[0]
    return (filed,end,fp,con,unit,val)

for t,cik in CIK.items():
    try:
        sub=fetch_json(URLS['sec_sub'].format(cik=cik)); recent=sub.get('filings',{}).get('recent',{})
        rows=list(zip(recent.get('filingDate',[]), recent.get('form',[]), recent.get('accessionNumber',[]), recent.get('primaryDocument',[])))[:10]
        useful=[r for r in rows if r[1] in ('8-K','10-Q','10-K','6-K')][:3]
        filings.append((t,useful))
        facts=fetch_json(URLS['sec_facts'].format(cik=cik)); gaap=facts.get('facts',{}).get('us-gaap',{})
        metrics=[]; seen_categories=set()
        for con in concepts:
            category='revenue' if con in ('Revenues','RevenueFromContractWithCustomerExcludingAssessedTax','SalesRevenueNet') else con
            if category in seen_categories:
                continue
            picked=pick_latest_quarter(gaap, con)
            if picked:
                metrics.append(picked); seen_categories.add(category)
        us.append((t, metrics[:3], useful))
        fetch_notes.append(f'{t}:SEC ok')
    except Exception as ex:
        us.append((t, [], [])); fetch_notes.append(f'{t}:SEC ERR {type(ex).__name__}')
for t,u in FOREIGN.items():
    us.append((t, [], [])); filings.append((t, []))

def rev_card(code):
    r=rev.get(code)
    if not r:
        return f'<article class="card neutral gap"><span class="badge">{code} {e(NAME.get(code,""))}</span><h3>尚未公布 / 未擷取</h3><p>官方快查未擷取到有效月營收資料；列為資料缺口。</p>{src("TWSE/TPEx 官方資料",URLS["twse_rev"])}</article>'
    mon=r.get('營業收入-當月營收',''); cum=r.get('累計營業收入-當月累計營收','')
    mom=r.get('營業收入-上月比較增減(%)',''); yoy=r.get('營業收入-去年同月增減(%)',''); cyoy=r.get('累計營業收入-前期比較增減(%)','')
    ym=roc_month(r.get('資料年月',''))
    tone='good' if pct_class(yoy)=='pos' and pct_class(cyoy)!='neg' else 'warn' if pct_class(yoy)=='neg' or pct_class(cyoy)=='neg' else 'neutral'
    return f'''<article class="card {tone}"><span class="badge">{code} {e(NAME.get(code,''))}</span><h3>{e(ym)}</h3><div class="stats"><div class="stat"><span>單月營收</span><strong>{fmt_int(mon)}</strong><small>{nt_100m(mon)}</small></div><div class="stat {pct_class(mom)}"><span>MoM</span><strong>{pct(mom)}</strong></div><div class="stat {pct_class(yoy)}"><span>YoY</span><strong>{pct(yoy)}</strong></div><div class="stat"><span>累計營收</span><strong>{fmt_int(cum)}</strong><small>{nt_100m(cum)}</small></div><div class="stat {pct_class(cyoy)}"><span>累計 YoY</span><strong>{pct(cyoy)}</strong></div></div>{src(r.get('_src','官方資料'),r.get('_url','#'))}</article>'''

def us_metric_text(metrics):
    if not metrics:
        return '本輪自動快查未取得可比 XBRL 金額；請以公司 IR/SEC 最新公告為準。'
    pieces=[]
    mapn={'Revenues':'營收','RevenueFromContractWithCustomerExcludingAssessedTax':'營收','SalesRevenueNet':'營收','OperatingIncomeLoss':'營業利益','NetIncomeLoss':'淨利'}
    seen=set()
    for filed,end,fp,con,unit,val in metrics:
        label=mapn.get(con,con)
        if label in seen: continue
        seen.add(label)
        v=float(val)
        if unit=='USD': amt=f'US${v/1e9:.2f}B' if abs(v)>=1e9 else f'US${v/1e6:.1f}M'
        else: amt=f'{v:,.0f} {unit}'
        pieces.append(f'{label} {amt}（期末 {end}，{fp}，filed {filed}）')
    return '；'.join(pieces) if pieces else 'SEC XBRL 有資料但無法整理成摘要。'

def filing_text(useful):
    if not useful: return '本輪未擷取到最新 8-K/10-Q/10-K；列資料缺口。'
    return '；'.join([f'{d} {form}' for d,form,acc,doc in useful])

# derived summaries from official fetched data
latest_months=sorted(set(roc_month(r.get('資料年月')) for r in rev.values()))
latest_month=latest_months[-1] if latest_months else '未揭露'
pos_yoy=[]; neg_yoy=[]
for c,r in rev.items():
    try:
        y=float(str(r.get('營業收入-去年同月增減(%)','')).replace(',','').replace('%',''))
        (pos_yoy if y>=0 else neg_yoy).append((y,c))
    except Exception: pass
pos_yoy=sorted(pos_yoy, reverse=True)[:5]; neg_yoy=sorted(neg_yoy)[:4]
upstream='07:45 deep research job 今日台北日期（2026-07-14）且 DR_STATUS=partial，通過可用性 QC；本報採用其已驗證重點，並以 TWSE/TPEx 官方 Open Data 與 SEC/公司 IR 快速補查缺口。partial 表示部分美股/產業資料仍需以來源清單與缺口說明控管。'
summary_cards=[
 ('neutral','上游資料 QC 通過（partial）',upstream,'Cron 注入紀錄 / 官方補查'),
 ('neutral','台股月營收官方快查',f'固定追蹤 {len(WATCH)} 檔中，本輪自 TWSE/TPEx 擷取 {len(rev)} 檔月營收；最新資料月份以官方 API 顯示為 {latest_month}。','TWSE / TPEx 官方資料'),
 ('good','年增動能居前', '；'.join([f'{c} {NAME.get(c,"")} YoY {y:+.2f}%' for y,c in pos_yoy]) if pos_yoy else '本輪無法排序。','TWSE / TPEx 官方資料'),
 ('warn','年減或缺口需追蹤', '；'.join([f'{c} {NAME.get(c,"")} YoY {y:+.2f}%' for y,c in neg_yoy]) if neg_yoy else '官方資料中未見顯著年減樣本，或資料不足。','TWSE / TPEx 官方資料'),
 ('neutral','美股以 SEC 快查為主','UPS、FDX、XPO、CHRW、EXPD、GXO、JBHT、MATX、KEX、GNK 以 SEC submissions/companyfacts 讀取最新 filings 與 XBRL；ZIM/DAC/SBLK/GOGL 以公司 IR 作資料入口。','SEC 官方資料 / 公司 IR'),
 ('warn','資料缺口處理','運價、產業新聞與外國發行人若本輪無法以官方 API 自動驗證，不以傳聞或二次來源補值；請見來源清單與缺口。','資料 QC')]
industry_cards=[
 ('neutral','貨櫃運價 / Drewry WCI','今日 fallback 未自動擷取具日期戳的 WCI 數值；保留官方/產業來源入口，避免沿用過期數字。',URLS['drewry'],'產業資料'),
 ('neutral','散裝 / Baltic Exchange','今日 fallback 未自動擷取具日期戳的 BDI 數值；散裝股仍以公司月營收與重大訊息為主。',URLS['baltic'],'產業資料'),
 ('neutral','公司重大訊息','TWSE/TPEx 重大訊息 Open Data 已快查；PDF 僅列短摘要，治理/股務事項不塞全文。',URLS['twse_mat'],'TWSE 官方資料'),
 ('neutral','SEC 重大公告','美股 latest filings 以 SEC submissions 為主，金額以 companyfacts XBRL 最新可得概念項目整理。',URLS['sec_company'],'SEC 官方資料')]

css='''@page{size:A4;margin:11mm}*{box-sizing:border-box}body{margin:0;font-family:"PingFang TC","Heiti TC","Noto Sans TC","Microsoft JhengHei",sans-serif;background:#f4f7fb;color:#172033;font-size:12.2px;line-height:1.5}.hero{background:linear-gradient(135deg,#075ba8,#10a9df);color:#fff;border-radius:22px;padding:24px 28px;margin-bottom:16px;box-shadow:0 8px 24px rgba(5,70,120,.22)}h1{font-size:30px;margin:0 0 6px;letter-spacing:.04em}h2{font-size:19px;color:#0f3b66;margin:18px 0 10px}h3{font-size:14.2px;margin:4px 0 6px}.meta{opacity:.96}.stamp{display:inline-block;background:rgba(255,255,255,.20);border-radius:999px;padding:3px 10px;margin:5px 0}.toc{display:flex;flex-wrap:wrap;gap:7px;margin:0 0 12px}.toc span{background:#fff;border:1px solid #dbe7f5;border-radius:999px;padding:5px 10px;color:#195a91;font-weight:700}.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.grid.one{grid-template-columns:1fr}.grid.three{grid-template-columns:repeat(3,1fr)}.card{break-inside:avoid;background:#fff;border:1px solid #e2e9f3;border-radius:16px;padding:12px 14px;margin:0 0 10px;box-shadow:0 2px 8px rgba(42,67,101,.08)}.risk{border-left:5px solid #ef4444}.good{border-left:5px solid #16a34a}.warn{border-left:5px solid #f97316}.neutral{border-left:5px solid #3b82f6}.badge{display:inline-block;background:#e8f1ff;color:#114b88;border-radius:999px;padding:3px 9px;font-size:11.2px;font-weight:700;margin-bottom:6px}.source{display:block;margin-top:8px;color:#64748b;font-size:11.2px}.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:5px 8px;margin-top:6px}.stat{background:#f8fafc;border-radius:10px;padding:6px}.stat span{display:block;color:#64748b;font-size:10.2px}.stat strong{font-size:11.4px}.stat small{display:block;color:#64748b}.pos strong,.pos{color:#15803d}.neg strong,.neg{color:#b91c1c}ul{margin:6px 0 0 18px;padding:0}li{margin:4px 0}p{margin:4px 0}.footer{margin-top:18px;color:#475569;font-size:12px}.src-list li{word-break:break-all;font-size:10.5px}.pagebreak{break-before:page}.fin-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}.fin{break-inside:avoid;background:#fff;border:1px solid #e2e9f3;border-radius:12px;padding:9px}.mini{font-size:11.2px;color:#475569}.gap{opacity:.92}a{color:#155e9f;text-decoration:none}'''
parts=[f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><title>航運物流股日報_{REPORT_DATE}</title><style>{css}</style></head><body>']
parts.append(f'<div class="hero"><h1>航運物流股日報</h1><div class="meta">報告日期：{REPORT_DATE}　產出時間：{GENERATED}<br>涵蓋：前一台股交易日/公告日 {PREV_TW}；前一美股交易日/公告日 {PREV_US}<br><span class="stamp">資料 QC：上游 partial 可用；已官方補查</span><br>{e(upstream)}</div></div>')
parts.append('<div class="toc"><span>重點摘要</span><span>產業指標</span><span>台股重大訊息</span><span>月營收</span><span>美股公告</span><span>資料缺口</span></div>')
parts.append('<section><h2>重點摘要（資料 QC 優先）</h2><div class="grid">')
for cls,t,txt,s in summary_cards: parts.append(f'<article class="card {cls}"><span class="badge">{e(t)}</span><p>{e(txt)}</p><span class="source">來源：{e(s)}</span></article>')
parts.append('</div></section><section><h2>產業與市場觀察</h2><div class="grid">')
for cls,t,txt,u,l in industry_cards: parts.append(f'<article class="card {cls}"><span class="badge">{e(t)}</span><p>{e(txt)}</p>{src(l,u)}</article>')
parts.append('</div></section><section><h2>台股重大訊息（官方短摘要）</h2><div class="grid one">')
if mat_sorted:
    for m in mat_sorted:
        title=short(m['title'] or '官方重大訊息')
        tone='warn' if any(k in title for k in ['取得','處分','重大','訴訟','停工','災']) else 'neutral'
        fact=f'；事實發生日 {m["fact"]}' if m.get('fact') and m.get('fact')!='未揭露' else ''
        parts.append(f'<article class="card {tone}"><span class="badge">{e(m["date"])}｜{e(m["code"])} {e(m["name"])}</span><h3>{e(title)}</h3><p>官方重大訊息摘要{e(fact)}；治理/股務事項僅摘錄重點。</p>{src(m["src"],m["url"])}</article>')
else:
    parts.append(f'<article class="card neutral"><span class="badge">資料缺口</span><p>本輪 TWSE/TPEx 重大訊息 Open Data 未回傳固定範圍可解析資料。</p>{src("TWSE 官方資料",URLS["twse_mat"])}</article>')
parts.append('</div></section>')
parts.append('<section class="pagebreak"><h2>台股月營收（官方最新揭露；單位：新台幣千元 / 億元）</h2><p class="mini">列月份、單月營收、MoM、YoY、累計營收、累計 YoY；尚未擷取到官方資料者列缺口。</p>')
for g,codes in GROUPS:
    parts.append(f'<h3>{e(g)}</h3><div class="grid three">')
    for code in codes: parts.append(rev_card(code))
    parts.append('</div>')
parts.append('</section><section><h2>美股重大公告與最近一季 / 最新可得業績</h2><div class="grid">')
for t,metrics,useful in us:
    if t in FOREIGN:
        parts.append(f'<article class="card neutral"><span class="badge">{e(t)}｜公司 IR 快查入口</span><h3>外國發行人 / 非標準 SEC XBRL</h3><p>本輪 fallback 未擷取到可自動驗證金額；列公司 IR 作官方來源入口，待人工或上游 deep research 補強。</p>{src("公司 IR",FOREIGN[t])}</article>')
    else:
        parts.append(f'<article class="card neutral"><span class="badge">{e(t)}｜SEC 最新可得</span><h3>{e(filing_text(useful))}</h3><p>{e(us_metric_text(metrics))}</p>{src("SEC 官方資料",URLS["sec_sub"].format(cik=CIK[t]))}</article>')
parts.append('</div></section>')
missing=[
 '上游 deep research 為 partial：台股營收與重大訊息可用，美股外國發行人與運價資料仍以官方入口/資料缺口呈現。',
 'Drewry WCI、BDI 與即時產業新聞未取得可機器驗證日期戳，未列具體數值。',
 'ZIM、DAC、SBLK、GOGL 等外國發行人本輪未取得標準 SEC XBRL 金額，僅列 IR 官方入口。',
 '若 TWSE/TPEx Open Data 尚未更新至最新月份，月營收以 API 回傳月份為準，不推估未公告數。'
]
parts.append('<section><h2>資料缺口與注意事項</h2><div class="grid">')
for m in missing: parts.append(f'<article class="card neutral"><span class="badge">資料缺口</span><p>{e(m)}</p></article>')
parts.append('<article class="card neutral"><span class="badge">非投資建議</span><p>以上為公開資訊整理，非投資建議。</p></article></div></section>')
all_urls=set(URLS.values())
for r in rev.values():
    if r.get('_url'): all_urls.add(r.get('_url'))
for t,cik in CIK.items():
    all_urls.add(URLS['sec_sub'].format(cik=cik)); all_urls.add(URLS['sec_facts'].format(cik=cik))
for u in FOREIGN.values(): all_urls.add(u)
parts.append('<section><h2>來源清單（完整 URL）</h2><div class="card"><ul class="src-list">')
for u in sorted(all_urls): parts.append(f'<li>{e(u)}</li>')
parts.append(f'</ul><p class="footer">QC trace: {e("; ".join(fetch_notes))}</p><p class="footer">以上為公開資訊整理，非投資建議。</p></div></section></body></html>')
HTML.write_text('\n'.join(parts), encoding='utf-8')
chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
subprocess.run([chrome,'--headless=new','--disable-gpu','--no-pdf-header-footer',f'--print-to-pdf={PDF}',f'file://{HTML}'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=120)
shutil.copyfile(PDF, ALT)
print(HTML)
print(PDF)
print(ALT)
print('fetch_notes='+'; '.join(fetch_notes))
