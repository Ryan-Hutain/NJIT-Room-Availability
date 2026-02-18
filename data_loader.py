from pathlib import Path
import pandas as pd
import glob

def load_and_clean_data():
    # Folder containing data, relative to this file
    data_dir = Path(__file__).parent / "data" / "Spring 2026 Catalog"
    
    # List CSV files
    all_files = list(data_dir.glob("*.csv"))
    if not all_files:
        raise FileNotFoundError(f"No CSV files found in {data_dir.resolve()}")

    # Concatenate
    catalog = pd.concat(map(pd.read_csv, all_files), ignore_index=True)

    # Drop classes with no location or days
    catalog = catalog.dropna(subset=['Days', 'Times', 'Location'])
    catalog = catalog.drop(columns=['Term', 'Info', 'Max', 'Status', 'Comments'])
    catalog = catalog.rename(columns={'Now': 'Enrolled'})

    # Expand days
    day_map = {'M':'Mon','T':'Tue','W':'Wed','R':'Thu','F':'Fri','S':'Sat'}
    expanded_rows = []

    for _, row in catalog.iterrows():
        for d in list(row['Days']):
            new_row = row.copy()
            new_row['Day'] = day_map[d]
            expanded_rows.append(new_row)

    catalog = pd.DataFrame(expanded_rows)

    # Split times
    catalog[['Start','End']] = catalog['Times'].str.split(' - ', expand=True)
    catalog['Start'] = pd.to_datetime(catalog['Start'], format='%I:%M %p').dt.time
    catalog['End'] = pd.to_datetime(catalog['End'], format='%I:%M %p').dt.time

    # Split location
    catalog[['Building','Room']] = catalog['Location'].str.split(' ', n=1, expand=True)
    catalog = catalog.drop(columns=['Times','Days','Location'])

    # Rearrange columns
    catalog = catalog[['Course', 'Section', 'Title', 'Day', 'Start', 'End', 'Instructor', 'CRN',
                       'Building', 'Room', 'Credits', 'Delivery Mode', 'Enrolled']]

    catalog = catalog.reset_index(drop=True)
    return catalog
