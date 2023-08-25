### This version build for the rules of this link: https://docs.google.com/document/d/10JWH6CJ1xgJgj0hK2378y0Y_Oqe1JMvvaRbMOnvy_bA/edit?usp=sharing
import random
import yaml
import sys
import curses
import math
COLORAMA_AVAILABLE = True
try:
    from colorama import init, Fore
except ModuleNotFoundError:
    COLORAMA_AVAILABLE = False

global show_bonuses_penalties_state
show_bonuses_penalties_state = True
def roll_dice_pool(dice_pool, ten_again=True, nine_again=False, eight_again=False):
    successes = 0
    rolls = []
    while dice_pool > 0:
        roll = random.randint(1, 10)
        rolls.append(roll)
        
        # Count successes
        if roll >= 8:
            successes += 1
            
        # Handle 10-again rule (almost always in effect)
        if ten_again and roll == 10:
            dice_pool += 1
            
        # Handle 9-again rule
        elif nine_again and roll >= 9:
            dice_pool += 1
            
        # Handle 8-again rule
        elif eight_again and roll >= 8:
            dice_pool += 1
        
        # Reduce dice pool for the next iteration
        dice_pool -= 1
    
    return successes, rolls

def create_awakened_item(config=None):
    if config is None:
        config = {}

    # Gather necessary inputs
    show_bonuses_penalties_state = get_bool(config, 'show_bonuses_penalties_state', "") #This should never prompt the user 
    gnosis = get_int(config, 'gnosis', "Enter the mage's Gnosis: ")
    mage_arcana = get_int(config, 'mage_arcana', "Enter the Arcana level of the mage: ")
    highest_crafting_arcana = get_int(config, 'highest_crafting_arcana', "Enter the items's highest Arcana level: ")
    total_spell_dots = get_int(config, 'total_spell_dots', "Enter the total dots required to cast this spell: ")
    yantras = get_int(config, 'yantras', "Enter the total bonus from item Yantras(including chanting)): ")
    places_of_power = get_int(config, 'places_of_power', "Enter the bonus from Places of Power: ")
    supporting_crafters = get_int(config, 'supporting_crafters', "Enter the bonus from Supporting Crafters: ")
    supporting_apprentices = get_int(config, 'supporting_apprentices', "Enter the bonus from Supporting Apprentices: ")

    primary_factor = get_multiple_choice(config, 'primary_factor', "What is the Primary Factor? (a Potency/b Duration): ", ['a', 'b'])
    
    is_persistent = get_bool(config, 'is_persistent', "is the item Persistent? (yes/no): ")
    duration_penalty = 0
    is_duration_extra_reach = True
    if config.get('duration_penalty') is not None:
        duration_penalty = abs(int(config.get('duration_penalty')))
    elif not is_persistent:
        user_input = input("what is the dice penalty for duration if any (ie: -4) or type 'help' for assistance: ")
        if user_input in ["help", "Help"]:
            is_duration_extra_reach = get_bool(config, 'is_duration_extra_reach', "Did you reach for Advanced Duration? (yes/no): ")
            duration_penalty = calc_duration_penalty(primary_factor, is_persistent, mage_arcana, is_duration_extra_reach, config)
        else:
            duration_penalty = abs(int(user_input))
    else:
        print("persistent")
        user_input = input("what is the dice penalty for duration if any (ie: -4) or type 'help' for assistance: ")
        if user_input in ["help", "Help"]:
            is_duration_extra_reach = get_bool(config, 'is_duration_extra_reach', "Did you reach for Advanced Duration? (yes/no): ")
            duration_penalty = calc_duration_penalty(primary_factor, is_persistent, mage_arcana, is_duration_extra_reach, config)
        else:
            duration_penalty = abs(int(user_input))
        

    extra_reaches = get_int(config, 'extra_reaches', "Enter How many total reaches above the free reaches where used? Include all reaches including duration because this is not auto calculated: ")
    mana_battery = get_int(config, 'mana_battery', "How many mana beyond the default 1 will it hold? (even numbers only): ")
    prior_craftings = get_int(config, 'prior_craftings', "How many total arcana have been put into item on prior craftings? ")
    is_praxis = get_bool(config, 'is_praxis', "Is the spell a Praxis? (yes/no): ")
    is_perfected = get_bool(config, 'is_perfected', "Is the material an appropriate perfected material? (yes/no): ")
    potency = get_int(config, 'potency', "Enter the potency of the spell: ")
    is_sympathetic = get_bool(config, 'is_sympathetic', "Is it a sympathetic range? (yes/no): ")
    is_temporal_sympathy = get_bool(config, 'is_temporal_sympathy', "Is it a temporal sympathy? (yes/no): ")
    is_advanced_scale = get_bool(config, 'is_advanced_scale', "Did you reach for Advanced Scale? (yes/no): ")
    is_willpower = get_bool(config, 'is_willpower', "Did you spend a willpower? (yes/no): ")
    is_double_time = get_bool(config, 'is_double_time', "Did you spend double time? (yes/no): ")

    # Calculate total dice pool and required successes
    gnosis = math.ceil(gnosis / 2) #1/2 gnosis rounded up.
    potency_penalty = calc_potency_successes(primary_factor, potency, mage_arcana)
    scale_penalty = 0
    if config.get('scale_penalty') is None:
        user_input = input("what is the dice penalty for scale if any (ie: -4) or type 'help' for assistance: ")
        if user_input in ["help", "Help"]:
            scale_penalty = int(curses.wrapper(choose_scale_index, is_advanced_scale) if scale_penalty is not None else scale_penalty)
            scale_penalty = max(scale_penalty, 0) *2
        else:
            scale_penalty = abs(int(user_input))
    perfected_bonus = bool(is_perfected)
    will_successes = roll_willpower(is_willpower, perfected_bonus)
    
    end_bonus = (places_of_power +
                 supporting_crafters +
                 supporting_apprentices +
                 yantras +
                 int(is_praxis)+
                 will_successes)

    required_successes = (potency_penalty +
                          duration_penalty +
                          scale_penalty +
                          extra_reaches * 2 +
                          int(mana_battery/2) +
                          prior_craftings +
                          highest_crafting_arcana +
                          int(is_sympathetic) +
                          int(is_temporal_sympathy)+
                          int(is_persistent)+
                          scale_penalty
                          )
    
    show_bonuses_penalties(potency_penalty, duration_penalty, scale_penalty, extra_reaches, mana_battery, prior_craftings, highest_crafting_arcana, is_sympathetic, is_temporal_sympathy, is_persistent, places_of_power, supporting_crafters, supporting_apprentices, yantras, is_praxis, will_successes)
    
    dice_pool = gnosis + mage_arcana
    
    perform_creation_roll(gnosis, mage_arcana, dice_pool, required_successes, end_bonus, is_double_time, perfected_bonus, total_spell_dots, is_persistent)

