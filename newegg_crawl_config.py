# THIS FILE CONTAINS VARIABLES FOR USE IN THE NEWEGG CRAWL
# newegg page url
url = "https://www.newegg.com/p/pl?N=100007709"

# set True for headless mode (to run silently in background) or false to open and view as it runs
headless_mode = False

# restrict results to those only sold by newegg
# setting as False will significantly increase results at the cost of time
# especially as lots of these 3rd party results aren't really for current tech
sold_by_newegg = True

# webdriver absolute path
webdriver_path = "D:/Github/newegg_crawler/geckodriver.exe"

# keywords to find in the title of the item
search_keywords = ["6800", "6900", "RTX", "2060", "2070", "2080",
                   "3060", "3070", "3080", "3090"]

# comma-separated list of strings of item numbers in order of buy preference
# the bot will attempt to purchase the item in order, giving highest
# preference to the first items -> last items
item_preference = []

# max price to catch as an integer or float
price_threshold = 600

# time in minutes between crawls
search_interval = 30

# time in seconds between page reloads
parse_interval = 3

output_filename = "log"
