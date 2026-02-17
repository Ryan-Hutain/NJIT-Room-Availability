# Load functionality from other files in project
from data_loader import data_loader
from schedule_engine import ScheduleEngine

catalog = data_loader()
engine = ScheduleEngine(catalog)


# Quick functionality tests

# Moment query
building = "COLT"
room = "416"
day = "Wed"
time = "11:00"

status = engine.get_room_status(building, room, day, time)
print(f"Room {building}{room} availability at {time} on {day}: {status}")
print('\n')


# Floor-based query
floor = 4
floor_status = engine.get_floor_availability(building, floor, day, time)
print(f"{building} floor {floor} availability at {time} on {day}:")
for r, available in floor_status.items():
    print(f"  {r}: {'Free' if available else 'Occupied'}")
print('\n')


# Check if room is free during interval
start_time = "13:00"
end_time = "14:00"

free_rooms = engine.get_free_rooms(building, day, start_time, end_time)
print(f"Rooms free in {building} on {day} from {start_time}-{end_time}: {free_rooms}")
print('\n')


# Make weekly overview of given room
weekly_schedule = engine.get_weekly_schedule(building, room)
print(f"Weekly schedule for room {building}{room}:")
print(weekly_schedule)
print('\n')

weekly_grid = engine.get_weekly_grid(building, room)
print(f"Weekly schedule for room {building}{room}:")
print(weekly_grid)
print('\n')

# Get building occupancy at time
print(engine.get_building_occupancy(day, time))
print(engine.get_building_headcount(day, time))