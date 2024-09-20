import os
import json
import re
import argparse

def build_database(debug=False):
    # Define the paths to the game files
    state_regions_folder = './input/map_data/state_regions/'
    pops_folder = './input/common/history/pops/'
    history_states_folder = './input/common/history/states/'

    # Create an empty dictionary to hold the entire database
    database = {
        "states": [],
        "pops": []
    }

    # Parse state regions, populations, etc., and add them to the database
    if debug:
        print("Starting to parse state regions...")

    # Example for state regions parsing
    for filename in os.listdir(state_regions_folder):
        if filename.endswith('.txt'):
            if debug:
                print(f"Parsing file: {filename}")

            with open(os.path.join(state_regions_folder, filename), 'r', encoding='utf-8-sig') as file:
                content = file.read()
                
                if debug:
                    print(f"File content (first 200 chars): {content[:200]}")
                
                # Parse the state data (you can reuse the existing parsing logic here)
                # Add parsed data to database['states']
                # This is where you'll include the parse_state_region function
                
                # Example: (replace with actual logic)
                state_info = {"state_name": filename.replace('.txt', ''), "data": content[:100]}  # Placeholder
                database['states'].append(state_info)

    if debug:
        print(f"Total states parsed: {len(database['states'])}")
    
    # Similarly for populations (pops folder)
    if debug:
        print("Starting to parse population data...")

    for filename in os.listdir(pops_folder):
        if filename.endswith('.txt'):
            if debug:
                print(f"Parsing file: {filename}")
            
            with open(os.path.join(pops_folder, filename), 'r', encoding='utf-8-sig') as file:
                content = file.read()
                
                if debug:
                    print(f"File content (first 200 chars): {content[:200]}")
                
                # Parse the population data (you can reuse the existing parsing logic here)
                # Add parsed data to database['pops']
                
                # Example: (replace with actual logic)
                pop_info = {"state_name": filename.replace('.txt', ''), "data": content[:100]}  # Placeholder
                database['pops'].append(pop_info)

    if debug:
        print(f"Total pops parsed: {len(database['pops'])}")

    # Export the data to a JSON file
    with open('./output/database.json', 'w', encoding='utf-8') as json_file:
        json.dump(database, json_file, indent=4)
    
    if debug:
        print("Database successfully built and saved to database.json")
        
def parse_state_region(state_block):
    state_data = {}
    
    # Extract relevant fields using regex
    state_name_match = re.search(r'STATE_(\w+)', state_block)
    state_id_match = re.search(r'id\s*=\s*(\d+)', state_block)
    arable_land_match = re.search(r'arable_land\s*=\s*(\d+)', state_block)
    traits_match = re.search(r'traits\s*=\s*{([^}]+)}', state_block)
    arable_resources_match = re.search(r'arable_resources\s*=\s*{([^}]+)}', state_block)
    capped_resources_match = re.search(r'capped_resources\s*=\s*{([^}]+)}', state_block)

    if state_name_match:
        state_data['state_name'] = state_name_match.group(1)
    if state_id_match:
        state_data['state_id'] = int(state_id_match.group(1))
    if arable_land_match:
        state_data['arable_land'] = int(arable_land_match.group(1))
    if traits_match:
        state_data['traits'] = [trait.strip() for trait in traits_match.group(1).split()]
    if arable_resources_match:
        state_data['arable_resources'] = [res.strip() for res in arable_resources_match.group(1).split()]
    if capped_resources_match:
        capped_resources = {}
        for res in re.findall(r'(\w+)\s*=\s*(\d+)', capped_resources_match.group(1)):
            capped_resources[res[0]] = int(res[1])
        state_data['capped_resources'] = capped_resources

    return state_data

# Define a function to parse state ownership from the 00_states.txt file
def parse_state_ownership(state_block):
    ownership_data = {}
    
    # Extract state name and ownership details
    state_name_match = re.search(r's:STATE_(\w+)', state_block)
    create_state_blocks = re.findall(r'create_state\s*=\s*{[^}]+}', state_block, re.DOTALL)
    homelands = re.findall(r'add_homeland\s*=\s*(cu:\w+)', state_block)

    if state_name_match:
        ownership_data['state_name'] = state_name_match.group(1)
    
    # Extract ownership and provinces for each `create_state` block
    ownership_entries = []
    for create_state_block in create_state_blocks:
        country_match = re.search(r'country\s*=\s*c:(\w+)', create_state_block)
        owned_provinces_match = re.search(r'owned_provinces\s*=\s*{([^}]+)}', create_state_block)

        entry = {}
        if country_match:
            entry['country'] = country_match.group(1)
        if owned_provinces_match:
            entry['owned_provinces'] = [prov.strip() for prov in owned_provinces_match.group(1).split()]
        ownership_entries.append(entry)
    
    ownership_data['ownership'] = ownership_entries
    ownership_data['homelands'] = homelands

    return ownership_data

def parse_population(state_block, debug=False):
    population_data = {}

    state_name_match = re.search(r's:STATE_(\w+)', state_block)
    if state_name_match:
        population_data['state_name'] = state_name_match.group(1)
        if debug:
            print(f"Parsing state: {population_data['state_name']}")

    region_blocks = re.findall(r'region_state:(\w+)\s*=\s*{([^}]*)}', state_block, re.DOTALL)
    
    regions = []
    for region_name, region_content in region_blocks:
        region = {'region_state': region_name}
        pops = []

        if debug:
            print(f"Parsing region state: {region_name}")

        create_pop_blocks = re.findall(r'create_pop\s*=\s*{([^}]*)}', region_content, re.DOTALL)

        for pop_block in create_pop_blocks:
            pop_data = {}
            culture_match = re.search(r'culture\s*=\s*(\w+)', pop_block)
            religion_match = re.search(r'religion\s*=\s*(\w+)', pop_block)
            size_match = re.search(r'size\s*=\s*(\d+)', pop_block)

            if culture_match:
                pop_data['culture'] = culture_match.group(1)
            if religion_match:
                pop_data['religion'] = religion_match.group(1)
            if size_match:
                pop_data['size'] = int(size_match.group(1))

            if debug:
                print(f"Pop: {pop_data}")

            pops.append(pop_data)

        region['pops'] = pops
        regions.append(region)

    population_data['regions'] = regions
    return population_data