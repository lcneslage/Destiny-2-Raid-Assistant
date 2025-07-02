import sqlite3
from openai import OpenAI

#this assignment builds off of my project 3 in that it adds crud operations into an sqlite3 database.

#database file.
DB = "your_saved_guides.txt"

#class for Database Operations, contains the CRUD operations that will take place.
class DatabaseOps:
    #initializing constructor for new instance of databaseops
    def __init__(self, db):
        self.db = db
    #create database with the table that will hold gpt's responses.
    def create_db(self):
        try:
            #connecting to sqlite database
            conn = sqlite3.connect(self.db)
            #create cursor object to execute sql commands
            cursor = conn.cursor()
            #sql statements for creating the table that will hold gpt responses. fields in the table include an identifier, raid name, encounter name, request type, and the gpt response.
            cursor.execute('''CREATE TABLE IF NOT EXISTS Responses (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            raid TEXT NOT NULL,
                            encounter TEXT NOT NULL,
                            request_type TEXT NOT NULL,
                            response TEXT NOT NULL)''')
            #commit changes to db
            conn.commit()
            #close connection
            conn.close()
        except sqlite3.Error as error:
            #when an sqlite3 error happens, a related message wil be printed and the program will exit.
            print(f"Error creating database: {error}")
            exit()

    #create entry method for creating entries in the sqlite db, it will need the raid name, raid encounter, request type, and gpt response to populate the fields of the table.
    def create_entry(self, raid: str, encounter: str, request_type: str, response: str):
        #try for error handling
        try:
            #connecting to db
            conn = sqlite3.connect(self.db)
            #create cursor object
            cursor = conn.cursor()
            #sql insert statement to insert the guide information into the database
            cursor.execute('''INSERT INTO Responses (raid, encounter, request_type, response)
                            VALUES (?, ?, ?, ?)''',
                           (raid, encounter, request_type, response))
            #commit changes
            conn.commit()
            #close connection
            conn.close()
            #if all of these things are successful then a success message is printed
            print("Entry saved successfully.")
        except sqlite3.Error as error:
            #if there is a database error then an error message will be printed.
            print(f"Error saving entry: {error}")

    #read entries method for displaying the user's already generated guides.
    def read_entries(self):
        #try for error handling
        try:
            #connecting to db
            conn = sqlite3.connect(self.db)
            #create cursor object
            cursor = conn.cursor()
            #select all columns from responses table
            cursor.execute('''SELECT *
                            FROM Responses''')
            #all of the results of the query are stored as a list called rows
            rows = cursor.fetchall()
            #close connection
            conn.close()
            #if there are no saved guides, (the rows list previously created is empty), then a corresponding error message is printed.
            if not rows:
                print("No saved guides found.")
            else:
                #else, all of the user's previously saved guides are printed.
                print("\n--- Saved Guides ---")
                for row in rows:
                    print("-" * 50)
                    print(f"\nID: {row[0]}\nRaid: {row[1]}\nEncounter: {row[2]}\nType: {row[3]}\nResponse:\n{row[4]}")
                    print("-" * 50)
        except sqlite3.Error as error:
            #if there is a database error then an error message will be printed.
            print(f"Error reading entries: {error}")

    #update entry method so the user can update a previously created guide
    def update_entry(self, entry_id: int, new_response: str):
        #try for error handling
        try:
            #connecting to db
            conn = sqlite3.connect(self.db)
            #create cursor object 
            cursor = conn.cursor()
            #sql statement to select all columns from responses table
            cursor.execute('''SELECT *
                           FROM Responses''')
            #all of the results of the query are stored as a list called rows
            rows = cursor.fetchall()
            #if there are no saved guides, (the rows list previously created is empty), then a corresponding error message is printed.
            if not rows:
                print("No saved entries found.")
                #the db connection is closed
                conn.close()
                #exit the method so an update is not carried out
                return
            #if there is entries to update, then an sql statement to update a response with a user-selected entry_id is executed.
            cursor.execute('''UPDATE Responses
                            SET response = ?
                            WHERE id = ?''',
                           (new_response, entry_id))
            #commit changes to db
            conn.commit()
            #close connection
            conn.close()
            #print message to show that the entry was updated successfully.
            print("Entry updated successfully.")
        except sqlite3.Error as error:
            #if there is a database error then an error message will be printed.
            print(f"Error updating entry: {error}")

    #delete entry method so the user can delete previously created entries.
    def delete_entry(self, entry_id: int):
        #try for error handling
        try:
            #connecting to db
            conn = sqlite3.connect(self.db)
            #create cursor object
            cursor = conn.cursor()
            #sql statement to select all columns from responses table
            cursor.execute('''SELECT *
                           FROM Responses''')
            #all of the results of the query are stored as a list called rows
            rows = cursor.fetchall()
            #if there are no saved guides, (the rows list previously created is empty), then a corresponding error message is printed.
            if not rows:
                print("No saved entries found.")
                #the db connection is closed
                conn.close()
                #exit the method so a deletion is not carried out
                return
            #if there are entries to delete, then an sql statement to delete a response with a user-selected entry_id is executed.
            cursor.execute('''DELETE
                           FROM Responses
                           WHERE id = ?''',
                           (entry_id,))
            #commit changes to db
            conn.commit()
            #close connection
            conn.close()
            #print message to show that the entry was deleted successfully.
            print("Entry deleted successfully.")
        except sqlite3.Error as error:
            #if there is a database error then an error message will be printed.
            print(f"Error deleting entry: {error}")

