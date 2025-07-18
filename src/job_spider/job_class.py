import re

import html2text


class Job:
    def __init__(self):
        self.url = None
        self.title = None
        self.company = None
        self.location = None
        self.requests = None
        self.modality = None
        self.description = None

    def __str__(self):
        return f"URL: {self.url}\nTITLE: {self.title}\nCOMPANY: {self.company}\nLOCATION: {self.location}\nREQUESTS: {self.requests}\nMODALITY: {self.modality}\nDESCRIPTION: {self.description}"

    def data(self):
        return f"TITLE: {self.title}\nMODALITY: {self.modality}\nDESCRIPTION: {self.description}"

    def parse_linkedin(self, base_url, page):
        base_container = "div.jobs-search__job-details--container"
        # URL
        job_url = page.query_selector(f"{base_container} h1 a").get_attribute("href")
        self.url = f"{base_url}{job_url.split('?')[0]}"
        # TITLE
        self.title = page.query_selector(f"{base_container} h1").text_content().strip()
        # COMPANY
        self.company = page.query_selector(f"{base_container} div.job-details-jobs-unified-top-card__company-name").text_content().strip()
        # LOCATION & REQUESTS
        elements = page.query_selector_all(f"{base_container} div.job-details-jobs-unified-top-card__primary-description-container span span.tvm__text")
        self.location = elements[0].text_content().strip()

        raw_text = elements[4].text_content().strip()
        digits = re.sub(r"\D", "", raw_text)
        requests_number = int(digits)
        self.requests = "+100" if requests_number > 100 else str(requests_number)
        # MODALITY
        elements = page.query_selector_all(f"{base_container} li.job-details-jobs-unified-top-card__job-insight.job-details-jobs-unified-top-card__job-insight--highlight span span span span")
        self.modality = elements[0].text_content().strip()
        # DESCRIPTION
        description = page.query_selector(f"{base_container} article.jobs-description__container")
        self.description = html2text.html2text(description.inner_html())
