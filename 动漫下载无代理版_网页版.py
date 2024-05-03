import re
import time
from os import makedirs
from os.path import exists
import streamlit as st

import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains  # 行为链
from selenium.webdriver import EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import trange

donghua_name = st.text_input('请输入你要下载的动漫的名字:')
url = f'https://www.agedm.org/search?query={donghua_name}'
resp = requests.get(url)
details = re.findall(r'"http://www.agedm.org/detail/(.*?)".*?>第(.*?)集', resp.text, re.S)
st.write('搜索中，请耐心等待')
if details:
    print(details[0][0], details[0][1])

    all = int(round(float(details[0][1])))
    detail_1 = int(details[0][0])

start, end = st.text_input(f'一共{all}集,请问你要下载的范围为(请输入两个整数，用空格分隔):').split()
start = int(start)
end = int(end)

Save_path = f'动漫/{donghua_name}'
exists(Save_path) or makedirs(Save_path)


def get_data_with_retry(url, proxies=None, max_retries=5, num=None):
    retry = 0
    if retry < max_retries:
        try:
            response = requests.get(url, timeout=5)
            # 如果请求成功，直接返回数据
            return response.text
        except requests.exceptions.Timeout:
            print("请求超时，2秒后尝试重连...")
            time.sleep(2)
        except requests.exceptions.ConnectionError:
            print(f"请求发生错误: 连接异常")
            time.sleep(2)
            # 出现其他请求异常，尝试重连
        except requests.exceptions.RequestException as e:
            print(f"请求发生错误: {e}")
            time.sleep(2)
        retry += 1
    else:
        xia_zai(num)
        print(f'第{num}集重试')

    print("重试次数已用完，无法获取数据")
    return None


task = 0
task_all = end + 1 - start


def xia_zai(num):
    global task
    task += 1
    url_manhuamunlu = f'https://www.agedm.org/play/{detail_1}/1/{num}'  # 对应到某一集的网页
    # print(url_manhuamunlu)
    resp = get_data_with_retry(url_manhuamunlu, num=num)
    pattern = r'src="(https://[^"]+/vip/\?url=[^"]+)"'  # 正则匹配
    resp = str(resp)
    try:
        url = re.findall(pattern, resp)  # 得到的链接为云播放器的链接
    except re.error as e:
        print(f"正则表达式异常：{e}")

    # 无头模式
    option = EdgeOptions()
    option.add_argument('--headless')  # 无头模式
    browser = webdriver.Edge(options=option)
    browser.set_window_size(1366, 768)

    if len(url) == 1:  # 判断url是否为空集
        # print(url)
        browser.get(url[0])
    else:
        print(f"第{num}集没有找到对应的URL")
        xia_zai(num)
        return 0

    wait = WebDriverWait(browser, 10)
    try:
        input = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div/div/video')))
    except TimeoutException:
        print('Time Out')

    action_chains = ActionChains(browser)
    action_chains.context_click(input).perform()

    try:
        tongjixinxi = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="artplayer"]/div/div[11]/div[3]')))
    except TimeoutException:
        print('Time Out')

    action_chains.click(tongjixinxi).perform()

    try:
        tongjixinxi_1 = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="artplayer"]/div/div[10]/div[1]/div[2]/div[2]')))
        # print(tongjixinxi_1.text)
    except TimeoutException:
        print('Time Out')

    video_url = tongjixinxi_1.text
    browser.close()

    with open("video_urls.txt", 'a') as f:  # 将视频链接写入text文件中
        f.write(str(video_url))
        f.closed
    resp_video = requests.get(video_url)
    # print(video_url)
    with open(f'{Save_path}/第{num}集.mp4', 'wb') as f:
        f.write(resp_video.content)
        f.closed
        # print(f'{donghua_name}/第{num}集下载完成')


for i in trange(start, end + 1):
    xia_zai(i)

# 加载视频
video_path = f'{Save_path}/第{1}集.mp4'

# 在Streamlit中显示视频
st.video(video_path)

down_btn = st.download_button(
    label="Download Video",
    data=open(f'{Save_path}/第{1}集.mp4', "rb"),
    file_name=f"第{1}集",
    mime="video/mp4"
)