#raidassistant class for retrieving all of the information that will go into the db, raid name, encounter name, guide/loadout, and the gpt response.
class RaidAssistant:
    #initialization for new instance of raidassistant, contains parameters for api_key and raid_data.
    def __init__(self, api_key, raid_data):
        #try for error handling
        try:
            #create an instance of OpenAI client.
            self.client = OpenAI(api_key=api_key)
        #if there is an error initialzing OpenAI client, then an error message is printed and the program will close.
        except Exception as error:
            #error message
            print(f"Error initializing OpenAI client: {error}")
            #program will exit.
            exit()

        #stores raid_data in self.raids, allowing this instance of RaidAssistant to access the list of raids and encounters that are listed at the end of the program.
        self.RAIDS = raid_data
    #method for getting the gpt response, takes the arguements for raid selected, encounter selected, and the type of request the user made (guide/loadout).
    def get_gpt_response(self, raid: str, encounter: str, request_type: str):
        #try for error handling
        try:
            #gpt prompt, asks gpt the respective request type, for the raid and encounter selected, make sure to ask for meta tactics.
            prompt = f"Give me a detailed {'guide' if request_type == 'guide' else 'loadout recommendation'} for the encounter '{encounter}' in the Destiny 2 raid '{raid}' Please use Reddit and other reputable sources for the most effective tactics available."
            #print to show the user's request type is being generated.
            print(f"\nGenerating your {request_type} — please wait...\n")
            #response object to contain the gpt response.
            response = self.client.chat.completions.create(
                #using gpt-4 model
                model="gpt-4",
                #messages object contains the role, which the role is 'user', and the content of the message is the prompt, which is called as an object called prompt. Essentially saying that the user is sending a prompt containing a message to gpt.
                messages=[{"role": "user", "content": prompt}],
                #for loadouts, allow for more randomness because effective loadouts can wildly vary, so the temperature is adjusted to 0.7.
                #for guides, it is best for the response to be as factual and accurate as possible, so the temperature is adjusted to 0.3.
                temperature=0.7 if request_type == "loadout" else 0.3,
            )
            #return gpt's text response.
            return response.choices[0].message.content
        #if there is an error getting gpt's response,
        except Exception as error:
            #print corresponding error message
            print(f"Error getting GPT response: {error}")
            #return nothing, to prevent the program from crashing.
            return None

    #get raid method to retrieve the user's selected raid.
    def get_raid(self):
        #user will keep being prompted until a valid choice is made.
        while True:
            #try for error handling
            try:
                #print header to ask user which raid they would like to select.
                print("\nWhich raid do you need help with?:")
                #goes through all raid names and assigns a value starting at 1.
                for index, raid_name in enumerate(self.RAIDS.keys(), 1):
                    #prints the list of raids in numerical order.
                    print(f"{index}. {raid_name}")
                #prompts the user to select a raid, they will enter the corresponding number assigned to the raid.
                raid_choice = input("Select a raid: ")
                #try for error handling
                try:
                    #convert the user input from a string to an int
                    raid_choice = int(raid_choice)
                    #choice must be at least 1, and cannot exceed the amount of raids in the list.
                    if 1 <= raid_choice <= len(self.RAIDS):
                        #returns the users selected raid, choice -1 because index starts at 0.
                        return list(self.RAIDS.keys())[raid_choice - 1]
                    else:
                        #if the user's selected number is outside of the valid range of numbers, then print an error message and prompt the user to try again.
                        print("Invalid choice. Try again.")
                #if the user types in something other than a number,
                except ValueError:
                    #print a corresponding error message.
                    print("Please enter a valid number.")
            #if another type of error occurs while selecting a raid,
            except Exception as error:
                #print corresponding error message.
                print(f"Error selecting raid: {error}")

    #get encounter method for getting the user's selected encounter, takes raid_name parameter to retrieve encounter names.
    def get_encounter(self, raid_name):
        #user will keep being prompted until a valid choice is made.
        while True:
            #try for error handling
            try:
                #prompts the user to select an encounter from the provided list.
                print(f"\nChoose an encounter from {raid_name}:")
                #retrieves the encounter names from the selected raid list.
                encounters = self.RAIDS.get(raid_name, [])
                #goes through all the encounter names for the selected raid and assigns a value starting at 1.
                for index, encounter in enumerate(encounters, 1):
                    #prints the encounters.
                    print(f"{index}. {encounter}")
                #prompts the user to select a number that corresponds to the encounter they desire and stores as an object.
                encounter_choice = input("Select an encounter: ")
                #try for error handling
                try:
                    #converts user selected encounter to an int
                    encounter_choice = int(encounter_choice)
                    #choice must be at least 1, and cannot exceed the amount of encounters in the list.
                    if 1 <= encounter_choice <= len(encounters):
                        #if the input is valid then returns the selected encounter -1 because the index starts at 0
                        return encounters[encounter_choice - 1]
                    else:
                        #otherwise prints an error, and the user can try again.
                        print("Invalid choice.")
                #if the user enters something invalid like a string then a corresponding error is printed and the user can try again.
                except ValueError:
                    print("Please enter a valid number.")
            #if another type of error occurs while selecting an encounter then a corresponding error is printed.
            except Exception as error:
                print(f"Error selecting encounter: {error}")

    def get_request_type(self):
        #user will keep being prompted until a valid choice is made.
        while True:
            #try for error handling
            try:
                #prints the text based menu for selecting whether the user wants an encounter guide, or a loadout recommendation
                print("\nWould you like a guide to the mechanics, or a loadout recommendation?")
                print("1. Encounter guide")
                print("2. Loadout recommendation")
                #the user is prompted to select a number, and this is stored as an object.
                request_choice = input("Enter your choice: ")
                if request_choice == "1":
                    return "guide"
                elif request_choice == "2":
                    return "loadout"
                else:
                    #if the user selects a number outside the range, an error message is printed.
                    print("Invalid choice.")
            #if another error selecting the request occurs then an error is displayed.
            except Exception as error:
                print(f"Error selecting request type: {error}")

