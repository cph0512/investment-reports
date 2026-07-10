#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, urllib.request, html, pathlib, datetime, re, subprocess, shutil, os, sys
TZ=datetime.timezone(datetime.timedelta(hours=8))
now=datetime.datetime.now(TZ)
REPORT_DATE=now.strftime('%Y-%m-%d')
GENERATED=now.strftime('%Y-%m-%d %H:%M Asia/Taipei')
PREV_TW='2026-07-09（週四）/ 最新公告日'
PREV_US='2026-07-09（美東，週四）/ 最新公告日'
OUT=pathlib.Path('/Users/cph/investment-reports/reports/shipping-logistics')/REPORT_DATE
OUT.mkdir(parents=True, exist_ok=True)
HTML=OUT/'report.html'; PDF=OUT/'report.pdf'; ALT=OUT/f'航運物流股日報_{REPORT_DATE}.pdf'
WATCH='2603 2609 2615 2605 2606 2612 2617 2637 5608 2641 2607 2608 2611 2613 2636 2642 5601 5603 5604 5607 5609 1443 2610 2618 2646 2630 2645'.split()
NAME={'2603':'長榮','2609':'陽明','2615':'萬海','2605':'新興','2606':'裕民','2612':'中航','2617':'台航','2637':'慧洋-KY','5608':'四維航','2641':'正德','2607':'榮運','2608':'嘉里大榮','2611':'志信','2613':'中櫃','2636':'台驊投控','2642':'宅配通','5601':'台聯櫃','5603':'陸海','5604':'中連','5607':'遠雄港','5609':'中菲行','1443':'立益物流','2610':'華航','2618':'長榮航','2646':'星宇航空','2630':'亞航','2645':'長榮航太'}
GROUPS=[('貨櫃航運',['2603','2609','2615']),('散裝 / 海運',['2605','2606','2612','2617','2637','5608','2641']),('港埠 / 物流 / 貨代',['2607','2608','2611','2613','2636','2642','5601','5603','5604','5607','5609','1443']),('航空 / 航太維修',['2610','2618','2646','2630','2645'])]
URLS={
 'twse_rev':'https://openapi.twse.com.tw/v1/opendata/t187ap05_L','tpex_rev':'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O','twse_mat':'https://openapi.twse.com.tw/v1/opendata/t187ap04_L','tpex_mat':'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap04_O',
 'cnyes_2603_rev':'https://news.cnyes.com/news/id/6525946','ctee_2603_rev':'https://www.ctee.com.tw/news/20260707701767-430503','ett_2609':'https://finance.ettoday.net/news/3198274','ltn_2609':'https://ec.ltn.com.tw/article/breakingnews/5499769','ett_2615':'https://finance.ettoday.net/news/3197671','ett_2637':'https://finance.ettoday.net/news/3194757','ct_2637':'https://www.chinatimes.com/newspapers/20260704000297-260206','udn_2606':'https://udn.com/news/story/7252/9547769','ett_2636':'https://finance.ettoday.net/news/3198284','yahoo_5609':'https://tw.stock.yahoo.com/news/ai出貨熱潮推升-中菲行6月營收年增35-3-連續3月刷新近四年高點-020247398.html','money_2630':'https://ww2.money-link.com.tw/RealtimeNews/NewsContent.aspx?SN=2389117002','ctee_2618':'https://www.ctee.com.tw/news/20260709701661-430503','udn_2618':'https://money.udn.com/money/story/5710/9618014','cnyes_2610':'https://news.cnyes.com/news/id/6059670','ett_2610_conflict':'https://finance.ettoday.net/news/2291978',
 'drewry_wci':'https://www.drewry.co.uk/supply-chain-advisors/supply-chain-expertise/world-container-index-assessed-by-drewry','scfi_te':'https://tradingeconomics.com/commodity/containerized-freight-index','baltic_te':'https://tradingeconomics.com/commodity/baltic','freightwaves_ups':'https://www.freightwaves.com/news/ups-navigates-amazon-draw-down-in-hard-pivot-to-premium-services','dat':'https://www.dat.com/blog','panama':'https://pancanal.com/en/maritime-services/customer-advisories/','zim_deal':'https://investors.zim.com/news/news-details/2026/ZIM-to-be-Acquired-by-Hapag-Lloyd-for-35-00-per-Share-in-Cash-at-Aggregate-Cash-Consideration-of-Approximately-4-2-Billion-New-Israeli-Company-New-ZIM-to-Acquire-Portion-of-ZIMs-Business/default.aspx','gnk_tender':'https://www.stocktitan.net/sec-filings/GNK/sc-to-t-a-genco-shipping-trading-ltd-amended-third-party-tender-offer-e1a1570f3fe7.html',
 'fdx_8k':'https://www.sec.gov/Archives/edgar/data/0001048911/000104891126000050/fdx-20260623.htm','fdxf':'https://www.sec.gov/Archives/edgar/data/0002082247/000162828026045515/fdxf-q4fy2026juneearningsr.htm','ups_ir':'https://investors.ups.com/sec-filings/all-sec-filings','xpo_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001166003.json','chrw_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001043277.json','expd_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000746515.json','gxo_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001852244.json','jbh_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000728535.json','matx_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000003453.json','dac_sec':'https://www.sec.gov/edgar/browse/?CIK=1369241&owner=exclude','sblk_ir':'https://www.starbulk.com/gr/en/press-releases/','gogl_ir':'https://www.cmb.tech/','gnk_ir':'https://investors.gencoshipping.com/','kex_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000056047.json','zim_ir':'https://www.zim.com/investors/press-releases','starlux':'https://www.chinatimes.com/realtimenews/20260610003520-260410','ci_order':'https://www.ctee.com.tw/news/20260526701943-430503'}

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
def short(t,n=118):
    t=re.sub(r'\s+',' ',str(t)).strip(); return t[:n]+('…' if len(t)>n else '')
