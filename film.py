from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time
import json
from os import makedirs
from os.path import exists

RESULTS_DIR = 'results11'
LAST_PAGE_FILE = 'last_page.txt'  # 用于保存最后爬取的页码

# 确保结果目录存在
if not exists(RESULTS_DIR):
    makedirs(RESULTS_DIR)

# 设置Chrome选项，禁用图片加载以减少页面加载时间
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 禁用图片加载

browser = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(browser, 10)
url_template = "http://www.ce.cn/xwzx/gnsz/szyw/index_{}.shtml"  # 修复了URL模板字符串

try:
    for page in range(1, 3):  # 假设我们最多爬取到第2页
        current_url = url_template.format(page)  # 电影页的URL
        browser.get(current_url)
        wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '.wrap .sec_left')))
        art_links = browser.find_elements(By.CSS_SELECTOR, '.wrap .con .f1 a')  # 获取全部电影链接

        for link in art_links:  # 每次处理前3个链接
            try:
                detail_url = link.get_attribute('href')
                new_window = browser.execute_script("window.open('');")  # 打开新标签页
                browser.switch_to.window(new_window)  # 切换到新标签页
                browser.get(detail_url)
                wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#neirong')))

                title_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#articleTitle')))
                timee_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#articleTime')))
                come_element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, '#articleSource')))
                contents_elements = wait.until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '#articleText .TRS_Editor p')))

                title = title_element.text.strip()
                timee = timee_element.text.strip()
                come = come_element.text.strip()
                contents = [c.text.strip().replace('\n', '') for c in contents_elements if c.text.strip()]

                time.sleep(1)  # 休息一秒，避免服务器压力过大
                browser.close()  # 关闭当前标签页
                browser.switch_to.window(browser.window_handles[0])  # 切换回原始窗口

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
            except TimeoutException:
                print("TimeoutException encountered. Skipping to the next movie.")
            except Exception as e:
                print(f"An error occurred: {e}")

finally:
    browser.quit()  # 确保最后关闭浏览器
