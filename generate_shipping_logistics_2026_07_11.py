#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, urllib.request, html, pathlib, datetime, re, subprocess, shutil
TZ=datetime.timezone(datetime.timedelta(hours=8))
now=datetime.datetime.now(TZ)
REPORT_DATE=now.strftime('%Y-%m-%d')
GENERATED=now.strftime('%Y-%m-%d %H:%M Asia/Taipei')
PREV_TW='2026-07-10（週五）/ 最新公告日'
PREV_US='2026-07-10（美東，週五）/ 最新公告日'
OUT=pathlib.Path('/Users/cph/investment-reports/reports/shipping-logistics')/REPORT_DATE
OUT.mkdir(parents=True, exist_ok=True)
HTML=OUT/'report.html'; PDF=OUT/'report.pdf'; ALT=OUT/f'航運物流股日報_{REPORT_DATE}.pdf'
WATCH='2603 2609 2615 2605 2606 2612 2617 2637 5608 2641 2607 2608 2611 2613 2636 2642 5601 5603 5604 5607 5609 1443 2610 2618 2646 2630 2645'.split()
NAME={'2603':'長榮','2609':'陽明','2615':'萬海','2605':'新興','2606':'裕民','2612':'中航','2617':'台航','2637':'慧洋-KY','5608':'四維航','2641':'正德','2607':'榮運','2608':'嘉里大榮','2611':'志信','2613':'中櫃','2636':'台驊投控','2642':'宅配通','5601':'台聯櫃','5603':'陸海','5604':'中連','5607':'遠雄港','5609':'中菲行','1443':'立益物流','2610':'華航','2618':'長榮航','2646':'星宇航空','2630':'亞航','2645':'長榮航太'}
GROUPS=[('貨櫃航運',['2603','2609','2615']),('散裝 / 海運',['2605','2606','2612','2617','2637','5608','2641']),('港埠 / 物流 / 貨代',['2607','2608','2611','2613','2636','2642','5601','5603','5604','5607','5609','1443']),('航空 / 航太維修',['2610','2618','2646','2630','2645'])]
URLS={
 'twse_rev':'https://openapi.twse.com.tw/v1/opendata/t187ap05_L','tpex_rev':'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap05_O','twse_mat':'https://openapi.twse.com.tw/v1/opendata/t187ap04_L','tpex_mat':'https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap04_O',
 'cnyes_2603':'https://news.cnyes.com/news/id/6525946','ett_2609':'https://finance.ettoday.net/news/3198274','ett_2615':'https://finance.ettoday.net/news/3197671','ett_2637':'https://finance.ettoday.net/news/3194757','udn_2606':'https://udn.com/news/story/7252/9547769','ett_2636':'https://finance.ettoday.net/news/3198284','ett_5609':'https://finance.ettoday.net/news/3196073','yahoo_2607':'https://statementdog.com/analysis/2607/monthly-revenue','cnyes_2610':'https://news.cnyes.com/news/id/6530439','udn_2610':'https://udn.com/news/story/7252/9619360','cnyes_2618':'https://news.cnyes.com/news/id/6529194','money_2630':'https://ww2.money-link.com.tw/realtimenews/NewsContent.aspx?SN=2389117002&PU=0010','nstock_2646':'https://www.nstock.tw/stock_info?stock_id=2646&status=2','cm_2645':'https://cmnews.com.tw/article/cmoneyairesearcher-fbd8aa07-7a6d-11f1-9cbf-35ca24deee14',
 'ctee_2610_div':'https://www.ctee.com.tw/news/20260708700096-439901','ltn_2618_div':'https://ec.ltn.com.tw/article/breakingnews/5481973','yahoo_2609_div':'https://tw.stock.yahoo.com/news/公告-陽明訂定配息基準日及現金股利發放日-060337982.html','cnyes_2606_ship':'https://news.cnyes.com/news/id/6508994','bavi_udn':'https://udn.com/news/story/124945/9617019','bavi_storm':'https://www.storm.mg/article/11148286',
 'cnn_houthi':'https://www.cnn.com/2026/07/09/middleeast/houthi-red-sea-attacks-magic-seas-eternity-c-intl','lloyds':'https://www.lloydslist.com/','seatrade':'https://www.seatrade-maritime.com/','drewry_wci':'https://www.drewry.co.uk/supply-chain-advisors/supply-chain-expertise/world-container-index-assessed-by-drewry','scfi_te':'https://tradingeconomics.com/commodity/containerized-freight-index','baltic_te':'https://tradingeconomics.com/commodity/baltic','nrf':'https://nrf.com/media-center/press-releases/monthly-import-cargo-volume-us-major-container-ports-set-new-record-july',
 'ups_8k':'https://www.sec.gov/Archives/edgar/data/1090727/000162828026003510/exhibit991-earningspressre.htm','ups_fw':'https://www.freightwaves.com/news/ups-to-close-27-additional-parcel-facilities-in-2026','fdx_spin':'https://newsroom.fedex.com/newsroom/global-english/fedex-completes-spin-off-of-fedex-freight','fdx_debt':'https://www.tipranks.com/news/company-announcements/fedex-reshapes-debt-after-fedex-freight-spin-off','xpo_may':'https://www.globenewswire.com/news-release/2026/06/03/3306382/0/en/xpo-provides-north-american-ltl-operating-data-for-may-2026.html','zim_deal':'https://investors.zim.com/news/news-details/2026/ZIM-to-be-Acquired-by-Hapag-Lloyd-for-35-00-per-Share-in-Cash-at-Aggregate-Cash-Consideration-of-Approximately-4-2-Billion-New-Israeli-Company-New-ZIM-to-Acquire-Portion-of-ZIMs-Business/default.aspx','gnk_tender':'https://www.stocktitan.net/sec-filings/GNK/sc-to-t-a-genco-shipping-trading-ltd-amended-third-party-tender-offer-e1a1570f3fe7.html',
 'ups_ir':'https://investors.ups.com/sec-filings/all-sec-filings','fdx_8k':'https://www.sec.gov/Archives/edgar/data/0001048911/000104891126000050/fdx-20260623.htm','xpo_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001166003.json','chrw_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001043277.json','expd_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000746515.json','gxo_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0001852244.json','jbh_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000728535.json','matx_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000003453.json','dac_sec':'https://www.sec.gov/edgar/browse/?CIK=1369241&owner=exclude','sblk_ir':'https://www.starbulk.com/gr/en/press-releases/','gogl_ir':'https://www.cmb.tech/','gnk_ir':'https://investors.gencoshipping.com/','kex_sec':'https://data.sec.gov/api/xbrl/companyfacts/CIK0000056047.json','zim_ir':'https://www.zim.com/investors/press-releases'}

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
    s=str(s); return f'{int(s[:3])+1911}-{s[3:5]}' if len(s)>=5 and s[:3].isdigit() else s