def src(label,url): return f'<span class="source">來源：<a href="{e(url)}">{e(label)}</a></span>'
rev={}; mat=[]; fetch_notes=[]
for key,label in [('twse_rev','TWSE 官方資料'),('tpex_rev','TPEx 官方資料')]:
    try:
        data=fetch_json(URLS[key]); fetch_notes.append(f'{key}:{len(data)}')
        for r in data:
            c=str(r.get('公司代號') or '').strip()
            if c in WATCH: r['_src']=label; r['_url']=URLS[key]; r['_is_latest_month']='official'; rev[c]=r
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
manual_rev={
 '2603':{'資料年月':'11506','營業收入-當月營收':'39141000','營業收入-上月比較增減(%)':'12.94','營業收入-去年同月增減(%)':'30.01','累計營業收入-當月累計營收':'191668000','累計營業收入-前期比較增減(%)':'-2.44','_src':'公司公告轉載 / 產業媒體','_url':URLS['cnyes_2603_rev'],'_note':'6月營收年增三成；上半年累計仍年減 2.44%。'},
 '2609':{'資料年月':'11506','營業收入-當月營收':'16591000','營業收入-上月比較增減(%)':'9.85','營業收入-去年同月增減(%)':'20.18','累計營業收入-當月累計營收':'84583000','累計營業收入-前期比較增減(%)':'0.49','_src':'公司公告轉載 / 產業媒體','_url':URLS['ett_2609'],'_note':'董座估 Q3 營運續佳；紅海繞航與旺季支撐運價。'},
 '2615':{'資料年月':'11506','營業收入-當月營收':'16166000','營業收入-上月比較增減(%)':'17.11','營業收入-去年同月增減(%)':'32.70','累計營業收入-當月累計營收':'76541000','累計營業收入-前期比較增減(%)':'6.39','_src':'公司公告轉載 / 產業媒體','_url':URLS['ett_2615'],'_note':'6月營收創同期新高，5–6月接收 3 艘新船。'},
 '2606':{'資料年月':'11506','營業收入-當月營收':'1715000','營業收入-上月比較增減(%)':'','營業收入-去年同月增減(%)':'35.52','累計營業收入-當月累計營收':'8905000','累計營業收入-前期比較增減(%)':'26.30','_src':'產業媒體','_url':URLS['udn_2606'],'_note':'散裝景氣帶動，6月與上半年年增雙位數。'},
 '2637':{'資料年月':'11506','營業收入-當月營收':'1878000','營業收入-上月比較增減(%)':'3.34','營業收入-去年同月增減(%)':'57.92','累計營業收入-當月累計營收':'9680000','累計營業收入-前期比較增減(%)':'32.32','_src':'公司自結轉載 / 產業媒體','_url':URLS['ett_2637'],'_note':'6月營業利益率 44%（疫情後新高），1H 稅前 EPS 4.11 元。'},
 '2636':{'資料年月':'11506','營業收入-當月營收':'2587000','營業收入-上月比較增減(%)':'23.21','營業收入-去年同月增減(%)':'25.18','累計營業收入-當月累計營收':'11422000','累計營業收入-前期比較增減(%)':'1.59','_src':'公司公告轉載 / 產業媒體','_url':URLS['ett_2636'],'_note':'今年單月新高，上半年累計 YoY 轉正。'},
 '5609':{'資料年月':'11506','營業收入-當月營收':'3452000','營業收入-上月比較增減(%)':'','營業收入-去年同月增減(%)':'35.26','累計營業收入-當月累計營收':'16583000','累計營業收入-前期比較增減(%)':'15.10','_src':'公司公告轉載 / 產業媒體','_url':URLS['yahoo_5609'],'_note':'連 3 月創近 4 年高點，空運 +39.4%、海運 +29.7%。'},
 '2618':{'資料年月':'11506','營業收入-當月營收':'23472000','營業收入-上月比較增減(%)':'5.12','營業收入-去年同月增減(%)':'26.58','累計營業收入-當月累計營收':'128286000','累計營業收入-前期比較增減(%)':'16.36','_src':'公司公告轉載 / 產業媒體','_url':URLS['ctee_2618'],'_note':'單月新高；客運 141.32 億、貨運 66.52 億（YoY +48.34%）。'},
 '2630':{'資料年月':'11506','營業收入-當月營收':'328000','營業收入-上月比較增減(%)':'','營業收入-去年同月增減(%)':'-30.49','累計營業收入-當月累計營收':'2096000','累計營業收入-前期比較增減(%)':'-20.73','_src':'產業媒體','_url':URLS['money_2630'],'_note':'MRO/航空維修營收年減，仍待官方月營收資料更新。'},
 '2610':{'資料年月':'11506','營業收入-當月營收':'16893000','營業收入-上月比較增減(%)':'1.64','營業收入-去年同月增減(%)':'-3.82','累計營業收入-當月累計營收':'104062000','累計營業收入-前期比較增減(%)':'5.24','_src':'公司公告轉載 / 產業媒體（與單一舊媒體數字衝突）','_url':URLS['cnyes_2610'],'_note':'另有 ETtoday 舊文數字 123.42 億疑似非本期；本報列資料衝突，待 MOPS/公司 IR 最終核驗。'},
}
rev.update(manual_rev)
upstream='07:45 deep research 為今日台北日期 2026-07-10，DR_STATUS=partial（非 failed）；可作今日線索。08:20 已用 TWSE/TPEx 官方 Open Data 快速補查；官方 Open Data 月營收仍多為 11505，6月已揭露者採公司公告轉載與產業媒體，其他明列「6月尚未公布」。'
summary_cards=[
 ('risk','今日時效：GNK 收購要約到期','Diana Shipping 對 Genco Shipping（GNK）現金+股票要約於 2026-07-10 17:00 NY 到期；截至 6/26 tender 約 24.3%，若未達條件可能展延或撤回。','SEC / StockTitan'),
 ('risk','ZIM–Hapag-Lloyd 交易遇監管政治風險','US$42 億、US$35/股現金合併案遭以色列國防部初步反對，提出 New ZIM 保留戰略資產方案；7/28 股東會與交易文件為追蹤點。','公司 IR'),
 ('good','貨櫃三雄 6 月營收全面雙位數年增','長榮 391.41 億（YoY +30.01%）、陽明 165.91 億（+20.18%）、萬海 161.66 億（+32.70%），旺季/繞航/缺櫃支撐營收。','公司公告轉載 / 產業媒體'),
 ('good','散裝與貨代同步走強','BDI 2,875 六連漲、慧洋 6 月營收 YoY +57.92%且營益率 44%；中菲行受 AI 出貨支撐，6 月 YoY +35.26%。','指數資料 / 產業媒體'),
 ('risk','UPS 結構性壓力升高','Amazon 貨量在 2H26 對 UPS 縮減逾 50%，UPS 加速裁員與成本節省；7/28 Q2 財報是美國快遞景氣分水嶺。','FreightWaves'),
 ('warn','華航 6 月營收數字需最終核驗','鉅亨/工商口徑 168.93 億（YoY -3.82%）與 ETtoday 舊文 123.42 億衝突；本報採較新公司公告轉載並標示資料衝突。','產業媒體')]