def show_bonuses_penalties(potency_penalty, duration_penalty, scale_penalty, extra_reaches, mana_battery, prior_craftings, highest_crafting_arcana, is_sympathetic, is_temporal_sympathy, is_persistent, places_of_power, supporting_crafters, supporting_apprentices, yantras, is_praxis, will_successes):
    if not show_bonuses_penalties_state:
        return

    print("\nplaces_of_power: " + str(places_of_power))
    print("supporting_crafters: " + str(supporting_crafters))
    print("supporting_apprentices: " + str(supporting_apprentices))
    print("yantras: " + str(yantras))
    print("is_praxis: " + str(int(is_praxis)))
    print("is_willpower: " + str(will_successes))
    print("End Bonuses")

    print("\npotency_penalty: " + str(potency_penalty))
    print("duration_penalty: " + str(duration_penalty))
    print("scale_penalty: " + str(scale_penalty))
    print("extra_reaches: " + str(extra_reaches * 2))
    print("mana_battery: " + str(int(mana_battery/2)))
    print("prior_craftings: " + str(prior_craftings))
    print("highest_crafting_arcana: " + str(highest_crafting_arcana))
    print("is_sympathetic: " + str(int(is_sympathetic)))
    print("is_temporal_sympathy: " + str(int(is_temporal_sympathy)))
    print("is_persistent: " + str(int(is_persistent)))
    print("scale_penalty: " + str(scale_penalty))
    print("End Penalties")

def perform_creation_roll(gnosis, mage_arcana, dice_pool, required_successes, end_bonus, is_double_time, perfected_bonus, total_spell_dots, is_persistent=False):
    # Inform the user about the goal
    print(f"\nGoal: Achieve {required_successes} successes.")

    # Rolling process
    total_successes = 0

    # Track all rolls for reporting
    all_rolls = []
    number_of_actual_rolls = 0

    for i in range(gnosis + mage_arcana):
        if (total_successes + end_bonus) < required_successes:
            if is_double_time:
                number_of_actual_rolls += 1
            successes, rolls = roll_dice_pool(dice_pool, nine_again=perfected_bonus)
            all_rolls.extend(rolls) 
            if is_double_time:
                total_successes += successes + 1
                print(f"Roll {i+1}: {rolls} => {successes} successes plus 1 for double time")
            else:
                total_successes += successes
                print(f"Roll {i+1}: {rolls} => {successes} successes")

    # Final results
    print(f"\nEnd Bonus successes: {end_bonus}")
    print(f"Rolled successes: {total_successes}")
    print(f"Total successes: {(total_successes + end_bonus)}")

    if (total_successes + end_bonus) >= required_successes:
        print((Fore.GREEN if COLORAMA_AVAILABLE else "") + "\nItem creation successful!")
        print_required_manacosts(total_spell_dots, is_persistent)
        roll_for_free_release(perfected_bonus)
    else:
        print((Fore.RED if COLORAMA_AVAILABLE else "") + "Item creation failed!")