def roc_date(s):
    s=str(s).strip()
    if len(s)==7 and s[:3].isdigit(): return f'{int(s[:3])+1911}-{s[3:5]}-{s[5:7]}'
    if len(s)==8 and s.isdigit(): return f'{s[:4]}-{s[4:6]}-{s[6:8]}'
    return s
def short(t,n=108):
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
manual_rev={
 '2603':{'資料年月':'11506','營業收入-當月營收':'39141000','營業收入-上月比較增減(%)':'12.94','營業收入-去年同月增減(%)':'30.01','累計營業收入-當月累計營收':'191668000','累計營業收入-前期比較增減(%)':'-2.44','_src':'公司公告轉載 / 產業媒體','_url':URLS['cnyes_2603'],'_note':'6月營收年增三成；H1 累計仍年減 2.44%。'},
 '2609':{'資料年月':'11506','營業收入-當月營收':'16591000','營業收入-上月比較增減(%)':'9.85','營業收入-去年同月增減(%)':'20.18','累計營業收入-當月累計營收':'84583000','累計營業收入-前期比較增減(%)':'0.49','_src':'公司公告轉載 / 產業媒體','_url':URLS['ett_2609'],'_note':'旺季/繞航支撐 6月營收，董事會另訂配息基準日。'},
 '2615':{'資料年月':'11506','營業收入-當月營收':'16166000','營業收入-上月比較增減(%)':'17.11','營業收入-去年同月增減(%)':'32.70','累計營業收入-當月累計營收':'76541000','累計營業收入-前期比較增減(%)':'6.39','_src':'公司公告轉載 / 產業媒體','_url':URLS['ett_2615'],'_note':'22 個月新高；5–6月接收 3 艘節能新船。'},
 '2637':{'資料年月':'11506','營業收入-當月營收':'1878000','營業收入-上月比較增減(%)':'3.34','營業收入-去年同月增減(%)':'57.92','累計營業收入-當月累計營收':'9680000','累計營業收入-前期比較增減(%)':'32.32','_src':'公司自結轉載 / 產業媒體','_url':URLS['ett_2637'],'_note':'6月營益率 44%（三年新高），H1 EPS 4.11 元。'},
 '2636':{'資料年月':'11506','營業收入-當月營收':'2587000','營業收入-上月比較增減(%)':'23.21','營業收入-去年同月增減(%)':'25.18','累計營業收入-當月累計營收':'11422000','累計營業收入-前期比較增減(%)':'1.59','_src':'公司公告轉載 / 產業媒體','_url':URLS['ett_2636'],'_note':'今年單月新高，H1 累計 YoY 轉正。'},
 '5609':{'資料年月':'11506','營業收入-當月營收':'3452000','營業收入-上月比較增減(%)':'6.53','營業收入-去年同月增減(%)':'35.26','累計營業收入-當月累計營收':'16583000','累計營業收入-前期比較增減(%)':'15.10','_src':'公司公告轉載 / 產業媒體','_url':URLS['ett_5609'],'_note':'半導體/AI 供應鏈出貨帶動，空運 +39.4%、海運 +29.7%。'},
 '2607':{'資料年月':'11506','營業收入-當月營收':'1847000','營業收入-上月比較增減(%)':'','營業收入-去年同月增減(%)':'25.41','累計營業收入-當月累計營收':'9044000','累計營業收入-前期比較增減(%)':'2.45','_src':'財經資料平台（二次來源，待 MOPS 驗證）','_url':URLS['yahoo_2607'],'_note':'來源為財經資料平台，列為待官方覆核。'},
 '2610':{'資料年月':'11506','營業收入-當月營收':'21761000','營業收入-上月比較增減(%)':'2.50','營業收入-去年同月增減(%)':'28.82','累計營業收入-當月累計營收':'120803000','累計營業收入-前期比較增減(%)':'16.09','_src':'公司公告轉載 / 產業媒體','_url':URLS['cnyes_2610'],'_note':'單月、Q2、H1 三高；貨運 80.85 億，YoY +51.60%。'},
 '2618':{'資料年月':'11506','營業收入-當月營收':'23472000','營業收入-上月比較增減(%)':'5.12','營業收入-去年同月增減(%)':'26.58','累計營業收入-當月累計營收':'128286000','累計營業收入-前期比較增減(%)':'16.36','_src':'公司公告轉載 / 產業媒體','_url':URLS['cnyes_2618'],'_note':'單月與 H1 新高；貨運 66.52 億，YoY +48.34%。'},
 '2646':{'資料年月':'11506','營業收入-當月營收':'4680000','營業收入-上月比較增減(%)':'-3.02','營業收入-去年同月增減(%)':'30.12','累計營業收入-當月累計營收':'','累計營業收入-前期比較增減(%)':'','_src':'財經資料平台（二次來源，待官方/主流媒體交叉驗證）','_url':URLS['nstock_2646'],'_note':'單一二次來源，未列為核心結論。'},
 '2630':{'資料年月':'11506','營業收入-當月營收':'328000','營業收入-上月比較增減(%)':'-9.11','營業收入-去年同月增減(%)':'-30.49','累計營業收入-當月累計營收':'2095550','累計營業收入-前期比較增減(%)':'-20.73','_src':'產業媒體 / 財經資料','_url':URLS['money_2630'],'_note':'五檔航空/航太中唯一衰退。'},
}
rev.update(manual_rev)
upstream='07:45 deep research 為今日台北日期 2026-07-11，DR_STATUS=partial（非 failed）；可作今日線索。08:20 已用 TWSE/TPEx 官方 Open Data 快速補查；未公開或僅單一二次來源者列資料缺口，不以推估值替代。'
summary_cards=[
 ('risk','紅海風險升級','Houthi 一週擊沉 Magic Seas、Eternity C 兩艘散裝船，並傳出傷亡與挾持；繞航好望角延長噸海里、支撐運價，但也提高保險與營運風險。','CNN / Lloyd’s List / Seatrade'),
 ('risk','颱風 Bavi 衝擊國籍航空與港口','7/10 晚間起至 7/11 桃機大量取消；華航、長榮航、星宇調整或取消航班，基隆港郵輪改航，屬短期一次性營運干擾。','聯合新聞網 / 風傳媒'),
 ('good','貨櫃三雄 6月營收全面雙位數年增','長榮 391.41 億（YoY +30.01%）、陽明 165.91 億（+20.18%）、萬海 161.66 億（+32.70%）；搶運、繞航、旺季推升。','公司公告轉載 / 產業媒體'),
 ('good','航空雙雄 6月創歷史新高','華航 217.61 億、YoY +28.82%；長榮航 234.72 億、YoY +26.58%。AI 伺服器與高價電子貨支撐航空貨運。','鉅亨 / 經濟日報'),
 ('risk','ZIM 併購與 GNK 敵意收購進入事件窗','ZIM–Hapag-Lloyd 交易遭以色列政治/國安疑慮卡關；Diana 對 GNK 要約 7/10 到期且董事會反對。','公司 IR / SEC'),
 ('warn','資料狀態 partial','核心大型股資料完整；部分小型散裝/物流股與長榮航太 6月營收截至 7/10 前未見可靠主流/官方來源，於月營收表列缺口。','上游 deep research + 官方快查')]
