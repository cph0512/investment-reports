#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, urllib.request, html, pathlib, datetime, re, subprocess, shutil, os
TZ=datetime.timezone(datetime.timedelta(hours=8))
now=datetime.datetime.now(TZ)
REPORT_DATE=now.strftime('%Y-%m-%d')
GENERATED=now.strftime('%Y-%m-%d %H:%M Asia/Taipei')
PREV_TW='2026-07-06 / 最新公告日'
PREV_US='2026-07-06（美東）/ 最新公告日'
OUT=pathlib.Path('/Users/cph/investment-reports/reports/shipping-logistics')/REPORT_DATE
OUT.mkdir(parents=True, exist_ok=True)
HTML=OUT/'report.html'; PDF=OUT/'report.pdf'; ALT=OUT/f'航運物流股日報_{REPORT_DATE}.pdf'
WATCH='2603 2609 2615 2605 2606 2612 2617 2637 5608 2641 2607 2608 2611 2613 2636 2642 5601 5603 5604 5607 5609 1443 2610 2618 2646 2630 2645'.split()
NAME={'2603':'長榮','2609':'陽明','2615':'萬海','2605':'新興','2606':'裕民','2612':'中航','2617':'台航','2637':'慧洋-KY','5608':'四維航','2641':'正德','2607':'榮運','2608':'嘉里大榮','2611':'志信','2613':'中櫃','2636':'台驊投控','2642':'宅配通','5601':'台聯櫃','5603':'陸海','5604':'中連','5607':'遠雄港','5609':'中菲行','1443':'立益物流','2610':'華航','2618':'長榮航','2646':'星宇航空','2630':'亞航','2645':'長榮航太'}
GROUPS=[('貨櫃航運',['2603','2609','2615']),('散裝 / 海運',['2605','2606','2612','2617','2637','5608','2641']),('港埠 / 物流 / 貨代',['2607','2608','2611','2613','2636','2642','5601','5603','5604','5607','5609','1443']),('航空 / 航太維修',['2610','2618','2646','2630','2645'])]
URLS={
 'twse_rev':'https://openapi.twse.com.tw/v1/opendata/t187ap05_L','tpex_rev':'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O','twse_mat':'https://openapi.twse.com.tw/v1/opendata/t187ap04_L','tpex_mat':'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap04_O',
 'cnbc_redsea':'https://www.cnbc.com/2026/07/05/cargo-vessel-in-red-sea-reports-attack-uk-maritime-body-says.html','scfi_te':'https://tradingeconomics.com/commodity/containerized-freight-index','baltic':'https://www.balticexchange.com/en/data-services/market-information0/dry-services.html','sse':'https://en.sse.net.cn/indices/scfinew.jsp','indexbox':'https://www.indexbox.io/blog/suez-canal-fees-2026/','hellenic':'https://www.hellenicshippingnews.com/',
 'cmoney_yumin':'https://cmnews.com.tw/article/cmoneyaicurator-0f7d28e7-63e3-11f1-9c13-7a6555fc3e7f','kerry_udn':'https://money.udn.com/money/story/5607/9530604','kerry_ett':'https://finance.ettoday.net/news/3130859','china_air_udn':'https://udn.com/news/story/7241/9324937','eva_air_cnyes':'https://news.cnyes.com/news/id/6466400','starlux_storm':'https://www.storm.mg/article/11074570','egat_cmoney':'https://cmnews.com.tw/article/cmoneyairesearcher-7820e38c-74ed-11f1-8270-bab43c378b2d',
 'cnyes_2603':'https://news.cnyes.com/news/id/6489307','ctee_2609':'https://www.ctee.com.tw/news/20260609701703-430503','udn_2615':'https://udn.com/news/story/7252/9555751','ett_2637':'https://finance.ettoday.net/news/3194757','cnyes_5609':'https://news.cnyes.com/news/id/6504210','ett_2636':'https://finance.ettoday.net/news/3180565','cmoney_2642':'https://cmnews.com.tw/article/cmoneyaicurator-071f5d85-63e3-11f1-bafa-179722fa6608',
 'ups_8k':'https://www.sec.gov/Archives/edgar/data/1090727/000162828026043196/ups-20260613.htm','ups_healthcare':'https://about.ups.com/us/en/newsroom/press-releases/customer-first/ups-extends-complex-healthcare-logistics-lead-with--48-million-i.html','ups_ir':'https://investors.ups.com/sec-filings/all-sec-filings',
 'fdx_8k':'https://www.sec.gov/Archives/edgar/data/0001048911/000104891126000050/fdx-20260623.htm','fdx_earn':'https://www.sec.gov/Archives/edgar/data/1048911/000104891126000050/fdx-earningsreleasefy2026q4.htm','fdxf':'https://www.sec.gov/Archives/edgar/data/0002082247/000162828026045515/fdxf-q4fy2026juneearningsr.htm',
 'matx_div':'https://www.prnewswire.com/news-releases/matson-increases-quarterly-dividend-to-0-38-per-share-302811160.html','gnk_629':'https://www.globenewswire.com/news-release/2026/06/29/3318793/','zim_ir':'https://www.zim.com/investors/press-releases','zim_confirm':'https://investor.zim.com/','gnk_sec':'https://www.sec.gov/Archives/edgar/data/1326200/000119312526153402/d549415dsc14d9a.htm',
 'xpo_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001166003.json','chrw_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001043277.json','expd_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000746515.json','gxo_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001852244.json','jbh_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000728535.json','matx_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000003453.json','dac_sec':'https://www.sec.gov/edgar/browse/?CIK=1369241&owner=exclude','sblk_ir':'https://www.starbulk.com/gr/en/press-releases/','gogl_ir':'https://www.cmb.tech/','gnk_ir':'https://investors.gencoshipping.com/','kex_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000056047.json'}
