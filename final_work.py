from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException
import time
import json
from os import makedirs
from os.path import exists
RESULTS_DIR = 'article_results'
# 确保结果目录存在
exists(RESULTS_DIR) or makedirs(RESULTS_DIR)
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)
url_template = "http://www.ce.cn/xwzx/gnsz/szyw/index_{}.shtml"
try:
    for page in range(1, 26):  # 时政页的URL
        current_url = url_template.format(page)
        browser.get(current_url)
        wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.wrap')))
        art_links = browser.find_elements(By.CSS_SELECTOR, '.wrap .con .f1 a')  # 获取全部要闻链接
        l = len(art_links)
        for link in art_links:
            try:
                detail_url = link.get_attribute('href')
                browser.execute_script("window.open('');")
                browser.switch_to.window(browser.window_handles[-1])  # 切换到新标签页
                browser.get(detail_url)
                wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#article')))
                #标题，时间，来源，文章
                title_element = browser.find_element(By.CSS_SELECTOR, '#articleTitle')
                timee_element = browser.find_element(By.CSS_SELECTOR, '#articleTime')
                come_element = browser.find_element(By.CSS_SELECTOR, '#articleSource')
                contents_elements = browser.find_elements(By.CSS_SELECTOR, '.TRS_Editor p')
                title = title_element.text.strip()
                timee = timee_element.text.strip()
                come = come_element.text.strip()
                contents = [c.text.strip().replace('\n', '') for c in contents_elements if c.text.strip()]
                time.sleep(1)  # 休息一秒，避免服务器压力过大
                datas = {
                    "url": detail_url,
                    "title": title,
                    "date": timee,
                    "source": come[3:],
                    "article": contents
                }
                name = datas.get('title')  # 使用标题作为文件名
                data_path = f'{RESULTS_DIR}/{name}.json'
                with open(data_path, 'w', encoding="utf-8") as f:
                    json.dump(datas, f, ensure_ascii=False, indent=2)
            except StaleElementReferenceException:
                print("StaleElementReferenceException encountered. Skipping to the next movie.")
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                browser.close()  # 关闭当前标签页
                browser.switch_to.window(browser.window_handles[0])  # 切换回原始窗口
except Exception as e:
    print(f"An error occurred while processing pages: {e}")
finally:
    browser.quit()  # 退出浏览器