industry_cards=[
 ('good','運價：SCFI / WCI','SCFI 7/3 收 3,326.87、連 10 週上漲；Drewry WCI 7/9 升至 US$4,639/FEU，2024/9 以來新高。',URLS['drewry_wci'],'指數資料'),
 ('good','散裝：BDI','BDI 週中高點 2,875，為 6/8 以來新高；紅海繞航與原物料需求支撐船噸使用。',URLS['baltic_te'],'交易資料'),
 ('risk','美國關稅期限搶運','NRF 估 7月美國主要港口進口量 247 萬 TEU，或創歷史單月新高；東亞—美西 40ft 單價 6週漲約 120%。',URLS['nrf'],'產業資料'),
 ('warn','港口壅塞','全球約 11% 船隊運能等泊、約 340 萬 TEU 卡在港口壅塞；船期不穩與設備周轉仍是旺季變數。',URLS['lloyds'],'產業媒體'),
 ('risk','UPS 設施整併','UPS 2H26 再關閉 27 個包裹處理設施，並投入 US$48M 擴冷鏈跨庫；Q2 財報 7/28。',URLS['ups_fw'],'SEC / 產業媒體'),
 ('neutral','FedEx Freight 分拆後新口徑','FedEx Freight 6/1 完成分拆為 FDXF；FedEx 另成立 Life Sciences 事業部並調整債務。',URLS['fdx_spin'],'公司公告')]
