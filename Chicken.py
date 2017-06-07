import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from itertools import count
import xml.etree.ElementTree as ET

def get_request_url(url, enc='utf-8'):
    
    req = urllib.request.Request(url)

    try: 
        response = urllib.request.urlopen(req)
        if response.getcode() == 200:
            try:
                rcv = response.read()
                ret = rcv.decode(enc)
            except UnicodeDecodeError:
                ret = rcv.decode(enc, 'replace')    
            
            return ret
            
    except Exception as e:
        print(e)
        print("[%s] Error for URL : %s" % (datetime.datetime.now(), url))
        return None


'''
#BBQ HTML 구조
<tbody>
    <tr>
        <td class="pdL25">강일지구점</td>
        <td>서울특별시 강동구 아리수로93길 27 202(강일동,,2강일타워2층202호~203호)</td>
        <td class="alignC">02-429-0669</td>
        <td class="alignL"><img src='/images/shop/ico_cafe.png' title='프리미엄카페'>&nbsp;<img src='/images/shop/ico_parking.png' alt='주차가능' title='주차가능'>&nbsp;<img src='/images/shop/ico_family.png' alt='패밀리룸' title='패밀리룸'>&nbsp;<img src='/images/shop/ico_wifi.png' alt='와이파이' title='와이파이'>&nbsp;<img src='/images/shop/ico_gg.png' alt='단체주문' title='단체주문'></td>
        <td class="alignC"><a href="/shop/shop_view.asp?CHAINID=3203" class="f12bG btn8">매장 상세정보</a></td>
    </tr>
    ... (이하 생략)
</tbody>
'''
def getBBQAddress(result):
   
    BBQ_URL = 'https://www.bbq.co.kr/shop/shop_ajax.asp?page=1&pagesize=2000&gu=&si='
    print(BBQ_URL)

    rcv_data = get_request_url(BBQ_URL)
    soupData = BeautifulSoup(rcv_data, 'html.parser')

    tbody = soupData.find('tbody')
    
    tr_tag = []

    for store_tr in tbody.findAll('tr'):
        tr_tag = list(store_tr.strings)
        store_name = tr_tag[1]
        store_address = tr_tag[3]
        store_sido_gu = store_address.split()[:2]
            
        result.append([store_name] + store_sido_gu + [store_address])
    
    return

'''
#페리카나 HTML 구조
<table class="table mt20">
<tbody>
	<tr>
	    <td class="t_center">가양동점</td>
	    <td>서울특별시 강서구 강서로74길 12 (가양동)</td>
	    <td class="t_center">
	    02-3663-3700</td>
	    <td class="t_center"><a href="#none" class="button h22 btn_gray" onclick="store_view('126.84170552834682','37.56748111916124','가양동점','02-3663-3700','서울특별시 강서구 강서로74길 12 (가양동)' );">상세정보</a></td>
	</tr>
</tbody>
</table>
'''
def getPelicanaAddress(result):
    
    for page_idx in count():
        
        Pelicana_URL = 'http://www.pelicana.co.kr/store/stroe_search.html?&branch_name=&gu=&si=&page=%s' % str(page_idx + 1)
        print ("[Pericana Page] : [%s]" % (str(page_idx + 1)))

        rcv_data = get_request_url(Pelicana_URL)
        soupData = BeautifulSoup(rcv_data, 'html.parser')
        
        store_table = soupData.find('table', attrs={'class':'table mt20'})
        tbody = store_table.find('tbody')
        bEnd = True
        for store_tr in tbody.findAll('tr'):
            bEnd = False
            tr_tag = list(store_tr.strings)
            store_name = tr_tag[1]
            store_address = tr_tag[3]
            store_sido_gu = store_address.split()[:2]

            result.append([store_name] + store_sido_gu + [store_address])

        if (bEnd == True):
            return

    return