industry_cards=[
 ('good','Drewry WCI / SCFI','Drewry WCI 7/2 報 US$4,530/FEU，WoW +9%、YoY +61%；上海—紐約 US$7,902、上海—洛杉磯 US$6,349；SCFI 約 3,326.87。',URLS['drewry_wci'],'指數資料'),
 ('good','BDI / 散裝','BDI 2,875 六連漲，BCI（Cape）4,514（+205）；鐵礦砂/煤與大西洋需求推升 Capesize。',URLS['baltic_te'],'交易資料'),
 ('risk','紅海 / 巴拿馬運河','紅海與 Bab el-Mandeb 通行量仍大幅低於常態；巴拿馬運河 7/24/8/15 下調 Neopanamax 最大吃水，留意乾旱與船期干擾。',URLS['panama'],'運河官方/產業資料'),
 ('warn','美國卡車運價轉折','DAT 6 月 dry van spot 首度自 2022/2 超過合約價，主因運力緊縮（駕駛供給與法規/移民執法），非單純需求爆量。',URLS['dat'],'產業資料'),
 ('risk','FedEx Freight 分拆後新口徑','FedEx Freight 6/1 分拆為 FDXF，分拆前支付 US$4.1B 特別股利；LTL 產業估值與財報口徑需更新。',URLS['fdxf'],'SEC / 公司公告'),
 ('good','航空運能投資','華航通過 NT$275 億購 2 架 777F；星宇 8/1 布拉格、10/1 峇里島，今年接收 14 架新機，航空固定資產投資進入高峰。',URLS['ci_order'],'公司公告轉載')]