#menu class for the main menu as well as the managing menu.
class Menu:
    #initialization contstructor for an instance of the menu, create instances of raidassistant and databaseops classes.
    def __init__(self, raid_assistant: RaidAssistant, db_handler: DatabaseOps):
        self.raid_assistant = raid_assistant
        self.db_handler = db_handler

    #manage saved entries method for managing user created entries.
    def manage_saved_entries(self):
        #user will keep being prompted until a valid choice is made.
        while True:
            #try for error handling
            try:
                #prints the text based menu for the crud operations on the user created entries.
                print("\nManage Saved Guides:")
                print("1. View all Guides")
                print("2. Update a Guide")
                print("3. Delete a Guide")
                print("4. Back")
                #user is prompted to choose a number off the list.
                choice = input("Enter your choice: ")
                #if the user chooses 1, then the read function is executed
                if choice == "1":
                    self.db_handler.read_entries()
                #the update entry function is executed, after the entry_id and new response are retrieved
                elif choice == "2":
                    entry_id = int(input("Enter the ID of the guide to update: "))
                    new_response = input("Enter the new response: ")
                    self.db_handler.update_entry(entry_id, new_response)
                elif choice == "3":
                    entry_id = int(input("Enter the ID of the guide to delete: "))
                    self.db_handler.delete_entry(entry_id)
                elif choice == "4":
                    break
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Invalid input. Please enter a valid number.")
            except Exception as error:
                print(f"Error managing saved entries: {error}")
    #starts the text based main menu for the program.
    def start(self):
        while True:
            try:
                print("\nWelcome to the KWTD Assistant, the Destiny 2 Raid Helper!")
                print("1. Get a Guide/Loadout")
                print("2. Manage Saved Entries")
                print("3. Exit")
                choice = input("Enter your choice: ")
                if choice == "1":
                    raid_name = self.raid_assistant.get_raid()  # This should now return the name of the raid
                    if not raid_name:
                        print("Invalid raid selection.")
                        continue
                    encounter = self.raid_assistant.get_encounter(raid_name)  # This should return the encounter name
                    if not encounter:
                        print("Invalid encounter selection.")
                        continue
                    request_type = self.raid_assistant.get_request_type()
                    result = self.raid_assistant.get_gpt_response(raid_name, encounter, request_type)
                    if result:
                        print("\n--- GPT Response ---\n")
                        print(result)
                        save = input("\nWould you like to save this guide? (y/n): ")
                        if save.lower() == "y":
                            self.db_handler.create_entry(raid_name, encounter, request_type, result)
                elif choice == "2":
                    self.manage_saved_entries()
                elif choice == "3":
                    print("Closing the program...")
                    exit()
                else:
                    print("Invalid choice. Please try again.")
            except Exception as error:
                print(f"Error in main menu: {error}")