'''
#굽네치킨 XML 형식
<lists>
    <item seq="a">
        <aname1>경기가평군가평점</aname1>
        <aname2>경기</aname2>
        <aname3>가평군</aname3>
        <aname4>경기 가평군 가평읍 석봉로</aname4>
        <aname5>경기도가평군가평읍석봉로230</aname5>
        <aname6>031</aname6>
        <aname7>031-581-9982</aname7>
        <aname8>287</aname8>
    </item>
</lists>
'''
def  getNeneAdddress(result):

    Nene_URL = 'http://nenechicken.com/subpage/where_list.asp?target_step2=%s&proc_type=step1&target_step1=%s' % (urllib.parse.quote('전체'), urllib.parse.quote('전체'))
    
    rcv_data = get_request_url(Nene_URL)

    root = ET.fromstring(rcv_data)
    
    for element in root.findall('item'):
        store_name = element.findtext('aname1')
        store_sido = element.findtext('aname2')
        store_gungu = element.findtext('aname3')
        store_address = element.findtext('aname5')
        
        result.append([store_name] + [store_sido] + [store_gungu] + [store_address])

    return

'''
#교촌치킨 HTML 구조
<div class="shopSchList">
	<!-- 매장 리스트 -->
	<ul class="list">
		<li>
			<a href="javascript:mapchange('서울 강동구 고덕동 650-1','고덕1호','541');">
				<dl>
					<dt>고덕1호</dt>
					<dd>
						서울 강동구 고덕동 650-1<br />
						(서울특별시 강동구 고덕로61길 116)<br />
						02 -481-9503~4
					</dd>
				</dl>
			</a>
			<p class="goView" onclick="return location.href='/shop/domestic_sch.asp?shop_id=541&sido1=1&sido2=2'"><img src="../images/shop/bg_btn_shop_on.gif" alt="상세" /></p>
		</li>
	</ul>
	<!-- 지도 -->
	<div class="mapBox" id="itfsMap">
	</div>
</div>
'''
def getKyochonAddress(sido1, result):
    
    for sido2 in count():
        Kyochon_URL = 'http://www.kyochon.com/shop/domestic.asp?txtsearch=&sido1=%s&sido2=%s' % (str(sido1), str(sido2+1))
        print (Kyochon_URL)

        try:
            rcv_data = get_request_url(Kyochon_URL)
            soupData = BeautifulSoup(rcv_data, 'html.parser')
    
            ul_tag= soupData.find('ul', attrs={'class': 'list'})

            for store_data in ul_tag.findAll('a', href=True):
                store_name = store_data.find('dt').get_text()
                store_address = store_data.find('dd').get_text().strip().split('\r')[0]
                store_sido_gu = store_address.split()[:2]
                result.append([store_name] + store_sido_gu + [store_address])
        except:
            break

    return

'''
#처갓집 양념치킨 HTML 구조
<table width="430" border="0" cellpadding="0" cellspacing="1" bgcolor="#E8E8E8">
<tr> 
    <td height="2" colspan="3" bgcolor="#70C5C2"></td>
</tr>
<tr align="center" bgcolor="#DDEFEE"> 
    <td width='80'><b>체인명</b></td>
    <td><b>주소</b></td>
    <td width='100'><b>전화번호</b></td>
</tr>
<tr align="center" bgcolor="#FFFFFF"> 
    <td>강화남산점<br></td>
    <td align='left'>인천시 강화군 강화읍 충렬사로 57</td>
    <td>032-933-2201<br/></td>
</tr>
</table>
'''
def CheogajipAddress(result):
    
    for page_idx in count():

        Cheogajip_URL = 'http://www.cheogajip.co.kr/establish02_02.html?&search=&keyword=&page=%s' % str(page_idx+1)
    
        print (Cheogajip_URL)
        response = urllib.request.urlopen(Cheogajip_URL)
        soupData = BeautifulSoup(response.read().decode('CP949'), 'html.parser')

        store_trs = soupData.findAll('tr', attrs={'align': 'center', 'bgcolor':'#FFFFFF'})

        if (store_trs):
            for store_tr in store_trs:
                tr_tag = list(store_tr.strings)
                if (tr_tag[1].count('[휴점]') == 0):
                    store_name = tr_tag[1]
                    store_address = tr_tag[3]
                    store_sido_gu = store_address.split()[:2]
                    result.append([store_name] + store_sido_gu + [store_address])
        else:
            break

    return
