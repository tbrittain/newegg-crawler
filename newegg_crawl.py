import newegg_crawl_config as config
from win10toast import ToastNotifier
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
import openpyxl
import schedule
import os
import time
from datetime import datetime
import pandas as pd
import cryptography


# This currently is only for Firefox-based Selenium


class NeweggCrawler:
    def __init__(self):
        self.product_hits = {}
        self.products_hit_count = 0
        self.search_url = config.url
        self.search_keywords = config.search_keywords
        self.price_threshold = config.price_threshold
        self.webdriver_path = config.webdriver_path
        self.headless_mode = config.headless_mode
        self.output_filename = config.output_filename
        self.parse_interval = config.parse_interval
        self.sold_by_newegg = config.sold_by_newegg
        self.buy_product = config.buy_product

        # may want to put this code under search method
        if self.headless_mode:
            options = Options()
            options.headless = self.headless_mode
            self.driver = webdriver.Firefox(executable_path=self.webdriver_path, options=options)
        else:
            self.driver = webdriver.Firefox(executable_path=self.webdriver_path)

        # apply some things to the url
        if self.sold_by_newegg:
            self.search_url += " 8000"
        self.search_url += f"&LeftPriceRange=0+{self.price_threshold}"

    def run(self):
        """
        Function to coordinate the running of the bot. Use this method directly rather than the others.
        """
        # clear variables from previous search, if applicable
        self.product_hits = {}
        self.products_hit_count = 0
        self.search()

        if self.products_hit_count > 0:
            self.notify()

        if self.buy_product:
            pass

    def search(self):
        """
        Search Newegg for products matching keywords in config file
        """
        # initiate selenium connection to webpage
        self.driver.maximize_window()
        self.driver.get(url=self.search_url)

        # going to iterate over many pages of results (potentially)
        pagination = self.driver.find_element_by_class_name("list-tool-pagination-text")
        page_info = pagination.text
        page_info = page_info.replace("Page ", "")

        # define the highest page for the bot to iterate through
        slash_index = page_info.index("/")
        max_page = int(page_info[slash_index + 1:])
        current_page = 1

        # keep track of products that match hits from

        # define empty pandas dataframe to hold product information
        columns = ["Product", "Price", "InStock", "URL", "Timestamp", "ItemNumber"]
        total_product_array = pd.DataFrame(columns=columns)

        print(f"Running job at {datetime.now()}")

        # begin iteration through pages
        begin_time = time.perf_counter()
        while current_page <= max_page:

            print(f"Current page: {current_page}")
            item_cells = self.driver.find_elements_by_class_name("item-container")
            for item in item_cells:
                title_info = item.find_element_by_class_name("item-title")

                # get product name
                product_name = title_info.text

                # get product url
                product_url = title_info.get_attribute("href")

                # get product price
                product_price = item.find_element_by_class_name("price-current")
                product_price = product_price.text
                product_price = product_price.replace("$", "")
                product_price = product_price.replace(",", "")

                print(f"\nCurrent item: {product_name} for {product_price}")
                print(product_url)
                if product_price:
                    try:
                        # print(product_price)
                        product_price = float(product_price)
                    except ValueError:
                        try:
                            space_split = product_price.index(" ")
                            product_price = float(product_price[:space_split])
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
                    promo = item.find_elements_by_xpath(".//p[@class='item-promo']")
                    if promo:
                        promo = promo[0].text
                        if promo == "OUT OF STOCK" or promo == "COMING SOON":
                            in_stock = False
                except NoSuchElementException:
                    pass

                # print(f"Item in stock: {in_stock}")

                keyword_match = False
                for keyword in self.search_keywords:
                    # TODO: use better method than __contains__ because
                    # false positive hits occur, e.g. keyword 570 causes 5700 to be a hit
                    if product_name.__contains__(keyword):
                        keyword_match = True
                        # print(f"Keyword hit for {keyword}")

                # product of interest that is in stock
                if keyword_match and in_stock and product_price is not None and product_price < self.price_threshold:
                    self.products_hit_count += 1
                    print(f"{product_name} is in stock with price {product_price}, "
                          f"({round(100 * (1 - (product_price / self.price_threshold)), 2)}% less "
                          f"than the threshold of {self.price_threshold})")
                    self.product_hits[item_no] = product_url

                # product of interest that is not in stock (for logging purposes)
                if keyword_match and product_price is not None and product_price < self.price_threshold:
                    product_row = self.format_row(product_name=product_name, product_price=product_price,
                                                  in_stock=in_stock, product_url=product_url, item_number=item_no)
                    total_product_array = pd.concat([total_product_array, product_row], ignore_index=True)

            # re-establish page information
            pagination = self.driver.find_element_by_class_name("list-tool-pagination-text")
            page_info = pagination.text
            page_info = page_info.replace("Page ", "")
            slash_index = page_info.index("/")
            current_page = int(page_info[:slash_index])

            # determine whether to click 'next page' or not
            next_page_button = pagination.find_element_by_xpath("//button[@title='Next']")
            if next_page_button.get_property("disabled"):
                break
            else:
                self.driver.execute_script("arguments[0].click();", next_page_button)
                time.sleep(self.parse_interval)

        end_time = time.perf_counter()
        print(f"Scrape completed in {round(end_time - begin_time, 2)} seconds")

        self.driver.close()

        pd.options.display.width = 0
        if len(total_product_array) > 0:
            self.log_products(product_dataframe=total_product_array, filename=self.output_filename)

    # TODO
    def purchase(self):
        pass

    @staticmethod
    def notify():
        notifier = ToastNotifier()
        notifier.show_toast("Newegg Scraper",
                            "Products of interest are in stock! Check log for details.",
                            duration=10,
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
    def log_products(product_dataframe, filename):
        try:
            product_dataframe.to_excel(filename + '.xlsx')
            print(f"File {filename}.xlsx exported to {os.getcwd()}")
        except PermissionError:
            print(f'Coule not write to "{filename}.xlsx". It may currently be in use. Please close '
                  'any programs currently using it and try again.')


if __name__ == "__main__":
    crawler = NeweggCrawler()
    search_interval = config.search_interval
    schedule.every(search_interval).minutes.do(crawler.run)

    crawler.run()
    # while True:
    #     schedule.run_pending()
    #     time.sleep(4)
