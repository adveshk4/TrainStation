from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import json
import os

app = FastAPI()

trains_db: Dict[str, Dict] = {}
stations_db: Dict[str, Dict] = {}

TRAINS_FILE = "trains.json"
STATIONS_FILE = "stations.json"

if os.path.exists(TRAINS_FILE):
    with open(TRAINS_FILE) as f:
        trains_db = json.load(f)
    print("trains.json loaded:", len(trains_db), "trains")
else:
    print("trains.json not found")

if os.path.exists(STATIONS_FILE):
    with open(STATIONS_FILE) as f:
        stations_db = json.load(f)
    print("stations.json loaded:", len(stations_db), "stations")
else:
    print("stations.json not found")

class TrainSchedule(BaseModel):
    train_id: str
    arrival: str
    departure: str
    days: List[str]

@app.get("/")
def root():
    return {"message": "API is working"}

@app.get("/stations")
def get_all_stations():
    return list(stations_db.keys())

@app.get("/stations/{station_name}")
def get_station_schedule(station_name: str):
    if station_name not in stations_db:
        raise HTTPException(status_code=404, detail="Station not found")
    return stations_db[station_name]

@app.post("/stations/{station_name}")
def add_or_update_station_schedule(station_name: str, schedule: TrainSchedule):
    if station_name not in stations_db:
        stations_db[station_name] = {}
    stations_db[station_name][schedule.train_id] = {
        "arrival": schedule.arrival,
        "deprature": schedule.departure,
        "days": schedule.days
    }
    return {"message": "Schedule updated", "schedule": schedule}

@app.get("/trains")
def get_all_trains():
    return [{"train_id": train_id, "stations": list(data.keys())} for train_id, data in trains_db.items()]

@app.get("/trains/{train_id}")
def get_train_schedule(train_id: str):
    if train_id not in trains_db:
        raise HTTPException(status_code=404, detail="Train not found")
    return trains_db[train_id]

@app.post("/trains")
def add_train_schedule(train: Dict[str, Dict]):
    train_id = train.get("train_id")
    schedule = train.get("schedule")
    if not train_id or not schedule:
        raise HTTPException(status_code=400, detail="train_id and schedule required")
    if train_id in trains_db:
        raise HTTPException(status_code=400, detail="Train already exists")
    trains_db[train_id] = schedule
    return {"message": "Train added", "train_id": train_id, "schedule": schedule}

@app.get("/search")
def search_trains(from_station: str, to_station: str):
    result = []
    for train_id, schedule in trains_db.items():
        stations = list(schedule.keys())
        if from_station in stations and to_station in stations:
            from_index = stations.index(from_station)
            to_index = stations.index(to_station)
            if from_index < to_index:
                segment = {station: schedule[station] for station in stations[from_index:to_index + 1]}
                result.append({
                    "train_id": train_id,
                    "segment": segment,
                    "days": schedule[from_station].get("days", [])
                })
    return result
