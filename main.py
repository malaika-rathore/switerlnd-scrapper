from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import helper,miscelleneous_helpers
from selenium.webdriver.common.keys import Keys
from pprint import pprint
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
    


# Wait for an element

# staring web scraping work
def handle_web_scraping( driver,full_document):

    try:
        companies_data = []
        print("here")
        # send data in text field
        search_data(driver,full_document)
        print("afte serach")
        # get valid links and data
        valid_links = save_and_send_basic_data(driver,full_document)

        if len(valid_links):
            companies_data = fetch_detailed_data(driver,valid_links)

    except Exception as e:
        print(e)
        pass

    return companies_data

def fetch_detailed_data(driver,valid_links):
    for company_initial_data in valid_links:
        try:
            driver.get(company_initial_data['link'])
            single_company_data = fetch_single_company_data(driver)
            
            
            # company = self.crawl_company_data(driver)
            # companies_data.append(company)
            # self.save_company_data_in_raw_collection(company, company_initial_data)
            time.sleep(3)
        except Exception as e:
            pass

    return []

def fetch_single_company_data(driver):
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "cage")))
    
    all_boxes = driver.find_elements(By.CSS_SELECTOR,".cage .cage--item:has(div.cage--title)")
    print("total boxex",len(all_boxes))
    company = {}
    
    company_name  = driver.find_element(By.CLASS_NAME,"crossbar--title").text
    company['name'] = company_name
    for box_index,single_box in enumerate(all_boxes):
        title = single_box.find_element(By.CSS_SELECTOR,".cage--title-caption").text
        
        if box_index == 0:
            company_about_data(driver,company,single_box)
        if box_index == 1:
            company_structure_data(driver,company,single_box)
        if box_index == 2:
            company_contacts_data(driver,company,single_box)
        if box_index == 3:
            company_managements_data(driver,company,single_box)
        if box_index == 5:
            company_publications_data(driver,company,single_box)
        if box_index == 6:
            company_website_data(driver,company,single_box)


    # if company:
    #     company = helper.nest_dot_separated_dict(company)
    
    pprint(company)
    
def company_website_data(driver,company,single_box):
    website = miscelleneous_helpers.find_text(driver,By.CSS_SELECTOR,"#bk_company_website_technologies_area .thumb--link")

    company['meta_detail.website'] = website

def company_publications_data(driver,company,single_box):
    publications = []
    try:
        all_publications = driver.find_elements(By.CSS_SELECTOR,".publication .publication--item:has(p)")

        for index, publication in enumerate(all_publications):
            try:
                description = miscelleneous_helpers.find_text(publication,By.CLASS_NAME,"publication--paragraph")
                a_tag = publication.find_element(By.TAG_NAME,"a")
                url = a_tag.get_attribute("href")

                publication_date = miscelleneous_helpers.find_text(publication,By.CLASS_NAME,"publication--title-date")
                name_number = miscelleneous_helpers.find_text(publication,By.CLASS_NAME,"publication--title-wrapper")
                name_number = name_number.replace(publication_date,"")
                starting    = name_number.index("(")
                number      =  name_number[starting:]
                name        = name_number.replace(number,"")

                publications.append({
                    "name" : name,
                    "filling_number" : number,
                    "description" : description,
                    "url" : url,
                    "publication_date" : publication_date.replace("/","")
                })
            except Exception as e:
                pass

    except Exception as e:
        pass
    
    if len(publications):
        company['publications'] = publications

def company_managements_data(driver,company,single_box):
    try:
        all_peoples = driver.find_elements(By.CSS_SELECTOR,"#bk_company_overview_managment_area .connection--item:has(p)")

        for people in all_peoples:
            try:
                person = {}
                name = miscelleneous_helpers.find_text(people,By.CSS_SELECTOR,"h3.connection--link-title")
                address = miscelleneous_helpers.find_text(people,By.CLASS_NAME,"connection--small")
            
                designation = people.find_element(By.CLASS_NAME,"connection--col__last")
                person_designation = miscelleneous_helpers.find_text(designation,By.CLASS_NAME,"connection--strong")
                agreement_Consent = miscelleneous_helpers.find_text(designation,By.CSS_SELECTOR,"p:last-of-type")
                appointment_date = ""
                appointment_till = ""

                joining_detail_rows = people.find_elements(By.CSS_SELECTOR,".connection--col__first .connection--paragraph .connection--strong")
                
                for row in joining_detail_rows:
                    parent = driver.execute_script( "return arguments[0].parentNode;", row)
                    if "Von:" in row.text:
                        appointment_date = parent.text.split("Von:")[1]
                    if "Bis:" in row.text:
                        appointment_till = parent.text.split("Bis:")[1]

                person = {
                    "name" : name,
                    "address" : address,
                    "designation" : person_designation,
                    "agreement_Consent" : agreement_Consent,
                    "appointment_date" : appointment_date,
                    "appointment_till" : appointment_till,
                }

                miscelleneous_helpers.append_people_detail(company,person)
            except Exception as e:
                pass

    except Exception as e:
        pass

