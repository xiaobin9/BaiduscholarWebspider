from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

from utils import get_llm_model


# 配置 ChromeDriver
def init_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 无头模式
    chrome_options.add_argument('--no-sandbox')  # 必需的参数，避免沙箱错误
    chrome_options.add_argument('--disable-dev-shm-usage')  # 共享内存不足问题



    driver = webdriver.Chrome(options=chrome_options)

    return driver


driver = init_driver()


# 百度学术查询函数
def search_baidu_scholar(query):
    driver.get("https://xueshu.baidu.com/")
    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input#kw"))
    )
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    time.sleep(1)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    results = []
    for item in soup.find_all('div', class_='result')[:30]:
        title = item.find('h3', class_='t').text
        link = item.find('h3', class_='t').find('a')['href']
        results.append({'title': title, 'link': link})

    results2 = []
    for i, result in enumerate(results):
        driver.get(result['link'])

        # 等待页面加载
        time.sleep(0.3)  # 可以根据需要调整为WebDriverWait

        soup1 = BeautifulSoup(driver.page_source, 'html.parser')

        # title = soup1.find('div',class_='main-info').find('h3').text
        # print(title)
        title1=result['title']
        print(title1)
        author = soup1.find('p', class_='author_text').text
        print(author)

        try:
            abstract = soup1.find('p', class_='abstract').text
        except Exception:
            abstract ='未知'
        print(abstract)

        try:
            DOI = soup1.find('div', class_='doi_wr').text
        except Exception:
            DOI = '未知'
        print(DOI)

        try:
            year = soup1.find('div', class_='year_wr').text
        except Exception:
            year = '未知'
        print(year)

        # try:
        #     journal = soup1.find('div', class_='container_right').find('a', class_='journal_title').text
        # except Exception:
        #     journal='未知'
        # print(journal)

        results2.append({
            'title': title1,
            'author': author,
            'abstract': abstract,
            'DOI': DOI,
            'year': year,
            # 'journal': journal
        })

    return results2


# 定义LangChain的Prompt模板
template = """
1.你是一位学术研究专家。基于{results}，使用中文给出一个有逻辑、科学的总结。
2.当问题设计到使用什么方法、采取哪些措施、设计了哪些实验等时，需要给出一个更具体的回答。
3.并且按照标准引用格式，给出总结中所使用到的文献，包含文献名称，作者，期刊来源，DOI，年份:
4.务必使用使用中文进行回答

这里给出如下一个示例，你可以参考这个格式进行回答，参考文献的数量按照实际用到的数量，
示例：
根据以上文献的研究内容，可以总结如下：XXXXXXXXXXXXXXXX\n
参考文献：
1.张三，文献标题1，期刊名称1，年份1，DOI信息1
2.李四，文献标题2，期刊名称2，年份2，DOI信息2

"""

# 并且按照下面的格式给出引用，
# reference:
# 1.Author: 作者名称
# 2.Title：文献名称
# 3.DOI：
# 4.Year：发表年份
# 的格式给出回答


prompt = PromptTemplate(
    input_variables=["results"],
    template=template,
)


# 构建LangChain
def generate_summary_from_academic_results(query):
    # Step 1: 查询百度学术
    baidu_results = search_baidu_scholar(query)

    # Step 2: 构建LLMChain并生成总结
    chain = LLMChain(llm=get_llm_model(), prompt=prompt)
    summary = chain.run(results=baidu_results)

    return summary


# 测试查询
query = "请为我介绍几种玉米杂交方法？"
summary = generate_summary_from_academic_results(query)
print(summary)
