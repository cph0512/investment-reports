#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, urllib.request, html, pathlib, datetime, re, subprocess, shutil, os
TZ=datetime.timezone(datetime.timedelta(hours=8))
now=datetime.datetime.now(TZ)
REPORT_DATE=now.strftime('%Y-%m-%d')
GENERATED=now.strftime('%Y-%m-%d %H:%M Asia/Taipei')
PREV_TW='2026-07-07 / 最新公告日'
PREV_US='2026-07-07（美東）/ 最新公告日'
OUT=pathlib.Path('/Users/cph/investment-reports/reports/shipping-logistics')/REPORT_DATE
OUT.mkdir(parents=True, exist_ok=True)
HTML=OUT/'report.html'; PDF=OUT/'report.pdf'; ALT=OUT/f'航運物流股日報_{REPORT_DATE}.pdf'
WATCH='2603 2609 2615 2605 2606 2612 2617 2637 5608 2641 2607 2608 2611 2613 2636 2642 5601 5603 5604 5607 5609 1443 2610 2618 2646 2630 2645'.split()
NAME={'2603':'長榮','2609':'陽明','2615':'萬海','2605':'新興','2606':'裕民','2612':'中航','2617':'台航','2637':'慧洋-KY','5608':'四維航','2641':'正德','2607':'榮運','2608':'嘉里大榮','2611':'志信','2613':'中櫃','2636':'台驊投控','2642':'宅配通','5601':'台聯櫃','5603':'陸海','5604':'中連','5607':'遠雄港','5609':'中菲行','1443':'立益物流','2610':'華航','2618':'長榮航','2646':'星宇航空','2630':'亞航','2645':'長榮航太'}
GROUPS=[('貨櫃航運',['2603','2609','2615']),('散裝 / 海運',['2605','2606','2612','2617','2637','5608','2641']),('港埠 / 物流 / 貨代',['2607','2608','2611','2613','2636','2642','5601','5603','5604','5607','5609','1443']),('航空 / 航太維修',['2610','2618','2646','2630','2645'])]
URLS={
 'twse_rev':'https://openapi.twse.com.tw/v1/opendata/t187ap05_L','tpex_rev':'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O','twse_mat':'https://openapi.twse.com.tw/v1/opendata/t187ap04_L','tpex_mat':'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap04_O',
 'marad':'https://www.maritime.dot.gov/msci/2026-006-various-regional-conflicts-and-increased-risk-vessel-operators','cnbc_redsea':'https://www.cnbc.com/2026/07/05/cargo-vessel-in-red-sea-reports-attack-uk-maritime-body-says.html','scfi_te':'https://tradingeconomics.com/commodity/containerized-freight-index','baltic':'https://www.balticexchange.com/en/data-services/market-information0/dry-services.html','sse':'https://en.sse.net.cn/indices/scfinew.jsp','indexbox':'https://www.indexbox.io/blog/suez-canal-fees-2026/','hellenic':'https://www.hellenicshippingnews.com/',
 'cmoney_yumin':'https://cmnews.com.tw/article/cmoneyaicurator-0f7d28e7-63e3-11f1-9c13-7a6555fc3e7f','kerry_udn':'https://money.udn.com/money/story/5607/9530604','kerry_ett':'https://finance.ettoday.net/news/3130859','china_air_udn':'https://udn.com/news/story/7241/9324937','eva_air_cnyes':'https://news.cnyes.com/news/id/6466400','starlux_storm':'https://www.storm.mg/article/11074570','egat_cmoney':'https://cmnews.com.tw/article/cmoneyairesearcher-7820e38c-74ed-11f1-8270-bab43c378b2d',
 'udn_2603_rev':'https://money.udn.com/money/story/5710/9613252','udn_2603_case':'https://udn.com/news/story/124943/9611228','ltn_2603_case':'https://news.ltn.com.tw/news/society/breakingnews/5495526','ct_2603_case':'https://www.chinatimes.com/newspapers/20260708000639-260110','cnyes_2603':'https://news.cnyes.com/news/id/6489307','ctee_2609':'https://www.ctee.com.tw/news/20260609701703-430503','udn_2615':'https://udn.com/news/story/7252/9555751','ett_2637':'https://finance.ettoday.net/news/3194757','cnyes_5609':'https://news.cnyes.com/news/id/6523389','ett_2636':'https://finance.ettoday.net/news/3180565','cmoney_2642':'https://cmnews.com.tw/article/cmoneyaicurator-071f5d85-63e3-11f1-bafa-179722fa6608',
 'ups_8k':'https://www.sec.gov/Archives/edgar/data/1090727/000162828026043196/ups-20260613.htm','ups_healthcare':'https://about.ups.com/us/en/newsroom/press-releases/customer-first/ups-extends-complex-healthcare-logistics-lead-with--48-million-i.html','ups_ir':'https://investors.ups.com/sec-filings/all-sec-filings',
 'fdx_8k':'https://www.sec.gov/Archives/edgar/data/0001048911/000104891126000050/fdx-20260623.htm','fdx_earn':'https://www.sec.gov/Archives/edgar/data/1048911/000104891126000050/fdx-earningsreleasefy2026q4.htm','fdxf':'https://www.sec.gov/Archives/edgar/data/0002082247/000162828026045515/fdxf-q4fy2026juneearningsr.htm',
 'matx_div':'https://www.prnewswire.com/news-releases/matson-increases-quarterly-dividend-to-0-38-per-share-302811160.html','gnk_629':'https://www.globenewswire.com/news-release/2026/06/29/3319047/0/en/','zim_6k':'https://www.sec.gov/Archives/edgar/data/0001654126/000117891326003413/zk2635648.htm','zim_merger':'https://investors.zim.com/news/news-details/2026/ZIM-Provides-Update-on-Merger-Agreement/default.aspx','zim_ir':'https://www.zim.com/investors/press-releases','zim_confirm':'https://investor.zim.com/','gnk_sec':'https://www.sec.gov/Archives/edgar/data/1326200/000119312526153402/d549415dsc14d9a.htm',
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
 '2603':{'資料年月':'11506','營業收入-當月營收':'39141000','營業收入-上月比較增減(%)':'12.94','營業收入-去年同月增減(%)':'30.01','累計營業收入-當月累計營收':'191668000','累計營業收入-前期比較增減(%)':'-2.44','_src':'公司公告轉載 / 產業媒體','_url':URLS['udn_2603_rev'],'_note':'6月營收受關稅前拉貨、港口壅塞與繞航/保險成本支撐；同日另受內線交易案壓抑。'},
 '2637':{'資料年月':'11506','營業收入-當月營收':'1878000','營業收入-上月比較增減(%)':'3.35','營業收入-去年同月增減(%)':'57.92','累計營業收入-當月累計營收':'9680000','累計營業收入-前期比較增減(%)':'32.32','_src':'公司公告轉載 / 產業媒體','_url':URLS['ett_2637'],'_note':'6月營業利益率 44%，上半年稅前 EPS 4.11 元。'},
 '5609':{'資料年月':'11506','營業收入-當月營收':'3452000','營業收入-上月比較增減(%)':'6.53','營業收入-去年同月增減(%)':'35.26','累計營業收入-當月累計營收':'16583000','累計營業收入-前期比較增減(%)':'15.10','_src':'公司公告轉載 / 產業媒體','_url':URLS['cnyes_5609'],'_note':'連 3 個月刷新近 4 年單月新高，AI 伺服器與半導體高單價貨支撐。'}
}
rev.update(manual_rev)
upstream='07:45 deep research 為今日台北日期 2026-07-08，DR_STATUS=partial（非 failed）；可作今日線索。已用 TWSE/TPEx 官方 Open Data 與公開來源快速補查；缺口：部分 6 月營收公告仍在 7/10 前陸續揭露。'
summary_cards=[
 ('risk','長榮內線交易案為最高風險','北檢 7/6 搜索 10 處，董事張國華以 1.2 億元交保；媒體引述檢調稱涉 2023 年處分長榮航持股重訊延遲公告，擬制獲利約 21 億元、未實現增值逾 150 億元。','媒體 / 檢調新聞'),
 ('risk','紅海與荷姆茲風險同步升溫','Houthi 7/6–7/7 連續攻擊商船，且荷姆茲傳油輪遇襲；US MARAD 2026-006 提醒區域衝突與航行風險。','US MARAD / 國際媒體'),
 ('good','貨櫃運價旺季仍強','SCFI 7/4 收 3,326.87 點，WCI 7/2 收 US$4,530；美線報價週增約 10–11%，支撐貨櫃三雄與 ZIM/DAC 情緒。','SSE / Drewry / 上游研究'),
 ('good','長榮 6 月營收率先公布','2603 6 月合併營收 391.41 億元，MoM +12.94%、YoY +30.01%；上半年 1,916.68 億元，累計 YoY -2.44%。','公司公告轉載 / 產業媒體'),
 ('good','散裝與貨代營運亮點','慧洋-KY 上半年稅前 EPS 4.11 元、6月營利率 44%；中菲行 6 月營收 34.52 億元、連 3 個月近 4 年新高。','公司自結 / 產業媒體'),
 ('risk','美股併購事件待決','ZIM–Hapag-Lloyd 併購案政治阻力升溫；GNK/DSX tender offer 延至 7/10 17:00 NY。','SEC / 公司公告')]
