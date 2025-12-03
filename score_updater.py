from datetime import date, datetime
from dotenv import load_dotenv, set_key
from os import environ as env
from nfl_bot import scraper, operations
from time import sleep
from selenium import webdriver
import json

# environment variables
load_dotenv(r'vars.env')

webhook_url = env.get('webhook_url')

# grab url variables
current_year = env.get('year')
current_season = env.get('season')
current_week = env.get('week')
# build url
url = f'https://www.espn.com/nfl/scoreboard/_/week/{current_week}/year/{current_year}/seasontype/{current_season}'

# load message data
with open(f"data/week_{current_week}.json", 'r') as f:
    message_data = json.load(f)

games_playing = []
for game_id in list(message_data.keys()):
    game_message_dict = message_data[game_id]
    game_time = game_message_dict['game_time']
    game_finished = int(game_message_dict['game_finished'])
    if int(game_time) < int(datetime.timestamp(datetime.now())):
        if game_finished == 0:
            games_playing.append(game_id)

if len(games_playing) > 0:
    # request the page
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    driver = webdriver.Firefox(options=options)

    driver.get(url=url)
    sleep(3)

    game_scores = scraper.parse_game_scores(driver)

    for game_score in game_scores:
        game_id = game_score['game_id']
        if game_id in games_playing:
            # collect scraped data
            home_score = game_score['home_score']
            away_score = game_score['away_score']
            game_finished = int(game_score['game_finished'])
            game_time_left = game_score['game_time_left']

            # update game finished
            message_data[game_id]['game_finished'] = game_finished

            # original message data to update message
            original_message = message_data[game_id]['message']
            original_message_id = message_data[game_id]['message_id']
            original_game_time = message_data[game_id]['game_time']
            # update message
            updated_message = original_message.replace('@', f'{away_score} @ {home_score}')
            updated_message = updated_message.replace(f'<t:{original_game_time}:t>', game_time_left)
            message_webhook = webhook_url.replace('?wait=true', '')
            message_webhook += f"/messages/{original_message_id}"

            print(operations.update(message=updated_message, webhook_url=message_webhook))

    driver.close()

    # write the message data back to a file for later
    with open(f"data/week_{current_week}.json", 'w') as f:
        json.dump(message_data, f, indent=4)