supp_tw=[
 ('2026-07-10','2610 華航','除息交易日','每股現金股利 0.82 元，現金發放日 8/14；颱風造成 7/10 晚間後多航班取消。','工商時報 / 航班公告',URLS['ctee_2610_div']),
 ('2026-07-10','2610 華航','6月營收創三高','6月 217.61 億元、YoY +28.82%；Q2 638.45 億、H1 1,208 億均創新高；貨運 YoY +51.60%。','鉅亨 / 聯合新聞網',URLS['cnyes_2610']),
 ('2026-07-09','2618 長榮航','6月營收創新高','6月 234.72 億元、YoY +26.58%，連 4 月破 200 億；貨運 YoY +48.34%。','鉅亨 / 經濟日報',URLS['cnyes_2618']),
 ('2026-07-08','2618 長榮航','除息交易日','每股現金股利 2 元；現金發放日 8/7。','自由財經',URLS['ltn_2618_div']),
 ('2026-07-08','2615 萬海','6月營收與新船','6月 161.66 億元、YoY +32.70%；5–6月接收 3 艘節能新船，2026–2030 共接 34 艘。','ETtoday',URLS['ett_2615']),
 ('2026-07-07','2603 長榮','6月營收','6月 391.41 億元、YoY +30.01%；H1 累計 1,916.68 億元、YoY -2.44%。','鉅亨 / 經濟日報',URLS['cnyes_2603']),
 ('2026-07-07','2645 長榮航太','注意股公布自結','自結 5月 EPS 0.81 元、YoY 大增；國防無人載具特別條例題材使股價波動，6月營收仍待公告。','CMoney',URLS['cm_2645']),
 ('2026-07-06','2609 陽明','配息基準日','董事會決議配息基準日與現金股利發放日；每股配息 2 元。','Yahoo 股市',URLS['yahoo_2609_div']),
 ('2026-07-06','5609 中菲行','6月營收','6月 34.52 億元、YoY +35.26%；空運 +39.4%、海運 +29.7%，受 AI/半導體出貨支撐。','ETtoday / 中時',URLS['ett_5609']),
 ('2026-07-03','2637 慧洋-KY','6月與H1自結','6月 18.78 億元、YoY +57.92%；6月營益率 44%，H1 EPS 4.11 元。','ETtoday / 工商時報',URLS['ett_2637']),
 ('2026-06-23','2606 裕民','訂造 Newcastlemax','與江蘇韓通簽 2+2 艘 21.1 萬噸 Newcastlemax；每艘 US$77–80M。','鉅亨',URLS['cnyes_2606_ship'])]
