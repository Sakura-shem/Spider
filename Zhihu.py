from lxml import etree
import requests


headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
    'cookie': r''
}



if __name__ == "__main__":
    url = "https://www.zhihu.com/question/434567067/answer/2463561472"
    html = requests.request('get', url, headers = headers)
    text_html = html.text
    text_encode = text_html.encode('utf-8')
    html_xpath = etree.HTML(text_encode)
    title, author = html_xpath.xpath('//meta[@itemprop="name"]/@content')
    url = html_xpath.xpath('//meta[@itemprop="url"]/@content')[-1]
    print(author, url)
    text = html_xpath.xpath('//span[@itemprop="text"]//text()')
    with open('./1.md','w+',encoding='utf-8') as f:
        f.write("".join(text))