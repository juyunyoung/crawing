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

class SakaniScraper:
    def __init__(self, headless: bool = True):
        self.driver = self._init_driver(headless)
        self.data = []
        self.base_url = "https://sakani.sa"
        self.target_url = f"{self.base_url}/app/marketplace?marketplace_purpose=buy&mode=maps&coordinates=[[46.71726065355138,25.074690133420606],[46.95175009446903,25.074690133420606],[46.95175009446903,24.865542584311747],[46.71726065355138,24.865542584311747],[46.71726065355138,25.074690133420606]]&zoom=11"

    def _init_driver(self, headless: bool) -> webdriver.Chrome:
        """Initialize Chrome WebDriver with appropriate options."""
        try:
            options = Options()
            # if headless:
            #     options.add_argument("--headless=new")
            # 자동화 감지 방지를 위한 옵션
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            # 보안 샌드박스 비활성화 (리눅스 환경에서 필요)
            #options.add_argument("--no-sandbox")
            
            # 공유 메모리 사용 비활성화 (리눅스 환경에서 필요)
            #options.add_argument("--disable-dev-shm-usage")
            
            # GPU 가속 비활성화 (일부 시스템에서 문제 해결)
            options.add_argument("--disable-gpu")
            
            # 브라우저 창 크기 설정 
            options.add_argument("--window-size=1920,1080")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 자동화 표시 제거
            options.add_experimental_option('useAutomationExtension', False)  # 자동화 확장 기능 사용 안 함
            #driver = webdriver.Chrome(options=options)
            driver = webdriver.Edge(options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return driver
            
        except Exception as e:
            print(f"Error initializing Chrome WebDriver: {str(e)}")
            print("System information:")
            print(f"Python version: {platform.python_version()}")
            print(f"Platform: {platform.platform()}")
            print(f"Architecture: {platform.architecture()}")
            raise

    def scroll_to_bottom(self, scroll_count: int = 5, delay: int = 2):
        """Scroll to the bottom of the page multiple times."""
        print(f"\nStarting to scroll {scroll_count} times...")
        scroll_script = "window.scrollTo(0, document.body.scrollHeight);"
        for i in range(scroll_count):
            self.driver.execute_script(scroll_script)
            print(f"Scroll {i+1}/{scroll_count} completed")
            time.sleep(delay)

    def parse_unit_details(self, unit_html: str) -> Dict:
        """Parse individual unit details from HTML."""
        soup = BeautifulSoup(unit_html, 'html.parser')
        data = {}
        
        try:
            price = soup.select_one('span.fw-normal.direction-neutral.sar-currency')
            data['Price'] = price.text.strip() if price else "N/A"
            print(f"Found price: {data['Price']}")
        except Exception as e:
            print(f"Error parsing price: {str(e)}")
            data['Price'] = "N/A"

        try:
            area_icon = soup.find('span', class_='svg-icon--small icon-house-solid-v5')
            data['Area'] = area_icon.find_next_sibling(text=True).strip() if area_icon else "N/A"
            print(f"Found area: {data['Area']}")
        except Exception as e:
            print(f"Error parsing area: {str(e)}")
            data['Area'] = "N/A"

        try:
            block_element = soup.find('div', class_='d-flex align-items-center gap-1 text-small mr-1')
            data['Block'] = block_element.get_text().replace('Block', '').replace('|', '').strip() if block_element else "N/A"
            print(f"Found block: {data['Block']}")
        except Exception as e:
            print(f"Error parsing block: {str(e)}")
            data['Block'] = "N/A"

        try:
            floor_div = soup.find('div', class_='d-flex align-items-center gap-1 text-small', string=lambda t: t and 'Floor' in t)
            data['Floor'] = floor_div.get_text().split('|')[0].replace('Floor', '').strip() if floor_div else "N/A"
            print(f"Found floor: {data['Floor']}")
        except Exception as e:
            print(f"Error parsing floor: {str(e)}")
            data['Floor'] = "N/A"

        return data

    def collect_project_data(self):
        """Collect data from all projects on the page."""
        try:
            print("\nWaiting for marketplace items list to load...")
            # First, wait for marketplace items list
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda driver: (print("Found element content:", driver.find_element(By.CSS_SELECTOR, 'div.marketplace-items-list').text), True)[1]
                )
                print("Found marketplace items list")
                
                # Then, wait for bottom modal within marketplace items list
                WebDriverWait(self.driver, 10).until(
                    #EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.marketplace-items-list div[class*="h-100"]'))
                    lambda driver: (print("Found element content2:", driver.find_element(By.CSS_SELECTOR,'div.marketplace-items-list div.h-100').text), True)[1]
                )
                print("Found h-100 elements")
                
                # Get all project items with bottom modal
                project_items = self.driver.find_elements(By.CSS_SELECTOR, 'div.marketplace-items-list div[class*="h-100"]')
                print(f"Found {len(project_items)} project items")
                
                for i, item in enumerate(project_items, 1):
                    try:
                        print(f"\nProcessing project {i}/{len(project_items)}")
                        
                        # Find and click the detail link within this project item
                        detail_link = item.find_element(By.CSS_SELECTOR, '.h-100 a')
                        self.driver.execute_script("arguments[0].click();", detail_link)
                        time.sleep(random.uniform(2, 4))
                        
                        print("Waiting for units section to load...")
                        # Wait for units section to load
                        WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.project-units'))
                        )
                        
                        # Parse units
                        units_section = self.driver.find_element(By.CSS_SELECTOR, 'div.project-units')
                        units = units_section.find_elements(By.CSS_SELECTOR, '.unit-card')
                        print(f"Found {len(units)} units in project {i}")
                        
                        for j, unit in enumerate(units, 1):
                            print(f"\nProcessing unit {j}/{len(units)} in project {i}")
                            unit_data = self.parse_unit_details(unit.get_attribute('outerHTML'))
                            self.data.append(unit_data)
                            print(f"Successfully added unit {j} data")
                        
                        # Go back to the main page
                        print("Going back to main page...")
                        self.driver.back()
                        time.sleep(random.uniform(1, 3))
                        
                    except (TimeoutException, WebDriverException, NoSuchElementException) as e:
                        print(f"Error processing project {i}: {str(e)}")
                        continue
                        
            except Exception as e:
                print("데이터를 찾을 수 없습니다. 디버깅을 시작합니다...")
                print("1. 현재 페이지 소스 확인:")
                print(self.driver.page_source[:10000])
                print("\n2. 실제 CSS 선택자 확인:")
                elements = self.driver.find_elements(By.CSS_SELECTOR, '*')
                print("페이지의 모든 요소:")
                for elem in elements[:10]:  # 처음 10개 요소만 출력
                    print(f"태그: {elem.tag_name}, 클래스: {elem.get_attribute('class')}")
                print("\n3. 페이지 로딩 상태:")
                print(f"페이지 준비 상태: {self.driver.execute_script('return document.readyState')}")
                raise
                    
        except Exception as e:
            print(f"Error collecting project data: {str(e)}")

    def save_to_csv(self, filename: str = 'sakani_projects.csv'):
        """Save collected data to CSV file."""
        if self.data:
            print(f"\nSaving {len(self.data)} records to {filename}")
            df = pd.DataFrame(self.data)
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"Data successfully saved to {filename}")
        else:
            print("No data to save")

    def run(self):
        """Main execution flow."""
        try:
            print("Starting Sakani scraper...")
            print(f"Navigating to: {self.target_url}")
            self.driver.get(self.target_url)
            time.sleep(15)  # Initial page load wait
            
            print("\nScrolling to load all projects...")
            self.scroll_to_bottom()
            
            print("\nCollecting project data...")
            self.collect_project_data()
            
            print("\nSaving data to CSV...")
            self.save_to_csv()
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            self.driver.quit()
            print("\nScraping completed.")

if __name__ == "__main__":
    scraper = SakaniScraper(headless=True)
    scraper.run() 