us_events=[
 ('UPS','2026-07 上旬','2H26 再關閉 27 個包裹處理設施，並投 US$48M 擴充冷鏈跨庫；FY2026 revenue outlook 約 US$89.7B，Q2 財報 7/28。','SEC / FreightWaves',URLS['ups_8k']),
 ('FDX','2026-07-09/10','成立 FedEx Life Sciences 事業部；債券 tender offer 投標超過 US$4.15B 上限，預定 7/14 結算。','公司公告 / 市場資料',URLS['fdx_debt']),
 ('XPO','2026-07-08','Citi 下調目標價至 US$226；UBS 上調至 US$257（Buy）。5月 LTL 每日噸位 YoY +0.5%、出貨數 +3.3%。','公司公告 / 分析師動作',URLS['xpo_may']),
 ('ZIM','2026-07-06','Hapag-Lloyd 擬以 US$35/股收購 ZIM，但以色列政界/國防部門因國安疑慮反對，Q4 2026 完成時程具不確定性。','公司 IR',URLS['zim_deal']),
 ('GNK','2026-07-10','Diana Shipping 敵意收購 GNK 要約到期；Genco 董事會反對，指價格低於 NAV；截至 6/26 已投標約 1,058 萬股。','SEC / StockTitan',URLS['gnk_tender'])]
