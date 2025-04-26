import sqlite3
import csv
import os


print(f"Database location: {os.path.abspath('skins.db')}")

def demand_to_score(demand_text):
    """Convert demand text to a numeric score."""
    demand_mapping = {
        "terrible demand": 0,
        "bad demand": 1,
        "ok demand": 2,
        "decent demand": 3,
        "good demand": 4,
        "great demand": 5
    }
    return demand_mapping.get(demand_text.lower().strip(), 0)  # Default to 0 if not found

def create_or_update_table():
    conn = sqlite3.connect("skins.db")
    cursor = conn.cursor()

    # Create the table with demand column
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS skins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        value INTEGER NOT NULL,
        demand INTEGER DEFAULT 0  -- New demand column
    )
    """)

    # Add demand column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE skins ADD COLUMN demand INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        # Column already exists, no action needed
        pass

    conn.commit()
    conn.close()

def clean_and_add_skin(name, value, demand_text):
    """Clean and add a skin to the database."""
    # Clean inputs
    name = name.strip("• ").strip()
    demand = demand_to_score(demand_text)
    value = int(value)

    # Insert into the database
    conn = sqlite3.connect("skins.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT OR IGNORE INTO skins (name, value, demand) VALUES (?, ?, ?)", (name, value, demand))
        conn.commit()
        print(f"Skin '{name}' added with value {value} and demand {demand_text}!")
    except Exception as e:
        print(f"Error adding skin: {e}")
    finally:
        conn.close()

def clean_and_update_skin(name, new_value, new_demand_text):
    """Clean and update a skin's value and demand."""
    # Clean inputs
    name = name.strip("• ").strip()
    new_demand = demand_to_score(new_demand_text)
    new_value = int(new_value)

    # Update the database
    conn = sqlite3.connect("skins.db")
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE skins SET value = ?, demand = ? WHERE name = ?", (new_value, new_demand, name))
        if cursor.rowcount > 0:
            print(f"Skin '{name}' updated to value {new_value} and demand {new_demand_text}!")
        else:
            print(f"Skin '{name}' not found!")
        conn.commit()
    except Exception as e:
        print(f"Error updating skin: {e}")
    finally:
        conn.close()

def import_skins_from_csv_with_cleaning(file_path):
    """Import skins from a CSV or formatted text file with cleaning."""
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return

    conn = sqlite3.connect("skins.db")
    cursor = conn.cursor()

    try:
        with open(file_path, "r") as file:
            for line in file:
                # Clean the line and extract data
                line = line.strip()
                if line.startswith("•"):
                    line = line[1:].strip()  # Remove bullet

                if ":" in line and "(" in line:  # Ensure valid format
                    parts = line.split(":")  # Split name and value-demand
                    name = parts[0].strip()
                    value_demand = parts[1].split("(")
                    value = value_demand[0].strip().replace(",", "")  # Remove commas from value
                    demand_text = value_demand[1].strip(" )")

                    # Add the cleaned data to the database
                    clean_and_add_skin(name, value, demand_text)

        print(f"Skins from {file_path} imported successfully!")
    except Exception as e:
        print(f"Error importing skins: {e}")
    finally:
        conn.close()

def list_skins():
    conn = sqlite3.connect("skins.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM skins")
    rows = cursor.fetchall()

    if rows:
        print("\nSkins in the database:")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Value: {row[2]}, Demand: {row[3]}")
    else:
        print("No skins in the database!")

    conn.close()

def calculate_dynamic_value_factor(trade_items):
    """Calculate a value factor dynamically based on the trade items."""
    conn = sqlite3.connect("skins.db")
    cursor = conn.cursor()

    total_value = 0
    count = 0

    for item in trade_items:
        cursor.execute("SELECT value FROM skins WHERE name = ?", (item,))
        result = cursor.fetchone()
        if result:
            total_value += result[0]
            count += 1

    conn.close()

    average_value = total_value / count if count > 0 else 1  # Avoid division by zero
    max_demand_score = 5  # Maximum demand score in your system
    target_demand_percentage = 0.3  # Target percentage of score from demand

    return target_demand_percentage / (average_value * max_demand_score**2)

def calculate_trade_score(trade_items):
    """Calculate the total score for trade items based on value and demand."""
    total_score = 0
    value_factor = calculate_dynamic_value_factor(trade_items)  # Dynamic scaling
    conn = sqlite3.connect("skins.db")
    cursor = conn.cursor()

    for item in trade_items:
        cursor.execute("SELECT value, demand FROM skins WHERE name = ?", (item,))
        result = cursor.fetchone()
        if result:
            value, demand = result

            # Adaptive demand weighting
            demand_contribution = (demand ** 2) * (value * value_factor)
            total_score += value + demand_contribution
        else:
            print(f"Warning: Skin '{item}' not found in the database!")

    conn.close()
    return total_score

def evaluate_trade(offered_items, requested_items):
    """Evaluate whether a trade is fair based on adaptive demand weighting."""
    offered_score = calculate_trade_score(offered_items)
    requested_score = calculate_trade_score(requested_items)

    print(f"Offered Score: {offered_score}")
    print(f"Requested Score: {requested_score}")

    if offered_score >= requested_score:
        return "Accept the trade!"
    else:
        return "Decline the trade."

def main():
    create_or_update_table()

    while True:
        print("\nMenu:")
        print("1. Add a skin")
        print("2. Update a skin's value and demand")
        print("3. Delete a skin")
        print("4. List all skins")
        print("5. Evaluate a trade")
        print("6. Import skins from a CSV file")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter the skin name: ")
            try:
                value = int(input("Enter the skin value: "))
                demand_text = input("Enter the skin demand (e.g., 'good demand'): ")
                clean_and_add_skin(name, value, demand_text)
            except ValueError:
                print("Value must be an integer!")

        elif choice == "2":
            name = input("Enter the skin name to update: ")
            try:
                new_value = int(input("Enter the new value: "))
                new_demand_text = input("Enter the new demand (e.g., 'good demand'): ")
                clean_and_update_skin(name, new_value, new_demand_text)
            except ValueError:
                print("Value must be an integer!")

        elif choice == "3":
            name = input("Enter the skin name to delete: ")
            conn = sqlite3.connect("skins.db")
            cursor = conn.cursor()

            cursor.execute("DELETE FROM skins WHERE name = ?", (name,))
            if cursor.rowcount > 0:
                print(f"Skin '{name}' deleted!")
            else:
                print(f"Skin '{name}' not found!")

            conn.commit()
            conn.close()

        elif choice == "4":
            list_skins()

        elif choice == "5":
            offered = input("Enter offered items (comma-separated): ").split(",")
            requested = input("Enter requested items (comma-separated): ").split(",")
            result = evaluate_trade([item.strip() for item in offered], [item.strip() for item in requested])
            print(result)

        elif choice == "6":
            file_path = input("Enter the CSV file name: ")
            import_skins_from_csv_with_cleaning(file_path)

        elif choice == "7":
            print("Exiting the program. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
