from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver as ChromeDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

import time
import random
import gc

from chat_driver import ChatDriver as ChatDriver

from pymongo import MongoClient

def xpath_element(driver, xpath):
    return driver.find_element(By.XPATH, xpath)

# MongoDB 클라이언트 생성
client = MongoClient('localhost', 27017)

# 데이터베이스 선택
db = client['mel_lyrics']

# 컬렉션 선택
collection = db['songs']

# Sleep 시간 설정
SLEEP_TIMES = [x/10 for x in [40, 20, 10, 30]]

# webdriver_manager를 사용하여 크롬 드라이버의 실행 경로 설정
service = Service(executable_path=ChromeDriverManager().install())

# chatgpt를 사용할 driver 생성
driver_chat = ChatDriver()

# 설정된 service를 사용하여 크롬 드라이버 인스턴스 생성
driver = ChromeDriver(service=service)
driver.implicitly_wait(10)  # 최대 10초 동안 대기

# 테스트하려는 웹사이트 열기
driver.get("https://www.melon.com/chart/index.htm")

# 차트 파인더 페이지로 이동
xpath_element(driver, r'/html/body/div/div[2]/div/div[2]/ul[1]/li[1]/div/div/button').click()

# 월간 차트 클릭
xpath_element(driver, r'/html/body/div/div[3]/div/div/form/div[1]/div/h4[2]/a').click()

# 중복 검사할 리스트 생성
check_list = []
try:
    with open("check_list.txt", 'r') as f:
        check_list = f.read().split("\n")
except:
    pass

# 일련번호 정의
id = len(check_list) - 1

# 중단시 재시작을 위한 변수
off_period = 1
off_year = 1
off_month = 4
off_el_idx = 41
try:
    # 시대별 차트 클릭
    for period in range(5):
        # 중단된 크롤러를 다시 실행할 때 사용
        if period < off_period:
            continue
        period_x_path = r'/html/body/div/div[3]/div/div/form/div[1]/div/div/div[1]/div[1]/ul/li[' + str(period + 1) + r']/span'
        period_btn = xpath_element(driver, period_x_path)
        period_btn.click()
        time.sleep(random.choice(SLEEP_TIMES))
        # 년도별 차트 클릭
        for year in range(10):
            if period == 0 and year >= 5:
                continue
            if period == 4 and year >= 6:
                continue
            # 중단된 크롤러를 다시 실행할 때 사용
            if period == off_period and year < off_year:
                continue
            year_x_path = r'/html/body/div/div[3]/div/div/form/div[1]/div/div/div[2]/div[1]/ul/li[' + str(year + 1) + r']/span'
            year_btn = xpath_element(driver, year_x_path)
            year_btn.click()
            time.sleep(random.choice(SLEEP_TIMES))
            # 월별 차트 클릭
            for month in range(12):
                if period == 0 and year == 0 and month >= 7:
                    continue
                if period == 4 and year == 5 and month >= 11:
                    continue
                # 중단된 크롤러를 다시 실행할 때 사용
                if period == off_period and year == off_year and month < off_month:
                    continue
                month_x_path = r'/html/body/div/div[3]/div/div/form/div[1]/div/div/div[3]/div[1]/ul/li[' + str(month + 1) + r']/span'
                driver.find_element(By.XPATH, month_x_path).click()
                time.sleep(random.choice(SLEEP_TIMES))
                
                cat_btns = driver.find_elements(By.XPATH, r'/html/body/div/div[3]/div/div/form/div[1]/div/div/div[5]/div[1]/ul/li')
                cat_btns[0].find_element(By.XPATH, './span').click()
                time.sleep(random.choice(SLEEP_TIMES))
                    
                btn_x_path = r'/html/body/div/div[3]/div/div/form/div[2]/button'
                xpath_element(driver, btn_x_path).click()
                time.sleep(random.choice(SLEEP_TIMES))
                
                elements = driver.find_elements(By.XPATH, r'/html/body/div/div[3]/div/div/div/div[1]/div[2]/form/div[1]/table/tbody/tr')
                for el_idx, element in enumerate(elements):
                    if el_idx == 50:
                        driver.find_element(By.XPATH, r'/html/body/div/div[3]/div/div/div/div[1]/div[2]/form/div[2]/span/a').click()
                        time.sleep(random.choice(SLEEP_TIMES))
                    # 중단된 크롤러를 다시 실행할 때 사용
                    if period == off_period and year == off_year and month == off_month and el_idx < off_el_idx:
                        continue
                    element.find_element(By.XPATH, './td[4]/div/a').click()
                    time.sleep(random.choice(SLEEP_TIMES))
            
                    song_title = driver.find_element(By.XPATH, r'/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[1]/div[1]').text
                    song_singer = driver.find_element(By.XPATH, r'/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[1]/div[2]').text
                    song_gengre = driver.find_element(By.XPATH, r'/html/body/div[1]/div[3]/div/div/div/form/div/div/div[2]/div[2]/dl/dd[3]').text
                    song_lyric = driver.find_element(By.XPATH, r'/html/body/div[1]/div[3]/div/div/div/div[2]/div[2]/div').text
                    if period == 0:
                        song_year = 2024 - year
                    elif period == 1:
                        song_year = 2019 - year
                    elif period == 2:
                        song_year = 2009 - year
                    elif period == 3:
                        song_year = 1999 - year
                    elif period == 4:
                        song_year = 1989 - year
                    # check_list에 중복 검사
                    if f"({song_title}, {song_singer})" in check_list:
                        driver.back()
                        time.sleep(random.choice(SLEEP_TIMES))
                        continue
                    
                    song_mood = driver_chat.make_mood(song_lyric)
                    if song_mood is None:
                        assert False, "Failed to retrieve the mood"
                    
                        
                    # mongoDB에 저장할 document 생성
                    document = {
                        'id':id,
                        'title':song_title,
                        'singer':song_singer,
                        'gengre':song_gengre,
                        'lyric':song_lyric,
                        'mood':song_mood,
                        'year':song_year}
                    # document 삽입
                    collection.insert_one(document)
                    with open('check_list.txt', 'a') as f:
                        f.write(f"({song_title}, {song_singer})\n")
                    check_list.append(f"({song_title}, {song_singer})")
                    driver.back()
                    
                    print(f'id: {id} done')
                    print(f"{song_title, song_singer}")
                    print(f"{check_list=}")
                    print(f"{song_mood=}")
                    # if el_idx == 49:
                    #     driver.find_element(By.XPATH, r'/html/body/div/div[3]/div/div/div/div[1]/div[2]/form/div[2]/span/a').click()
                    #     time.sleep(random.choice(SLEEP_TIMES))
                    
                    gc.collect()
                    time.sleep(random.choice(SLEEP_TIMES))
                    id += 1
                    
except Exception as e:
    print(f"Error encountered: {e}")
    print(f"period : {period + 1}")
    print(f"year : {year + 1}")
    print(f"month : {month + 1}")
    print(f"el_idx : {el_idx + 1}")
    print(f"title : {song_title}")
    print(f"singer : {song_singer}")
            
        
        

# 필요한 작업 수행 후 드라이버 종료
driver.quit()
exit()
