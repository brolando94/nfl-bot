from datetime import date, datetime
from dotenv import load_dotenv, set_key
from os import environ as env
from nfl_bot import scraper, operations
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from seleniumrequests import Firefox

options = Options()
options.set_preference("browser.download.panel.shown", False)
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
options.headless = False
driver = Firefox()
driver.set_window_size(1920, 1080)

local_timezone_list = str(datetime.now().astimezone().tzinfo).split()
local_timezone = ''
for word in local_timezone_list:
    local_timezone += word[0]


team_mapping = {
    'rams': '<:rams:1316594568690536500>',
    '49ers': '<:49ers:1316594555969339455>',
    'chiefs': '<:cheifs:1316594869887701043>',
    'browns': '<:browns:1316594586402947082>',
    'bengals': '<:bengals:1316596205131792435>',
    'titans': '<:titans:1316594551988944917>',
    'commanders': '<:commanders:1316594550617149514>',
    'saints': '<:saints:1316594562181103656>',
    'ravens': '<:ravens:1316596315261763584>',
    'giants': '<:giants:1316595232015650916>',
    'cowboys': '<:cowboys:1316596123661500568>',
    'panthers': '<:panthers:1316596300405276763>',
    'jets': '<:jets:1316594559417061407>',
    'jaguars': '<:jaguars:1316594575250427964>',
    'dolphins': '<:dolphins:1316594863763882095>',
    'texans': '<:texans:1316594578966581248>',
    'colts': '<:colts:1316595526828953640>',
    'broncos': '<:broncos:1316594581977960470>',
    'bills': '<:bills:1316594592660979753>',
    'lions': '<:lions:1316596028668907550>',
    'steelers': '<:steelers:1316594557374435389>',
    'eagles': '<:eagles:1316594558523543582>',
    'patriots': '<:patriots:1316594860807159808>',
    'cardinals': '<:cardinals:1316596487534280714>',
    'buccaneers': '<:bucaneers:1316594553200971876>',
    'chargers': '<:chargers:1316595445954248825>',
    'packers': '<:packers:1316595567878606899>',
    'seahawks': '<:seahawks:1316594554136297472>',
    'bears': '<:bears:1316594589422850080>',
    'vikings': '<:vikings:1316594565834215516>',
    'falcons': '<:falcons:1316594596326674472>',
    'raiders': '<:raiders:1316594571798384660>'
}

# environment variables
load_dotenv(r'vars.env')

webhook_url = env.get('webhook_url')

current_year = env.get('year')
if current_year is None:
    current_year = str(date.today().year)
    set_key(r'vars.env', 'year', f'{current_year}')
else:
    current_year = str(current_year)

current_week = env.get('week')
if current_week is None:
    current_week = '1'
    set_key(r'vars.env', 'week', f'{current_week}')
else:
    current_week = int(current_week) + 1
    current_week = str(current_week)

set_key(r'vars.env', 'week', f'{current_week}')
# request the page
driver.get(url=f'https://www.espn.com/nfl/scoreboard/_/week/{current_week}/year/{current_year}/seasontype/2')
sleep(3)
# parse the game data
game_dict = scraper.parse_game_details(driver)

# send the staring message if there are games
starting_msg = f"Week {current_week} NFL Pick'ems.\nVote using team emoji's on each game message"
if len(game_dict) > 0:
    print(operations.send(message=starting_msg, webhook_url=webhook_url))

# separate into day of the week with lists of games
game_days = game_dict.keys()
for game_day in game_days:
    # send the message for the date
    print(operations.send(message=f"# {game_day}", webhook_url=webhook_url))
    sleep(1)
    # loop the game data and build the message
    for game in game_dict[game_day]:
        home = game['home_team']
        home_emoji = team_mapping[home.lower()]
        away = game['away_team']
        away_emoji = team_mapping[away.lower()]
        game_msg = f"**{away}** {away_emoji} @ **{home}** {home_emoji}" \
                   f"\nGame Info: {game['game_time']} {local_timezone} - {game['channel']}"

        # send message
        print(operations.send(message=game_msg, webhook_url=webhook_url))
        sleep(1)

driver.close()
