import os.path
import threading
import time
import urllib.parse

import bs4
import requests


def generate_gallery_page_url(tags, page):
    """
    生成图片列表页url
    :param tags:标签列表
    :param page:页码
    :return:生成的url字符串
    """

    tags_param = "tags="
    for one_tage in tags:
        tags_param += urllib.parse.quote(one_tage)
        tags_param += "+"
    page_param = f"page={page}"
    return "https://yande.re/post" + f"?{page_param}&{tags_param}"


def perform_get_request(url):
    """
    从给定url下载网页html源代码
    :param url: 要下载的url
    :return:requests的response
    """

    # 代理设置
    proxies = {
        "http": "http://127.0.0.1:52338",
        "https": "http://127.0.0.1:52338",
    }
    # 请求头，UA设置
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/101.0.4951.54 Safari/537.36 Edg/101.0.1210.39"
    }
    return requests.get(url, headers=headers, proxies=proxies)


def extract_post_page_urls(gallery_page_html):
    """
    从图片列表页html中提取详情页的url
    :param gallery_page_html:列表页html
    :return:详情页url列表
    """
    soup = bs4.BeautifulSoup(gallery_page_html, "html.parser")
    post_elements = soup.select("a.thumb[href]")
    return list(map(lambda element: urllib.parse.urljoin("https://yande.re/", element.get("href")), post_elements))


def extract_changed_download_url(post_page_html):
    """
    从详情页提取被压缩过的（larger、jpeg版）图片下载链接
    :param post_page_html:详情页html
    :return:图片下载url
    """
    soup = bs4.BeautifulSoup(post_page_html, "html.parser")
    return soup.select_one("a.original-file-changed[href]").get("href")


def save_to_file(download_url):
    original_filename = urllib.parse.unquote(os.path.basename(download_url))
    with open(original_filename, "xb") as file:
        file.write(perform_get_request(download_url).content)
    print(f"Saved {original_filename}")


def main():
    # 输入tags和页码范围，目前用固定的代替
    tags = ["hakurei_reimu", "seifuku"]
    page = 1

    # 生成预览页面url
    gallery_page_url = generate_gallery_page_url(tags, page)

    # 加载预览页面并提取详情页url
    gallery_page_html = perform_get_request(gallery_page_url).text

    # 解析详情页url
    post_page_urls = extract_post_page_urls(gallery_page_html)
    print(len(post_page_urls))

    # 解析下载链接
    for a_post_page_url in post_page_urls:
        save_to_file(extract_changed_download_url(perform_get_request(a_post_page_url).text))


if __name__ == "__main__":
    main()
    print("exited")