us_fin=[('UPS','FY2026 Q1 / 最新可得','Revenue 約 US$21.2B；Adj EPS 約 US$1.07；焦點轉向 Amazon 貨量縮減、設施整併與醫療物流。','公司 IR / SEC',URLS['ups_ir']),('FDX','FY2026 Q4','Revenue 約 US$25.0B；Adj EPS US$6.31；FedEx Freight 已分拆，FY27 指引口徑改變。','SEC / 公司公告',URLS['fdx_8k']),('XPO','FY2026 Q1','Revenue 約 US$2.10B；北美 LTL 價量、service quality 與 margin 為主軸。','SEC Companyfacts',URLS['xpo_sec']),('CHRW','FY2026 Q1 / 最新可得','Revenue 約 US$4.01B；貨運經紀與貨代景氣仍看量價復甦，7月有投資者會議與 Form 4。','SEC / 公司公告',URLS['chrw_sec']),('EXPD','FY2026 Q1','Revenue 約 US$2.78B；空海運貨代費率與高價電子貨出貨為焦點。','SEC Companyfacts',URLS['expd_sec']),('GXO','FY2026 Q1','Revenue 約 US$3.30B；合約物流新約、自動化與整合效率為主軸。','SEC Companyfacts',URLS['gxo_sec']),('JBHT','FY2026 Q1','Revenue 約 US$2.92B；多式聯運旺季前後貨量與 pricing 是 Q2 重點。','SEC Companyfacts',URLS['jbh_sec']),('MATX','FY2026 Q1','Revenue 約 US$758M；跨太平洋/夏威夷線與股利政策為觀察點。','SEC Companyfacts',URLS['matx_sec']),('ZIM','交易案 / 最新可得','Hapag-Lloyd 每股 US$35 現金收購案推進但面臨國安/股東會條件。','公司 IR',URLS['zim_ir']),('DAC','最新可得','以 20-F/6-K、charter backlog 與貨櫃船租金為主；本輪未見新增重大公告。','SEC 官方資料',URLS['dac_sec']),('SBLK','最新可得','散裝運價、船隊處分與股利政策為觀察重點；本輪未見新增重大公告。','公司 IR',URLS['sblk_ir']),('GOGL','追蹤口徑變更','GOGL 已併入 CMB.TECH 後下市，不再有獨立申報；固定清單後續宜改追 CMB.TECH。','公司 IR',URLS['gogl_ir']),('GNK','2026 Q1 / 收購戰','Q1 revenue 約 US$114M；Diana tender/董事會反對為短線公告主軸。','公司 IR / SEC',URLS['gnk_ir']),('KEX','FY2026 Q1','Revenue 約 US$844M；內河油品、化工與農產品 barge 需求為重點。','SEC Companyfacts',URLS['kex_sec'])]
css='''@page{size:A4;margin:11mm}*{box-sizing:border-box}body{margin:0;font-family:"PingFang TC","Heiti TC","Noto Sans TC","Microsoft JhengHei",sans-serif;background:#f4f7fb;color:#172033;font-size:12.2px;line-height:1.5}.hero{background:linear-gradient(135deg,#075ba8,#10a9df);color:#fff;border-radius:22px;padding:24px 28px;margin-bottom:16px;box-shadow:0 8px 24px rgba(5,70,120,.22)}h1{font-size:30px;margin:0 0 6px;letter-spacing:.04em}h2{font-size:19px;color:#0f3b66;margin:18px 0 10px}h3{font-size:14.2px;margin:4px 0 6px}.meta{opacity:.96}.stamp{display:inline-block;background:rgba(255,255,255,.20);border-radius:999px;padding:3px 10px;margin:5px 0}.toc{display:flex;flex-wrap:wrap;gap:7px;margin:0 0 12px}.toc span{background:#fff;border:1px solid #dbe7f5;border-radius:999px;padding:5px 10px;color:#195a91;font-weight:700}.grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}.grid.one{grid-template-columns:1fr}.grid.three{grid-template-columns:repeat(3,1fr)}.card{break-inside:avoid;background:#fff;border:1px solid #e2e9f3;border-radius:16px;padding:12px 14px;margin:0 0 10px;box-shadow:0 2px 8px rgba(42,67,101,.08)}.risk{border-left:5px solid #ef4444}.good{border-left:5px solid #16a34a}.warn{border-left:5px solid #f97316}.neutral{border-left:5px solid #3b82f6}.badge{display:inline-block;background:#e8f1ff;color:#114b88;border-radius:999px;padding:3px 9px;font-size:11.2px;font-weight:700;margin-bottom:6px}.source{display:block;margin-top:8px;color:#64748b;font-size:11.2px}.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:5px 8px;margin-top:6px}.stat{background:#f8fafc;border-radius:10px;padding:6px}.stat span{display:block;color:#64748b;font-size:10.2px}.stat strong{font-size:11.6px}.stat small{display:block;color:#64748b}.pos strong,.pos{color:#15803d}.neg strong,.neg{color:#b91c1c}ul{margin:6px 0 0 18px;padding:0}li{margin:4px 0}p{margin:4px 0}.footer{margin-top:18px;color:#475569;font-size:12px}.src-list li{word-break:break-all;font-size:10.5px}.pagebreak{break-before:page}.mini{font-size:11.2px;color:#64748b}.gap{background:#fff7ed}.muted{color:#64748b}a{color:#2563eb;text-decoration:none}.fin-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}.fin{break-inside:avoid;background:#fff;border:1px solid #e2e9f3;border-radius:14px;padding:10px}.fin b{color:#0f3b66}'''
parts=[f'<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8"><title>航運物流股日報_{REPORT_DATE}</title><style>{css}</style></head><body>']
parts.append(f'<div class="hero"><h1>航運物流股日報</h1><div class="meta">報告日期：{REPORT_DATE}　產出時間：{GENERATED}<br>涵蓋：前一台股交易日/公告日 {PREV_TW}；前一美股交易日/公告日 {PREV_US}<br><span class="stamp">資料 QC：上游今日 partial、非 failed；已官方快查補強</span><br>{e(upstream)}</div></div>')
parts.append('<div class="toc"><span>重點摘要</span><span>產業指標</span><span>台股重大訊息</span><span>月營收</span><span>美股公告</span><span>資料缺口</span></div>')
parts.append('<section><h2>重點摘要（風險優先）</h2><div class="grid">')
for cls,t,txt,s in summary_cards: parts.append(f'<article class="card {cls}"><span class="badge">{e(t)}</span><p>{e(txt)}</p><span class="source">來源：{e(s)}</span></article>')
parts.append('</div></section><section><h2>產業與市場觀察</h2><div class="grid">')
for cls,t,txt,u,l in industry_cards: parts.append(f'<article class="card {cls}"><span class="badge">{e(t)}</span><p>{e(txt)}</p>{src(l,u)}</article>')
parts.append('</div></section><section><h2>台股重大訊息（短摘要）</h2><div class="grid one">')
for m in sorted(mat, key=lambda x: x.get('date',''), reverse=True)[:8]:
    tone='warn' if any(k in m['title'] for k in ['颱風','重大','處分','取得']) else 'neutral'
    fact=f'；事實發生日 {m["fact"]}' if m.get('fact') else ''
    parts.append(f'<article class="card {tone}"><span class="badge">{e(m["date"])}｜{e(m["code"])} {e(m["name"])}</span><h3>{e(short(m["title"] or "官方重大訊息"))}</h3><p>官方重大訊息摘要{e(fact)}；例行/股利/治理事項僅摘錄重點，不展開全文。</p>{src(m["src"],m["url"])}</article>')
