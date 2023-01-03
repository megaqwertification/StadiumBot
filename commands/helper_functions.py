def filter_btt_tags(tags_list: list, cur) -> list:
    '''
    Filter tags

    Riddle if the riddle run is not a complete....how to do this?

    '''

    # Pre-processing for queried SuS tags
    filtered_list = list(cur)
    
    if tags_list:
        filtered_list = [record for record in filtered_list if set(tags_list).issubset(record[9])]

    if '1T' not in tags_list:
        filtered_list = [record for record in filtered_list if not set(['1T']).issubset(record[9])]
    if 'misfire' not in tags_list: # or 'misfire' not in tags_list or 'AR' not in tags_list:
        filtered_list = [record for record in filtered_list if not set(['misfire']).issubset(record[9])]
    if 'AR' not in tags_list:
        filtered_list = [record for record in filtered_list if not set(['AR']).issubset(record[9])]
    # more temporary filtering, probably a more efficient way to do things
    if 'LSS' not in tags_list:
        filtered_list = [record for record in filtered_list if not set(['LSS']).issubset(record[9])]
    if 'BSS' not in tags_list:
        filtered_list = [record for record in filtered_list if not set(['BSS']).issubset(record[9])]
    if 'RSS' not in tags_list:
        filtered_list = [record for record in filtered_list if not set(['RSS']).issubset(record[9])]
    if 'TSS' not in tags_list:
        filtered_list = [record for record in filtered_list if not set(['TSS']).issubset(record[9])]

    return filtered_list