def print_required_manacosts(total_spell_dots, is_persistent):
    total_mana = total_spell_dots + int(is_persistent)
    print(f"Total required mana: {total_mana}")
    
def roll_for_free_release(perfected_bonus):
    successes, rolls = roll_dice_pool(3, nine_again=perfected_bonus)
    [].extend(rolls)
    print("\nRolling for Free Release Chance!")
    print(f"Roll for Free Release: {rolls} => {successes} successes")
    if successes >= 2:
            print((Fore.GREEN if COLORAMA_AVAILABLE else "") + "Lucky! Item has released for free!")
    else:
            print((Fore.RED if COLORAMA_AVAILABLE else "") + "Unlucky! Item will cost to release.")

def roll_willpower(is_willpower, perfected_bonus):
    will_successes = 0
    if is_willpower: 
        will_successes, rolls = roll_dice_pool(3, nine_again=perfected_bonus)
        [].extend(rolls)
        if COLORAMA_AVAILABLE:
            final_color = Fore.GREEN if will_successes >= 1 else Fore.RED
            print(final_color + f"Roll Willpower: {rolls} => {will_successes} willpower successes")
        else:
            print(f"Roll Willpower: {rolls} => {will_successes} willpower successes")
    return will_successes

# (a Potency/b Duration)
def calc_potency_successes(primary_factor, potency, mage_arcana):
    additional_potency_successes = 0
    if primary_factor == "a":
        additional_potency_successes = max((potency-mage_arcana)*2, 0) #potency successes never below 0
    else:
        additional_potency_successes = max((potency-1)*2, 0)
    return additional_potency_successes

def calc_duration_penalty(primary_factor, is_persistent, mage_arcana, is_duration_extra_reach, config):
    print("calc_duration_penalty")
    duration_penalty = 0

    if is_persistent and is_duration_extra_reach and primary_factor:
        duration_penalty = max((6 - mage_arcana), 0) * 2
        return duration_penalty
    elif is_persistent and not is_duration_extra_reach:
        exit_with_error("Bad Request - If item is persistant, then you must use the advanced duration chart.")
    else:
        duration_penalty += curses.wrapper(choose_duration_index, mage_arcana, is_duration_extra_reach)
        print("duration penalty")
        print(duration_penalty)

    duration_penalty = max((duration_penalty - mage_arcana), 0) * 2

    return duration_penalty

def choose_duration_index(stdscr, mage_arcana, is_duration_extra_reach):
    curses.curs_set(0)  # Hide cursor
    stdscr.keypad(1)   # Enable special keys
    
    options = generate_standard_duration_array(mage_arcana) if not is_duration_extra_reach else generate_advanced_duration_array(mage_arcana)

    index = 0
    top_line = 0  # This will track the top line currently being displayed

    while True:
        stdscr.clear()
        
        height = curses.LINES  # Get the height of the terminal
        
        # Loop to print only the lines that fit on the screen
        for i in range(top_line, min(top_line + height, len(options))):
            # Adjust line to start from 0
            line = i - top_line

            if i == index:
                stdscr.addstr(line, 0, options[i], curses.A_REVERSE)
            else:
                stdscr.addstr(line, 0, options[i])

        key = stdscr.getch()

        if key == curses.KEY_DOWN:
            if index + 1 < len(options) or not is_duration_extra_reach:
                index += 1

            # Scroll down when the selected line goes off the bottom
            if index - top_line >= height:
                top_line += 1

            if index == len(options) and not is_duration_extra_reach:
                # Calculate the new option based on the last option
                turns = int(options[-1].split()[0]) + 10
                dice = int(options[-1].split()[-2].replace("(", "")) - 2
                new_option = f"{turns} turns ({dice} dice)"
                options.append(new_option)

        elif key == curses.KEY_UP and index > 0:
            index -= 1
            
            # Scroll up when the selected line goes off the top
            if index < top_line:
                top_line -= 1

        elif key == curses.KEY_ENTER or key in [10, 13]:
            return index + 1

