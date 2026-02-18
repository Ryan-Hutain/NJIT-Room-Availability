# NJIT-Room-Availability

## Overview
Pulling an all-nighter and then reaching an absolutely inspired idea is a very dangerous combination. Someone in class this morning threw out the idea of having something to track the availability of open classrooms to use as study spots, and the idea stuck in my head.

This analysis is largely based on the NJIT course catalog to track rooms and class availability. CSVs of the catalog for the current term (Spring 2026) are stored as raw data in the folder sharing that name.

## Current Functionality
This project is still in its sleep-deprived infancy, but after a few hours I have managed to get some basic functionality out of it.

- data_loader: Loads in and cleans up the raw catalog data to make it more useful for eveything else.
- schedule_engine: Handles functionality relating to timeslots and scheduling. Currently can:
  - Tell the availability status of a classroom at a specified query time (get_room_status)
  - Create a weekly schedule of a given room, showing all classes to be held there (get_weekly_schedule)
  - Track the current availability status of all rooms on a given floor (get_floor_availability)
    - Not terribly useful currently, but aims to be a key component in later functionality
  - Make a list of all rooms in a given building which will be vacant during a specified time interval (get_free_rooms)
  - Additionally, can keep track of larger analytics such as building occupancy (by proportion of rooms as well as by student headcount)
- main: Where the magic happens. Draws in the functionality from everywhere else and allows the user to interface with it. Currently only being used to test functionality of the other two.

- Currently setting up an API to potentially start on the front-end of this as well.

## Future Plans
In the future, I hope to make this a more useful tool complete with a GUI, help it become its own little niche applet in time. Ideally, you could navigate from a campus map to a building to a floor, and be able to track real-time occupancy of rooms as well as view structured schedules of specific rooms you may select to track their activity through the week. Class data would also be attached to these schedules, to see which classes exactly may be involved. In a way, this is simply a way to consolidate and visualize the NJIT course catalog in a way more useful to students.

Who knows though. Maybe I've just been up for 36 hours straight and now it's 2 am and when I wake up I'll lose motivation for this. But here's hoping.
