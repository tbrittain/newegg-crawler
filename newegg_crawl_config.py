# THIS FILE CONTAINS VARIABLES FOR USE IN THE NEWEGG CRAWL


# newegg generic result page url
url = "https://www.newegg.com/p/pl?N=100007709"


# set True for headless mode (to run silently in background) or false to open and view as it runs
headless_mode = False

# restrict results to those only sold by newegg
# setting as False will significantly increase results at the cost of time
# especially as lots of these 3rd party results aren't really for current tech
sold_by_newegg = True

# geckodriver webdriver absolute path
webdriver_path = "D:/Github/newegg/geckodriver.exe"

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

# time in seconds between bot actions on page -- keep above 2 or 3 to not flag your IP as a bot
parse_interval = 3.5

# output file name without extension (is .xlsx by default)
output_filename = "log"

# ========================== experimental features - not functional ==========================
buy_product = False

hashed_key = b'y28wf4TOxUJBScdL4QajuSg1SMuTNIvHEDz-G4MbHKs='

salt = b'\xb4-9\x0035\xedYE\xe1LUd"\xe5$'
