import json
import jsonParser as jp
import cv2
import numpy as np


def find_most_similar_hu_moments(reference_hu_moments):
    # Load json-data
    with open('datasheet.json', 'r', encoding='utf-8') as db:
        json_data = json.load(db)

    # Results of jsonParser
    tile_data = jp.get_tile_info(json_data)

    # HuMoments of huMomentsCalculator - Use it for test
    #reference_hu_moments = mc.huMoments_aussen

    # Check for reference HuMoments
    if len(reference_hu_moments) == 0:
        print("No references of HuMoments found in huMomentsCalculator.")
        return

    # Vars for best result
    best_match_value = float('inf')
    best_tile_label = None

    # Iterate for every tile label and compare HuMoments
    for tile in tile_data:
        tile_label = tile["tileLabel"]
        hu_moments = np.array(tile["huMomentsOutlines"])

        if hu_moments is None:
            print(f"No HuMoments found for {tile_label}. Skipping.")
            continue

        match_value = cv2.matchShapes(reference_hu_moments, hu_moments, cv2.CONTOURS_MATCH_I1, 0)

        print(f"TileLabel: {tile_label}, Match Value: {match_value}")

        # Check if best value
        if match_value < best_match_value:
            best_match_value = match_value
            best_tile_label = tile_label


    # Best result
    if best_tile_label is not None:
        print("\n--- Best Match ---")
        print(f"TileLabel: {best_tile_label}")
        print(f"Match Value: {best_match_value}")
    else:
        print("No matching tile found.")

    return best_tile_label

