# Terminal RPG
A lightweight, data-driven terminal adventure game engine written in Python.

The engine is intentionally simple: every scene, dialogue option, and ending is stored in a JSON file, while the Python parser handles loading data, displaying prompts, validating input, tracking persistent progress, and unlocking new routes.

The entire game can be rewritten without modifying the Python source code. Simply edit the JSON files to create completely new adventures.

<img width="1920" height="1080" alt="TerminalRPGGif" src="https://github.com/user-attachments/assets/4fbcb4fa-7e3e-47d2-8e96-e580b49d5277" />

## Features
* **Data-driven design**
  * No game logic is hardcoded into the story.
  * Entire games are described using JSON.

* **Recursive dialogue trees**
  * Unlimited branching conversations.
  * Nested choices of arbitrary depth.

* **Persistent progression**
  * Titles earned by the player are saved between runs.
  * Previously unlocked routes remain available.

* **Title-gated progression**
  * Story branches can require previously earned titles.
  * Encourages replaying the game to unlock additional content.

* **Hidden routes**
  * Secret commands can exist without appearing in the option list.
  * Hidden title routes allow entirely secret progression paths.

* **Wildcard responses**
  * Handle any unexpected input gracefully.
  * Useful for joke responses or "incorrect answer" branches.

* **Automatic save system**
  * Progress is automatically written to `save.json` whenever the game exits.

* **Minimal parser**
  * The entire engine is less than 150 lines of Python.
  * Most development effort goes into writing the JSON rather than programming.

---

# Project Structure

```
.
├── data.json      # Story, dialogue, routes, and endings
├── save.json      # Persistent player progression
├── main.py        # Game parser
└── .env           # Optional DEBUG configuration
```

---

# Installation

1. Clone the repository.
```bash
git clone git@github.com/TheWhiteLionGod/TerminalRPG
```

2. Install dependencies(with UV):
```bash
uv sync
```

3. Run the game(with UV):
```bash
uv run main.py
```

# How It Works
The engine loads two files(examples in the games/ folder):

## `data.json`
Contains the entire game.
Every node contains three fields:
```json
{
    "prompt": "...",
    "question": "...",
    "answer": ...
}
```

### prompt
Displayed next to an option.
Example:
```
1) Open Door
```

### question
Displayed after selecting an option.
Example:
```
The room is dark.
What would you like to do?
```

### answer
Can be one of two things.
A string:
```json
"answer": "Awarded Title: Explorer"
```
which immediately ends the game,
or another object containing additional choices:
```json
"answer": {
    "1": {  // User has to type "1" to enter this section.
        "prompt": "...",
        "question": "...",
        "answer": "...",
    },
    "yes": {
        ...
    }
}
```
which continues the adventure.

# save.json
Stores persistent player progress.
```json
{
    "all": [
        "Explorer",
        "Master Detective"
    ],
    "obtained": [
        "Explorer"
    ]
}
```

## all
Contains every obtainable title in the game.
This list is used to determine:
* completion percentage
* locked routes
* whether the game has been fully completed

## obtained
Titles the player has earned.
These persist across multiple runs.

# Title System
Titles act as permanent achievements.
Example ending:
```
Awarded Title: Explorer
```
Once earned, the title is permanently stored in `save.json`.
Future routes may require this title before becoming available.

# Locked Routes
A route can require a title simply by using the title as the option key.
Example:
```json
{
    "Explorer": {
        "prompt": "Enter the hidden cave",
        ...
    }
}
```

If the player has not earned the title **Explorer**, the option is hidden.
Once earned, it appears like a normal option.

# Hidden Options
Hidden options begin with a period.
Example:
```json
".Dance"
```

The player will **not** see this option listed.
Instead, they must type:
```
Dance
```
to activate it.

This is useful for:
* secret commands
* easter eggs
* hidden endings
* puzzle solutions

Hidden options can also be title-gated:
```json
".Explorer"
```

This creates an invisible route that only players with the **Explorer** title can access.

# Wildcard Responses
A wildcard route is written as:
```json
"*"
```

If no other input matches, the wildcard route is selected.
Example:
```json
{
    "*": "Nothing happens."
}
```

This is useful for:
* incorrect answers
* joke responses
* catch-all dialogue
* forgiving player mistakes

# Blank Input
An empty string may also be used as an option key.
```json
""
```
This allows progression when the player simply presses **Enter**.

# Game Completion
The game is considered complete once every title listed in `save.json` has been earned.
Internally, completion compares the contents of:
* `all`
* `obtained`
using a multiset comparison.

# DEBUG Mode
Create a `.env` file.
```
ENV=DEBUG
DATA=path/to/your_data.json
SAVE=path/to/your_save.json
```

When enabled, invalid input raises an exception showing the current game state instead of printing a generic error message.
This makes debugging dialogue trees significantly easier.

# Writing Stories
Since every story is JSON, creating new adventures requires no Python knowledge.
You can build:
* Interactive fiction
* Escape rooms
* Puzzle games
* Visual novel prototypes
* Dialogue systems
* Decision trees
* Choose-your-own-adventure stories
using the same parser.

# Limitations
## Colons (`:`) in ending strings
Titles are detected via the ":" at the end of the chocie in the following format:
```json
Awarded Title: TitleNameHere
```

As a result, using colons in text may falsely trigger awarding a title.
**Avoid placing additional colons earlier in the same ending string**.

Good:
```json
"answer": "You escaped successfully.\nAwarded Title: Explorer"
```

Bad:
```json
"answer": "Awarded Title: Explorer\nGreat job: Player"
```
The parser may incorrectly interpret the title name.

---

## Every title must exist
Every obtainable title should also appear in:
```json
save.json
```
under the `all` list.
Otherwise, the game can never reach 100% completion.

## Circular progression
Since progression is based entirely on titles, avoid creating situations where:
* Route A requires Title B
* Title B can only be earned through Route A
Such routes are impossible to unlock.

## Invalid JSON
Because the parser loads JSON directly, malformed JSON will prevent the game from starting.
Using a JSON formatter or validator while editing is highly recommended.

# TODOS
Possible extensions include:
* Inventory system
* Variables and flags
* Conditional dialogue
* Random events
* Multiple save slots
* Named node references
* Undo / backtracking
* Rich text formatting
* ANSI color support
* Sound effects
* Save encryption

The current implementation intentionally keeps the engine small and easy to understand.

# Contributing
Improvements to the parser, bug fixes, new gameplay mechanics, and sample stories are welcome.
When introducing new features, try to preserve the engine's primary goal:
> Keep the parser simple, and let the JSON do the storytelling.

# License
This project is released under the MIT License.

# Extras
Hey there, this is a small story from myself, Aryan Agarwal. 
I made the RPG in an hour as a birthday present for my younger sister(she was delighted). You can see it under games/birthday_game

Interestingly enough(I guess all the random stuff I work on made me a better programmer), the parser itself was super short: just 100 lines(became longer with additional features). Instead, I probably spent 45 minutes or so writing out the entire story and mentalizing how to parser the json instead of coding.

The simplicity was really nice, and I was quite shocked at how many features it supported. With the addition of features such as title routes, I made a second terminal game which is longer and tries to push the limits of the system.

Overall, it was quite the fun time, and I never imagined the simple game idea I had in my head would result in this parser. If you have any neat features you think would be great, feel free to open an issue / pull request. Other than that, see you later.

PS. Sorry for the terrible git history, I accidently deleted the .git/ folder when cleaning up the files. This is why you back up your commits to a remote repository.