#getting the api_key from a text file, MAKE SURE THE API KEY IS IN THE SAME FOLDER AS THE PROGRAM
def get_api_key(file_path="api_key.txt"):
    try:
        with open(file_path, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Error: The API key file '{file_path}' was not found.")
        exit(1)
    except Exception as e:
        print(f"Error reading the API key file: {e}")
        exit()

#main function to execute all of the functions.
def main():
    #dictionary of all raids in the Destiny 2 video game (as of 2021, because GPT has no knowledge of newer raids :/ ), with their respective encounters as they are named in the game.
    raid_data = {
        "King's Fall": [
            "Basilica (Totems)", "Boss: Warpriest", "Boss: Golgoroth", "Boss: Daughters of Oryx", "Boss: Oryx, The Taken King"],
        "Vault of Glass": [
            "Defend the Confluxes", "Oracles", "Boss: The Templar", "Gatekeepers", "Boss: Atheon"],
        "Deep Stone Crypt": [
            "Crypt Security", "Boss: Atraks-1", "Descent", "Boss: Taniks, the Abomination"],
        "Garden of Salvation": [
            "Evade the Consecrated Mind", "Summon the Consecrated Mind", "Boss: Consecrated Mind", "Boss: Sanctified Mind"],
        "Last Wish": [
            "Boss: Kalli", "Boss: Shuro Chi", "Boss: Morgeth", "The Vault", "Boss: Riven of a Thousand Voices", "Queenswalk"]
        }
    api_key = get_api_key()
    raid_assistant = RaidAssistant(api_key, raid_data)
    db_handler = DatabaseOps(DB)
    db_handler.create_db()
    menu = Menu(raid_assistant, db_handler)
    menu.start()


if __name__ == "__main__":
    main()
