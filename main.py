from __future__ import annotations
from collections import Counter
from typing import TypedDict, Any
from dotenv import load_dotenv
import json
import os

load_dotenv()

if (data := os.getenv("DATA")) is not None:
    DATA_FILE: str = data

if (save := os.getenv("SAVE")) is not None:
    SAVE_FILE: str = save

if (env := os.getenv("ENV")) is not None:
    DEBUG: bool = True if env == "DEBUG" else False

class GameData(TypedDict):
    """
    Prompt Is What Appears Next To The Option
    When You Choose The Option, The Question Appears(Context For The Next Option)
    Answers Can Either Be: 
        - String: Only One Option
        - Dict: Multiple Options
            - GameData: New Game State As Result Of The Option
            - String: No New Game State, End Game(Will Be Converted Into Blank Game Data State)
    """
    prompt: str
    question: str
    answer: str | dict[str, GameData]

class SaveData(TypedDict):
    all: list[str]
    obtained: list[str]

def load_game_data() -> GameData:
    with open(DATA_FILE, "r") as file:
        return process_json_data(json.load(file))

def load_save_data() -> SaveData:
    with open(SAVE_FILE, "r") as file:
        return SaveData(json.load(file))

def save_data_to_file(save_data: SaveData) -> None:
    with open(SAVE_FILE, "w") as file:
        json.dump(save_data, file, indent=4)

def string_to_game_data(answer_string: str) -> GameData:
    return GameData(prompt="", question="", answer=answer_string)

def process_json_data(data: dict[str, Any]) -> GameData:
    if isinstance(data["answer"], str):
        return GameData(**data)

    for option, answer in data["answer"].items():
        data["answer"][option] = string_to_game_data(answer) \
            if isinstance(answer, str) \
            else process_json_data(answer)
    return GameData(**data)

def is_game_complete(save_data: SaveData) -> bool:
    return Counter(save_data["all"]) == Counter(save_data["obtained"])

def award_title(title: str, save_data: SaveData) -> None:
    title = title.strip()
    if title not in save_data["obtained"]:
        save_data["obtained"].append(title)

def end_game_if_end(game_data: GameData, save_data: SaveData) -> bool:
    if isinstance(game_data["answer"], dict):
        return False

    if "Awarded Title" in game_data["answer"]:
        award_title(game_data["answer"].rsplit(":", 1)[1], save_data)
    return True

def is_not_unlocked_route(option: str, save_data: SaveData) -> bool:
    return option in save_data["all"] and option not in save_data["obtained"]

def is_hidden_option(option: str, save_data: SaveData) -> bool:
    """
    - Not Blank(Enter)
    - Not *(Wildcard Any)
    - Not .(Secret)
    """
    return option == "" or "*" in option or "." in option or is_not_unlocked_route(option, save_data)

def run_game(game_data: GameData, save_data: SaveData) -> None:
    while True:
        print("-------------")
        print(game_data["prompt"]) if game_data["prompt"] else None
        print(game_data["question"]) if game_data["question"] else None

        if end_game_if_end(game_data, save_data):
            print(game_data["answer"])
            return
        assert isinstance(game_data["answer"], dict) # Answer Is Guarantee To Be Dict Cuz Otherwise End Game. Assert For Type Checkers

        option_str: str = "\n".join([
            f"{option}) {data["prompt"]}" 
            for option, data in game_data["answer"].items() 
            if not is_hidden_option(option, save_data)
        ])

        response: str = input(option_str + "\n")
        if is_not_unlocked_route(response, save_data):
            print("Invalid Input?")
            continue

        if (data := game_data["answer"].get(response)) is not None:
            game_data = data
            continue

        secret_options = [key.split(".", 1)[1].strip() for key in game_data["answer"].keys() if "." in key]
        if response in secret_options:
            game_data = game_data["answer"][f".{response}"]
            continue

        if "*" in game_data["answer"].keys():
            game_data = game_data["answer"]["*"]
            continue

        if DEBUG:
            raise Exception(f"Failed to read input.\nInput: {response}\nGame Data: {game_data}")
        print("Invalid Input!")

def main():
    game_data: GameData = load_game_data()
    save_data: SaveData = load_save_data()

    if is_game_complete(save_data):
        print("Game Completed!")
        return

    try:
        run_game(game_data, save_data)
    finally:
        save_data_to_file(save_data)

if __name__ == "__main__":
    main()