'''
#굽네치킨 HTML 형식
<tbody id="store_list">
    <tr class="on lows" idx="788" onclick="store.viewdt('788','37.2755111612','127.070853941');" id="788">
        <td>흥덕지구점<span><!--031-651-9294--></span></td>
        <td class="store_phone">
            <a href="javascript:void(0);" onclick="store.teldt('031-212-9293');">031-212-9293</a>
        </td>
        <td class="t_left">
    		<a href="javascript:void(0);">경기도 용인시 기흥구  흥덕1로 79번길 9, 105호</a>
    		<p>
    		<i class="online ">온라인</i>
     		<i class="coupon ">e-쿠폰</i>
			<!--<i class="cesco on">세스코</i>-->
			<i class="card_dis ">카드할인</i>
    		</p>
	</td>
</tr>
'''
from selenium import webdriver
import time
def GoobneAddress(result):

    Goobne_URL = 'http://www.goobne.co.kr/store/search_store.jsp'
    
    wd = webdriver.Chrome('d:/Program Files/Python/WebDriver/chromedriver.exe')
    wd.get(Goobne_URL)
    time.sleep(10)

    for page_idx in count():
        
        wd.execute_script("store.getList('%s')" % str(page_idx + 1))
        print ("PageIndex [%s] Called" % (str(page_idx + 1)))

        time.sleep(5)
 
        rcv_data = wd.page_source
        
        soupData = BeautifulSoup(rcv_data, 'html.parser')
        
        for store_list in soupData.findAll('tbody', attrs={'id': 'store_list'}):
            for store_tr in store_list:
                tr_tag = list(store_tr.strings)
                if (tr_tag[0] == '등록된 데이터가 없습니다.'):
                   return result
               
                store_name = tr_tag[1]
                if (tr_tag[3] == ''):
                    store_address = tr_tag[5]
                else:
                    store_address = tr_tag[6]
                store_sido_gu = store_address.split()[:2]

                result.append([store_name] + store_sido_gu + [store_address])

    return

def main():

    result = []

    print('BBQ ADDRESS CRAWLING START')
    getBBQAddress(result)
    bbq_table = pd.DataFrame(result, columns=('store', 'sido', 'gungu', 'store_address'))
    bbq_table.to_csv("d:/temp/chicken_data/bbq.csv", encoding="cp949", mode='w', index=True)
    del result[:]

    print('PERICANA ADDRESS CRAWLING START')
    getPelicanaAddress(result)
    pericana_table = pd.DataFrame(result, columns=('store', 'sido', 'gungu', 'store_address'))
    pericana_table.to_csv("d:/temp/chicken_data/pericana.csv", encoding="cp949", mode='w', index=True)
    del result[:]

    print('NENE ADDRESS CRAWLING START')
    getNeneAdddress(result)
    nene_table = pd.DataFrame(result, columns=('store', 'sido', 'gungu', 'store_address'))
    nene_table.to_csv("d:/temp/chicken_data/nene.csv", encoding="cp949", mode='w', index=True)
    del result[:]

    print('KYOCHON ADDRESS CRAWLING START')
    for sido1 in range(1, 18):
        getKyochonAddress(sido1, result)
    kyochon_table = pd.DataFrame(result, columns=('store', 'sido', 'gungu', 'store_address'))
    kyochon_table.to_csv("d:/temp/chicken_data/kyochon.csv", encoding="cp949", mode='w', index=True)
    del result[:]

    print('CHEOGAJIP ADDRESS CRAWLING START')
    CheogajipAddress(result)
    cheogajip_table = pd.DataFrame(result, columns=('store', 'sido', 'gungu', 'store_address'))
    cheogajip_table.to_csv("d:/temp/chicken_data/cheogajip.csv", encoding="cp949", mode='w', index=True)
    del result[:]

    print('GOOBNE ADDRESS CRAWLING START')
    GoobneAddress(result)
    goobne_table = pd.DataFrame(result, columns=('store', 'sido', 'gungu', 'store_address'))
    goobne_table.to_csv("d:/temp/chicken_data/goobne.csv", encoding="cp949", mode='w', index=True)

    print('FINISHED')
    
if __name__ == '__main__':
     main()