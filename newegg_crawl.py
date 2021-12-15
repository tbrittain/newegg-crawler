import os
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
from alive_progress import alive_bar, config_handler
from apscheduler.schedulers.background import BlockingScheduler
from win10toast import ToastNotifier
import newegg_crawl_config as config
from project_logging import logger


class NeweggCrawler:
    def __init__(self):
        self.product_hits = {}
        self.search_keywords = config.search_keywords
        self.price_threshold = config.price_threshold
        self.headless_mode = config.headless_mode
        self.output_filename = config.output_filename
        self.parse_interval = config.parse_interval
        self.sold_by_newegg = config.sold_by_newegg
        self.watched_items = config.watched_items

        assert NeweggCrawler.validate_url(
            config.search_url), "Invalid search url"
        assert NeweggCrawler.validate_url(
            config.discord_webhook_url), "Invalid discord webhook url"

        self.search_url = config.url
        self.discord_webhook_url = config.discord_webhook_url

        if self.sold_by_newegg:
            self.search_url += " 8000"
        self.search_url += f"&LeftPriceRange=0+{self.price_threshold}"

        if config.webdriver_type == "firefox":
            self.webdriver_path = os.path.join(
                os.path.dirname(__file__), "geckodriver.exe")
        elif config.webdriver_type == "chrome":
            self.webdriver_path = os.path.join(
                os.path.dirname(__file__), "chromedriver.exe")
        else:
            raise Exception("Invalid webdriver type")

    def _create_driver(self):
        if config.webdriver_type == "firefox":
            options = FirefoxOptions()
            if self.headless_mode:
                options.add_argument("--headless")
            return webdriver.Firefox(options=options, executable_path=self.webdriver_path)
        elif config.webdriver_type == "chrome":
            options = ChromeOptions()
            if self.headless_mode:
                options.add_argument("--headless")
            return webdriver.Chrome(options=options, executable_path=self.webdriver_path)

    def run(self):
        """
        Runs the crawler and notifies the user when items are in stock
        """
        config_handler.set_global(spinner='dots_recur')
        # log to console and recent_run.log
        # clear variables from previous search, if applicable
        self.product_hits = {}
        self._search()

        if len(self.product_hits) > 0:
            self.notify_toast()

        if self.discord_webhook_url:
            self._post_discord_webhook()

    def _search(self):
        """
        Search Newegg for products matching keywords in config file
        """
        # initiate selenium connection to webpage
        logger.info(f"\nRunning job on {datetime.now()}")
        logger.debug(f"Initializing connection to {self.search_url}")
        driver = self._create_driver()
        driver.maximize_window()
        driver.get(url=self.search_url)

        # going to iterate over many pages of results (potentially)
        attempts = 1
        while attempts <= 3:
            try:
                pagination = driver.find_element_by_class_name(
                    "list-tool-pagination-text")
                break
            except NoSuchElementException:
                logger.critical(f"Webpage unable to be loaded. Site may be performing captcha check. "
                                f"Attempt #{attempts}/3")
                time.sleep(5)
                attempts += 1
                driver.refresh()

        page_info = pagination.text
        page_info = page_info.replace("Page ", "")

        # define the highest page for the bot to iterate through
        slash_index = page_info.index("/")
        max_page = int(page_info[slash_index + 1:])
        current_page = 1

        # keep track of products that match hits from

        # define empty pandas dataframe to hold product information
        columns = ["Product", "Price", "InStock",
                   "URL", "Timestamp", "ItemNumber"]
        total_product_array = pd.DataFrame(columns=columns)

        # begin iteration through pages
        begin_time = time.perf_counter()
        with alive_bar(total=max_page, title='Parsing pages...', bar='bubbles') as bar:
            while current_page <= max_page:

                # print(f"Current page: {current_page}")
                item_cells = driver.find_elements_by_class_name(
                    "item-container")
                for item in item_cells:
                    title_info = item.find_element_by_class_name("item-title")

                    # get product name
                    product_name = title_info.text

                    # get product url
                    product_url = title_info.get_attribute("href")

                    # get product price
                    product_price = item.find_element_by_class_name(
                        "price-current")
                    product_price = product_price.text
                    product_price = product_price.replace("$", "")
                    product_price = product_price.replace(",", "")

                    logger.debug(
                        f"\nCurrent item: {product_name} for {product_price}")
                    logger.debug(product_url)

                    if product_price:
                        try:
                            product_price = float(product_price)
                        except ValueError:
                            try:
                                space_split = product_price.index(" ")
                                product_price = float(
                                    product_price[:space_split])
                            except ValueError:  # occasionally happens when no price found
                                product_price = None
                    else:
                        product_price = None

                    # get product id
                    try:
                        item_url_index = product_url.index("Item=")
                        item_no = product_url[item_url_index + 5:]
                        try:
                            ampersand_index = item_no.index("&")
                            item_no = item_no[:ampersand_index]
                        except ValueError:
                            pass
                    except ValueError:
                        combo_url_index = product_url.index("ItemList=")
                        item_no = product_url[combo_url_index + 9:]
                        item_no = item_no.replace(".", ": ")

                    # track whether in stock
                    in_stock = True
                    try:  # if this item-promo class is present, item is not in stock
                        promo = item.find_elements_by_xpath(
                            ".//p[@class='item-promo']")
                        if promo:
                            promo = promo[0].text
                            if promo == "OUT OF STOCK" or promo == "COMING SOON":
                                in_stock = False
                    except NoSuchElementException:
                        pass

                    keyword_match = False
                    for keyword in self.search_keywords:
                        # TODO: use better method than __contains__ because
                        # false positive hits occur, e.g. keyword 570 causes 5700 to be a hit
                        if product_name.__contains__(keyword):
                            keyword_match = True
                            logger.debug(f"Keyword hit for {keyword}")

                    # product of interest that is in stock
                    if keyword_match and in_stock and product_price is not None and \
                            product_price < self.price_threshold:
                        logger.info(f"{product_name} is in stock with price ${product_price} "
                                    f"({round(100 * (1 - (product_price / self.price_threshold)), 2)}% less "
                                    f"than the threshold of ${self.price_threshold})")

                        product_information = {
                            "name": product_name,
                            "url": product_url,
                            "price": product_price
                        }
                        self.product_hits[item_no] = product_information

                    # product of interest that is not in stock (for logging purposes)
                    if keyword_match and product_price is not None and product_price < self.price_threshold:
                        product_row = self.format_row(product_name=product_name, product_price=product_price,
                                                      in_stock=in_stock, product_url=product_url, item_number=item_no)
                        total_product_array = pd.concat(
                            [total_product_array, product_row], ignore_index=True)

                # re-establish page information
                pagination = driver.find_element_by_class_name(
                    "list-tool-pagination-text")
                page_info = pagination.text
                page_info = page_info.replace("Page ", "")
                slash_index = page_info.index("/")
                current_page = int(page_info[:slash_index])

                # determine whether to click 'next page' or not
                next_page_button = pagination.find_element_by_xpath(
                    "//button[@title='Next']")
                if next_page_button.get_property("disabled"):
                    break
                else:
                    driver.execute_script(
                        "arguments[0].click();", next_page_button)
                    time.sleep(self.parse_interval)
                bar()

            end_time = time.perf_counter()
            logger.info(
                f"Scrape completed in {round(end_time - begin_time, 2)} seconds")

            driver.close()

            pd.options.display.width = 0
            if len(total_product_array) > 0:
                self.write_products_to_csv(
                    product_dataframe=total_product_array, filename=self.output_filename)

    # FIXME: push to webhook instead of printing to console
    def _post_discord_webhook(self):
        assert isinstance(self.watched_items,
                          list), "Watched items must be a list of item IDs"
        logger.info("Checking if watched item(s) in stock")

        # TODO: get a product image too?
        # https://gist.github.com/dragonwocky/ea61c8d21db17913a43da92efe0de634
        # https://www.geeksforgeeks.org/json-dumps-in-python/

        for item in self.watched_items:
            if item in list(self.product_hits.keys()):
                print(f"{self.product_hits[item]['name']} is in stock for "
                      f"${self.product_hits[item]['price']}! {self.product_hits[item]['url']}")

    @staticmethod
    def notify_toast():
        notifier = ToastNotifier()
        notifier.show_toast("Newegg Scraper",
                            "Products of interest are in stock! Check log for details.",
                            duration=5,
                            icon_path=None,
                            threaded=True)

    @staticmethod
    def format_row(product_name, product_price, in_stock: bool, product_url, item_number):
        if in_stock:
            stock_status = "Yes"
        else:
            stock_status = "No"
        row = {
            "Product": product_name,
            "Price": product_price,
            "InStock": stock_status,
            "URL": product_url,
            "Timestamp": datetime.now(),
            "ItemNumber": item_number
        }
        return pd.DataFrame(row, index=[0])

    @staticmethod
    def write_products_to_csv(product_dataframe: pd.DataFrame, filename):
        try:
            # FIXME output to csv instead of excel
            product_dataframe.to_excel(filename + '.xlsx')
            logger.info(f"File {filename}.xlsx exported to {os.getcwd()}")
        except PermissionError:
            logger.warning(f'Coule not write to "{filename}.xlsx". It may currently be in use. Please close '
                           'any programs currently using it and try again.')

    @staticmethod
    def write_products_to_db():
        # TODO: use sqlite3 and write to a db in the working directory
        pass

    @staticmethod
    def validate_url(url: str):
        # Django url validation regex
        regex = re.compile(r'^(?:http|ftp)s?://'  # http:// or https://
                           r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
                           r'localhost|'  # localhost...
                           r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                           r'(?::\d+)?'  # optional port
                           r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, url) is not None


if __name__ == "__main__":
    newegg_scraper = NeweggCrawler()

    scheduler = BlockingScheduler()
    scheduler.add_job(func=newegg_scraper.run, trigger='interval',
                      seconds=config.search_interval * 60)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
