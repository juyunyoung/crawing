import time
import random
from typing import List, Dict
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
import os
import platform

# Chrome 옵션 설정
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)

def crawl_gemini_models():
    """Gemini 모델 정보를 크롤링하는 함수"""
    base_url = "https://ai.google.dev/gemini-api/docs/models"
    driver = webdriver.Chrome(options=options)
    
    try:
        # 웹드라이버 감지 방지
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # 페이지 로드
        driver.get(base_url)
        
        # 페이지가 완전히 로드될 때까지 대기
        time.sleep(5)
        
        print("페이지 로드 완료")
        
        # 올바른 CSS 선택자 사용 (.devsite-table-wrapper)
        try:
            # 먼저 페이지에 devsite-table-wrapper 요소가 있는지 확인
            elements = driver.find_elements(By.CSS_SELECTOR, '.devsite-table-wrapper')
            print(f"Found {len(elements)} devsite-table-wrapper elements")
            
            if elements:
                # 첫 번째 요소의 텍스트 출력
                print("Found element content:", elements[0].text)
                return elements[0].text
            else:
                # 대안: 다른 선택자들 시도
                print("No devsite-table-wrapper found, trying alternative selectors...")
                
                # 테이블 관련 요소들 찾기
                tables = driver.find_elements(By.TAG_NAME, 'table')
                print(f"Found {len(tables)} tables")
                
                # gemini-api-model-table 클래스를 가진 테이블 찾기
                model_tables = driver.find_elements(By.CSS_SELECTOR, '.gemini-api-model-table')
                print(f"Found {len(model_tables)} gemini-api-model-table elements")
                
                if model_tables:
                    print("Found model table content:", model_tables[0].text)
                    return model_tables[0].text
                
                # 더 일반적인 테이블 선택자 시도
                all_tables = driver.find_elements(By.CSS_SELECTOR, 'table')
                if all_tables:
                    print("Found general table content:", all_tables[0].text)
                    return all_tables[0].text
                
        except Exception as e:
            print(f"Error finding elements: {e}")
            
        # 페이지 소스 출력하여 디버깅
        print("Page source preview:")
        page_source = driver.page_source
        print(page_source[:2000])
        
        # BeautifulSoup으로 파싱 시도
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # devsite-table-wrapper 클래스를 가진 div 찾기
        table_wrappers = soup.find_all('div', class_='devsite-table-wrapper')
        print(f"BeautifulSoup found {len(table_wrappers)} devsite-table-wrapper divs")
        
        if table_wrappers:
            print("BeautifulSoup content:", table_wrappers[0].get_text())
            return table_wrappers[0].get_text()
        
        # gemini-api-model-table 클래스를 가진 테이블 찾기
        model_tables = soup.find_all('table', class_='gemini-api-model-table')
        print(f"BeautifulSoup found {len(model_tables)} gemini-api-model-table tables")
        
        if model_tables:
            print("BeautifulSoup model table content:", model_tables[0].get_text())
            return model_tables[0].get_text()
        
        return None
        
    except Exception as e:
        print(f"General error: {e}")
        return None
        
    finally:
        driver.quit()

def main():
    """메인 함수"""
    print("Gemini 모델 크롤링 시작...")
    result = crawl_gemini_models()
    
    if result:
        print("크롤링 성공!")
        print("결과:")
        print(result)
    else:
        print("크롤링 실패")

if __name__ == "__main__":
    main() 