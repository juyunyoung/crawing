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
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', True)

def wait_for_element(driver, selector, timeout=20, by=By.CSS_SELECTOR):
    """요소가 로드될 때까지 대기하는 함수"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, selector))
        )
        return element
    except TimeoutException:
        print(f"Timeout waiting for element: {selector}")
        return None

def wait_for_elements(driver, selector, timeout=20, by=By.CSS_SELECTOR):
    """여러 요소가 로드될 때까지 대기하는 함수"""
    try:
        elements = WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((by, selector))
        )
        return elements
    except TimeoutException:
        print(f"Timeout waiting for elements: {selector}")
        return []

def crawl_gemini_models_advanced():
    """고급 Gemini 모델 크롤링 함수"""
    base_url = "https://ai.google.dev/gemini-api/docs/models"
    driver = webdriver.Chrome(options=options)
    
    try:
        # 웹드라이버 감지 방지
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # 페이지 로드
        print("페이지 로딩 중...")
        driver.get(base_url)
        
        # 초기 대기
        time.sleep(3)
        
        # 페이지가 완전히 로드될 때까지 대기
        print("페이지 완전 로드 대기 중...")
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        print("페이지 로드 완료")
        
        # 여러 선택자 시도
        selectors_to_try = [
            '.devsite-table-wrapper',
            '.gemini-api-model-table',
            'table',
            '[class*="table"]',
            '[class*="model"]'
        ]
        
        for selector in selectors_to_try:
            print(f"Trying selector: {selector}")
            
            # 요소 대기
            elements = wait_for_elements(driver, selector, timeout=10)
            
            if elements:
                print(f"Found {len(elements)} elements with selector: {selector}")
                
                # 각 요소의 텍스트 출력
                for i, element in enumerate(elements[:3]):  # 처음 3개만
                    try:
                        text = element.text.strip()
                        if text:
                            print(f"Element {i+1} content (first 200 chars): {text[:200]}")
                            return text
                    except Exception as e:
                        print(f"Error getting text from element {i+1}: {e}")
                        continue
        
        # 대안: JavaScript로 요소 찾기
        print("Trying JavaScript approach...")
        js_script = """
        return Array.from(document.querySelectorAll('*')).filter(el => {
            return el.textContent && el.textContent.includes('Gemini') || 
                   el.textContent && el.textContent.includes('model') ||
                   el.className && el.className.includes('table');
        }).map(el => el.textContent).slice(0, 5);
        """
        
        js_results = driver.execute_script(js_script)
        if js_results:
            print("JavaScript found content:", js_results[0][:200])
            return js_results[0]
        
        # BeautifulSoup으로 파싱
        print("Trying BeautifulSoup parsing...")
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # 다양한 방법으로 테이블 찾기
        table_selectors = [
            'div.devsite-table-wrapper',
            'table.gemini-api-model-table',
            'table',
            '[class*="table"]',
            '[class*="model"]'
        ]
        
        for selector in table_selectors:
            elements = soup.select(selector)
            if elements:
                print(f"BeautifulSoup found {len(elements)} elements with {selector}")
                text = elements[0].get_text(strip=True)
                if text:
                    print(f"BeautifulSoup content: {text[:200]}")
                    return text
        
        # 페이지 소스에서 직접 검색
        print("Searching in page source...")
        if 'devsite-table-wrapper' in page_source:
            print("Found 'devsite-table-wrapper' in page source")
            # 페이지 소스에서 해당 부분 추출
            start_idx = page_source.find('devsite-table-wrapper')
            if start_idx != -1:
                # 해당 부분 주변 텍스트 추출
                end_idx = page_source.find('</div>', start_idx)
                if end_idx != -1:
                    content = page_source[start_idx:end_idx+6]
                    print(f"Extracted content: {content[:500]}")
                    return content
        
        return None
        
    except Exception as e:
        print(f"General error: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        try:
            driver.quit()
        except:
            pass

def main():
    """메인 함수"""
    print("고급 Gemini 모델 크롤링 시작...")
    result = crawl_gemini_models_advanced()
    
    if result:
        print("\n" + "="*50)
        print("크롤링 성공!")
        print("="*50)
        print("결과:")
        print(result)
        
        # 결과를 파일로 저장
        with open('gemini_models_result.txt', 'w', encoding='utf-8') as f:
            f.write(result)
        print("\n결과가 'gemini_models_result.txt' 파일에 저장되었습니다.")
    else:
        print("크롤링 실패")

if __name__ == "__main__":
    main() 