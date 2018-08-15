######################################################################################
######################################################################################
##
## Latham & Watkins directory WebsScraping
## Filename: latham & watkins scrape.py
## Date: July 22, 2018
## Programmer: Chinanu Onyekachi
##
## Description:
##          This program uses selenium and BeautifulSoup to
##          navigate through the Latham & Watkins directory website
##          and scrape the pages for lawyers' information.
##
######################################################################################
######################################################################################
"""
FireFox -
    browser 53.0.3  (64-bit)
    driver geckodriver-v0.16.1 (64bit)

Chrome -
    browser Version 67.0.3396.99 (Official Build) (64-bit)
    driver chromedriver 2.40 (32bit)
"""

########################################################################################################################
########################################################################################################################

import os
import sys
import requests
import string
import pprint
import datetime
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.select import Select
#######################################################################################################################
#######################################################################################################################

def main():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get("https://www.lw.com/GlobalDirectory")
    print(driver.title)

    lawyers = getLawyers(driver)
    print()
    print('Latham & Watkins has '+ str(len(lawyers)) + ' lawyers under their books.')
    print()

    lawyers_dict = get_lawyers_info(driver, lawyers)
    #print(lawyers_dict)
    #pprint.pprint(lawyers_dict)

    convert_to_json(lawyers_dict)

    create_sql(lawyers_dict)

    print('Check for JSON and SQL files in folder.')

    user_choice = input('Please click ENTER button to close application')
    if not user_choice:
        print("ABORTED")
        quit()
#######################################################################################################################


#######################################################################################################################
def getLawyers(driver):
    wait = WebDriverWait(driver, 5)
    #alphabets = list(string.ascii_uppercase)
    alphabets = ['Q']
    lawyers = []
    for letter in alphabets:
        #print(letter)
        try:
            elem = wait.until(EC.element_to_be_clickable(
                (By.LINK_TEXT, letter)))
            elem.click()


            list_view = wait.until(EC.presence_of_element_located(
                (By.ID, "ContentPlaceHolder1_MainContentPlaceHolder_ListTab")))
            list_view.click()


            table_view = wait.until(EC.presence_of_element_located((By.ID, 'PeopleList')))
            try:
                view_all = driver.find_element_by_xpath("//div/span/a[contains(text(),'All')]")
                view_all.click()
            except NoSuchElementException:
                pass

            select_lawyer = []
            soup = BeautifulSoup(driver.page_source, "html.parser")

            table = soup.findChild('table', {'id': 'PeopleList'})
            if table is not None:
                rows = table.findChildren('tr')
                for row in rows:
                    links = row.findChildren('a')
                    for link in links:
                        if link:
                            select_lawyer.append(link['href'])

            for i in select_lawyer:
                if 'people' in i:
                    lawyers.append(i)

            #print(lawyers)

        except TimeoutException as err:
            print("Click Failed")
            print(str(err))
            return

    driver.get_screenshot_as_file("capture.png")
    return lawyers
#######################################################################################################################


