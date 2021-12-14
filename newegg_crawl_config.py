# THIS FILE CONTAINS VARIABLES FOR USE IN THE NEWEGG CRAWL

# newegg generic result page url
url = "https://www.newegg.com/p/pl?N=100007709"

# set True for headless mode (to run silently in background) or False to open and view as it runs
headless_mode = True

# restrict results to those only sold by newegg
# setting as False will significantly increase results at the cost of time
# especially as lots of these 3rd party results aren't really for current tech
sold_by_newegg = True

# valid webdriver types:
# chrome: https://chromedriver.chromium.org/downloads
# firefox: https://github.com/mozilla/geckodriver/releases
webdriver_type = "firefox"

# geckodriver (firefox) path
# leave empty if it exists in the current working directory
geckodriver_path = ""

# chromedriver path
# leave empty if it exists in the current working directory
chromium_path = ""

# keywords to find in the title of the item
# search_keywords = ["6800", "6900", "RTX", "2060", "2070", "2080",
#                    "3060", "3070", "3080", "3090"]

search_keywords = ["1060", "1050", "970", "980"]

# comma-separated list of strings of item numbers in order of buy preference
# the bot will attempt to purchase the item in order, giving highest
# preference to the first items -> last items
watched_items = ['N82E16814125915', 'N82E16814125916', 'N82E16814126170']

# max price in USD to catch as an integer or float
price_threshold = 600

# time in minutes between crawls
search_interval = 5

# time in seconds between bot actions on page -- keep above a reasonable amount to not flag your IP as a bot
parse_interval = 3.5

# output file name without extension (is .csv by default)
output_filename = "log"

# push results to Discord webhook
discord_webhook_url = ""

# logging
# DEBUG, INFO, WARNING, ERROR, CRITICAL
# set to WARNING to only log errors
# set to ERROR to only log errors and critical errors
# set to CRITICAL to only log critical errors
# set to DEBUG to log everything
# set to INFO to log everything but debug messages
log_level = "DEBUG"

log_to_file = True