industry_cards=[
 ('risk','紅海 / Bab el Mandeb','Magic Seas 與 Eternity C 事件顯示 Houthi 威脅重新外溢至散裝船；若保險與護航成本上升，繞航與船期可靠度仍受壓。',URLS['cnbc_redsea'],'國際媒體'),
 ('risk','荷姆茲 / 中東能源航道','上游資料稱 7/7 兩船遭火箭攻擊、卡達 LNG 油輪起火；需追蹤油價、LNG 與海運保費。',URLS['marad'],'官方航行警示'),
 ('good','SCFI / WCI','SCFI 7/4 報 3,326.87 點，月增 22%、年增 88.65%；Drewry WCI 7/2 報 US$4,530、週增 9%。',URLS['sse'],'指數資料'),
 ('good','BDI / 散裝','BDI 7 月初升至 2,717 點、週增 7.6%，Capesize 約 4,100 點；散裝股營運槓桿改善。',URLS['baltic'],'交易所 / 產業資料'),
 ('risk','治理風險與股價','長榮內線交易案短期壓抑市場評價；需區分基本面營收利多與治理/司法風險折價。',URLS['udn_2603_case'],'媒體'),
 ('good','空運貨代','中菲行 6 月營收 34.52 億元，AI 伺服器與半導體高單價貨支撐空運；華航 7/1 下調貨運燃油附加費。',URLS['cnyes_5609'],'產業媒體')]
