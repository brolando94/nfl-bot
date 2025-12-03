from typing import TypedDict
from selenium.webdriver.common.by import By


class Game(TypedDict):
    game_date: str
    game_time: str
    home_team: str
    channel: str
    away_team: str
    game_id: str

class GameScore(TypedDict):
    game_id: str
    home_score: str
    away_score: str
    game_finished: int
    game_time_left: str


def parse_game_details(driver):
    game_days = driver.find_elements(By.XPATH, "//section[@class='Card gameModules']")
    game_dict = {}
    for game_day in game_days:
        game_list = []
        game_date = game_day.find_element(By.XPATH, ".//header//h3").text
        games = game_day.find_elements(By.XPATH, "./div/section")
        for game in games:
            game_id = game.get_attribute("id")
            game_time = game.find_element(By.XPATH, ".//div[@class='ScoreCell__Time ScoreboardScoreCell__Time h9 clr-gray-03']").text
            channels = game.find_elements(By.XPATH, ".//div[@class='ScoreCell__NetworkItem']")
            channel_list = []
            for channel_elem in channels:
                channel_list.append(channel_elem.text.strip())
            channel = ', '.join(channel_list)

            teams = game.find_elements(By.XPATH, ".//div[@class='ScoreCell__TeamName ScoreCell__TeamName--shortDisplayName db']")
            home_team = teams[1].text
            away_team = teams[0].text

            game_list.append(Game(game_date=game_date, game_time=game_time, home_team=home_team,
                                  away_team=away_team, channel=channel, game_id=game_id))

        game_dict[game_date] = game_list
    return game_dict


def parse_game_scores(driver):
    game_scores = []
    games = driver.find_elements(By.XPATH, "//section[@class='Card gameModules']/div/section")
    for game in games:
        game_finished = 0
        game_id = game.get_attribute("id")
        game_time_left = game.find_element(By.XPATH, ".//div[contains(@class, 'ScoreboardScoreCell__Time')]").text
        if 'FINAL' in game_time_left:
            game_finished = 1
        scores = game.find_elements(By.XPATH, ".//li//div[contains(@class, 'ScoreboardScoreCell__Value')]")
        total_amount = int(len(scores))
        if total_amount == 0:
            game_scores.append(GameScore(game_id=game_id, home_score='0', away_score='0',
                                         game_finished=0, game_time_left=game_time_left))
        else:
            split = int(total_amount/2)
            home_score = 0
            away_score = 0
            # away score is first half
            for i in range(split):
                try:
                    away_score += int(scores[i].text)
                except ValueError:
                    pass
            for i in range(split, total_amount):
                try:
                    home_score += int(scores[i].text)
                except ValueError:
                    pass

            game_scores.append(GameScore(game_id=game_id, home_score=str(home_score), away_score=str(away_score),
                                         game_finished=game_finished, game_time_left=game_time_left))

    return game_scores
