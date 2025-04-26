# DynoTrade

A Python-based trade helper program that evaluates multi-item trades using an SQLite database to manage item value and demand scoring.

## Features
- Import and manage item data (name, value, demand) from CSV files into an SQLite database
- SQL-based storage and retrieval of skin data for fast trade evaluation
- Fairness checker for trades involving multiple items
- Dynamic scoring algorithm that weights item demand relative to value
- (Planned) Trade route optimizer to find the shortest sequence of 3-item trades to reach a desired item

## How to Run
1. Install Python 3 (SQLite comes built-in with Python).
2. Run `main.py`.
3. Follow the menu instructions to import skins, add new items, or evaluate trades.

## Technologies Used
- **Python 3**
- **SQLite3** (for database management)
- **CSV parsing** (to load skin data)

## Future Plans
- Implement shortest-path trading optimizer using graph algorithms
- Improve the interface with a basic web dashboard or desktop app
