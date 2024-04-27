import pandas as pd
import requests
from bs4 import BeautifulSoup
import logging

class AmbitionBoxScraper:
    def __init__(self, num_pages):
        self.num_pages = num_pages
        self.df = pd.DataFrame(columns=['Company', 'Rating', 'Reviews', 'Salaries', 'Interviews', 'Jobs', 'Benefits', 'Type', 'Employees', 'Age', 'Ownership', 'Place', 'Rated Highly For', 'Rated Critical For'])

    def scrape(self):
        logging.basicConfig(filename='scraper_log.txt', level=logging.ERROR)  # Configure logging

        for page in range(1, self.num_pages + 1):
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'}
                page = requests.get(f'https://www.ambitionbox.com/list-of-companies?campaign=desktop_nav&page={page}', headers=headers)
                soup = BeautifulSoup(page.content, 'lxml')

                company_container = soup.find_all('div', class_='companyCardWrapper__metaInformation')
                numerical_data = soup.find_all('a', class_='companyCardWrapper__ActionWrapper')

                names = []
                rating = []
                reviews = []
                salaries = []
                interviews = []
                jobs = []
                benefits = []
                type_list = []
                employees_list = []
                age_list = []
                ownership_list = []
                place_list = []
                rated_highly_for = []
                rated_critical_for = []

                for company in company_container:
                    info = company.find('span', class_='companyCardWrapper__interLinking').get_text().strip()
                    parts = [part.strip() for part in info.split('|')]
                    company_type = parts[0]
                    employees = None  # Initialize as None
                    ownership = None
                    age = None
                    place = None

                    if len(parts) >= 2:  # Check if enough elements are available
                        employees = parts[1]

                    for part in parts:
                        if "years old" in part:
                            age = part.strip()
                            break

                    for part in parts:
                        if part in ['Public', 'Private']:
                            ownership = part
                            break

                    for part in parts:
                        if part.endswith("more"):
                            place = part
                            break

                    names.append(company.find('h2').get_text().strip())
                    rating.append(company.find('span', class_='companyCardWrapper__companyRatingValue').get_text().strip())
                    type_list.append(company_type)
                    employees_list.append(employees)
                    age_list.append(age)
                    ownership_list.append(ownership)
                    place_list.append(place)

                    comparision_wrapper = company.find('div', class_='companyCardWrapper__ratingComparisonWrapper')
                    if comparision_wrapper:
                        high_low = comparision_wrapper.find_all('span')
                        highly_rated = None
                        critically_rated = None

                        for index, span in enumerate(high_low):
                            if span.text.strip() == "Highly Rated For" and index + 1 < len(high_low):
                                highly_rated = high_low[index + 1].text.strip()
                            elif span.text.strip() == "Critically Rated For" and index + 1 < len(high_low):
                                critically_rated = high_low[index + 1].text.strip()

                        rated_highly_for.append(highly_rated)
                        rated_critical_for.append(critically_rated)
                    else:
                        rated_highly_for.append(None)
                        rated_critical_for.append(None)

                for data in numerical_data:
                    spans = data.find_all('span')
                    count = spans[0].get_text().strip()
                    title = spans[1].get_text().strip()

                    if title == 'Reviews':
                        reviews.append(count)
                    elif title == 'Salaries':
                        salaries.append(count)
                    elif title == 'Interviews':
                        interviews.append(count)
                    elif title == 'Jobs':
                        jobs.append(count)
                    elif title == 'Benefits':
                        benefits.append(count)

                page_df = pd.DataFrame({
                    'Company': names,
                    'Rating': rating,
                    'Reviews': reviews,
                    'Salaries': salaries,
                    'Interviews': interviews,
                    'Jobs': jobs,
                    'Benefits': benefits,
                    'Type': type_list,
                    'Employees': employees_list,
                    'Age': age_list,
                    'Ownership': ownership_list,
                    'Place': place_list,
                    'Rated Highly For': rated_highly_for,
                    'Rated Critical For': rated_critical_for
                })

                self.df = pd.concat([self.df, page_df], ignore_index=True)

            except Exception as e:
                logging.error(f"Error occurred while scraping page {page}: {str(e)}")
                continue

        return self.df

scraper = AmbitionBoxScraper(num_pages=50)
data = scraper.scrape()
print(data.tail())
