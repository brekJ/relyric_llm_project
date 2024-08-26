from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

import time
import random

SLEEP_TIMES = [x/10 for x in [40, 60, 10, 50]]

# webdriver_manager를 사용하여 크롬 드라이버의 실행 경로 설정
service = Service(executable_path=ChromeDriverManager().install())
# 설정된 service를 사용하여 크롬 드라이버 인스턴스 생성
driver = ChromeDriver(service=service)
driver.implicitly_wait(10)  # 최대 10초 동안 대기

# 테스트하려는 웹사이트 열기
driver.get("https://www.melon.com/chart/index.htm")
x_path = r'/html/body/div/div[2]/div/div[2]/ul[1]/li[1]/div/div/button'
driver.find_element(By.XPATH, x_path).click()

x_path = r'/html/body/div/div[3]/div/div/form/div[1]/div/h4[2]/a'
driver.find_element(By.XPATH, x_path).click()
try:
    for period in range(5):
        period_x_path = r'/html/body/div/div[3]/div/div/form/div[1]/div/div/div[1]/div[1]/ul/li[' + str(period + 1) + r']/span'
        period_btn = driver.find_element(By.XPATH, period_x_path)
        period_btn.click()
        time.sleep(random.choice(SLEEP_TIMES))
        for year in range(10):
            if period == 0 and year >= 5:
                continue
            if period == 4 and year >= 6:
                continue
            year_x_path = r'/html/body/div/div[3]/div/div/form/div[1]/div/div/div[2]/div[1]/ul/li[' + str(year + 1) + r']/span'
            year_btn = driver.find_element(By.XPATH, year_x_path)
            year_btn.click()
            time.sleep(random.choice(SLEEP_TIMES))
            for month in range(12):
                if period == 0 and year == 0 and month >= 7:
                    continue
                if period == 4 and year == 5 and month >= 11:
                    continue
                month_x_path = r'/html/body/div/div[3]/div/div/form/div[1]/div/div/div[3]/div[1]/ul/li'
                month_btns = driver.find_elements(By.XPATH, month_x_path)
                for month_btn in month_btns:
                    month_btn.find_element(By.XPATH, './span').click()
                    time.sleep(random.choice(SLEEP_TIMES))
                    
                    cat_btns = driver.find_elements(By.XPATH, r'/html/body/div/div[3]/div/div/form/div[1]/div/div/div[5]/div[1]/ul/li')
                    cat_btns[0].find_element(By.XPATH, './span').click()
                    time.sleep(random.choice(SLEEP_TIMES))
                    
                    btn_x_path = r'/html/body/div/div[3]/div/div/form/div[2]/button'
                    driver.find_element(By.XPATH, btn_x_path).click()
                    time.sleep(random.choice(SLEEP_TIMES))
                    
                    elements = driver.find_elements(By.XPATH, r'/html/body/div/div[3]/div/div/div/div[1]/div[2]/form/div[1]/table/tbody/tr')
                    for element in elements:
                        element.find_element(By.XPATH, './td[4]/div/a').click()
                        time.sleep(random.choice(SLEEP_TIMES))
                        print(driver.find_element(By.XPATH, r'/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[1]/div[1]').text)
                        print(driver.find_element(By.XPATH, r'/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[1]/div[2]').text)
                        print(driver.find_element(By.XPATH, r'/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[2]/dl/dd[3]').text)
                        print(driver.find_element(By.XPATH, r'/html/body/div[1]/div[3]/div/div/div/div[2]/div[2]/div').text)
                        driver.back()
                        time.sleep(random.choice(SLEEP_TIMES))
                    driver.quit()
                    exit()
except:
    print(f"period : {period + 1}")
    print(f"year : {year + 1}")
    print(f"month : {month + 1}")
            
        
        

# 필요한 작업 수행 후 드라이버 종료
driver.quit()
exit()
r'/html/body/div/div[3]/div/div/form/div[1]/div/div/div[1]/div[1]/ul/li[2]/span/input'
for i in range(7):
    year_month_btn.click()
    month_btn = r'#conts > div.calendar_prid > div > div > dl > dd.month_calendar > ul > li:nth-child(' + str(i+1) + r') > a'
    driver.find_element(By.CSS_SELECTOR, month_btn).click()
    time.sleep(random.choice(SLEEP_TIMES))

for index in range(100, 800+1, 100):
    url = f"https://www.melon.com/chart/month/index.htm?classCd=GN0{index}"
    driver.get(url)
    xpath = r'//*[@id="lst50"]/td[5]/div/a'
    elements = driver.find_elements(By.XPATH, xpath)
    for element in elements:
        element.click()
        spread = driver.find_element(By.XPATH, r'//*[@id="lyricArea"]/button/i')
        spread.click()
        text = driver.find_element(By.XPATH, r'//*[@id="d_video_summary"]').text
        print(text)
        driver.back()
        time.sleep(random.choice(SLEEP_TIMES))
    time.sleep(random.choice(SLEEP_TIMES))


