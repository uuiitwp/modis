import requests_html


terra_tag = 'MOD13Q1.006/'
find_name = 'h26v05'
username = 'futureweather'
password = 'Future1234'
url = r'https://lpdaac.usgs.gov/tools/data-pool/'

proxies = {
    "http": "127.0.0.1:10800",
    "https": "127.0.0.1:10800",
}


def getHTML(s, url) -> requests_html.HTML:
    print(f"开始访问:{url}")
    response = s.get(url, proxies=proxies)
    return response.html


def isDate(s: str) -> bool:
    s_splited = s.split(".")
    try:
        if len(s_splited[0]) != 4 or len(s_splited[1]) != 2 or len(s_splited[2]) != 2:
            return False
        int(s_splited[0])
        int(s_splited[1])
        int(s_splited[2])
        return True
    except:
        return False
    return False


def isDes(s: str) -> bool:
    try:
        s_splited = s.split(".")
        if s_splited[2] == find_name and s_splited[-1].lower() == 'hdf':
            return True
    except:
        return False
    return False


def process():
    pass


def main():
    try:
        s = requests_html.HTMLSession()
        html = getHTML(s, url)
        a = html.find("a")
        # aqua = [x for x in a if x.text == "Aqua MODIS"][0].attrs["href"]
        terra = [x for x in a if x.text == "Terra MODIS"][0].attrs["href"]
        html = getHTML(s, terra)
        a = html.find("a")
        product = [x for x in a if x.text == terra_tag][0].attrs["href"]
        product_url = requests_html.urljoin(terra, product)
        html = getHTML(s, product_url)
        a = html.find("a")
        a = [x for x in a if isDate(x.attrs['href'].replace('/', ''))]
        maxa = max(a, key=lambda x: x.attrs['href'])
        latest_product_url = requests_html.urljoin(
            product_url, maxa.attrs['href'])
        html = getHTML(s, latest_product_url)
        a = html.find("a")
        des = [x for x in a if isDes(x.attrs['href'])]
        if len(des) == 0:
            raise Exception(f"未在'{latest_product_url}'地址中找到'{find_name}'数据")
        download_url = requests_html.urljoin(
            latest_product_url, des[0].attrs['href'])
        print("开始下载")
        response = s.get(download_url, proxies=proxies,
                         auth=(username, password), stream=True)
        if response.status_code == 401:
            print("未登录，进行登录")
            response = s.get(response.url, proxies=proxies,
                             auth=(username, password), stream=True)

        print("写入文件")
        with open(des[0].attrs['href'], 'wb') as f:
            for chunk in response.iter_content(chunk_size=4096):
                if chunk:
                    f.write(chunk)
    except:
        print("发生错误，重新开始")
        main()

    print("完成下载")
    print("开始处理")
    process()
    print("处理完成")


if __name__ == "__main__":
    main()
