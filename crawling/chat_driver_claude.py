from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
import subprocess
import time

import pandas as pd

import os
import random
import platform

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pyautogui as pg

SLEEP_TIMES = [x/10 for x in [40, 20, 10, 30]]

def r_sleep():
    time.sleep(random.choice(SLEEP_TIMES))

class ChatDriver():
    def __init__(self, go_id):
        self.go_id = go_id
        self.chat_cnt = 6
        # 디버거 모드로 Chrome 구동 (리눅스용으로 경로 수정)
        if platform.system() == "Linux":
            subprocess.Popen(["/usr/bin/google-chrome", "--remote-debugging-port=9223", "--user-data-dir=/tmp/chrome_dev_test", "--disable-dev-shm-usage"])
        elif platform.system() == "Windows":
            chrome_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
            subprocess.Popen([chrome_path, "--remote-debugging-port=9221", "--user-data-dir=C:\\tmp\\chrome_dev_test"])

        # Chrome 옵션 설정
        option = Options()
        option.add_experimental_option("debuggerAddress", "127.0.0.1:9221")

        # Chrome 버전 가져오기 및 ChromeDriver 경로 설정
        chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
        if platform.system() == "Linux":
            driver_path = f'./{chrome_ver}/chromedriver'
        elif platform.system() == "Windows":
            driver_path = f'./{chrome_ver}/chromedriver.exe'
        
        # Windows의 경우와 달리, 리눅스에서는 .exe 확장자가 없습니다.
        service = Service(driver_path)

        try:
            self.driver_chat = webdriver.Chrome(service=service, options=option)
        except Exception as e:
            print(f"Error encountered: {e}")
            # ChromeDriver 자동 설치 (이미 설치되어 있으면 해당 경로 사용)
            chromedriver_autoinstaller.install(True)
            self.driver_chat = webdriver.Chrome(service=Service(driver_path), options=option)
        # 암시적 대기
        self.driver_chat.implicitly_wait(20)

        self.driver_chat.get("https://claude.ai/")
        try:
            self.driver_chat.find_element(By.XPATH, r'/html/body/div[2]/div/main/div[3]/div[2]/ul/li[1]/a').click()
        except Exception as e:
            print(f"Error encountered: {e}")
        r_sleep()
        # try:
        #     # 로그인 버튼 클릭
        #     self.driver_chat.find_element(By.XPATH, r'/html/body/div[1]/div[1]/div/main/div[1]/div[1]/div/div[1]/div/div[3]/div/button[1]').click()

        #     # Google 계정으로 로그인 버튼 클릭
        #     self.driver_chat.find_element(By.XPATH, r'/html/body/div/main/section/div[2]/div[3]/button[1]').click()

        #     # workspace 선택
        #     self.driver_chat.find_element(By.XPATH, r'/html/body/div[3]/div/div/div/div[2]/div/div/button[1]').click()
        # except Exception as e:
        #     print(f"Error encountered: {e}")
        self.tuning_df = pd.read_csv("../fine_tuning/tuning_dataset.csv", index=False)


    
    def make_response(self, song):
        len_list = []
        df_length = len(self.tuning_df)
        for _ in range(100):
            r_choice = random.choice(range(df_length))
            if r_choice in len_list:
                continue
            examples = """#### 예시\n"""
            examples += self.tuning_df.loc[r_choice, "inputs"].split("작성하라")[-1]
            examples += self.tuning_df.loc[r_choice, "response"]
            examples += "\n"
            len_list.append(r_choice)
            if len(len_list) == 3:
                break
        chat_template = '''lyric_template = f\"\"\"조건에 맞추어서 입력 가사를 출력 가사로 재작성하라.
        단, 상위 > 중위 > 하위 순으로 중요도가 존재한다.

        [상위 조건]
        -- 입력되는 상황에 어울리도록 작성하라
        -- 입력 가사와 출력 가사의 리듬 및 음절 수를 일치하라

        [중위 조건]
        -- 입력 가사의 리듬과 Rhyme을 유지하라
        -- 입력 가사의 단어의 음절과 강세, 발음을 고려하라
        -- 입력 가사와 동일한 단어를 사용할 수는 있지만 남발해서는 안된다.

        [하위 조건]
        -- 발음하기 쉽고, 노래부르기에 적합하도록 작성하라

        입력 가사: {input_lyrics} 

        상황 : {situation}

        출력 가사: \"\"\"

        #### 입력 가사 : '''
        examples += chat_template
        examples += song
        
        try:
            if self.go_id == "gmail":
                input_area = WebDriverWait(self.driver_chat, 10).until(
                    EC.element_to_be_clickable((By.XPATH, r'/html/body/div[2]/div/div/div[2]/div[1]/div[2]/div/fieldset/div[1]/div[1]/div[1]/div/p'))
                )
                input_area.send_keys(examples)
                r_sleep()
                input_btn = WebDriverWait(self.driver_chat, 10).until(
                    EC.element_to_be_clickable((By.XPATH, r'/html/body/div[2]/div/div/div[2]/div[1]/div[2]/div/fieldset/div[1]/div[1]/div[3]/div/button'))
                )
                input_btn.click()
                r_sleep()
        except TimeoutException:
            print("Failed to find or interact with the input area")
            pg.press('enter')
            # return None
        time.sleep(7)
        input_df = song
        situation_df = self.driver_chat.find_element(By.XPATH, f'/html/body/div[2]/div/div/div[2]/div[1]/div[1]/div[{self.chat_cnt}]/div/div/div[1]/div/div/p[1]').text
        situation_df = situation_df.split("노래를 ")[-1]
        situation_df = situation_df.split(".")[0]
        df_inputs = f"""조건에 맞추어서 입력 가사를 출력 가사로 재작성하라.
단, 상위 > 중위 > 하위 순으로 중요도가 존재한다.

[상위 조건]
-- 입력되는 상황에 어울리도록 작성하라
-- 입력 가사와 출력 가사의 리듬 및 음절 수를 일치하라

[중위 조건]
-- 입력 가사의 리듬과 Rhyme을 유지하라
-- 입력 가사의 단어의 음절과 강세, 발음을 고려하라
-- 입력 가사와 동일한 단어를 사용할 수는 있지만 남발해서는 안된다.

[하위 조건]
-- 발음하기 쉽고, 노래부르기에 적합하도록 작성하라


입력 가사: {input_df} 

상황 : {situation_df}

출력 가사: """
        self.driver_chat.find_element(By.XPATH, f'/html/body/div[2]/div/div/div[2]/div[1]/div[1]/div[{self.chat_cnt}]/div/div/div[1]/div/div/div/button').click()
        r_sleep()
        p_s = self.driver_chat.find_element(By.XPATH, r'/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/div[3]/div/div/div')
        p_s = p_s.find_elements(By.XPATH, "/p")
        response = ""
        for p in p_s:
            response = response + p.text + '\n\n'
        response -= '\n\n'
        self.driver_chat.find_element(By.XPATH, r'/html/body/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/div[1]/div[2]/button').click()
        r_sleep()
        data = pd.DataFrame({"inputs": [df_inputs], "response": [response]})
        self.tuning_df = pd.concat([self.tuning_df, data], ignore_index=True)
        print(f"{len(self.tuning_df)=}")
        self.tuning_df.to_csv("../fine_tuning/tuning_dataset.csv", index=False)
        self.chat_cnt += 2
        

if __name__ == "__main__":
    drive = ChatDriver("gmail")
    with open("../songs.json", "r", encoding="utf-8") as f:
        song_dicts = f.read()
    song_lists = song_dicts.split("\n")
    song_len = len(song_lists)
    for _ in range(940):
        r_song_cnt = random.choice(range(song_len))
        lyric = song_lists[r_song_cnt].split("\"lyric\":")[-1]
        lyric = lyric.split(",\"mood\"")[0]

        drive.make_response(lyric)