supp_tw=[
 ('2026-07-07','2603 長榮','6 月營收','合併營收 391.41 億元、MoM +12.94%、YoY +30.01%；上半年累計 1,916.68 億元、YoY -2.44%。','公司公告轉載 / 產業媒體',URLS['udn_2603_rev']),
 ('2026-07-06','2603 長榮','治理 / 司法風險','北檢指揮調查局搜索 10 處；董事張國華 1.2 億元交保，案涉 2023 年處分長榮航持股重大訊息延遲公告。','媒體',URLS['udn_2603_case']),
 ('2026-07-06','5609 中菲行','6 月營收','6 月營收 34.52 億元，MoM +6.53%、YoY +35.26%；上半年 165.83 億元、YoY +15.1%。','公司公告轉載 / 產業媒體',URLS['cnyes_5609']),
 ('2026-07 上旬','2637 慧洋-KY','自結營運','6 月營收 18.78 億元、YoY +58%；上半年稅前 EPS 4.11 元；6 月營業利益率 44%。','公司自結轉載 / 產業媒體',URLS['ett_2637']),
 ('2026-06-26','2618 長榮航','航線','開航桃園—華盛頓 DC 每週四班，北美航點增至 10 個、每週往返 98 班。','公司公告 / 媒體','https://udn.com/news/story/7266/9590599'),
 ('2026-06-18','2610 華航','貨運燃油附加費','7/1 起長程每公斤 84→62 元、短程 29→21 元；若油價低檔有利毛利但附加費收入下修。','公司公告轉載 / 媒體','https://www.ctee.com.tw/news/20260618700742-430503'),
 ('2026-06-12','2610 華航','股利時程','每股現金股利 0.82 元，除息 7/10、發放 8/14；屬股利時程事項。','公開資訊彙整',URLS['twse_mat']),
 ('2026-05-28','2608 嘉里大榮','收購 / 股東會','股東會通過收購嘉里國際物流 100% 股權案，交易對價約 26 億元；摘要列示。','公司公告轉載 / 媒體',URLS['kerry_udn'])]
us_events=[
 ('ZIM','2026-07-07','6-K 更新併購審查；上游稱 Netanyahu 反對 Hapag-Lloyd 交易、政治阻力升溫；新 CEO Dr. Chen Lichtenstein 7/1 上任。','SEC / 公司 IR',URLS['zim_6k']),
 ('FDX','2026-07-07','季度現金股利 US$1.22/股（+5%）支付；另 7/9 為 US$4.15B 債券 tender offer Early Tender Time。','SEC / 公司公告',URLS['fdx_8k']),
 ('JBHT','2026-07-01','公告 Q2 2026 財報將於 7/15 盤後發布，為美國陸運/多式聯運旺季前重要觀察點。','公司公告','https://www.businesswire.com/news/home/20260701126804/en/'),
 ('GNK','2026-06-29','Diana 延長 tender offer 至 7/10 17:00 NY；已 tender 28.4%；Genco 董事會重申拒絕。','公司公告 / SEC',URLS['gnk_629']),
 ('GOGL/CMB.TECH','2026-06-29','CMB.TECH 出售兩艘 Suezmax（Brest、Brugge），預計 Q3 2026 認列約 US$100.5M 資本利得。','公司公告','https://www.globenewswire.com/news-release/2026/06/29/3318658/0/en/cmb-tech-fleet-update.html'),
 ('KEX','2026-07 上旬','公告 Q2 2026 財報日為 7/29；內河油品、化工與乾貨 barge 需求為焦點。','公司 IR','https://investors.kirbycorp.com/news-releases/news-release-details/kirby-corporation-announces-date-2026-second-quarter-earnings')]
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
missing=['台股除 2603、2637、5609 等已揭露 6 月數字外，多數公司 6 月營收仍待 7/10 前公告；不以推估值替代。','上游 deep research 為 partial：部分中小型台股缺乏可引用專題報導；本報以官方 Open Data 與已公開來源補齊。','GOGL 已併入 CMB.TECH 後不再有獨立申報，後續美股固定清單需調整追蹤口徑。','本報以 07:45 deep research、SEC/公司 IR 與官方/公開資料補查為準；若公司公告頁短暫不可用，列入資料缺口而不自行推估。']
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
