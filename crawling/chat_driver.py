from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import chromedriver_autoinstaller
import subprocess
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
class ChatDriver():
    def __init__(self):
        self.chat_cnt = 2
        # 디버거 모드로 Chrome 구동 (리눅스용으로 경로 수정)
        subprocess.Popen(["/usr/bin/google-chrome", "--remote-debugging-port=9223", "--user-data-dir=/tmp/chrome_dev_test", "--disable-dev-shm-usage"])

        # subprocess.Popen(["/usr/bin/google-chrome", "--remote-debugging-port=9222", "--user-data-dir=/tmp/chrome_dev_test"])

        # Chrome 옵션 설정
        option = Options()
        option.add_experimental_option("debuggerAddress", "127.0.0.1:9223")

        # Chrome 버전 가져오기 및 ChromeDriver 경로 설정
        chrome_ver = chromedriver_autoinstaller.get_chrome_version().split('.')[0]
        driver_path = f'./{chrome_ver}/chromedriver'

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

        self.driver_chat.get("https://chatgpt.com/")

        # try:
        #     # 로그인 버튼 클릭
        #     self.driver_chat.find_element(By.XPATH, r'/html/body/div[1]/div[1]/div/main/div[1]/div[1]/div/div[1]/div/div[3]/div/button[1]').click()

        #     # Google 계정으로 로그인 버튼 클릭
        #     self.driver_chat.find_element(By.XPATH, r'/html/body/div/main/section/div[2]/div[3]/button[1]').click()

        #     # workspace 선택
        #     self.driver_chat.find_element(By.XPATH, r'/html/body/div[3]/div/div/div/div[2]/div/div/button[1]').click()
        # except Exception as e:
        #     print(f"Error encountered: {e}")
    
    def make_mood(self, lyric):
        chat_template = f'''####
        input
        노래가사 : {lyric}

        분위기 종류 : 밝고 긍정적임: 에너지 넘치고 희망적인 분위기,
        슬픔 : 슬픔, 눈물, 그리움을 담은 분위기,
        어둡고 우울함: 절망, 긴장, 불안을 담은 분위기,
        로맨틱하고 감성적임: 사랑과 애정을 담은 분위기,
        자신감과 강렬함: 힘과 에너지가 넘치는, 결단력 있는 분위기,
        평화롭고 차분함: 조용하고 안정된 분위기,
        혼란스럽고 복잡함: 복잡한 감정과 혼란스러운 분위기,
        유쾌하고 재미있음: 가볍고 유쾌한 분위기,
        분노와 공격적임: 강한 분노와 공격성을 담은 분위기,

        #### "가사의 분위기 : "만 한글로 출력하라
        return
        가사의 분위기 : '''.replace('\n', ' ')
        
        try:
            input_area = WebDriverWait(self.driver_chat, 10).until(
                EC.element_to_be_clickable((By.XPATH, r'/html/body/div[1]/div[1]/div[2]/main/div[1]/div[2]/div[1]/div/form/div/div[2]/div/div/div[2]/textarea'))
            )
            input_area.send_keys(chat_template + '\n')
            
        except TimeoutException:
            print("Failed to find or interact with the input area")
            return None
        
        time.sleep(5)
        
        try:
            mood = WebDriverWait(self.driver_chat, 10).until(
                EC.visibility_of_element_located((By.XPATH, f'/html/body/div[1]/div[1]/div[2]/main/div[1]/div[1]/div/div/div/div/article[{self.chat_cnt}]/div/div/div[2]/div/div[1]/div/div/div/p'))
            ).text
        except TimeoutException:
            print("Failed to retrieve the mood")
            return None
        self.chat_cnt += 2
        mood = mood.split(': ')[1]
        mood = mood.replace(' ', '')
        return mood
