import pandas as pd

class ScheduleEngine:
    # Import catalog dataframe
    def __init__(self, df):
        self.df = df.copy()
        self._add_floor_column()

    # Helper function to add floor data as column
    def _add_floor_column(self):
        def extract_floor(room):
            # If the room name is a non-empty string and starts with a digit, that is the floor number; otherwise, default to 1
            if isinstance(room, str) and room and room[0].isdigit():
                return int(room[0])
            return 1
        
        self.df.insert(10, 'Floor', self.df['Room'].apply(extract_floor))
    
    # Given a query time in a specific room, check if there is a class in that room during that time
    def get_room_status(self, building, room, day, time_str):
        query_time = pd.to_datetime(time_str, format='%H:%M').time()

        # Check if query time is in the right place during meeting time
        matches = self.df[
            (self.df['Day'] == day) &
            (self.df['Building'] == building) &
            (self.df['Room'] == room) &
            (self.df['Start'] <= query_time) &
            (self.df['End'] > query_time)
        ]
        
        if matches.empty: # If no class matches description, then will return empty; room is available during query time
            return {'Available': True}
        else: # Otherwise, will return with a populated dataframe row for the class that occupies that slot
            row = matches.iloc[0]

            # If room shared by multiple sections at a given time, include all
            if len(matches) == 1:
                section = row['Section']
            else:
                section = '/'.join(matches['Section'])
            
            return {
                'Available': False,
                'Course': row['Course'],
                'Section': section
            }
    
    # Given a room, obtain the classes which are held in it, in chronological order
    def get_weekly_schedule(self, building, room):
        week_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        self.df['Day'] = pd.Categorical(self.df['Day'], categories=week_order, ordered=True)

        return self.df[
            (self.df['Building'] == building) &
            (self.df['Room'] == room)
        ].sort_values(['Day', 'Start']).to_dict(orient="records")

    
    # Similar to schedule, but more API-friendly
    def get_weekly_grid(self, building, room):
        df_room = self.df[
            (self.df["Building"] == building) &
            (self.df["Room"] == room)
        ].copy()

        week_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
        df_room['Day'] = pd.Categorical(df_room['Day'], categories=week_order, ordered=True)

        df_room = df_room.sort_values(["Day", "Start"])

        schedule = {day: [] for day in week_order}

        # Group by matching time blocks
        grouped = df_room.groupby(["Day", "Start", "End"])

        for (day, start, end), group in grouped:
            sections = "/".join(str(s) for s in group["Section"].tolist())

            schedule[day].append({
                "start": start,
                "end": end,
                "course": group["Course"].iloc[0],
                "section": sections,
                "title": group["Title"].iloc[0],
                "instructor": group["Instructor"].iloc[0]
            })

        return schedule


    
    # Get availability of all rooms on a given floor at a given time
    def get_floor_availability(self, building, floor, day, time_str):
        query_time = pd.to_datetime(time_str, format='%H:%M').time()

        # Given floor in building, get array of rooms on that floor
        floor_rooms = self.df[
            (self.df['Building'] == building) &
            (self.df['Floor'] == floor)
        ]

        # Create dictionary: keys are rooms, values are availability status
        results = {}

        for room in floor_rooms['Room'].unique():
            occupied = floor_rooms[
                (floor_rooms['Room'] == room) &
                (floor_rooms['Day'] == day) &
                (floor_rooms['Start'] <= query_time) &
                (floor_rooms['End'] > query_time)
            ]

            results[room] = occupied.empty

        return results
    
    # Get list of all free rooms in a building during a given time interval
    def get_free_rooms(self, building, day, start, end):
        requested_start = pd.to_datetime(start, format='%H:%M').time()
        requested_end = pd.to_datetime(end, format='%H:%M').time()

        # Narrow to building and day
        building_df = self.df[
            (self.df['Building'] == building) &
            (self.df['Day'] == day)
        ]

        # Get all rooms in the building (even if no class scheduled)
        all_rooms = self.df[self.df['Building'] == building]['Room'].unique()

        free_rooms = []

        for room in all_rooms:
            room_classes = building_df[building_df['Room'] == room]

            # Check if any class overlaps
            overlap = room_classes[
                (room_classes['Start'] < requested_end) &
                (room_classes['End'] > requested_start)
            ]

            if overlap.empty:
                free_rooms.append(room)

        return sorted(free_rooms)


    # Analytics

    # Get proportion of rooms occupied in each building at any given time
    def get_building_occupancy(self, day, time_str):
        query_time = pd.to_datetime(time_str, format="%H:%M").time()

        results = {}

        for building in self.df["Building"].unique():

            building_df = self.df[self.df["Building"] == building]

            total_rooms = building_df["Room"].nunique()

            occupied_rooms = building_df[
                (building_df["Day"] == day) &
                (building_df["Start"] <= query_time) &
                (building_df["End"] > query_time)
            ]["Room"].nunique()

            proportion = occupied_rooms / total_rooms if total_rooms > 0 else 0

            results[building] = {
                "occupied_rooms": occupied_rooms,
                "total_rooms": total_rooms,
                "proportion_occupied": round(proportion, 3)
            }

        return results

    def get_building_headcount(self, day, time_str):
        query_time = pd.to_datetime(time_str, format="%H:%M").time()

        active = self.df[
            (self.df["Day"] == day) &
            (self.df["Start"] <= query_time) &
            (self.df["End"] > query_time)
        ]

        # Aggregate per room-time
        active_grouped = (
            active
            .groupby(["Building", "Room", "Day", "Start", "End"], as_index=False)
            ["Enrolled"]
            .sum()
        )

        headcount = (
            active_grouped
            .groupby("Building")["Enrolled"]
            .sum()
            .sort_values(ascending=False)
            .to_dict()
        )

        return headcount