for d,c,t,txt,l,u in supp_tw: parts.append(f'<article class="card neutral"><span class="badge">{e(d)}｜{e(c)}</span><h3>{e(t)}</h3><p>{e(txt)}</p>{src(l,u)}</article>')
parts.append('</div></section>')
parts.append('<section class="pagebreak"><h2>台股月營收（6月最新揭露；單位：新台幣千元 / 億元）</h2><p class="mini">已揭露 6月者列月份、單月營收、MoM、YoY、累計營收與累計 YoY。未揭露或僅待核來源者標註資料狀態，不以推估值補列。</p>')
for g,codes in GROUPS:
    parts.append(f'<h3>{e(g)}</h3><div class="grid three">')
    for code in codes:
        r=rev.get(code)
        if r and r.get('資料年月')=='11506':
            mon=r.get('營業收入-當月營收',''); cum=r.get('累計營業收入-當月累計營收',''); mom=r.get('營業收入-上月比較增減(%)',''); yoy=r.get('營業收入-去年同月增減(%)',''); cyoy=r.get('累計營業收入-前期比較增減(%)','')
            ccls='good' if (pct_class(yoy)=='pos' and (not cyoy or pct_class(cyoy)=='pos')) else 'warn'
            note=f'<p class="mini">{e(r.get("_note",""))}</p>' if r.get('_note') else ''
            parts.append(f'''<article class="card {ccls}"><span class="badge">{code} {e(NAME.get(code,''))}</span><h3>{e(roc_month(r.get('資料年月','')))}</h3><div class="stats"><div class="stat"><span>單月營收</span><strong>{e(mon)}</strong><small>（{e(nt_100m(mon))}）</small></div><div class="stat {pct_class(mom)}"><span>MoM</span><strong>{pct(mom) if mom else '未揭露'}</strong></div><div class="stat {pct_class(yoy)}"><span>YoY</span><strong>{pct(yoy) if yoy else '未揭露'}</strong></div><div class="stat"><span>累計營收</span><strong>{e(cum) if cum else '未揭露'}</strong><small>{('（'+e(nt_100m(cum))+'）') if cum else ''}</small></div><div class="stat {pct_class(cyoy)}"><span>累計 YoY</span><strong>{pct(cyoy) if cyoy else '未揭露'}</strong></div></div>{note}{src(r.get('_src','資料來源'),r.get('_url','#'))}</article>''')
        elif r:
            parts.append(f'''<article class="card neutral gap"><span class="badge">{code} {e(NAME.get(code,''))}</span><h3>2026-06 尚未公布</h3><p>本次官方快查未見 6月可靠資料；不以推估值補列。</p><p class="mini">官方最新參考：{e(roc_month(r.get('資料年月','')))} 單月 {e(r.get('營業收入-當月營收',''))}（{e(nt_100m(r.get('營業收入-當月營收','')))}），YoY {pct(r.get('營業收入-去年同月增減(%)',''))}。</p>{src(r.get('_src','官方資料'),r.get('_url',URLS['twse_rev']))}</article>''')
        else:
            parts.append(f'<article class="card neutral gap"><span class="badge">{code} {e(NAME.get(code,""))}</span><h3>2026-06 尚未公布</h3><p>官方快查未擷取到有效資料；列為資料缺口。</p>{src("TWSE/TPEx 官方資料",URLS["twse_rev"])}</article>')
    parts.append('</div>')