supp_tw=[
 ('2026-07-09','2618 長榮航','6 月營收創單月新高','合併營收 234.72 億元、YoY +26.58%、MoM +5.12%；貨運 66.52 億、YoY +48.34%。','公司公告轉載 / 產業媒體',URLS['ctee_2618']),
 ('2026-07-08','2609 陽明','6 月營收','單月 165.91 億元、YoY +20.18%、MoM +9.85%；董事長估 Q3 營運仍佳。','公司公告轉載 / 產業媒體',URLS['ett_2609']),
 ('2026-07-08','2615 萬海','6 月營收','單月 161.66 億元、MoM +17.11%、YoY +32.70%；5–6 月接收 3 艘新船。','公司公告轉載 / 產業媒體',URLS['ett_2615']),
 ('2026-07-07','2603 長榮','6 月營收','合併營收 391.41 億元、MoM +12.94%、YoY +30.01%；H1 1,916.68 億元、YoY -2.44%。','公司公告轉載 / 產業媒體',URLS['cnyes_2603_rev']),
 ('2026-07 上旬','2637 慧洋-KY','自結營運','6 月 18.78 億元、YoY +57.92%；6 月營益率 44%，H1 稅前 EPS 4.11 元。','公司自結轉載 / 產業媒體',URLS['ett_2637']),
 ('2026-07 上旬','2606 裕民','6 月營收','6 月 17.15 億元、YoY +35.52%；累計 89.05 億元、YoY +26.3%。','產業媒體',URLS['udn_2606']),
 ('2026-07 上旬','2636 台驊投控','6 月營收','6 月 25.87 億元今年單月新高，YoY +25.18%、MoM +23.21%；H1 累計 YoY 轉正至 +1.59%。','產業媒體',URLS['ett_2636']),
 ('2026-07 上旬','5609 中菲行','6 月營收','6 月 34.52 億元、YoY +35.26%，連 3 月創近 4 年新高；AI/半導體貨支撐空運與海運。','產業媒體',URLS['yahoo_5609']),
 ('2026-06-10','2646 星宇航空','航點 / 機隊','8/1 開航台北—布拉格、10/1 台北—峇里島；今年接收 14 架新機含 6 架 A350-1000。','產業媒體',URLS['starlux']),
 ('2026-05-26','2610 華航','貨機訂單','通過 NT$275 億購 2 架 Boeing 777F，強化貨運長程運能；後續交機與折舊成本需追蹤。','產業媒體',URLS['ci_order'])]
