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
    
    


time.sleep(3)

# 필요한 작업 수행 후 드라이버 종료
driver.quit()