def fetch_json(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 cph-investment-report/1.0 contact@example.com'})
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
    s=str(s); return f'{int(s[:3])+1911}-{s[3:5]}' if len(s)>=5 and s[:3].isdigit() else s
def roc_date(s):
    s=str(s).strip()
    if len(s)==7 and s[:3].isdigit(): return f'{int(s[:3])+1911}-{s[3:5]}-{s[5:7]}'
    if len(s)==8 and s.isdigit(): return f'{s[:4]}-{s[4:6]}-{s[6:8]}'
    return s
def short(t,n=112):
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
                title=(r.get('主旨 ') or r.get('主旨') or r.get('Subject') or '').strip()
                mat.append({'code':c,'name':r.get('公司名稱') or r.get('CompanyName') or NAME.get(c,''),'date':roc_date(r.get('發言日期') or r.get('Date') or r.get('出表日期') or ''),'title':title,'fact':roc_date(r.get('事實發生日') or ''),'src':label,'url':URLS[key]})
    except Exception as ex: fetch_notes.append(f'{key}:ERR {type(ex).__name__}')
# Manual latest 6月 figures already reported by public company/news sources before official open data rolled.
manual_rev={
 '2637':{'資料年月':'11506','營業收入-當月營收':'1878000','營業收入-上月比較增減(%)':'3.35','營業收入-去年同月增減(%)':'57.92','累計營業收入-當月累計營收':'9680000','累計營業收入-前期比較增減(%)':'32.32','_src':'公司公告轉載 / 產業媒體','_url':URLS['ett_2637'],'_note':'6月營業利益率 44%（媒體轉載公司自結）。'},
 '5609':{'資料年月':'11506','營業收入-當月營收':'3452000','營業收入-上月比較增減(%)':'6.53','營業收入-去年同月增減(%)':'35.26','累計營業收入-當月累計營收':'16583000','累計營業收入-前期比較增減(%)':'15.10','_src':'公司公告轉載 / 產業媒體','_url':URLS['cnyes_5609'],'_note':'近 4 年新高，AI 伺服器與半導體高單價貨支撐。'}
}
rev.update(manual_rev)
upstream='07:45 deep research 為今日台北日期 2026-07-07，DR_STATUS=partial（非 failed）；可作今日線索。缺口：6 月營收多數尚未公布、部分中小型股媒體覆蓋低、GOGL 已併入 CMB.TECH。'
summary_cards=[
 ('neutral','上游 QC 通過','注入上游為今日台北日期 2026-07-07、DR_STATUS=partial 且非 failed；本報採用並以 TWSE/TPEx 官方 Open Data 快速補查。','上游深度研究 / 官方補查'),
 ('risk','紅海攻擊復燃','7/5 Hodeida 西南約 30 浬散裝船遇攻擊，7/7 另傳 Eternity C 事件；Bab el Mandeb 通行仍遠低於戰前，地緣風險重新墊高繞航與保險成本。','CNBC / Lloyd\'s List / 產業媒體'),
 ('risk','蘇伊士 7/15 加徵臨時費','上游資料指蘇伊士運河多數船型加徵臨時過境費，油輪最高 +37%；對油輪與相關航線成本最直接。','IndexBox / Hellenic Shipping News'),
 ('good','運價高檔：SCFI 與 BDI 同強','SCFI 7/6 報 3,326.87 點，月增約 22%；BDI 突破 2,700，Capesize、Panamax 均走強。','Trading Economics / Baltic Exchange / SSE'),
 ('good','6月率先公布者動能佳','慧洋-KY 6 月營收 18.78 億、YoY +57.92%；中菲行 34.52 億、YoY +35.26%，均優於多數同業揭露節奏。','公司公告轉載 / 產業媒體'),
 ('risk','美股公告：FDX 與併購倒數','FDX FY26 Q4 EPS 優於指引並完成 Freight 分拆；ZIM 收購案推進、Diana 對 GNK 要約 7/10 到期。','SEC / 公司 IR')]
industry_cards=[
 ('risk','紅海 / Bab el Mandeb','Houthi 停止攻擊宣示後再現商船攻擊，若風險延續，亞洲—歐洲繞航與船期可靠度仍受壓。',URLS['cnbc_redsea'],'國際媒體'),
 ('risk','Suez Canal fee','7/15 起臨時費率變動將墊高部分船型通行成本，尤其油輪；需追蹤船東是否改道或轉嫁。',URLS['indexbox'],'產業媒體'),
 ('good','SCFI','7/6 SCFI 報 3,326.87 點，月增 22%、年增 88.6%；反映旺季提前拉貨與供給繞航支撐。',URLS['scfi_te'],'指數資料'),
 ('good','BDI / 散裝','BDI 綜合指數突破 2,700；Capesize 連四漲、Panamax 約 2,203 點，散裝情緒轉強。',URLS['baltic'],'交易所 / 產業資料'),
 ('neutral','貨櫃三雄 6月待公布','2603/2609/2615 5 月營收均 YoY 雙位數成長，6 月公告期限至 7/10 前，今日仍列缺口。',URLS['twse_rev'],'TWSE 官方資料'),
 ('good','空運貨代','中菲行 6 月創近 4 年新高，AI 伺服器與半導體急單支持空運高單價貨。',URLS['cnyes_5609'],'產業媒體')]
supp_tw=[
 ('2026-07-06','2603 長榮','TWSE 重大訊息','公司發布董事會/資金貸與相關公告；屬治理與例行資訊，摘要列示不展開全文。','TWSE 官方資料',URLS['twse_mat']),
 ('2026-07-06','2606 裕民','TWSE 重大訊息','公司發布公告事項；以官方重大訊息為準，非本報判定之新增財務指引。','TWSE 官方資料',URLS['twse_mat']),
 ('2026-07-06','5608 四維航','TWSE 重大訊息','公司發布公告事項；摘要處理，避免公告全文塞版。','TWSE 官方資料',URLS['twse_mat']),
 ('2026-07-15','2636 台驊投控','除權息預定日','每股現金股利 5 元；股利時程事項，非營運基本面變動。','公開資訊彙整',URLS['ett_2636']),
 ('2026-07-08','2618 長榮航','航線 / 除息觀察','6 月開航華盛頓 DC、擴充米蘭並評估北歐新據點；除息日程接近，需區分營運與股利事件。','產業媒體',URLS['eva_air_cnyes']),
 ('近期','2646 星宇航空','歐洲航線規劃','下半年歐洲首航候選米蘭/布拉格/赫爾辛基；A350-1000 首架年底交機。','產業媒體',URLS['starlux_storm']),
 ('近期','2645 長榮航太','維修 / 零組件','獲 B787 C Check、B737 MAX、A350 維修認證並打入空巴零組件供應鏈；媒體另提無人機/國防題材。','產業媒體',URLS['egat_cmoney']),
 ('2026/05/28','2608 嘉里大榮','股東會 / 收購','股東會通過收購嘉里國際物流、現金股利 1.65 元；屏東場站 7 月啟用。','公司公告轉載 / 媒體',URLS['kerry_udn'])]
us_events=[
 ('UPS','2026-06-13','8-K：董事 Eva Boratto 通知公司辭任董事會成員；治理事項，不作營運推論。','SEC 官方資料',URLS['ups_8k']),
 ('UPS','2026-06-22','投資 US$48M 強化 27 個全球溫控冷鏈 cross-dock，聚焦 GLP-1、生物製劑等醫療物流。','公司公告',URLS['ups_healthcare']),
 ('FDX','2026-06-23','FY26 Q4 營收約 US$24.5–25.0B、調整 EPS US$6.31；FY26 全年調整 EPS US$20.24，並完成 Freight 分拆。','SEC / 公司公告',URLS['fdx_earn']),
 ('FDXF','2026-06-25','FedEx Freight 分拆後首份季報：Q4 FY26 營收約 US$2.4B，FedEx 保留 19.9%。','SEC 官方資料',URLS['fdxf']),
 ('MATX','2026-06-25','Q3 季股利調升至 US$0.38/股（QoQ +5.6%）；9/3 支付、8/6 record。','公司公告',URLS['matx_div']),
 ('ZIM','2026-07-06','上游資料指 Hapag-Lloyd 現金收購案於 7/6 再確認照原計畫推進；仍以公司 IR/交易文件更新為準。','公司 IR',URLS['zim_confirm']),
 ('GNK','2026-06-29','Diana 延長 tender 至 7/10 17:00 ET；Genco 重申反對。至 6/26 已 tender 約 28.4%。','公司公告 / SEC',URLS['gnk_629'])]
us_fin=[('UPS','FY2026 Q1 / 最新 8-K','Revenue US$21.2B；Adj EPS US$1.07；6/13 8-K 為董事辭任。','公司 IR / SEC',URLS['ups_ir']),('FDX','FY2026 Q4','Revenue 約 US$24.5–25.0B；Adj EPS US$6.31；FY26 Adj EPS US$20.24；CY2026 指引 Adj EPS US$16.90–18.10。','SEC 官方資料',URLS['fdx_earn']),('XPO','FY2026 Q1','Revenue 約 US$2.10B；Adj EPS 約 US$1.01；LTL 量價為觀察重點。','SEC 官方資料',URLS['xpo_sec']),('CHRW','FY2026 Q1','Revenue 約 US$4.01B；貨代/經紀景氣仍待量價復甦。','SEC 官方資料',URLS['chrw_sec']),('EXPD','FY2026 Q1','Revenue 約 US$2.78B；國際貨代需求與費率口徑續追。','SEC 官方資料',URLS['expd_sec']),('GXO','FY2026 Q1','Revenue 約 US$3.30B；合約物流新約與自動化效率為核心。','SEC 官方資料',URLS['gxo_sec']),('JBHT','FY2026 Q1','Revenue 約 US$2.92B；多式聯運與 Dedicated 需求為核心。','SEC 官方資料',URLS['jbh_sec']),('MATX','FY2026 Q1 / 股利','Revenue 約 US$758M；6/25 宣布調高季股利。','SEC / 公司 IR',URLS['matx_sec']),('ZIM','收購案 / 最新可得','上游資料指 Hapag-Lloyd 每股 US$35 現金收購案推進；仍需以公司 IR 與交易文件核驗。','公司 IR',URLS['zim_ir']),('DAC','最新可得','以 20-F/6-K、charter backlog 與貨櫃船租金為主；本輪未見新增重大公告。','SEC 官方資料',URLS['dac_sec']),('SBLK','最新可得','散裝船隊處分、股利政策與 BDI 敏感度為觀察重點。','公司 IR',URLS['sblk_ir']),('GOGL','上市口徑變動','上游指出 GOGL 已於 2025/8 併入 CMB.TECH 下市，不再有獨立申報；追蹤口徑改看 CMB.TECH。','公司 IR',URLS['gogl_ir']),('GNK','2026 Q1 / 收購戰','Q1 revenue 約 US$114M；Diana tender/董事會反對為短線公告主軸。','公司 IR / SEC',URLS['gnk_ir']),('KEX','FY2026 Q1','Revenue 約 US$844M；內河運輸與能源/農產品物流需求為重點。','SEC 官方資料',URLS['kex_sec'])]
css='''@page{size:A4;margin:11mm}*{box-sizing:border-box}body{margin:0;font-family:"PingFang TC","Heiti TC","Noto Sans TC","Microsoft JhengHei",sans-serif;background:#f4f7fb;color:#172033;font-size:12.5px;line-height:1.52}.hero{background:linear-gradient(135deg,#075ba8,#10a9df);color:#fff;border-radius:22px;padding:24px 28px;margin-bottom:16px;box-shadow:0 8px 24px rgba(5,70,120,.22)}h1{font-size:30px;margin:0 0 6px;letter-spacing:.04em}h2{font-size:19px;color:#0f3b66;margin:18px 0 10px}h3{font-size:14.5px;margin:4px 0 6px}.meta{opacity:.95}.toc{display:flex;flex-wrap:wrap;gap:7px;margin:0 0 12px}.toc span{background:#fff;border:1px solid #dbe7f5;border-radius:999px;padding:5px 10px;color:#195a91;font-weight:700}.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.grid.one{grid-template-columns:1fr}.grid.three{grid-template-columns:repeat(3,1fr)}.card{break-inside:avoid;background:#fff;border:1px solid #e2e9f3;border-radius:16px;padding:12px 14px;margin:0 0 10px;box-shadow:0 2px 8px rgba(42,67,101,.08)}.risk{border-left:5px solid #ef4444}.good{border-left:5px solid #16a34a}.warn{border-left:5px solid #f97316}.neutral{border-left:5px solid #3b82f6}.badge{display:inline-block;background:#e8f1ff;color:#114b88;border-radius:999px;padding:3px 9px;font-size:11.5px;font-weight:700;margin-bottom:6px}.source{display:block;margin-top:8px;color:#64748b;font-size:11.5px}.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:5px 8px;margin-top:6px}.stat{background:#f8fafc;border-radius:10px;padding:6px}.stat span{display:block;color:#64748b;font-size:10.5px}.stat strong{font-size:12px}.stat small{display:block;color:#64748b}.pos strong,.pos{color:#15803d}.neg strong,.neg{color:#b91c1c}ul{margin:6px 0 0 18px;padding:0}li{margin:4px 0}p{margin:4px 0}.footer{margin-top:18px;color:#475569;font-size:12px}.src-list li{word-break:break-all;font-size:10.8px}.pagebreak{break-before:page}.mini{font-size:11.5px;color:#64748b}a{color:#2563eb;text-decoration:none}.fin-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}.fin{break-inside:avoid;background:#fff;border:1px solid #e2e9f3;border-radius:13px;padding:10px;margin-bottom:8px}@media print{body{background:#fff}.card,.fin{box-shadow:none}.hero{box-shadow:none}}'''
parts=[f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><title>航運物流股日報_{REPORT_DATE}</title><style>{css}</style></head><body>']
parts.append(f'<div class="hero"><h1>航運物流股日報</h1><div class="meta">報告日期：{REPORT_DATE}　產出時間：{GENERATED}<br>涵蓋：前一台股交易日/公告日 {PREV_TW}；前一美股交易日/公告日 {PREV_US}<br>資料狀態：{e(upstream)}</div></div>')
parts.append('<div class="toc"><span>今日重點</span><span>產業指標</span><span>台股重大訊息</span><span>月營收</span><span>美股公告</span><span>資料缺口</span></div>')
parts.append('<section><h2>今日重點</h2><div class="grid">')
for cls,t,txt,s in summary_cards: parts.append(f'<article class="card {cls}"><span class="badge">{e(t)}</span><p>{e(txt)}</p><span class="source">來源：{e(s)}</span></article>')
parts.append('</div></section><section><h2>產業與市場觀察</h2><div class="grid">')
for cls,t,txt,u,l in industry_cards: parts.append(f'<article class="card {cls}"><span class="badge">{e(t)}</span><p>{e(txt)}</p>{src(l,u)}</article>')
parts.append('</div></section><section><h2>台股重大訊息（短摘要）</h2><div class="grid one">')
mat_sorted=sorted(mat, key=lambda x: x.get('date',''), reverse=True)
if mat_sorted:
    for m in mat_sorted[:8]:
        tone='warn' if m['code'] in ('2609','2610','2618','2646') else 'neutral'
        fact=f'；事實發生日 {m["fact"]}' if m.get('fact') else ''
        title=short(m['title'] or '官方重大訊息')
        parts.append(f'<article class="card {tone}"><span class="badge">{e(m["date"])}｜{e(m["code"])} {e(m["name"])}</span><h3>{e(title)}</h3><p>官方重大訊息摘要{e(fact)}；治理/例行事項僅摘要，不展開全文。</p>{src(m["src"],m["url"])}</article>')
for d,c,t,txt,l,u in supp_tw: parts.append(f'<article class="card neutral"><span class="badge">{e(d)}｜{e(c)}</span><h3>{e(t)}</h3><p>{e(txt)}</p>{src(l,u)}</article>')
parts.append('</div></section>')
parts.append('<section class="pagebreak"><h2>台股月營收（官方最新；單位：新台幣千元 / 億元）</h2><p class="mini">多數 6 月營收尚未達完整公告；已見 6 月公開數字者列 6 月，其他列 TWSE/TPEx 官方最新月別或「尚未公布」。</p>')
for g,codes in GROUPS:
    parts.append(f'<h3>{e(g)}</h3><div class="grid three">')
    for code in codes:
        r=rev.get(code)
        if r:
            mon=r.get('營業收入-當月營收',''); cum=r.get('累計營業收入-當月累計營收',''); mom=r.get('營業收入-上月比較增減(%)',''); yoy=r.get('營業收入-去年同月增減(%)',''); cyoy=r.get('累計營業收入-前期比較增減(%)','')
            ccls='good' if (pct_class(yoy)=='pos' and pct_class(cyoy)=='pos') else 'warn'
            note=f'<p class="mini">{e(r.get("_note",""))}</p>' if r.get('_note') else ''
            parts.append(f'''<article class="card {ccls}"><span class="badge">{code} {e(NAME.get(code,''))}</span><h3>{e(roc_month(r.get('資料年月','')))}</h3><div class="stats"><div class="stat"><span>單月營收</span><strong>{e(mon)}</strong><small>（{e(nt_100m(mon))}）</small></div><div class="stat {pct_class(mom)}"><span>MoM</span><strong>{pct(mom)}</strong></div><div class="stat {pct_class(yoy)}"><span>YoY</span><strong>{pct(yoy)}</strong></div><div class="stat"><span>累計營收</span><strong>{e(cum)}</strong><small>（{e(nt_100m(cum))}）</small></div><div class="stat {pct_class(cyoy)}"><span>累計 YoY</span><strong>{pct(cyoy)}</strong></div></div>{note}{src(r['_src'],r['_url'])}</article>''')
        else: parts.append(f'<article class="card neutral"><span class="badge">{code} {e(NAME.get(code,""))}</span><h3>尚未公布 / 本次官方資料未擷取到</h3><p>不以推估值補列。</p>{src("TWSE/TPEx 官方資料",URLS["twse_rev"])}</article>')
    parts.append('</div>')
parts.append('</section><section><h2>美股重大公告 / 最新可得業績</h2><div class="grid">')
for tick,d,txt,l,u in us_events: parts.append(f'<article class="card {"risk" if tick in ("FDX","GNK","ZIM") else "neutral"}"><span class="badge">{e(d)}｜{e(tick)}</span><p>{e(txt)}</p>{src(l,u)}</article>')
parts.append('</div><h3>最近一季 / 最新可得業績摘要</h3><div class="fin-grid">')
for tick,period,txt,l,u in us_fin: parts.append(f'<div class="fin"><b>{e(tick)}</b>｜{e(period)}<p>{e(txt)}</p>{src(l,u)}</div>')
parts.append('</div></section>')
missing=['台股 2603/2609/2615 等多數公司 6 月營收尚未公布；法定期限前不以推估值替代。','上游 deep research 為 partial：部分中小型台股缺乏可引用專題報導；本報以官方 Open Data 與已公開來源補齊。','GOGL 已併入 CMB.TECH 後不再有獨立申報，後續美股固定清單需調整追蹤口徑。','本報未逐一重抓所有美股固定清單的最新 8-K/6-K；最新可得業績以 SEC companyfacts、公司 IR 與上游已核公告為準。']
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
chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
cmd=[chrome,'--headless=new','--disable-gpu','--no-pdf-header-footer',f'--print-to-pdf={PDF}',f'file://{HTML}']
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=120)
shutil.copyfile(PDF,ALT)
print(str(HTML)); print(str(PDF)); print(str(ALT))
