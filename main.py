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

# grab url variables
current_year = env.get('year')
current_season = env.get('season')
current_week = env.get('week')

# check to make sure they exist
if current_year is None:
    current_year = str(date.today().year)
    set_key(r'vars.env', 'year', f'{current_year}')
else:
    current_year = str(current_year)

if current_season is None:
    current_season = '1'
    set_key(r'vars.env', 'season', '1')
else:
    current_season = str(current_season)

if current_week is None:
    current_week = '2'
    set_key(r'vars.env', 'week', '2')
else:
    # move to the next week
    current_week = int(current_week) + 1
    current_week = str(current_week)
    set_key(r'vars.env', 'week', f'{current_week}')

# switch to regular season
if current_week == '5' and current_season == '1':
    current_season = '2'
    set_key(r'vars.env', 'season', '2')
    current_week = '1'
    set_key(r'vars.env', 'week', '1')
# switch for playoffs
elif current_week == '19' and current_season == '2':
    current_season = '3'
    set_key(r'vars.env', 'season', '3')
    current_week = '1'
    set_key(r'vars.env', 'week', '1')


# request the page
url = f'https://www.espn.com/nfl/scoreboard/_/week/{current_week}/year/{current_year}/seasontype/{current_season}'
driver.get(url=url)
sleep(3)
# parse the game data
game_dict = scraper.parse_game_details(driver)

# translate the season number and week into the staring message
match current_season:
    case '1':
        starting_msg = f'Preseason Week {current_week}\nVote using team emoji\'s on each game message'
    case '2':
        starting_msg = f'Week {current_week}\nVote using team emoji\'s on each game message'
    case '3':
        match current_week:
            case '1':
                starting_msg = 'Playoff Wild Card\nVote using team emoji\'s on each game message'
            case '2':
                starting_msg = 'Playoff Divisional\nVote using team emoji\'s on each game message'
            case '3':
                starting_msg = 'Conference Championships\nVote using team emoji on game message'
            case '4':
                starting_msg = 'Pro Bowl\nVote using team emoji on game message'
            case '5':
                starting_msg = 'Super Bowl\nVote using team emoji on game message'

if len(game_dict) > 0:
    print(operations.send(message=starting_msg, webhook_url=webhook_url))

# separate into day of the week with lists of games
game_days = game_dict.keys()
for game_day in game_days:
    # send the message for the date
    # print(operations.send(message=f"# {game_day}", webhook_url=webhook_url))
    sleep(1)
    # loop the game data and build the message
    for game in game_dict[game_day]:
        home = game['home_team']
        home_emoji = team_mapping[home.lower()]
        away = game['away_team']
        away_emoji = team_mapping[away.lower()]
        # convert date and time to unix timestamp
        date_to_convert = f"{game_day} {game['game_time']}"
        # Parse the date string into a datetime object
        dt_object = datetime.strptime(date_to_convert, "%A, %B %d, %Y %I:%M %p")
        # Convert the datetime object to a Unix timestamp
        game_timestamp = int(dt_object.timestamp())
        game_msg = f"**{away}** {away_emoji} @ **{home}** {home_emoji}" \
                   f"\nGame Time: <t:{game_timestamp}:t>" \
                   f"\nChannel: {game['channel']}"

        # send message
        print(operations.send(message=game_msg, webhook_url=webhook_url))
        sleep(1)

driver.close()

# need to end the game and set it up for next year
if current_season == '3' and current_week == '5':
    set_key(r'vars.env', 'year', f'{int(current_year) + 1}')
    set_key(r'vars.env', 'week', '2')
    set_key(r'vars.env', 'season', '1')
