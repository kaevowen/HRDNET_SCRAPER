import json
import selenium

from time import sleep
from selenium import webdriver


class getCB_Value:
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('headless')
        self.options.add_argument('window-size=1280x1024')
        self.options.add_argument('disable-gpu')
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"
        )

    def get_area_json(self):
        _area = dict()
        try:
            with open(".\\AreaCd.json", 'r', encoding='utf-8') as f:
                return json.load(f)

        except FileNotFoundError:
            dr = webdriver.Chrome('C:\\chromedriver\\chromedriver.exe', options=self.options)
            dr.get('http://www.hrd.go.kr/hrdp/ma/pmmao/indexNew.do')

            _area = dict()
            print("지역 데이터를 다운로드 중입니다...")
            dr.find_element_by_xpath('//*[@id="btnRegion"]').click()
            sleep(0.1)
            for i in dr.find_elements_by_xpath('//*[@id="areaUl"]//li'):
                _area2 = dict()
                _area[i.text] = dict()
                i.click()
                sleep(0.05)
                dr.switch_to.window(self.dr.window_handles[0])
                for j in dr.find_elements_by_xpath('//*[@id="areaUl2"]/li'):
                    _area2[j.text] = j.get_attribute('data-code')
                    print(f'{i.text} {j.text}')

                _area[i.text] = _area2

            dr.quit()

            with open(".\\AreaCd.json", 'w+', encoding='utf-8') as f:
                return json.dump(_area, f, indent=4, ensure_ascii=False)

    def get_ncs_json(self):
        try:
            with open(".\\NCSCd.json", 'r', encoding='utf-8') as f:
                return json.load(f)

        except FileNotFoundError:
            dr = webdriver.Chrome('C:\\chromedriver\\chromedriver.exe', options=self.options)
            dr.get('http://www.hrd.go.kr/hrdp/ma/pmmao/indexNew.do')

            _ncs = dict()
            _ncs1 = dict()
            print("ncs 데이터를 다운로드 중입니다...")
            dr.find_element_by_xpath('//*[@id="btnCategory"]').click()
            sleep(0.1)
            for i in dr.find_elements_by_xpath('//*[@id="ncsDept1"]/li'):
                _ncs2 = dict()
                _ncs1[i.text] = dict()
                i.click()
                sleep(1)
                for j in dr.find_elements_by_xpath('//*[@id="ncsDept2"]/li'):
                    _ncs3 = dict()
                    _ncs2[j.text] = j.get_attribute('data-code')
                    j.click()
                    sleep(1)

                    for k in dr.find_elements_by_xpath('//*[@id="ncsDept3"]/li'):
                        _ncs4 = dict()
                        _ncs3[k.text] = k.get_attribute('data-code')
                        k.click()
                        sleep(1)

                        for l in dr.find_elements_by_xpath('//*[@id="ncsDept4"]/li'):
                            _ncs4[l.text] = l.get_attribute('data-code')
                            print(f'{i.text} {j.text} {k.text} {l.text}')

                        if k.text != '전체':
                            _ncs3[k.text] = _ncs4
                    _ncs2[j.text] = _ncs3
                _ncs[i.text] = _ncs2

            dr.quit()

            with open(".\\NCSCd.json", 'w+', encoding='utf-8') as f:
                return json.dump(_ncs, f, indent=4, ensure_ascii=False)

