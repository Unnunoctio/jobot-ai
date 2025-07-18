from playwright.sync_api import sync_playwright

from config import HOURS, KEYWORDS, LINKEDIN_PASSWORD, LINKEDIN_USER, LOCATION
from job_spider.job_class import Job


class LinkedIn:
    def __init__(self):
        self.base_url = "https://www.linkedin.com"

    def login(self, page):
        page.goto(f"{self.base_url}/login/es")
        page.wait_for_selector("input[name='session_key']")

        page.fill("input[name='session_key']", LINKEDIN_USER)
        page.fill("input[name='session_password']", LINKEDIN_PASSWORD)

        page.click("button[type='submit']")
        page.wait_for_load_state("load")

        #! Ver como sortear el captcha
        page.wait_for_timeout(15000)

    def get_jobs(self):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            self.login(page)

            jobs = []
            page.goto(f"{self.base_url}/jobs/search/?keywords={KEYWORDS}&geoId={LOCATION}&f_TPR=r{HOURS * 60 * 60}")

            while True:
                page.wait_for_load_state("load")
                page.wait_for_timeout(2000)

                elements = page.query_selector_all("li.ember-view.scaffold-layout__list-item")
                for i in range(len(elements)):
                    locator = page.locator("li.ember-view.scaffold-layout__list-item").nth(i)
                    locator.scroll_into_view_if_needed()
                    locator.locator("a").click()

                    page.wait_for_selector("article.jobs-description__container")
                    page.wait_for_timeout(2000)

                    new_job = Job()
                    new_job.parse_linkedin(base_url=self.base_url, page=page)

                    jobs.append(new_job)

                locator = page.locator("button.jobs-search-pagination__button--next")
                if locator.is_visible():
                    locator.click()
                else:
                    browser.close()
                    break

            return jobs