def generate_standard_duration_array(number):
    # Define the initial pattern for turns
    turns_pattern = list(range(1, number + 1)) + list(range(number + 10, number * 10 + 10, 10))
    
    # Construct the array
    array = []
    dice_penalty = 0
    for turns in turns_pattern:
        # Add the dice penalty only after reaching the given number
        if turns > number:
            dice_penalty += 2
        array.append(f"{turns} turn{'s' if turns > 1 else ''} (-{dice_penalty} dice)")
    
    return array

def generate_advanced_duration_array(number):
    # Define the time frames and penalties
    time_frames = ["scene/hour", "day", "week", "month", "year", "Indefinite"]
    
    # Start with 0 dice penalty for the specified number of time frames
    dice_penalties = [0] * number + list(range(2, (len(time_frames) - number + 1) * 2, 2))
    
    # Construct the array
    array = []
    for time_frame, dice_penalty in zip(time_frames, dice_penalties):
        if time_frame == "Indefinite":
            array.append(f"{time_frame} (-{dice_penalty} dice)")
        else:
            array.append(f"1 {time_frame} (-{dice_penalty} dice)")
    
    return array

def generate_scale_table_display(table):
    """Generates the display for each row of the table"""
    display = []
    for row in table:
        display.append(
            f"Subjects: {row['Number of Subjects']}, Size: {row['Size of Largest Subject']}, "
            f"Area: {row['Area of Effect'] or 'N/A'}, Penalty: {row['Dice Penalty']}"
        )
    return display

def extend_table(table):
    """Generates the next line based on the table's pattern"""
    last_row = table[-1]
    new_subjects = last_row['Number of Subjects'] * 2
    new_size = last_row['Size of Largest Subject'] + 1
    new_penalty = last_row['Dice Penalty'] - 2

    new_row = {
        'Number of Subjects': new_subjects,
        'Size of Largest Subject': new_size,
        'Area of Effect': 'A ballroom or small house',
        'Dice Penalty': new_penalty
    }

    table.append(new_row)
    
def extend_advanced_table(table):
    """Generates the next line based on the table's pattern for advanced version"""
    last_row = table[-1]
    new_subjects = last_row['Number of Subjects'] * 2
    new_size = last_row['Size of Largest Subject'] + 5
    new_penalty = last_row['Dice Penalty'] - 2

    new_row = {
        'Number of Subjects': new_subjects,
        'Size of Largest Subject': new_size,
        'Area of Effect': 'A campus, or a small neighborhood',
        'Dice Penalty': new_penalty
    }

    table.append(new_row)

