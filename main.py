from fastapi import FastAPI, HTTPException
from data_loader import load_and_clean_data
from schedule_engine import ScheduleEngine

app = FastAPI(title="NJIT Campus Room Availability API")

# Load data once at startup
df = load_and_clean_data()
engine = ScheduleEngine(df)


# --- Basic health check ---
@app.get("/")
def root():
    return {"status": "API running"}


# --- Room-level queries ---
@app.get("/rooms/status")
def room_status(building: str, room: str, day: str, time: str):
    try:
        return engine.get_room_status(building, room, day, time)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/rooms/weekly_schedule")
def weekly_schedule(building: str, room: str):
    try:
        return engine.get_weekly_schedule(building, room)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/rooms/weekly_grid")
def weekly_schedule(building: str, room: str):
    try:
        return engine.get_weekly_grid(building, room)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Floor-level availability ---
@app.get("/floors/status")
def floor_status(building: str, floor: int, day: str, time: str):
    try:
        return engine.get_floor_availability(building, floor, day, time)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Building analytics ---
@app.get("/analytics/building_occupancy")
def building_occupancy(day: str, time: str):
    try:
        return engine.get_building_occupancy(day, time)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/analytics/building_headcount")
def building_headcount(day: str, time: str):
    try:
        return engine.get_building_headcount(day, time)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Campus discovery endpoints ---
@app.get("/buildings")
def get_buildings():
    return sorted(engine.df["Building"].unique())


@app.get("/buildings/{building}/floors")
def get_floors(building: str):
    floors = engine.df[engine.df["Building"] == building]["Floor"].unique()
    return sorted(floors)


@app.get("/buildings/{building}/floors/{floor}/rooms")
def get_rooms(building: str, floor: int):
    rooms = engine.df[
        (engine.df["Building"] == building) &
        (engine.df["Floor"] == floor)
    ]["RoomNumber"].unique()
    return sorted(rooms)
