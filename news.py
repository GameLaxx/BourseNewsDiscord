from playwright.async_api import async_playwright
import requests
from PIL import Image
from io import BytesIO
import cairosvg


class News():
    def __init__(self, provider, title, url):
        self.provider = provider
        self.title = title
        self.url = url
    def __repr__(self):
        return f"{self.provider} : {self.title} (>{self.url})"

async def get_news(nav):
    url_nav = f"https://fr.tradingview.com/symbols/{nav}/news/"
    base_url = "https://fr.tradingview.com"
    news = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url_nav)
        await page.wait_for_selector(".container-BpSwpmE_.container-DmjQR0Aa")
        rows = await page.locator(".container-BpSwpmE_.container-DmjQR0Aa").all()
        for row in rows:
            parent_a = row.locator("xpath=ancestor::a")
            url = await parent_a.get_attribute("href")
            provider = await row.locator(".provider-BpSwpmE_").inner_text()
            title = await row.locator(".title-BpSwpmE_.title-DmjQR0Aa").inner_text()
            news.append(News(provider, title, base_url+url))
        await browser.close()
    return news

async def check_nav(nav):
    url_nav = f"https://fr.tradingview.com/symbols/{nav}/news/"
    try:
        ret = {}
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url_nav)
            await page.wait_for_selector(".logo-PsAlMQQF")
            img = await page.query_selector(".logo-PsAlMQQF")
            img_src = await img.get_attribute("src")
            response = requests.get(img_src)
            img_data = response.content if img_src[-3:] != "svg" else cairosvg.svg2png(bytestring=response.content)
            image = Image.open(BytesIO(img_data))
            average_color = image.resize((1, 1)).getpixel((0, 0))
            ret["color"] = average_color
            await page.wait_for_selector(".title-HDE_EEoW")
            full_name = await page.query_selector(".title-HDE_EEoW")
            ret["name"] = await full_name.inner_text()
            ret["ping"] = []
            await browser.close()
        return ret
    except:
        return None