def choose_scale_index(stdscr, is_advanced_scale):
    # Hide cursor and enable special keys
    curses.curs_set(0)
    stdscr.keypad(1)

    # Define and extend the table
    normtable = [
        {"Number of Subjects": 1, "Size of Largest Subject": 5, "Area of Effect": "Arm’s reach from a central point", "Dice Penalty": 0},
        {"Number of Subjects": 2, "Size of Largest Subject": 6, "Area of Effect": "A small room", "Dice Penalty": -2},
        {"Number of Subjects": 4, "Size of Largest Subject": 7, "Area of Effect": "A large room", "Dice Penalty": -4},
        {"Number of Subjects": 8, "Size of Largest Subject": 8, "Area of Effect": "Several rooms, or a single floor of a house", "Dice Penalty": -6},
        {"Number of Subjects": 16, "Size of Largest Subject": 9, "Area of Effect": "A ballroom or small house", "Dice Penalty": -8},
        {"Number of Subjects": 32, "Size of Largest Subject": 10, "Area of Effect": "A ballroom or small house", "Dice Penalty": -10},
        {"Number of Subjects": 64, "Size of Largest Subject": 11, "Area of Effect": "A ballroom or small house", "Dice Penalty": -12},
        {"Number of Subjects": 128, "Size of Largest Subject": 12, "Area of Effect": "A ballroom or small house", "Dice Penalty": -14},
        {"Number of Subjects": 256, "Size of Largest Subject": 13, "Area of Effect": "A ballroom or small house", "Dice Penalty": -16}
    ]
    advtable = [
        {'Number of Subjects': 'Five', 'Size of Largest Subject': 5, 'Area of Effect': 'A large house or building', 'Dice Penalty': 0},
        {'Number of Subjects': 10, 'Size of Largest Subject': 10, 'Area of Effect': 'A small warehouse or parking lot', 'Dice Penalty': -2},
        {'Number of Subjects': 20, 'Size of Largest Subject': 15, 'Area of Effect': 'A large warehouse or supermarket', 'Dice Penalty': -4},
        {'Number of Subjects': 40, 'Size of Largest Subject': 20, 'Area of Effect': 'A small factory, or a shopping mall', 'Dice Penalty': -6},
        {'Number of Subjects': 80, 'Size of Largest Subject': 25, 'Area of Effect': 'A large factory, or a city block', 'Dice Penalty': -8},
        {'Number of Subjects': 160, 'Size of Largest Subject': 30, 'Area of Effect': 'A campus, or a small neighborhood', 'Dice Penalty': -10},
        {'Number of Subjects': 320, 'Size of Largest Subject': 35, 'Area of Effect': 'A campus, or a small neighborhood', 'Dice Penalty': -12},
        {'Number of Subjects': 640, 'Size of Largest Subject': 40, 'Area of Effect': 'A campus, or a small neighborhood', 'Dice Penalty': -14},
        {'Number of Subjects': 1280, 'Size of Largest Subject': 45, 'Area of Effect': 'A campus, or a small neighborhood', 'Dice Penalty': -16},
    ]
    
    table = advtable if is_advanced_scale else normtable
    
    options = generate_scale_table_display(table)

    index = 0
    top_line = 0  # Track the top line being displayed

    while True:
        stdscr.clear()

        height = curses.LINES  # Get the height of the terminal

        # Loop to print only the lines that fit on the screen
        for i in range(top_line, min(top_line + height, len(options))):
            # Adjust line to start from 0
            line = i - top_line

            if i == index:
                stdscr.addstr(line, 0, options[i], curses.A_REVERSE)
            else:
                stdscr.addstr(line, 0, options[i])

        key = stdscr.getch()

        if key == curses.KEY_DOWN:
            if index + 1 < len(options):
                index += 1
                # Scroll down when the selected line goes off the bottom
                if index - top_line >= height:
                    top_line += 1
            else:
                # Generate a new line based on the table's pattern and extend options
                extend_table(table)
                options = generate_scale_table_display(table)
                index += 1

        elif key == curses.KEY_UP and index > 0:
            index -= 1
            # Scroll up when the selected line goes off the top
            if index < top_line:
                top_line -= 1

        elif key == curses.KEY_ENTER or key in [10, 13]:
            return index

def get_int(config, key, prompt):
    while True:
        if config.get(key) is not None:
            value = config.get(key)
            return value
        else:
            value = input(prompt)
        try:
            value = int(value)
            return value
        except ValueError:
            print("Error: Please enter a valid integer.")

def get_multiple_choice(config, config_key, prompt, choices):
    while True:
        if config.get(config_key):
            result = config.get(config_key)
        else:
            result = input(prompt)

        if result in choices:
            return result
        else:
            print(f"Error: Please enter one of {', '.join(choices)}.")

def get_bool(config, config_key, prompt):
    while True:
        result = config.get(config_key)  # Try to get the value from the config
        
        if config_key == 'show_bonuses_penalties_state' and result is None:
            return show_bonuses_penalties_state
        
        # Check if result is already a boolean
        if isinstance(result, bool):
            return result
        
        # If result is None or empty or any other falsy value
        if not result:  
            result = input(prompt).lower()  # Prompt the user for input
        
        if result == 'yes':
            return True
        elif result == 'no':
            return False
        else:
            print(f"Error for {config_key}: Please enter either 'yes' or 'no'.")
            if config_key in config:
                del config[config_key]  # Remove the invalid entry so we can prompt again

def read_yaml_config(file_path):
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data

def exit_with_error(message, code=400):
    print(f"Error {code}: {message}")
    sys.exit(code)

def main():
    if COLORAMA_AVAILABLE:
        init(autoreset=True)  # initializes colorama and autoresets color to default after each print

    # Check for command line argument
    if len(sys.argv) > 1 and sys.argv[1] in ["file", "manual"]:
        choice = sys.argv[1]
    else:
        choice = input("Do you want to provide manual input or use a configuration file? (manual/file): ")

    if choice == "manual":
        create_awakened_item()
    elif choice == "file":
        if len(sys.argv) > 2:  # Check if a filename was provided as the next argument
            file_path = sys.argv[2]
        else:
            file_path = input("Please enter the configuration file name (default is itemconfig.yaml(enter)): ") or "./itemconfig.yaml"
        config = read_yaml_config(file_path)
        create_awakened_item(config)
    else:
        print("Invalid choice. Exiting.")

if __name__ == "__main__":
    main()


