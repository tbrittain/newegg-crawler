# newegg_crawler
 
Newegg_Crawler is a product scraping tool for [Newegg](https://www.newegg.com/). You can customize it to search for any
type of product offered on the website, and it provides product price and stock tracking over time
(optionally with notifications directly to your Discord private messages).

# Installation
Install the necessary dependencies:
```
pip install -r requirements.txt
```
This project uses Selenium and more specifically Firefox's Geckodriver, so install Geckodriver to the working
directory of the project, found [here](https://github.com/mozilla/geckodriver/releases). (Currently only tested
on Windows, so use the Geckodriver EXE)

# Configuration
All configuration variables are set in the newegg_crawl_config.py file.

For the generic result page url, you could use the following:
- `https://www.newegg.com/p/pl?N=100007709` for Graphics cards
- `https://www.newegg.com/Processors-Desktops/SubCategory/ID-343?Tid=7671` for CPUs
- `https://www.newegg.com/p/pl?d=motherboard` for motherboards

Be sure to set the `webdriver_path` to the path of the Geckodriver executable.

`search_keywords` and `watched_items` are lists of strings. In the case of `search_keywords`, this may be any keyword
specific to the product you are trying to filter down to, such as `"RTX"` or `3090`. `watched_items` must be the product ID
specific to the unique product you are trying to buy. 

For example, [this graphics card](https://www.newegg.com/gigabyte-geforce-gtx-1050-ti-gv-n105toc-4gd/p/N82E16814125915?Item=N82E16814125915&Tpk=N82E16814125915)
has the product ID `N82E16814125915`. You can quickly determine product IDs by running a scan of products
and examining the product ID as a column of the `log.xlsx` file. All other config variables are self-explanatory.

Since this crawler is Discord integrated, you must register it as an application in the [Discord Developer Portal](https://discord.com/developers/applications).
Save your `DISCORD_TOKEN` and `DISCORD_USER` (discord user ID, NOT username) to a .env file.

# Run
Run the newegg_crawl.py script to start the bot
```
python newegg_crawl.py
```

## Personal note
I have not purchased a graphics card with this yet, but hopefully I will soon 😉
