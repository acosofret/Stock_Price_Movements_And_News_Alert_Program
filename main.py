import requests
# For safety add your Sensitive data, such as API keys in a separate file "my_vars", and include it in the .gitignore
# Then import them all:
from my_vars import *

# Set a variable for the symbol of the stock we want to track:
STOCK = "TSLA" # In our case is Tesla (symbol: TSLA)
# Set a variable for the company name:
COMPANY_NAME = "Tesla Inc"

# Go to https://www.alphavantage.co/, and get a free API Key:
# For safety you shouldn't write it here, but set it as an ENVIRONMENT variable, or in a separate file, and call it here.
ALPHAVANTAGE_API_KEY = MY_STOCK_API_KEY
ALPHAVANTAGE_END_POINT = "https://www.alphavantage.co/query"
ALPHAVANTAGE_PARAMETERS = {
	"function" : "TIME_SERIES_DAILY",
	"symbol" : STOCK,
	"outputsize" : "compact",
	"apikey" : ALPHAVANTAGE_API_KEY,
}


## Now, from the https://www.alphavantage.co endpoint, pull out the data for the stock we are tracking:
stock_response = requests.get(ALPHAVANTAGE_END_POINT, params=ALPHAVANTAGE_PARAMETERS)
stock_response.raise_for_status()
data = stock_response.json()["Time Series (Daily)"]

# Define the price increase/decrease that you want to track, in %:
# For example, when do you want to get notified about the price change? When it change by 1%, 5%, 10%?
# Insert the right number below:
tracked_percentage = 1 # for testing purposes we'll set it to 1. (To make sure we get a notification about
# a price change; if we set it higher, the price may have not moved that much and we won't be notified, meaning we
# can't test our code

# print(data) # We add this line just temporarily, so we can see what data we get and how we can manipulate it

# we define a list to add the last 2 days of the market, so we can get the price data just for those 2 days
last_market_days = []
previous_day = ""
message_part1 = ""

# Now we can define a function that checks the price for the last 2 days in the data pulled from endpoint:
def check_price():
	global previous_day
	global message_part1
	def extract_last_2_market_days(data):
		n = 0
		for key in data:
			if n < 2:
				last_market_days.append(key)
			n += 1
			# that way, the function pulls only data for the first 2 days (index 0 and 1)
	extract_last_2_market_days(data) # We run the function and get the keys for the last 2 days in our list

	last_day = last_market_days[0] # we define the last day from those 2 in the list
	previous_day = last_market_days[1] # and the previous day....

	# we know that the opening price for each day is the closing price for the previous day:
	today_op = float(data[last_day]["4. close"])
	yesterday_op = float(data[previous_day]["4. close"])
	price_dif = float(today_op) - float(yesterday_op) # We check the price difference
	tracked_price_change = (float(yesterday_op) * tracked_percentage) / 100 # We add formula for the percentage we want to track
	increase_percentage = ((today_op-yesterday_op)*100)/yesterday_op # We add formula for the increasing percentage
	decrease_percentage = ((yesterday_op-today_op)*100)/yesterday_op # We add formula for the decreasing percentage

	# If STOCK price increase/decreases by x% between yesterday and the day before yesterday then
	# we select the first part of the message to be sent via SMS,
	# and proceed ahead with checking also the news
	if today_op > yesterday_op and price_dif >= tracked_price_change:
		message_part1 = f"\n{COMPANY_NAME} is up +{increase_percentage}% in the last 24h."
	elif today_op < yesterday_op and (price_dif * (-1)) >= tracked_price_change:
		message_part1 = f"\n{COMPANY_NAME} is down -{round(decrease_percentage, 2)}% in the last 24h."
	else:
		message_part1 = f"\n{COMPANY_NAME} had no major price movement in the last 24h."
	# print(message_part1) # this line is just for testing

check_price() # we run the price change check and write furthe the code for getting the news (in case is necessary)


# Use https://newsapi.org
NEWS_API_KEY = MY_NEWS_APY_KEY # use your API key and ideally store it as ENVIRONMENT variable, or in a .gitignore file
NEWS_END_POINT = "https://newsapi.org/v2/everything"
NEWS_PARAMETERS = {
	"q" : COMPANY_NAME,
	"from" : previous_day,
	"language" : "en",
	"sortBy" : "popularity",
	"apiKey" : NEWS_API_KEY,
}
news = requests.get(NEWS_END_POINT, NEWS_PARAMETERS)
news.raise_for_status()
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME:
news_data = news.json()["articles"][:3]
# formulate the 2nd part of the SMS message:
message_part2 = f"Headlines:\n\n ➀ {news_data[0]['title']}.\nRead the full article:{news_data[0]['url']}\n\n ② {news_data[1]['title']}.\nRead the full article:{news_data[1]['url']}\n\n ③ {news_data[2]['title']}.\nRead the full article:{news_data[2]['url']}"
# print(news_data) # only for testing

# And finally we use https://www.twilio.com, for
# sending a separate message with the percentage change and each article's title and description to your phone number.
from twilio.rest import Client
twilio_account_sid = MY_TWILIO_ACC_SID # use your own & store it as ENVIRONMENT variable, or in a .gitignore file
twilio_auth_token = MY_TWILIO_AUTH_TOKEN # use your own & store it as ENVIRONMENT variable, or in a .gitignore file

client = Client(twilio_account_sid, twilio_auth_token)
message = client.messages \
	.create(
	body=f"{message_part1}.\n{message_part2}",
	from_=MY_TWILIO_NUMBER,
	to=MY_NUMBER
)
print(message.status)
