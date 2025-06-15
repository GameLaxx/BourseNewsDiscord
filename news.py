from playwright.async_api import async_playwright

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
        print("Went on page")
        await page.wait_for_selector(".container-BpSwpmE_.container-DmjQR0Aa")
        print("Selector appeared")
        rows = await page.locator(".container-BpSwpmE_.container-DmjQR0Aa").all()
        for row in rows:
            parent_a = row.locator("xpath=ancestor::a")
            url = await parent_a.get_attribute("href")
            provider = await row.locator(".provider-BpSwpmE_").inner_text()
            title = await row.locator(".title-BpSwpmE_.title-DmjQR0Aa").inner_text()
            news.append(News(provider, title, base_url+url))
    return news

async def check_nav(nav):
    url_nav = f"https://fr.tradingview.com/symbols/{nav}/news/"
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url_nav)
        return True
    except:
        return False