us_events=[
 ('GNK','2026-07-10','Diana Shipping 對 GNK 要約今日到期；現金 US$24.80/股 + 1 股 Diana，隱含價值約 US$27.34，接受率不足風險高。','SEC / StockTitan',URLS['gnk_tender']),
 ('ZIM','2026-07 上旬','ZIM–Hapag-Lloyd US$42 億合併案受以色列國防部反對；New ZIM 架構與 7/28 股東會為後續觀察。','公司 IR',URLS['zim_deal']),
 ('UPS','2026-07 上旬','Amazon 對 UPS 貨量於 2H26 砍逾 50%，UPS 另裁 30,000 人、目標 US$3B 成本節省；Q2 財報 7/28。','產業媒體',URLS['freightwaves_ups']),
 ('FDX / FDXF','2026-06-01','FedEx Freight 完成分拆為 FDXF（NYSE），分拆前向母公司支付 US$4.1B 特別股利；FDX FY27 指引 revenue +11%。','SEC / 公司公告',URLS['fdxf']),
 ('FDX','FY2026 Q4','FedEx Q4 FY26 revenue 約 US$25.0B、adj EPS US$6.31 優於預期；FY27 adj EPS 指引 US$16.90–18.10。','SEC 官方資料',URLS['fdx_8k'])]
