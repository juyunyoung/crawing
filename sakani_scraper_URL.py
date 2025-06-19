import time
import random
from typing import List, Dict
import pandas as pd
from bs4 import BeautifulSoup
import requests
import json
import os
import platform

class SakaniScraper:
    def __init__(self):
        self.data = []
        self.base_url = "https://sakani.sa/app/marketplace?marketplace_purpose=buy&mode=maps&coordinates=%5B%5B46.71726065355138,25.074690133420606%5D,%5B46.95175009446903,25.074690133420606%5D,%5B46.95175009446903,24.865542584311747%5D,%5B46.71726065355138,24.865542584311747%5D,%5B46.71726065355138,25.074690133420606%5D%5D&zoom=11"
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
            'Content-Type': 'application/json',
            'Origin': 'https://sakani.sa',
            'Referer': 'https://sakani.sa/app/marketplace'
        }

    def get_marketplace_data(self):
        """Get marketplace data from API."""
        try:
            print("\nFetching marketplace data...")
            
            # API 요청 데이터
            payload = {
                "marketplace_purpose": "buy",
                "mode": "maps",
                "coordinates": [[46.71726065355138,25.074690133420606],
                              [46.95175009446903,25.074690133420606],
                              [46.95175009446903,24.865542584311747],
                              [46.71726065355138,24.865542584311747],
                              [46.71726065355138,25.074690133420606]],
                "zoom": 11,
                "page": 1,
                "per_page": 100
            }

            # API 요청
            #response = requests.get(self.api_url, headers=self.headers, params=payload)
            response = requests.post(self.base_url)
            response.raise_for_status()  # HTTP 에러 체크
            
            # JSON 응답 파싱
            data = response.json()
            print(f"Successfully fetched {len(data.get('data', []))} projects")
            
            return data.get('data', [])
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching marketplace data: {str(e)}")
            return []

    def get_project_details(self, project_id: str) -> List[Dict]:
        """Get project details from API."""
        try:
            print(f"\nFetching details for project {project_id}...")
            
            # 프로젝트 상세 API URL
            detail_url = f"{self.base_url}/api/marketplace/projects/{project_id}"
            
            # API 요청
            response = requests.get(detail_url, headers=self.headers)
            response.raise_for_status()
            
            # JSON 응답 파싱
            data = response.json()
            units = data.get('data', {}).get('units', [])
            print(f"Found {len(units)} units in project {project_id}")
            
            return units
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching project details: {str(e)}")
            return []

    def parse_unit_details(self, unit: Dict) -> Dict:
        """Parse unit details from API response."""
        try:
            data = {
                'Price': unit.get('price', 'N/A'),
                'Area': unit.get('area', 'N/A'),
                'Block': unit.get('block', 'N/A'),
                'Floor': unit.get('floor', 'N/A'),
                'Bedrooms': unit.get('bedrooms', 'N/A'),
                'Bathrooms': unit.get('bathrooms', 'N/A')
            }
            print(f"Successfully parsed unit details: {data}")
            return data
        except Exception as e:
            print(f"Error parsing unit details: {str(e)}")
            return {
                'Price': 'N/A',
                'Area': 'N/A',
                'Block': 'N/A',
                'Floor': 'N/A',
                'Bedrooms': 'N/A',
                'Bathrooms': 'N/A'
            }

    def collect_project_data(self):
        """Collect data from all projects."""
        try:
            # Get marketplace data
            projects = self.get_marketplace_data()
            
            for i, project in enumerate(projects, 1):
                try:
                    print(f"\nProcessing project {i}/{len(projects)}")
                    project_id = project.get('id')
                    
                    if not project_id:
                        print(f"No project ID found for project {i}")
                        continue
                    
                    # Get project details
                    units = self.get_project_details(project_id)
                    
                    # Parse unit details
                    for unit in units:
                        unit_data = self.parse_unit_details(unit)
                        self.data.append(unit_data)
                    
                    # Add delay between requests
                    time.sleep(random.uniform(1, 2))
                    
                except Exception as e:
                    print(f"Error processing project {i}: {str(e)}")
                    continue
                    
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
            
            print("\nCollecting project data...")
            self.collect_project_data()
            
            print("\nSaving data to CSV...")
            self.save_to_csv()
            
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            print("\nScraping completed.")

if __name__ == "__main__":
    scraper = SakaniScraper()
    scraper.run() 