def company_contacts_data(driver,company,single_box):
    print("company contacts data")

    WebDriverWait(single_box, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, "cage--paragraph")))
    
    address = single_box.find_element(By.CLASS_NAME,"cage--paragraph").text

    miscelleneous_helpers.append_addresses(company,"office_address",address)

def company_structure_data(driver,company,single_box):
    print("company structure data")

    company_purpose = miscelleneous_helpers.find_text(single_box,By.ID,"company_purpose_de")
    if company_purpose:
        company['meta_detail.purpose'] = company_purpose
        
    # fetch company registration detail
    try:
        registration_detail_row = single_box.find_elements(By.CSS_SELECTOR,".cage--col .cage--row:nth-child(2) p")
        
        company['registration_date']    = registration_detail_row[0].text
        company['registration_number']  = registration_detail_row[1].text
    except Exception as e:
        # print(e)
        pass
    
    #fetch related companies data
    try:
        companies = []
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "related_companies")))
        
        related_companies = single_box.find_elements(By.CSS_SELECTOR,"#related_companies div:has(h4)")
        for single_company in related_companies:
            title           = single_company.find_element(By.TAG_NAME,"h4").text
            similar_report  = single_company.find_element(By.TAG_NAME,"p").text
            
            companies.append({"title":title, "report":similar_report})
            
        if len(companies):
            miscelleneous_helpers.append_additional_detail(company,"related_companies",companies)
            
    except Exception as e:
        print(e)
        
    #fetch the branches data of company
    try:
        WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "company_branches")))
        
        branches        = single_box.find_elements(By.CSS_SELECTOR,"#company_branches div:has(h4)")
        all_branches    = []
        
        for single_branch in branches:
            branch_name = single_branch.text
            
            all_branches.append(branch_name)        
        
        if len(all_branches):
            miscelleneous_helpers.append_additional_detail(company,"branches",all_branches)

    except Exception as e:
        print(e)

def company_about_data(driver,company,box):
    about_company = box.find_element(By.TAG_NAME,"p").text
    company['meta_detail.about_company'] =  about_company


def save_and_send_basic_data(driver,full_document):
    WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.ID, "company-info-results")))
    
    valid_links = []
    all_rows = driver.find_elements(By.CSS_SELECTOR,"#company-info-results .plank--row")
    try:
        for row_index, single_row in enumerate(all_rows):
            if row_index > 0:
                row_data    = single_row.find_element(By.CSS_SELECTOR,"a .plank--title .plank--title-box")
                name        = row_data.find_element(By.TAG_NAME,"h2").text
                
                if(helper.check_companies_validation(valid_links,full_document,{"name":name})):
                    
                    type_and_number     = row_data.find_element(By.CLASS_NAME,"plank--title-box-small").text
                    company_type        = type_and_number.split(" / ")[1]
                    registration_number = type_and_number.split(" / ")[0]
                    status              = row_data.find_element(By.CLASS_NAME,"status--title").text
                    link_url            = single_row.find_element(By.CSS_SELECTOR,"a").get_attribute("href")
                    
                    # company_detail = self.prepare_company_immediate_data_and_save(full_document, name, link_url, status,registration_number,type= company_type)
                    company_detail = {
                        "link": link_url,
                        "type" :company_type,
                        "status": status
                    }
                    valid_links.append(company_detail)
                else:
                    break
    except Exception as e:
        print("--->",e)
        pass
        
    return valid_links
        

def search_data(driver,full_document):
    WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.ID, "company_info_homepage_query")))

    # find text field
    search_field = driver.find_element(By.ID, "company_info_homepage_query")
    search_field.click()

    search_field.send_keys(full_document.get("search_text"))

    search_field.send_keys(Keys.RETURN)



# Set up the driver
options = Options()
options.add_argument("--disable-notifications")

driver_path = "C:/Users/hp/Downloads/chromedriver_win32.zip/chromedriver" # replace with the path to your driver executable
driver = webdriver.Chrome(options= options)

base_url = "https://business-monitor.ch/de?gclid=Cj0KCQiApKagBhC1ARIsAFc7Mc5MuN8A0KqiWmVl4lTQXkLqtIk7BTjVRJ9bXUtVIN0olPFsuUBZPPoaAjWREALw_wcB"

driver.get(base_url)


handle_web_scraping(driver,{"search_text": "bank"})