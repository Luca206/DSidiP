import json

# Find all values of specific key
def find_values_by_key(data, target_key):
    found_values = []

    if isinstance(data, dict):
        # Iterate through all key-value pairs in dictionary
        for key, value in data.items():
            if key == target_key:
                found_values.append(value)
            else:
                found_values.extend(find_values_by_key(value, target_key))

    elif isinstance(data, list):
        # Iterate through list and check elements
        for item in data:
            found_values.extend(find_values_by_key(item, target_key))

    return found_values

def process_item(item):
    results = []
    has_cutouts = False

    if isinstance(item, dict):
        tile_label = item.get("tileLabel", None)
        characteristics = item.get("characteristics", {})

        if tile_label is not None:
            # Check for numberCutouts in characteristics
            number_cutouts = characteristics.get("numberCutouts", 0)
            if number_cutouts is not None:
                has_cutouts = number_cutouts > 0

            hu_moments_outlines = characteristics.get("huMomentsOutlines", None)

            # Save result
            results.append(
                {"tileLabel": tile_label, "has_cutouts": has_cutouts, "huMomentsOutlines": hu_moments_outlines})

        for value in item.values():
            results.append(process_item(value))

    elif isinstance(item, list):
        for sub_item in item:
            results.append(process_item(sub_item))
    return results

# Check for cutouts
def get_tile_info(data):

    # Iterate through structure
    results = process_item(data)
    return results


# Load json-data
with open('datasheet.json', 'r', encoding='utf-8') as db:
    json_data = json.load(db)



#Obsolete code for test methods


## Find all values for tileLabel
# key_to_find = "tileLabel"
# values = find_values_by_key(data, key_to_find)
#
# print({key_to_find})
# for value in values:
#    print(value)

# Check cutouts for all tileLabels
tile_info_results = get_tile_info(json_data)

# print("Result for every tileLabel:")
# for result in tile_info_results:
#    print(
#        f"TileLabel: {result['tileLabel']}, Has Cutouts: {result['has_cutouts']}, HuMomentsOutlines: {result['huMomentsOutlines']}")

# print("test")
# for result in tile_info_results:
#    print(f"{result['huMomentsOutlines']}")