parts.append('</section><section><h2>美股重大公告 / 最新可得業績</h2><div class="grid">')
for tick,d,txt,l,u in us_events: parts.append(f'<article class="card {"risk" if tick in ("GNK","ZIM","UPS") else "neutral"}"><span class="badge">{e(d)}｜{e(tick)}</span><p>{e(txt)}</p>{src(l,u)}</article>')
parts.append('</div><h3>最近一季 / 最新可得業績摘要</h3><div class="fin-grid">')
for tick,period,txt,l,u in us_fin: parts.append(f'<div class="fin"><b>{e(tick)}</b>｜{e(period)}<p>{e(txt)}</p>{src(l,u)}</div>')
parts.append('</div></section>')
missing=['上游 deep research 今日狀態為 partial：核心大型股完整；10 檔小型物流/散裝與長榮航太 6月營收截至 7/10 前未見可交叉驗證的主流/官方來源。','星宇 6月營收目前為單一財經資料平台口徑，未納入核心結論，待官方公告/主流媒體交叉驗證。','GOGL 已併入 CMB.TECH 後下市，不再是獨立有效標的；固定清單後續應調整追蹤口徑。','本報不提供買賣建議，所有數字後續仍以公司公告、MOPS、SEC/公司 IR 更新為準。']
parts.append('<section><h2>資料缺口與注意事項</h2><div class="grid">')
for m in missing: parts.append(f'<article class="card neutral"><span class="badge">資料缺口</span><p>{e(m)}</p></article>')
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
cmd=[chrome,'--headless=new','--disable-gpu','--no-pdf-header-footer',f'--print-to-pdf={PDF}',f'file://{HTML}']
subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=120)
shutil.copyfile(PDF,ALT)
print(str(HTML)); print(str(PDF)); print(str(ALT))
