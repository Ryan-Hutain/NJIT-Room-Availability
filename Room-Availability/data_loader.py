import os, glob, pandas as pd

def data_loader():
    # Define dataframe
    catalog = pd.concat(map(pd.read_csv, glob.glob(os.path.join('Room-Availability\data\Spring 2026 Catalog', '*.csv'))))
    catalog = catalog.dropna(subset=['Days', 'Times', 'Location']) # Only classes that meet at a defined room at defined times are to be included
    catalog = catalog.drop(columns=['Term', 'Info', 'Max', 'Status']) # Discarding unneeded columns
    catalog = catalog.rename(columns={'Now': 'Enrolled'})

    # Day processing: make each meeting its own row
    day_map = {
        'M': 'Mon',
        'T': 'Tue',
        'W': 'Wed',
        'R': 'Thu',
        'F': 'Fri',
        'S': 'Sat'
    }

    def expand_days(row):
        days = list(row['Days'])
        rows = []
        for d in days:
            new_row = row.copy()
            new_row['Day'] = day_map[d]
            rows.append(new_row)
        return rows

    expanded_rows = []

    for _, row in catalog.iterrows():
        expanded_rows.extend(expand_days(row))
    catalog = pd.DataFrame(expanded_rows)

    # Convert times into separate start and end
    catalog[['Start', 'End']] = catalog['Times'].str.split(' - ', expand=True)

    catalog['Start'] = pd.to_datetime(catalog['Start'], format='%I:%M %p').dt.time
    catalog['End'] = pd.to_datetime(catalog['End'], format='%I:%M %p').dt.time

    # Separate room numbers into building + room
    catalog[['Building', 'Room']] = catalog['Location'].str.split(' ', n=1, expand=True)
    #print(catalog[catalog['Location'].str.count(' ') != 1]['Location'].unique()) # Lecture halls have a space in room number

    # Delete old columns
    catalog = catalog.drop(columns=['Times', 'Days', 'Location'])

    # Rearranging column order to a way I like better
    catalog = catalog[['Course', 'Section', 'Title', 'Day', 'Start', 'End', 'Instructor', 'CRN', 'Building', 'Room',
                        'Credits', 'Delivery Mode', 'Enrolled', 'Comments']]

    catalog = catalog.reset_index()

    return catalog