#######################################################################################################################
def get_lawyers_info(driver, lawyers):
    domain = 'https://www.lw.com'
    wait = WebDriverWait(driver, 5)
    lawyers_dict = []


    for lawyer in lawyers:
        lawyer = domain + lawyer
        driver.get(lawyer)

        try:
            elem = wait.until(EC.presence_of_element_located(
                (By.ID,"RightColumnMainContent")))

            soup = BeautifulSoup(driver.page_source, "html.parser")
            content = soup.findChild('div', {'id': 'RightColumnMainContent'})

            if content is not None:
                name = (content.find('h1', {'id': 'ContentPlaceHolder1_HeadingPlaceHolder_NameLabel'})
                        ).get_text(strip=True)

                title = (content.find('span', {'id': 'ContentPlaceHolder1_HeadingPlaceHolder_TitleLabel'})
                         ).get_text(strip=True)

                location = (content.find('span', {'id': 'ContentPlaceHolder1_HeadingPlaceHolder_OfficesLabel'})
                            ).get_text(strip=True)

                company = 'Latham & Watkins'



                phone = None
                try:
                    phone = (content.find('span', {'id': 'PhoneNumberLabel'})).get_text(strip=True)
                except AttributeError:
                    pass


                email = None
                try:
                    email = (content.find('a', {'id': 'ContentPlaceHolder1_HeadingPlaceHolder_EmailLink'})
                             ).get_text(strip=True)

                except AttributeError:
                    pass


                linkedIn = None
                cv = None



                edu = []
                lawyer_meta = soup.findChild('ul', {'id': 'AttorneyMetaData'})
                edu_ul = lawyer_meta.select('div')[1].find_next_siblings('ul')[0]
                edu_li = edu_ul.findChildren('li')

                for uni in edu_li:
                    edu.append(uni.contents[0])
                edu = "; ".join(edu)



                bio = None
                try:
                    bio_area = soup.findChild('div', {'id': 'ExpertiseContentArea'})
                    bio_p = bio_area.findChildren(['p', 'li'])
                    bio = ''

                    for i in bio_p:
                        bio = bio + ' ' + i.get_text(" ", strip=True)
                    bio = bio.replace("  ", " ")
                    bio = (bio.encode('ascii','ignore')).decode("utf-8")

                except AttributeError:
                    pass



                xp = None
                try:
                    find_xp = driver.find_element_by_link_text("ExperienceContentArea")
                    xp_area = soup.findChild('div', {'id': 'ExperienceContentArea'})
                    xp_p = xp_area.findChildren(['p', 'li', 'br'])
                    xp = ''

                    for i in xp_p:
                        xp = xp + ' ' + i.get_text(" ", strip=True)
                    xp = xp.replace("  ", " ")
                    xp = (xp.encode('ascii', 'ignore')).decode("utf-8")

                except NoSuchElementException:
                    pass



                xpts = None
                try:
                    pracs_ul = lawyer_meta.select('div')[2].find_next_siblings('ul')[0]
                    pracs_li = pracs_ul.findChildren('li')
                    xpts = []

                    for prac in pracs_li:
                        xpts.append((prac.contents[0].get_text(" ", strip=True
                                                               ).encode('ascii', 'ignore')).decode("utf-8"))

                    try:
                        inds_ul = lawyer_meta.select('div')[3].find_next_siblings('ul')[0]
                        inds_li = inds_ul.findChildren('li')

                        for ind in inds_li:
                            xpts.append((ind.contents[0].get_text(" ", strip=True
                                                                  ).encode('ascii', 'ignore')).decode("utf-8"))

                    except IndexError:
                        pass

                    xpts = "; ".join(xpts)

                except IndexError:
                    pass




                barQ = []
                try:
                    bar_ul = lawyer_meta.select('div')[0].find_next_siblings('ul')[0]
                    bar_li = bar_ul.findChildren('li')

                    for bar in bar_li:
                        barQ.append(bar.contents[0].get_text(" ", strip=True))

                except IndexError:
                    pass

                barQ = "; ".join(barQ)



                mAffl = None



                newsEvents = None
                try:
                    find_events = driver.find_element_by_link_text("Events")
                    events_area = soup.findChild('li', {'id': 'ContentPlaceHolder1_RightColumnNavigationPlaceHolder_'
                                                'AdditionalInfoControl1_EventsSection_AdditionalInfoSectionWrapper'})

                    events_li = events_area.findChild('ul').findChildren('li')
                    Events = []

                    for event in events_li:
                        if event.get_text(" ", strip=True) != 'more':
                            Events.append(event.get_text(" ", strip=True))

                    newsEvents = Events

                except NoSuchElementException:
                    pass
                except AttributeError:
                    pass

                try:
                    find_news = driver.find_element_by_link_text("News")
                    news_area = soup.findChild('li', {'id': 'ContentPlaceHolder1_RightColumnNavigationPlaceHolder_'
                                                'AdditionalInfoControl1_NewsSection_AdditionalInfoSectionWrapper'})

                    news_li = news_area.findChild('ul').findChildren('li')
                    News = []

                    for news in news_li:
                        if news.get_text(" ", strip=True) != 'more':
                            News.append(news.get_text(" ", strip=True))

                    if newsEvents:
                        newsEvents = newsEvents + News
                    else:
                        newsEvents = News

                    newsEvents = "; ".join(newsEvents)

                except NoSuchElementException:
                    pass
                except AttributeError:
                    pass



                publications = None
                try:
                    find_publications = driver.find_element_by_link_text("Thought Leadership")
                    publications_area = soup.findChild('li', {'id': 'ContentPlaceHolder1_'
                        'RightColumnNavigationPlaceHolder_AdditionalInfoControl1_ThoughtLeadershipSection_'
                        'AdditionalInfoSectionWrapper'})

                    publications_li = publications_area.findChild('ul').findChildren('li')
                    publications = []

                    for publication in publications_li:
                        if publication.get_text(" ", strip=True) != 'more':
                            publications.append(publication.get_text(" ", strip=True))

                    publications = "; ".join(publications)

                except NoSuchElementException:
                    pass
                except AttributeError:
                    pass



                clients = None



                awards_rankings = None
                try:
                    find_AR = driver.find_element_by_link_text("Awards & Rankings")
                    ARs_area = soup.findChild('li', {'id': 'ContentPlaceHolder1_RightColumnNavigationPlaceHolder_'
                                        'AdditionalInfoControl1_AwardsRankingsSection_AdditionalInfoSectionWrapper'})

                    ARs_li = ARs_area.findChild('ul').findChildren('li')
                    awards_rankings = []

                    for AR in ARs_li:
                        if AR.get_text(" ", strip=True) != 'more':
                            awards_rankings.append(AR.get_text(" ", strip=True))

                    awards_rankings = "; ".join(awards_rankings)

                except NoSuchElementException:
                    pass
                except AttributeError:
                    pass



                priorAssc = None



                lawyer_pic = None
                try:
                    find_pic = driver.find_element_by_class_name("bioPhoto")
                    bio_pic = soup.find('img', {'class': 'bioPhoto'})

                    lawyer_pic = domain + bio_pic['src']

                except NoSuchElementException:
                    pass
                except AttributeError:
                    pass



                now = datetime.datetime.today()
                now = now.strftime("%Y-%b-%d")


                lawyers_dict.append({
                    'Name': name,
                    'Title': title,
                    'Location': location,
                    'Company': company,
                    'Phone': phone,
                    'Email': email,
                    'LinkedIn': linkedIn,
                    'CV': cv,
                    'Education': edu,
                    'Biography': bio,
                    'Experience': xp,
                    'Expertise': xpts,
                    'AdmissionsQualifications': barQ,
                    'MembershipsAffiliations': mAffl,
                    'NewsEvents': newsEvents,
                    'Publications': publications,
                    'Clients': clients,
                    'Distinctions': awards_rankings,
                    'PriorAssociations': priorAssc,
                    'Image': lawyer_pic,
                    'WebpageURL': lawyer,
                    'Timestamp': now,
                    })


        except TimeoutException as err:
            print(str(err))
            return

    return lawyers_dict
#######################################################################################################################


#######################################################################################################################
def convert_to_json(lawyers_dict):
    with open('LW_Lawyers.json', 'w') as outfile:
        json.dump(lawyers_dict, outfile, indent= 4)
#######################################################################################################################


#######################################################################################################################
def create_sql(lawyers_dict):
    table_name = 'L_W_Directory'

    columns = []
    for row in lawyers_dict:
        for key in row.keys():
            if key not in columns:
                columns.append(key)
    ##print(columns)
    create_table = ("""CREATE TABLE {} (
  {}
);

""".format(table_name, (",\n  ".join(map(lambda x: "{} VARCHAR(2000)".format(x), columns))))
        )

    ins_statements = ''
    for row in lawyers_dict:
        ins_statements += ("""\nINSERT INTO {} VALUES({});""".format(table_name,
            (",".join(map(lambda key: "'{}'".format(row[key].replace("'","''")) if row[key] is not None else "NULL", columns))))
              )

    with open('LW_Lawyers.sql', 'w') as sql_file:
        sql_file.write(create_table)
        sql_file.write(ins_statements)
#######################################################################################################################


#######################################################################################################################
main()