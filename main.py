import os.path
import urllib.parse
from abc import abstractmethod

import bs4
import requests


class UserPromptArgument:
    """
    用于用户交互输入标签与页码范围
    """

    # 标签
    tags = []
    # 页码范围
    start_page, end_page = -1, -1

    def __init__(self):
        while True:
            if self.__input_tags():
                break
        while True:
            if self.__input_page_range():
                break

    def __input_tags(self):
        """
        用户交互标签输入
        :return: 是否输入成功，标签可在tags属性获取
        """
        input_tags_list = input("输入空格间隔的tags(如: miko bare_shoulders): ").split(" ")
        if len(input_tags_list) < 1 or len(input_tags_list[0]) < 1:
            print("至少应有一个tag。")
            return False
        else:
            self.tags = input_tags_list
            print(f"Tag数量: {len(input_tags_list)}, Tag列表: {input_tags_list}")
            return True

    def __input_page_range(self):
        """
        用户交互页码输入
        :return: 是否输入成功，页码可在start_page, end_page属性获取
        """
        range_input = list(map(int, input("输入空格间隔的开始和结束页(包括): ").split(" ")))
        if len(range_input) < 1:
            print("不正确的输入。")
            return False
        elif range_input[0] < 1 or range_input[1] < 1:
            print("页码应从1开始。")
            return False
        elif range_input[0] > range_input[1]:
            print("开始页不应大于结束页")
            return False
        else:
            print(f"从页 {range_input[0]} 到页 {range_input[1]}，总共 {range_input[1] - range_input[0] + 1} 页")
            self.start_page, self.end_page = range_input[0], range_input[1]
            return True


class BaseProcess:
    """
    抽象的流程，包含生成链接、分析列表和预览页和提取下载链接等操作
    """

    # UserPromptArgument，包含标签和页码
    user_prompt_argument: UserPromptArgument

    def __init__(self, user_prompt_argument: UserPromptArgument):
        self.user_prompt_argument = user_prompt_argument

    @abstractmethod
    def generate_gallery_page_url(self, page_number):
        """
        生成图片列表页url
        :param page_number:页码
        :return: 生成的url字符串
        """

    @abstractmethod
    def extract_post_page_urls(self, gallery_page_html):
        """
        从列表页提取每张图片的预览（详情页）url
        :param gallery_page_html:预览页html源代码
        :return: 详情页url列表
        """

    @abstractmethod
    def extract_changed_download_url(self, post_page_html):
        """
        从详情页提取被压缩过的（larger、jpeg版）图片下载链接
        :param post_page_html:详情页html
        :return:图片下载url
        """


class YandereProcess(BaseProcess):

    def generate_gallery_page_url(self, page_number):
        tags_param = "tags="
        for one_tage in self.user_prompt_argument.tags:
            tags_param += urllib.parse.quote(one_tage)
            tags_param += "+"
        page_param = f"page={page_number}"
        return "https://yande.re/post" + f"?{page_param}&{tags_param}"

    def extract_post_page_urls(self, gallery_page_html):
        soup = bs4.BeautifulSoup(gallery_page_html, "html.parser")
        post_elements = soup.select("a.thumb[href]")
        return list(map(lambda element: urllib.parse.urljoin("https://yande.re/", element.get("href")), post_elements))

    def extract_changed_download_url(self, post_page_html):
        soup = bs4.BeautifulSoup(post_page_html, "html.parser")
        return soup.select_one("a.original-file-changed[href]").get("href")


class HttpUtil:
    """
    一些HTTP相关的工具
    """

    @staticmethod
    def request_get(url):
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

    @staticmethod
    def save_to_file(download_url):
        original_filename = urllib.parse.unquote(os.path.basename(download_url))
        with open(original_filename, "xb") as file:
            file.write(HttpUtil.request_get(download_url).content)
        print(f"Saved {original_filename}")


def main():
    # 输入tags和页码范围，目前用固定的代替
    user_prompt_argument = UserPromptArgument()

    process_procedure = YandereProcess(user_prompt_argument)

    for page_number in range(user_prompt_argument.start_page, user_prompt_argument.end_page + 1):
        # 生成预览页面url
        gallery_page_url = process_procedure.generate_gallery_page_url(page_number)
        # 加载预览页面并提取详情页url
        post_page_urls = process_procedure.extract_post_page_urls(HttpUtil.request_get(gallery_page_url).text)
        # 解析下载链接并下载
        for a_post_page_url in post_page_urls:
            post_page_html = HttpUtil.request_get(a_post_page_url).text
            HttpUtil.save_to_file(process_procedure.extract_changed_download_url(post_page_html))


if __name__ == "__main__":
    print("WaifuDownloaderPy 0.0.1")
    main()
    print("程序已退出")
