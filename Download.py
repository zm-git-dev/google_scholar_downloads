import os.path
import re
import requests
from bs4 import BeautifulSoup


class Download:
    head = { \
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36' \
        }  # 20210607更新，防止HTTP403错误

    def pdf_hub(url, path):
        try:
            pdf = requests.get(url, headers=Download.head)
            with open(path, "wb") as f:
                f.write(pdf.content)
            print("\n" + "pdf found directly!")
        except:
            print("\n" + "failed to download pdf directly!\n" + url)
            Download.err_log(url)

    def sci_hub(path, doi):
        doi = str(doi).split("https://doi.org/")[1]
        url = "https://www.sci-hub.ren/doi:" + doi + "#"
        r = requests.get(url, headers=Download.head)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")
        download_url = soup.iframe.attrs["src"]
        try:
            download_r = requests.get(download_url, headers=Download.head)
            download_r.raise_for_status()
            with open(path, "wb+") as temp:
                temp.write(download_r.content)
                print("\n" + "Article downloaded by doi!")
        except:
            print("\n" + "failed to download pdf by doi!\n" + url)
            Download.err_log(url)

    def err_log(url):
        with open("download_err.txt", "a+", encoding="utf-8") as error:
            error.write("PDF not found,download link may be: \n" + url + "\n")

    def getSoup(url):
        r = requests.get(url, headers=Download.head)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, "html.parser")
        return soup

    def getPDF(url, path):
        if os.path.exists(path) == True:
            print("\n" + "Article already exists")
        else:
            if (len(re.findall('pdf', url)) != 0):
                print("\n" + 'pdf link already!')
                Download.pdf_hub(url, path)
            elif re.match("https://www.sci-hub.ren/", url):
                print("\n" + 'sci_hub link!')
                url = str(url).replace("https://www.sci-hub.ren/", "https://doi.org/")
                Download.sci_hub(path, url)
            # if pdf can be easily found!
            elif re.match("https://academic.oup.com/", url):
                soup = Download.getSoup(url)
                pdf_link = "https://academic.oup.com" + soup.find(class_="al-link pdf article-pdfLink").get('href')
                # print("\n"+pdf_link)
                Download.pdf_hub(pdf_link, path)
                '''
                doi = soup.select('div[class="ww-citation-primary"]')[0].a.get('href')
                #print("\n"+doi)
                Download.sci_hub(path,doi)
                '''
            elif re.match("https://content.iospress.com/", url):
                soup = Download.getSoup(url)
                pdf_link = soup.find(class_="btn btn-download btn-right get-pdf").get('href')
                # print("\n"+pdf_link)
                Download.pdf_hub(pdf_link, path)
            elif re.match("https://wwwnature.53yu.com/", url):
                soup = Download.getSoup(url)
                pdf_link = soup.find(class_="c-pdf-download__link").get('href')
                # print("\n"+pdf_link)
                Download.pdf_hub(pdf_link, path)
            elif re.match("https://bjo.bmj.com/", url):
                soup = Download.getSoup(url)
                pdf_link = soup.find(class_="article-pdf-download").get('href')
                pdf_link = "https://bjo.bmj.com" + pdf_link
                # print("\n"+pdf_link)
                Download.pdf_hub(pdf_link, path)
            elif re.match("https://jamanetwork.com/", url):
                soup = Download.getSoup(url)
                pdf_link = soup.find(class_="toolbar-tool toolbar-pdf al-link pdfaccess").get('data-article-url')
                pdf_link = "https://jamanetwork.com" + pdf_link
                # print("\n"+pdf_link)
                Download.pdf_hub(pdf_link, path)

            # if pdf can't be easily found,but doi can!
            elif re.match("https://sciencedirect.53yu.com/", url):
                soup = Download.getSoup(url)
                doi = soup.find(class_="doi").get('href')
                Download.sci_hub(path, doi)
            elif re.match("https://diabetes.diabetesjournals.org/", url):
                soup = Download.getSoup(url)
                doi = soup.select('.citation-doi')[0].a.get('href')
                Download.sci_hub(path, doi)
            elif re.match("https://journals.lww.com/", url):
                soup = Download.getSoup(url)
                doi = "https://doi.org/" + str(soup.find(id="ej-journal-doi").text).split("doi: ")[1]
                Download.sci_hub(path, doi)
            else:
                '''
                https://europepmc.org/
                https://iovs.arvojournals.org/
                https://linkspringer.53yu.com/
                '''
                print("\n" + "To be prettified!Download link may be: " + "\n" + url)
                Download.err_log(url)


if __name__ == '__main__':
    url = "http://www.cs.cmu.edu/~tom/pubs/Science-ML-2015.pdf"
    url1 = "https://www.sci-hub.ren/doi:10.1067/mva.2003.139#"
    url2 = "https://www.sci-hub.ren/doi:10.1067/mva.2003.139#"
    Download.getPDF(url, "test3.pdf")
    Download.getPDF(url1, "test4.pdf")
    Download.getPDF(url2, "test5.pdf")