us_fin=[('UPS','FY2026 Q1 / 最新可得','Revenue 約 US$21.2B；Adj EPS 約 US$1.07；結構焦點轉向 Amazon 貨量縮減與醫療物流。','公司 IR / SEC',URLS['ups_ir']),('FDX','FY2026 Q4','Revenue 約 US$25.0B；Adj EPS US$6.31；FY27 revenue +11%、Adj EPS US$16.90–18.10。','SEC / 公司公告',URLS['fdx_8k']),('XPO','FY2026 Q1','Revenue 約 US$2.10B；北美 LTL 價量與 margin 為主軸。','SEC Companyfacts',URLS['xpo_sec']),('CHRW','FY2026 Q1','Revenue 約 US$4.01B；貨運經紀與貨代景氣仍看量價復甦。','SEC Companyfacts',URLS['chrw_sec']),('EXPD','FY2026 Q1','Revenue 約 US$2.78B；空海運貨代費率與高價電子貨出貨為焦點。','SEC Companyfacts',URLS['expd_sec']),('GXO','FY2026 Q1','Revenue 約 US$3.30B；合約物流新約、自動化與整合效率為主軸。','SEC Companyfacts',URLS['gxo_sec']),('JBHT','FY2026 Q1','Revenue 約 US$2.92B；多式聯運旺季前後貨量與 pricing 是 Q2 重點。','SEC Companyfacts',URLS['jbh_sec']),('MATX','FY2026 Q1','Revenue 約 US$758M；跨太平洋/夏威夷線與股利政策為觀察點。','SEC Companyfacts',URLS['matx_sec']),('ZIM','交易案 / 最新可得','Hapag-Lloyd 每股 US$35 現金收購案推進但面臨國安/股東會條件。','公司 IR',URLS['zim_ir']),('DAC','最新可得','以 20-F/6-K、charter backlog 與貨櫃船租金為主；本輪未見新增重大公告。','SEC 官方資料',URLS['dac_sec']),('SBLK','最新可得','散裝運價、船隊處分與股利政策為觀察重點。','公司 IR',URLS['sblk_ir']),('GOGL','追蹤口徑變更','GOGL 已併入 CMB.TECH 後不再有獨立申報；固定清單後續應改追 CMB.TECH。','公司 IR',URLS['gogl_ir']),('GNK','2026 Q1 / 收購戰','Q1 revenue 約 US$114M；Diana tender/董事會反對為短線公告主軸。','公司 IR / SEC',URLS['gnk_ir']),('KEX','FY2026 Q1','Revenue 約 US$844M；內河油品、化工與農產品 barge 需求為重點。','SEC Companyfacts',URLS['kex_sec'])]
css='''@page{size:A4;margin:11mm}*{box-sizing:border-box}body{margin:0;font-family:"PingFang TC","Heiti TC","Noto Sans TC","Microsoft JhengHei",sans-serif;background:#f4f7fb;color:#172033;font-size:12.2px;line-height:1.5}.hero{background:linear-gradient(135deg,#075ba8,#10a9df);color:#fff;border-radius:22px;padding:24px 28px;margin-bottom:16px;box-shadow:0 8px 24px rgba(5,70,120,.22)}h1{font-size:30px;margin:0 0 6px;letter-spacing:.04em}h2{font-size:19px;color:#0f3b66;margin:18px 0 10px}h3{font-size:14.2px;margin:4px 0 6px}.meta{opacity:.95}.toc{display:flex;flex-wrap:wrap;gap:7px;margin:0 0 12px}.toc span{background:#fff;border:1px solid #dbe7f5;border-radius:999px;padding:5px 10px;color:#195a91;font-weight:700}.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.grid.one{grid-template-columns:1fr}.grid.three{grid-template-columns:repeat(3,1fr)}.card{break-inside:avoid;background:#fff;border:1px solid #e2e9f3;border-radius:16px;padding:12px 14px;margin:0 0 10px;box-shadow:0 2px 8px rgba(42,67,101,.08)}.risk{border-left:5px solid #ef4444}.good{border-left:5px solid #16a34a}.warn{border-left:5px solid #f97316}.neutral{border-left:5px solid #3b82f6}.badge{display:inline-block;background:#e8f1ff;color:#114b88;border-radius:999px;padding:3px 9px;font-size:11.2px;font-weight:700;margin-bottom:6px}.source{display:block;margin-top:8px;color:#64748b;font-size:11.2px}.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:5px 8px;margin-top:6px}.stat{background:#f8fafc;border-radius:10px;padding:6px}.stat span{display:block;color:#64748b;font-size:10.2px}.stat strong{font-size:11.6px}.stat small{display:block;color:#64748b}.pos strong,.pos{color:#15803d}.neg strong,.neg{color:#b91c1c}ul{margin:6px 0 0 18px;padding:0}li{margin:4px 0}p{margin:4px 0}.footer{margin-top:18px;color:#475569;font-size:12px}.src-list li{word-break:break-all;font-size:10.5px}.pagebreak{break-before:page}.mini{font-size:11.2px;color:#64748b}.gap{background:#fff7ed}.muted{color:#64748b}a{color:#2563eb;text-decoration:none}.fin-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px}.fin{break-inside:avoid;background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:9px}.fin p{font-size:11.4px}.stamp{display:inline-block;background:rgba(255,255,255,.2);border:1px solid rgba(255,255,255,.35);padding:4px 9px;border-radius:999px;margin-top:8px;font-weight:700}'''
parts=[f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><title>航運物流股日報_{REPORT_DATE}</title><style>{css}</style></head><body>']
parts.append(f'<div class="hero"><h1>航運物流股日報</h1><div class="meta">報告日期：{REPORT_DATE}　產出時間：{GENERATED}<br>涵蓋：前一台股交易日/公告日 {PREV_TW}；前一美股交易日/公告日 {PREV_US}<br><span class="stamp">資料 QC：上游今日 partial、非 failed；已官方快查補強</span><br>{e(upstream)}</div></div>')
parts.append('<div class="toc"><span>重點摘要</span><span>產業指標</span><span>台股重大訊息</span><span>月營收</span><span>美股公告</span><span>資料缺口</span></div>')
parts.append('<section><h2>重點摘要（風險優先）</h2><div class="grid">')
for cls,t,txt,s in summary_cards: parts.append(f'<article class="card {cls}"><span class="badge">{e(t)}</span><p>{e(txt)}</p><span class="source">來源：{e(s)}</span></article>')
parts.append('</div></section><section><h2>產業與市場觀察</h2><div class="grid">')
for cls,t,txt,u,l in industry_cards: parts.append(f'<article class="card {cls}"><span class="badge">{e(t)}</span><p>{e(txt)}</p>{src(l,u)}</article>')
parts.append('</div></section><section><h2>台股重大訊息（短摘要）</h2><div class="grid one">')
for m in sorted(mat, key=lambda x: x.get('date',''), reverse=True)[:8]:
    tone='warn' if '颱風' in m['title'] else 'neutral'
    fact=f'；事實發生日 {m["fact"]}' if m.get('fact') else ''
    parts.append(f'<article class="card {tone}"><span class="badge">{e(m["date"])}｜{e(m["code"])} {e(m["name"])}</span><h3>{e(short(m["title"] or "官方重大訊息"))}</h3><p>官方重大訊息摘要{e(fact)}；例行/股利/治理事項僅摘錄重點，不展開全文。</p>{src(m["src"],m["url"])}</article>')
for d,c,t,txt,l,u in supp_tw: parts.append(f'<article class="card neutral"><span class="badge">{e(d)}｜{e(c)}</span><h3>{e(t)}</h3><p>{e(txt)}</p>{src(l,u)}</article>')
parts.append('</div></section>')
parts.append('<section class="pagebreak"><h2>台股月營收（6月最新揭露；單位：新台幣千元 / 億元）</h2><p class="mini">6月營收公告日適逢 7/10 截止日前後；已揭露 6月者列完整欄位。未揭露 6月者明列「6月尚未公布」，並附官方 Open Data 最新可得 5月作為參考。</p>')
for g,codes in GROUPS:
    parts.append(f'<h3>{e(g)}</h3><div class="grid three">')
    for code in codes:
        r=rev.get(code)
        if r and r.get('資料年月')=='11506':
            mon=r.get('營業收入-當月營收',''); cum=r.get('累計營業收入-當月累計營收',''); mom=r.get('營業收入-上月比較增減(%)',''); yoy=r.get('營業收入-去年同月增減(%)',''); cyoy=r.get('累計營業收入-前期比較增減(%)','')
            ccls='good' if (pct_class(yoy)=='pos' and (not cyoy or pct_class(cyoy)=='pos')) else 'warn'
            note=f'<p class="mini">{e(r.get("_note",""))}</p>' if r.get('_note') else ''
            parts.append(f'''<article class="card {ccls}"><span class="badge">{code} {e(NAME.get(code,''))}</span><h3>{e(roc_month(r.get('資料年月','')))}</h3><div class="stats"><div class="stat"><span>單月營收</span><strong>{e(mon)}</strong><small>（{e(nt_100m(mon))}）</small></div><div class="stat {pct_class(mom)}"><span>MoM</span><strong>{pct(mom) if mom else '未揭露'}</strong></div><div class="stat {pct_class(yoy)}"><span>YoY</span><strong>{pct(yoy)}</strong></div><div class="stat"><span>累計營收</span><strong>{e(cum)}</strong><small>（{e(nt_100m(cum))}）</small></div><div class="stat {pct_class(cyoy)}"><span>累計 YoY</span><strong>{pct(cyoy)}</strong></div></div>{note}{src(r['_src'],r['_url'])}</article>''')
        elif r:
            parts.append(f'''<article class="card neutral gap"><span class="badge">{code} {e(NAME.get(code,''))}</span><h3>2026-06 尚未公布</h3><p>本次 08:20 官方快查未見 6月資料；不以推估值補列。</p><p class="mini">官方最新參考：{e(roc_month(r.get('資料年月','')))} 單月 {e(r.get('營業收入-當月營收',''))}（{e(nt_100m(r.get('營業收入-當月營收','')))}），YoY {pct(r.get('營業收入-去年同月增減(%)',''))}。</p>{src(r['_src'],r['_url'])}</article>''')
        else:
            parts.append(f'<article class="card neutral gap"><span class="badge">{code} {e(NAME.get(code,""))}</span><h3>2026-06 尚未公布</h3><p>官方快查未擷取到有效資料；列為資料缺口。</p>{src("TWSE/TPEx 官方資料",URLS["twse_rev"])}</article>')
    parts.append('</div>')
parts.append('</section><section><h2>美股重大公告 / 最新可得業績</h2><div class="grid">')
for tick,d,txt,l,u in us_events: parts.append(f'<article class="card {"risk" if tick in ("GNK","ZIM","UPS") else "neutral"}"><span class="badge">{e(d)}｜{e(tick)}</span><p>{e(txt)}</p>{src(l,u)}</article>')
parts.append('</div><h3>最近一季 / 最新可得業績摘要</h3><div class="fin-grid">')
for tick,period,txt,l,u in us_fin:
    parts.append(f'<div class="fin"><b>{e(tick)}</b>｜{e(period)}<p>{e(txt)}</p>{src(l,u)}</div>')
parts.append('</div></section>')
missing=[
 '上游 deep research 今日狀態為 partial：小型散裝/陸運物流多數 6月營收在 08:20 官方 Open Data 尚未更新；本報不以推估值替代。',
 '官方 TWSE/TPEx 月營收 Open Data 本次擷取仍多停留 11505；6月數字主要採公司公告轉載/產業媒體，需後續以 MOPS t51sb02 最終值覆核。',
 '華航 2610 6月營收存在來源衝突：較新鉅亨/工商口徑 168.93 億，ETtoday 舊文 123.42 億疑似非本期；已標示衝突。',
 'CCFI、BPI/BSI、BDTI 與多數美股 2026-07-09 精確收盤價/日漲跌幅本輪未取得可核驗來源；未放入主結論。'
]
parts.append('<section><h2>資料缺口與注意事項</h2><div class="grid">')
for m in missing:
    parts.append(f'<article class="card neutral"><span class="badge">資料缺口</span><p>{e(m)}</p></article>')
parts.append('<article class="card neutral"><span class="badge">非投資建議</span><p>以上為公開資訊整理，非投資建議。</p></article></div></section>')
all_urls=set(URLS.values())
for row in supp_tw: all_urls.add(row[-1])
for row in us_events: all_urls.add(row[-1])
for row in us_fin: all_urls.add(row[-1])
for r in rev.values():
    if r.get('_url'): all_urls.add(r.get('_url'))
parts.append('<section><h2>來源清單（完整 URL）</h2><div class="card"><ul class="src-list">')
for u in sorted(all_urls): parts.append(f'<li>{e(u)}</li>')
parts.append(f'</ul><p class="footer">QC trace: {e("; ".join(fetch_notes))}</p><p class="footer">以上為公開資訊整理，非投資建議。</p></div></section></body></html>')
HTML.write_text('\n'.join(parts),encoding='utf-8')
chrome='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
if not pathlib.Path(chrome).exists():
    raise SystemExit('Chrome not found')
cmd=[chrome,'--headless=new','--disable-gpu','--no-pdf-header-footer',f'--print-to-pdf={PDF}',f'file://{HTML}']
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=120)
shutil.copyfile(PDF,ALT)
print(str(HTML)); print(str(PDF)); print(str(ALT))
