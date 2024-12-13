from typing import TypedDict
from selenium.webdriver.common.by import By


class Game(TypedDict):
    game_date: str
    game_time: str
    home_team: str
    channel: str
    away_team: str


def parse_game_details(driver):
    game_days = driver.find_elements(By.XPATH, "//section[@class='Card gameModules']")
    game_dict = {}
    for game_day in game_days:
        game_list = []
        game_date = game_day.find_element(By.XPATH, ".//header").text
        games = game_day.find_elements(By.XPATH, "./div/section")
        for game in games:
            game_time = game.find_element(By.XPATH, ".//div[@class='ScoreCell__Time ScoreboardScoreCell__Time h9 clr-gray-03']").text
            channel = game.find_element(By.XPATH, ".//div[@class='ScoreCell__NetworkItem']").text
            teams = game.find_elements(By.XPATH, ".//div[@class='ScoreCell__TeamName ScoreCell__TeamName--shortDisplayName db']")
            home_team = teams[1].text
            away_team = teams[0].text

            game_list.append(Game(game_date=game_date, game_time=game_time, home_team=home_team,
                                  away_team=away_team, channel=channel))

        game_dict[game_date] = game_list
    return game_dict


