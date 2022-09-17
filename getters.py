import os
import math
import pandas as pd
import numpy as np
import functools
import fastf1
import requests
import json
from scipy.interpolate import interp1d
from scipy.signal import savgol_filter
from scipy.spatial.distance import cdist
from scipy import stats
from constants import *
from styling import *
from paths import *

fastf1.api.Cache.enable_cache(FF1_CACHE_DIR)


def fill_local_cache():
    for season in [2021, 2020, 2019, 2018]:
        # cache_tracks(season)
        for session in (
            get_all_race_sessions(season)
            + get_all_sprint_sessions(season)
            + get_all_qualifying_sessions(season)
            + get_all_practice_sessions(season)
            + get_all_testing_sessions(season)
        ):
            print(season, session.info["Meeting"], session.info["Session"])


def cache_migrate():
    entries = [
        os.path.join(cache_directory, filename)
        for filename in os.listdir(cache_directory)
    ]
    cached_pickles = [
        entry
        for entry in entries
        if os.path.isfile(entry) and os.path.splitext(entry)[1] == ".pkl"
    ]

    for cache_path in cached_pickles:
        print(cache_path)
        try:
            dataset = pd.read_pickle(cache_path)
            dataset = dataset.rename(columns={"Race": "Meeting"})
            dataset.to_pickle(cache_path)
        except:
            print("FAILED DATASET CACHE MIGRATION")


def cache_dataset(cache_name, update_cache=False):
    def outer(getter):
        @functools.wraps(getter)
        def wrapper(*args, **kwargs):
            season = args[0]
            cache_path = os.path.join(cache_directory, f"{season}_{cache_name}.pkl")
            print(cache_path)
            if not update_cache and os.path.exists(
                cache_path
            ):  # if cache exists, return the cached dataset

                dataset = pd.read_pickle(cache_path)
                dataset["Team"] = dataset["Driver"].apply(lambda val: get_team(season, val))
                dataset.to_pickle(cache_path)
                return pd.read_pickle(cache_path)
            else:  # if cache does not exist, build the dataset and cache it for future use before returning
                dataset = getter(*args, **kwargs)
                dataset.to_pickle(cache_path)
                return dataset

        return wrapper

    return outer


def get_all_race_sessions(season, selected_rounds=None):
    all_events = fastf1.get_event_schedule(season)
    if selected_rounds is not None:
        selected_events = all_events[all_events]
    else:
        selected_events = all_events[all_events["RoundNumber"] > 0]
    race_sessions = []
    for index, event in selected_events.iterrows():
        print(season, event["EventName"])
        try:
            race_sessions.append(get_session(season, event["EventName"], "Race"))
        except:
            print("ERROR RETRIEVING MEETING RACE")
    return race_sessions


def get_all_sprint_sessions(season, selected_rounds=None):
    sprint_rounds = {2021: [10, 14, 19], 2022: []}[season]
    if selected_rounds is not None and all(
        round in sprint_rounds for round in selected_rounds
    ):
        rounds = selected_rounds
    else:
        rounds = sprint_rounds
    if season in [2021, 2022]:
        sprint_race_sessions = []
        for round_number in rounds:
            print(season, round_number)
            sprint_race_sessions.append(get_session(season, round_number, "Sprint Qualifying"))
        return sprint_race_sessions
    else:
        return []


def get_all_qualifying_sessions(season, selected_rounds=None):
    all_events = fastf1.get_event_schedule(season)
    if selected_rounds is not None:
        selected_events = all_events[all_events]
    else:
        selected_events = all_events[all_events["RoundNumber"] > 0]
    qualifying_sessions = []
    for index, event in selected_events.iterrows():
        print(season, event["EventName"])
        try:
            qualifying_sessions.append(get_session(season, event["EventName"], "Qualifying"))
        except:
            print("ERROR RETRIEVING MEETING QUALIFYING")
    return qualifying_sessions


def get_all_practice_sessions(season, selected_rounds=None):
    sprint_rounds = [10, 14, 19]
    if selected_rounds is not None:
        rounds = selected_rounds
    else:
        rounds = range(1, len(CALENDAR[season]) + 1)
    practice_sessions = []
    for round_number in rounds:
        print(season, round_number)
        try:
            practice_sessions.append(get_session(season, round_number, "Practice 1"))
        except:
            print("ERROR RETRIEVING MEETING FP1")
        try:
            practice_sessions.append(get_session(season, round_number, "Practice 2"))
        except:
            print("ERROR RETRIEVING MEETING FP2")
            pass
        if round_number not in sprint_rounds:
            try:
                practice_sessions.append(get_session(season, round_number, "Practice 3"))
            except:
                print("ERROR RETRIEVING MEETING FP3")
    return practice_sessions


def get_all_testing_sessions(season):
    testing_sessions = []
    for test_number in [1, 2, 3]:
        for day in [1, 2, 3]:
            try:
                testing_sessions.append(get_session(season, f"Test {test_number}", day))
            except:
                pass
    return testing_sessions


def laps_per_driver(session):
    return session.laps.groupby("Driver")

def get_session(season, meeting, session_identifier):
    print(season, meeting, session_identifier)
    session = fastf1.get_event_schedule(season).get_event_by_name(meeting).get_session(session_identifier)
    
    session.info = dict(
        Season=season, Meeting=session.event.EventName, Session=session_identifier
    )
    session.cache_name = f"""{str(session.info["Meeting"]).replace("Grand Prix", "GP").replace(" ", "")}_{session.info["Season"]}""".replace(" ", "_")
    session.telemetry_cache_path = os.path.join(
        telemetry_cache_directory,
        session.cache_name + f"""_{session.info["Session"]}""" + ".pkl",
    )

    session.load()

    # from fastf1.livetiming.data import LiveTimingData
    # session.load(telemetry=True, livedata=LiveTimingData("/mnt/c/Users/dl/Downloads/race.txt"))
    # print(session.laps[["Driver", "LapTime", "LapNumber"]].to_string())

    # session.laps["Driver"] = session.laps["DriverNumber"].apply(lambda val: [driver for driver, num in DRIVER_NUMBERS[2022].items() if int(num) == int(val)][0])
    # session.laps["Team"] = session.laps["Driver"].apply(lambda val: get_team(season, val))

    # if not os.path.exists(session.telemetry_cache_path):
    #     session.load()
    #     session.laps.to_pickle(session.telemetry_cache_path)
    # else:
    #     print(session.telemetry_cache_path)
    #     # session.load(laps=False, telemetry=False)
    #     print(pd.read_pickle(session.telemetry_cache_path))
    #     session.laps = pd.read_pickle(session.telemetry_cache_path)

    try:
        session.laps["ReadableLapTime"] = session.laps["LapTime"].apply(
            lambda laptime: f"{laptime.seconds // 60}:{int(laptime.seconds % 60):02d}.{int(laptime.microseconds / 10000):02d}"
            if not pd.isna(laptime)
            else "0:00.00"
        )
        session.laps["Label"] = session.laps.apply(
            lambda row: f"""{row["Driver"]} {row["ReadableLapTime"]}""", axis=1
        )
        session.laps["Color"] = session.laps["Driver"].apply(
            lambda driver_identifier: get_driver_color(
                session.info["Season"], driver_identifier
            )
            if not pd.isna(driver_identifier)
            else LIGHT_COLOR
        )
    except:
        print("[SESSION LAPS MISSING ATTRIBUTES]")

    return session


class LapContainer:
    def __init__(self, lap):
        self.info = lap
        self.telemetry = lap.telemetry

    def as_color(self, color):
        if color:
            self.info["Color"] = color
        return self

    def with_description(self, description):
        self.info["Description"] = description
        return self

    def plot(self, axes_lookup):
        for channel_name in axes_lookup.keys():
            ax = axes_lookup[channel_name]
            ax.plot(
                self.telemetry["Distance"],
                self.telemetry[channel_name],
                color=self.info["Color"],
                label=self.info["Label"],
                linewidth=TRACE_THICKNESS,
        )

def fetch_lap(season, meeting, session_identifier, driver_identifier, lap_number=None):
    session = get_session(season, meeting, session_identifier)
    laps_by_driver = session.laps.pick_driver(driver_identifier).set_index(
        "LapNumber", drop=True
    )
    if lap_number is False:
        print(f"[LAPS FOR {driver_identifier}]")
        print(laps_by_driver[["ReadableLapTime", "Compound"]].to_string())
        exit(1)
    selected_lap = (
        laps_by_driver.pick_fastest()
        if lap_number is None
        else laps_by_driver.loc[lap_number]
    )
    return LapContainer(enhance_telemetry(selected_lap))

def enhance_telemetry(lap):
    telemetry = lap.telemetry.rename(columns=dict(nGear="Gear")).reset_index(
        drop=True
    )
    telemetry["TimeInSeconds"] = telemetry["Time"].dt.total_seconds()

    # filter with Savitsky Golay
    for column in ["Distance", "TimeInSeconds", "Speed", "Throttle", "X", "Y", "Z"]:
        telemetry[column] = savgol_filter(
            telemetry[column], window_length=7, polyorder=1
        )

    # resample and interpolate to distance
    interpolation_columns = [
        "TimeInSeconds",
        "Speed",
        "RPM",
        "Gear",
        "Throttle",
        "Brake",
        "DRS",
        "X",
        "Y",
        "Z",
    ]
    interpolated_telemetry = pd.DataFrame()
    new_index = range(round(telemetry.iloc[-1]["Distance"]))
    for column in interpolation_columns:
        interp = interp1d(
            telemetry["Distance"],
            telemetry[column],
            fill_value="extrapolate",
        )
        interpolated_telemetry[column] = interp(new_index)
    interpolated_telemetry[
        "Distance"
    ] = interpolated_telemetry.index.astype(int)
    interpolated_telemetry["Gear"] = interpolated_telemetry[
        "Gear"
    ].round()
    interpolated_telemetry.loc[0, "TimeInSeconds"] = 0
    interpolated_telemetry["Time"] = interpolated_telemetry[
        "TimeInSeconds"
    ].apply(lambda seconds: pd.Timedelta(seconds=seconds))

    lap.telemetry = interpolated_telemetry

    return lap

def get_track_cache_path(season, meeting):
    return os.path.join(
        cache_directory,
        "tracks",
        f"""{meeting.replace("Grand Prix", "GP").replace(" ", "")}_{season}_Track.pkl""".replace(" ", "_"),
    )

def get_track_name(season, meeting):
    return [round for round in CALENDAR[season] if round.name == meeting][0].track_name

def determine_track_section(sections, percentage):
    determined_section = ""
    for percentage_completed, section_name in sections.items():
        if percentage >= percentage_completed:
            determined_section = section_name
        else:
            break
    return determined_section

def add_track_locations(lap):
    season, meeting = lap.session.t0_date.year, lap.session.event.EventName
    # lap.track = pd.read_pickle(get_track_cache_path(season, meeting))
    lap.telemetry["Location"] = lap.telemetry.apply(lambda sample: cdist([(sample["X"], sample["Y"])], lap.track[["X", "Y"]]).argmin(), axis=1)
    lap.telemetry["PercentageCompleted"] = (lap.telemetry["Location"] / len(lap.track)) * 100
    # lap.telemetry["PercentageCompleted"] = lap.telemetry["Distance"].apply(lambda distance: distance / lap.telemetry.iloc[-1]["Distance"]) * 100

    track_sections = TRACKS_SECTIONS[get_track_name(season, meeting)]
    lap.telemetry["Section"] = lap.telemetry["PercentageCompleted"].apply(lambda percentage: determine_track_section(track_sections, percentage))

    return lap

def correct_distance_offset(laps):
    for lap in laps:
        lap.telemetry.sort_values("Location", inplace=True)
        lap.telemetry["Distance"] = lap.telemetry["Location"]
        # lap.telemetry = lap.telemetry[20:-20]
        # lap.telemetry.drop_duplicates("Location", inplace=True)
        # lap.telemetry.set_index("Location", drop=True, inplace=True)


def get_team(season, driver_identifier):
    return DRIVER_TEAM[season][driver_identifier]


def get_team_color(season, team_name):
    if season == 2021 and team_name == "Racing Point":  # fixing API error
        team_name = "Aston Martin"
    return TEAM_COLORS[season][team_name]


def get_driver_color(season, driver_identifier):
    return get_team_color(season, DRIVER_TEAM[season][driver_identifier])


def get_team_engine_supplier(season, team_name):
    return TEAM_ENGINES[season][team_name]


def get_driver_engine_supplier(season, driver_identifier):
    return get_team_engine_supplier(season, DRIVER_TEAM[season][driver_identifier])


def filter_standin_drivers(dataset):
    races_per_driver = dataset.groupby("Driver")["Meeting"].transform("nunique")
    # filter away drivers who have particiapted in less than half of the season's races
    filtered_dateset = dataset[races_per_driver.ge(races_per_driver.max() / 2)]
    return filtered_dateset


@cache_dataset("Engine_RPM")
def get_all_engine_data(season):
    columns = [
        "Driver",
        "Team",
        "Speed",
        "Gear",
        "Throttle",
        "RPM",
        "LapNumber",
        "Meeting",
    ]
    all_engine_data = pd.DataFrame(columns=columns).astype(
        dict(Speed=int, Gear=int, Throttle=int, RPM=int, LapNumber=int)
    )
    # for session in get_all_race_sessions(season):
    for session in get_all_testing_sessions(season):
        print(session.info["Meeting"])
        for driver_identifier, laps in laps_per_driver(session):
            print(driver_identifier)

            laps = laps[laps["LapTime"].notnull() & laps["IsAccurate"]]

            for lap_number, lap in laps.iterrows():
                try:
                    data = enhance_telemetry(lap).telemetry
                except:
                    continue
                data["Driver"] = driver_identifier
                data["Team"] = get_team(season, driver_identifier)
                data["LapNumber"] = int(lap_number)
                data["Meeting"] = session.info["Meeting"]
                all_engine_data = all_engine_data.append(
                    data[columns], ignore_index=True
                )

    # all_engine_data = filter_standin_drivers(all_engine_data)
    return all_engine_data


@cache_dataset("Launches")
def get_all_launches(season):
    compounds_to_compare = ["SOFT", "MEDIUM", "HARD"]
    launches = []
    for session in get_all_race_sessions(season):
        print(session.info["Meeting"])
        for driver_identifier, laps in laps_per_driver(session):
            print(driver_identifier)
            try:
                first_lap = laps.iloc[0]
                if not first_lap["Compound"] in compounds_to_compare:
                    continue
                data = enhance_telemetry(first_lap).telemetry

                launch = data.loc[: data[data["Speed"] > 200].iloc[0].name]
                launched_moment = launch.iloc[0]
                index_launch_began = launched_moment.name
            except:
                continue

            index_launch_ended = None
            interpolate_remaining_acceleration = False
            for index, row in data.iloc[index_launch_began:].iterrows():
                speed, brake = row["Speed"], row["Brake"]
                if speed >= 200:
                    index_launch_ended = index
                    break
                if speed > 150 and brake > 0:
                    interpolate_remaining_acceleration = True
                    index_launch_ended = index
                    break
            else:
                continue

            launched_moment, reached_200_moment = (
                data.iloc[index_launch_began],
                data.iloc[index_launch_ended],
            )
            time_launch_began = launched_moment["Time"]
            time_launch_ended = reached_200_moment["Time"]
            time_taken = (time_launch_ended - time_launch_began).total_seconds()

            if interpolate_remaining_acceleration:
                # interpolating linearly for the last acceleration missing for cars not reaching 200 km/h before braking for turn 1
                reached_speed = data["Speed"].iloc[index_launch_ended]
                time_taken_to_reach_speed = time_taken
                time_still_needed_to_reach_200 = (200 - reached_speed) * (
                    time_taken_to_reach_speed / reached_speed
                )
                time_taken += time_still_needed_to_reach_200

            # filter freak results caused by lag, glitches or on-track obstacles
            if time_taken < 4 or time_taken > 6.5:
                continue

            final_speed = reached_200_moment["Speed"]
            if final_speed > 200:
                # interpolating linearly to correct for cars surpassing 200 km/h between samples
                time_taken = time_taken * (200 / final_speed)

            median_reaction_time = 0.33

            launches.append(
                dict(
                    Driver=driver_identifier,
                    Team=DRIVER_TEAM[season][driver_identifier],
                    Compound=first_lap["Compound"],
                    Time=round(time_taken, 3) - median_reaction_time,
                    Gear=launched_moment["Gear"],
                    Meeting=session.info["Meeting"],
                    IsInterpolated=interpolate_remaining_acceleration,
                )
            )

    print(pd.DataFrame(launches))
    all_launches = filter_standin_drivers(pd.DataFrame(launches))
    return all_launches


@cache_dataset("All_Gearshifts")
def get_all_gearshifts(season):
    recorded_shifts = []
    for session in get_all_race_sessions(season):
        print(session.info["Meeting"])
        for driver_identifier, laps in laps_per_driver(session):
            print(driver_identifier)
            laps = laps[laps["LapTime"].notnull() & laps["IsAccurate"]]

            for lap_number, lap in laps.iterrows():
                data = enhance_telemetry(lap).telemetry
                data["GearDelta"] = data["Gear"].diff(1)
                # filter to get only samples where gearshift occurs
                data = data[abs(data["GearDelta"]) > 0]
                data["Direction"] = data["Delta"].apply(
                    lambda val: "Up" if val > 0 else "Down"
                )
                for index, shift in data.iterrows():
                    recorded_shifts.append(
                        dict(
                            Driver=lap["Driver"],
                            Team=get_team(season, lap["Driver"]),
                            Direction=shift["Direction"],
                            ToGear=shift["Gear"],
                            AtSpeed=shift["Speed"],
                            Meeting=session.info["Meeting"],
                            Lap=lap_number,
                            Time=shift["Time"],
                            Distance=shift["Distance"],
                            LapNumber=lap_number,
                        )
                    )

    all_shifts = filter_standin_drivers(pd.DataFrame(recorded_shifts))
    return all_shifts


def find_upshifts(lap):
    try:
        lap_data = enhance_telemetry(lap).telemetry
    except:
        return []

    lap_data = lap_data[lap_data["Throttle"] > 95]
    lap_data["GearChange"] = lap_data["Gear"].diff(1).apply(lambda value: value > 0)

    upshifts = []
    for index, sample in lap_data.iterrows():
        if sample["GearChange"] is True:
            upshifts.append(
                dict(
                    Driver=lap["Driver"],
                    ToGear=sample["Gear"],
                    RPM=lap_data.loc[max(0, index - 5) : index, "RPM"].max(),
                )
            )

    return upshifts


@cache_dataset("Race_Laps_Upshifts_RPM")
def get_all_upshifts(season):
    compounds_to_compare = ["SOFT", "MEDIUM", "HARD"]
    recorded_upshifts = []
    for session in get_all_race_sessions(season):
    # for session in get_all_qualifying_sessions(season):
        print(session.info["Meeting"])
        for driver_identifier, laps in laps_per_driver(session):
            print(driver_identifier)

            laps = laps[laps["LapTime"].notnull() & laps["IsAccurate"]]

            for lap_index, race_lap in laps.iterrows():
                if race_lap["Compound"] not in compounds_to_compare:
                    continue

                lap_upshifts = find_upshifts(race_lap)
                for upshift in lap_upshifts:
                    upshift["Team"] = get_team(season, upshift["Driver"])
                    upshift["Meeting"] = session.info["Meeting"]

                recorded_upshifts += lap_upshifts

    all_upshifts = filter_standin_drivers(pd.DataFrame(recorded_upshifts))
    return all_upshifts

def get_pre_season_improvements(season):
    pre_season_fastest_laps = dict()
    for day in [1, 2, 3]:
        pre_season_test = get_session(season, "Test 2", day)
        for driver_identifier, laps in laps_per_driver(pre_season_test):
            print(driver_identifier)

            try:
                best_lap_on_day = laps[laps["IsAccurate"]].pick_fastest()
            except:
                continue
            if driver_identifier in pre_season_fastest_laps:
                pre_season_fastest_laps[driver_identifier] = min(
                    [pre_season_fastest_laps[driver_identifier], best_lap_on_day],
                    key=lambda lap: lap["LapTime"],
                )
            else:
                pre_season_fastest_laps[driver_identifier] = best_lap_on_day

    qualifying_fastest_laps = dict()
    round_1_qualifying = get_session(season, 1, "Q")
    for driver_identifier, laps in laps_per_driver(round_1_qualifying):
        print(driver_identifier)
        qualifying_fastest_laps[driver_identifier] = laps[
            laps["IsAccurate"]
        ].pick_fastest()

    improvements = []
    for driver in pre_season_fastest_laps:
        pre, qual = pre_season_fastest_laps[driver], qualifying_fastest_laps[driver]
        improvements.append(
            dict(
                Driver=driver,
                PreSeasonLapTime=pre["LapTime"],
                Round1QualifyingLapTime=qual["LapTime"],
                LapTimeImprovement=round(
                    qual["LapTime"].total_seconds() - pre["LapTime"].total_seconds(), 2
                ),
            )
        )

    return pd.DataFrame(improvements)


@cache_dataset("Racing_Laps")
def get_all_racing_laps(season, selected_rounds=None):
    all_racing_laps = []
    for session in get_all_race_sessions(
        season, selected_rounds=selected_rounds
    ) + get_all_sprint_sessions(season, selected_rounds=selected_rounds):
        print(session.info["Meeting"])
        for driver_identifier, laps in laps_per_driver(session):
            print(driver_identifier)
            laps = laps[laps["LapTime"].notnull()]
            laps["IsSafetyCar"] = laps["TrackStatus"].str.contains("4")
            print(driver_identifier)

            for lap_number, lap in laps.iterrows():
                lap["Meeting"] = session.info["Meeting"]
                all_racing_laps.append(lap)

    all_laps = filter_standin_drivers(pd.DataFrame(all_racing_laps))
    return all_laps


@cache_dataset("DRS_Activations")
def get_DRS_activations(season):
    DRS_activations = []
    for session in get_all_race_sessions(season):
        print(session.info["Meeting"])
        for driver_identifier, laps in laps_per_driver(session):
            print(driver_identifier)
            laps = laps[laps["LapTime"].notnull()]
            print(driver_identifier)

            for lap_number, lap in laps.iterrows():
                data = enhance_telemetry(lap).telemetry
                moments_of_activations = data[
                    (data["DRS"].diff() > 0) & (data["DRS"] == 14)
                ]
                amount_DRS_activations = len(moments_of_activations)

                if amount_DRS_activations > 0:
                    print(lap_number, amount_DRS_activations)
                    lap["Meeting"] = session.info["Meeting"]
                    lap["Team"] = get_team(season, driver_identifier)
                    lap["AmountDRSActivations"] = amount_DRS_activations
                    DRS_activations.append(lap)

    all_DRS_activations = filter_standin_drivers(pd.DataFrame(DRS_activations))
    return all_DRS_activations


@cache_dataset("Race_Control_Messages")
def get_all_race_control_messages(season):
    all_race_control_messages = []
    for session in (
        get_all_practice_sessions(season)
        + get_all_qualifying_sessions(season)
        + get_all_sprint_sessions(season)
        + get_all_race_sessions(season)
    ):
        # for session in get_all_race_sessions(season, selected_rounds=[1]):
        base_url = f"http://livetiming.formula1.com"
        headers = {
            "Host": "livetiming.formula1.com",
            "Connection": "close",
            "TE": "identity",
            "User-Agent": "BestHTTP",
            "Accept-Encoding": "gzip, identity",
        }
        event_path = session.api_path
        race_control_messages_url = base_url + event_path + "RaceControlMessages.json"

        def item_generator(json_input, lookup_key):
            if isinstance(json_input, dict):
                for k, v in json_input.items():
                    if k == lookup_key:
                        yield v
                    else:
                        yield from item_generator(v, lookup_key)
            elif isinstance(json_input, list):
                for item in json_input:
                    yield from item_generator(item, lookup_key)

        response = requests.get(race_control_messages_url, headers=headers)
        response.encoding = "utf-8-sig"
        messages = json.loads(response.text)
        for message in messages["Messages"]:
            all_race_control_messages.append(
                dict(
                    Message=message.get("Message", None),
                    TimeIssued=message.get("Utc", None),
                    Lap=message.get("Lap", None),
                    Category=message.get("Category"),
                    Status=message.get("Status", None),
                    Flag=message.get("Flag", None),
                    Scope=message.get("Scope", None),
                    Sector=message.get("Sector", None),
                    Mode=message.get("Mode", None),
                    DriverNumber=message.get("RacingNumber", None),
                    Meeting=session.info["Meeting"],
                    Session=session.info["Session"],
                )
            )

    all_messages = pd.DataFrame(all_race_control_messages)
    all_messages.fillna(value=np.nan, inplace=True)

    all_messages["Driver"] = all_messages["DriverNumber"].apply(
        lambda number: (
            [
                key
                for key, value in DRIVER_NUMBERS[season].items()
                if str(value) == number
            ]
            + [np.nan]
        )[0]
    )

    return all_messages


@cache_dataset("Pit_Stop_Times")
def get_all_pitstop_times(season):
    pit_stop_times = pd.read_csv(
        os.path.join(cache_directory, f"{season}_Pit_Stop_Times.csv"),
        dtype=dict(
            Round=int,
            Position=int,
            Team=str,
            Driver=str,
            Time=float,
            Lap=int,
            Points=float,
        ),
    )
    print(pit_stop_times)
    pit_stop_times["Meeting"] = pit_stop_times["Round"].replace(
        {index: round.name for index, round in enumerate(CALENDAR[season], start=1)}
    )
    # map driver to team name
    pit_stop_times["Team"] = pit_stop_times["Driver"].apply(
        lambda driver: get_team(season, driver)
    )

    return filter_standin_drivers(pit_stop_times)


@cache_dataset("Pit_Stop_Laps")
def get_all_pitstop_laps(season):
    pitstop_laps = pd.DataFrame()
    for session in get_all_race_sessions(season):
        for driver_identifier, laps in laps_per_driver(session):
            # print(driver_identifier)
            laps.reset_index(inplace=True)

            # filter away all laps without a pitstop occuring
            laps["IsPitting"] = laps["Stint"].diff(-1).apply(lambda value: value < 0)
            laps["WithTireChange"] = (
                laps["TyreLife"].diff(-1).apply(lambda value: value > 0)
            )
            laps["IsRedFlag"] = laps["TrackStatus"].str.contains("5")
            laps["Meeting"] = session.info["Meeting"]
            laps["PitOutTime"] = laps["PitOutTime"].shift(-1)
            laps["TimeInPitlane"] = (
                laps["PitOutTime"] - laps["PitInTime"]
            ).dt.total_seconds()

            print(driver_identifier)
            for lap_index, lap in laps.iterrows():
                if not lap["IsPitting"] or not lap["WithTireChange"]:
                    continue

                lap.telemetry = enhance_telemetry(lap).telemetry
                next_lap = laps.iloc[lap_index + 1]
                next_lap.telemetry = enhance_telemetry(next_lap).telemetry
                for column in ["Time", "Distance"]:
                    lap.telemetry[column] = (
                        lap.telemetry[column] - lap.telemetry[column].iloc[0]
                    )
                    next_lap.telemetry[column] = next_lap.telemetry[column] - (
                        next_lap.telemetry[column].iloc[0]
                        - lap.telemetry[column].iloc[-1]
                    )
                data = lap.telemetry.append(next_lap.telemetry, ignore_index=True)

                try:
                    time_in_session = lap["LapStartTime"] + data["Time"]
                    in_pit = data[
                        (time_in_session >= lap["PitInTime"])
                        & (time_in_session <= lap["PitOutTime"])
                    ]
                    distance_travelled_in_pitlane = len(in_pit)
                    laps.loc[
                        lap_index, "PitlaneDistance"
                    ] = distance_travelled_in_pitlane
                except:
                    print("ERROR ESTABLISHING PITLANE LENGTH")
                    pass

            pitstop_laps = pitstop_laps.append(
                laps[laps["IsPitting"] & laps["WithTireChange"] & ~laps["IsRedFlag"]],
                ignore_index=True,
            )

    return filter_standin_drivers(pitstop_laps)


@cache_dataset("Pit_Stops")
def get_all_pitstops(season):
    pitstops = []
    for session in get_all_race_sessions(season):
        amount_laps_completed_by_winner = int(session.results[0]["laps"])

        for driver_identifier, laps in laps_per_driver(session):
            print(driver_identifier)
            # filter away all laps without a pitstop occuring
            laps["IsPitting"] = laps["Stint"].diff(-1).apply(lambda value: value < 0)

            for lap_number, lap in laps.iterrows():
                current_compound = lap["Compound"]
                if current_compound == "UNKNOWN":
                    rest_of_laps = laps.loc[lap_number:]
                    laps.at[lap_number, "Compound"] = rest_of_laps[
                        rest_of_laps["Compound"] != "UNKNOWN"
                    ].iloc[0]["Compound"]

            laps["IsSafetyCar"] = laps["TrackStatus"].str.contains("4")
            laps["IsVSC"] = laps["TrackStatus"].str.contains("6")
            laps["IsRedFlag"] = laps["TrackStatus"].str.contains("5")
            laps_with_pitstop = laps[laps["IsPitting"] & ~laps["IsRedFlag"]]

            pit_stop_count = 0
            for lap_number, lap in laps_with_pitstop.iterrows():
                pit_stop_count += 1
                pitstops.append(
                    dict(
                        Driver=lap["Driver"],
                        Team=get_team(season, lap["Driver"]),
                        LapNumber=int(lap_number),
                        LapsCompletedByWinner=amount_laps_completed_by_winner,
                        Meeting=session.info["Meeting"],
                        FromCompound=lap["Compound"],
                        ToCompound=laps["Compound"].shift(-1).loc[lap_number],
                        PitStopCount=pit_stop_count,
                        WasUnderSafetyCar=lap["IsSafetyCar"],
                    )
                )
                if lap["Compound"] == "UNKNOWN":
                    print(lap_number)
                    exit(1)

    return filter_standin_drivers(pd.DataFrame(pitstops))


def get_Q1_improvements(season):
    efforts = []
    # for qualifying_session in get_all_qualifying_sessions(season):
    for qualifying_session in get_all_qualifying_sessions(season, selected_rounds=[1]):
        qualifying_session.laps.dropna(subset=["Time", "LapStartTime"], inplace=True)
        qualifying_session.laps = qualifying_session.laps[
            qualifying_session.laps["IsAccurate"]
        ]
        subsession_finished_times = qualifying_session.session_status[
            qualifying_session.session_status["Status"] == "Finished"
        ]
        if len(subsession_finished_times) == 2:
            subsession_finished_times = subsession_finished_times.append(
                qualifying_session.session_status[
                    qualifying_session.session_status["Status"] == "Finalised"
                ].iloc[0]
            )
        qualifying_session.laps["SubSession"] = qualifying_session.laps[
            "LapStartTime"
        ].apply(
            lambda lap_start_time: ["Q3", "Q2", "Q1"][
                len(
                    subsession_finished_times.loc[
                        subsession_finished_times["Time"] > lap_start_time
                    ]
                )
                - 1
            ]
        )

        for driver_identifier, laps in laps_per_driver(qualifying_session):
            # print(laps[["Time", "LapNumber", "Driver", "ReadableLapTime", "LapStartTime", "SubSession"]].to_string())
            # find first representative Q1 lap that is within the 3% threshold of the fastest Q1 lap
            q1_laps = laps[laps["SubSession"] == "Q1"].pick_quicklaps(threshold=1.03)
            first_Q1_lap = q1_laps.iloc[0]
            fastest_Q1_lap = q1_laps.pick_fastest()
            efforts.append(
                dict(
                    Driver=first_Q1_lap["Driver"],
                    Team=DRIVER_TEAM[season][driver_identifier],
                    FirstQ1Time=first_Q1_lap["LapTime"],
                    FastestQ1Time=fastest_Q1_lap["LapTime"],
                    Improvement=(
                        first_Q1_lap["LapTime"] - fastest_Q1_lap["LapTime"]
                    ).total_seconds(),
                    Meeting=qualifying_session.info["Meeting"],
                )
            )
    return pd.DataFrame(efforts)


@cache_dataset("Downshift_Rates")
def get_downshift_rates(season):
    shift_sequences = []
    # for session in get_all_qualifying_sessions(season, selected_rounds=[1]):
    for session in get_all_qualifying_sessions(season):
        print(session.info["Meeting"])
        for driver_identifier, laps in laps_per_driver(session):
            print(driver_identifier)
            laps = laps[laps["LapTime"].notnull() & laps["IsAccurate"]].pick_quicklaps(
                threshold=1.03
            )

            for lap_number, lap in laps.iterrows():
                try:
                    data = enhance_telemetry(lap).telemetry
                except:
                    continue
                data["GearDelta"] = data["Gear"].diff(1)
                grouping = data.groupby((data["Throttle"].diff(1) < 0).cumsum())
                for _, window in grouping:
                    downshifts = window[window["GearDelta"] < 0]
                    if len(downshifts) > 1:
                        first_downshift, last_downshift = (
                            downshifts.iloc[0],
                            downshifts.iloc[-1],
                        )
                        from_gear, to_gear = (
                            first_downshift["Gear"] + 1,
                            last_downshift["Gear"],
                        )
                        amount_downshifts = from_gear - to_gear
                        shift_sequences.append(
                            dict(
                                Driver=lap["Driver"],
                                Team=get_team(season, lap["Driver"]),
                                FromGear=from_gear,
                                ToGear=to_gear,
                                Meeting=session.info["Meeting"],
                                Lap=lap_number,
                                TimeTaken=(
                                    last_downshift["TimeInSeconds"]
                                    - first_downshift["TimeInSeconds"]
                                )
                                / amount_downshifts,
                                LapNumber=lap_number,
                            )
                        )

    downshift_rates = filter_standin_drivers(pd.DataFrame(shift_sequences))
    return downshift_rates


def cache_tracks(season):
    for session in get_all_qualifying_sessions(season) + get_all_testing_sessions(season):
        track_cache_path = os.path.join(
            cache_directory,
            "tracks",
            session.cache_name + "_Track.pkl",
        )
        print(track_cache_path)

        try:
            lap = enhance_telemetry(session.laps.pick_fastest())
        except:
            continue

        alpha = np.linspace(0, 1, round(len(lap.telemetry)))
        try:
            distance = np.cumsum(
                np.sqrt(
                    np.ediff1d(lap.telemetry["X"], to_begin=0) ** 2
                    + np.ediff1d(lap.telemetry["Y"], to_begin=0) ** 2
                )
            )
            distance /= distance[-1]
            fx, fy = interp1d(
                distance, lap.telemetry["X"], fill_value="extrapolate",
            ), interp1d(
                distance, lap.telemetry["Y"], fill_value="extrapolate",
            )
            track = pd.DataFrame(dict(Distance=range(len(alpha)), PercentageCompleted=distance, X=fx(alpha), Y=fy(alpha)))
        except:
            print("INVALID GPS ON LAP")

        track.to_pickle(track_cache_path)

# cache_tracks(2022)

def show_track(season, selected_round):
    for session in get_all_race_sessions(season, selected_rounds=[selected_round]):
        track_cache_path = os.path.join(
            cache_directory,
            "tracks",
            session.cache_name + "_Track.pkl",
        )
        track = pd.read_pickle(track_cache_path)
        fig, ax = plt.subplots(figsize=(12, 18), dpi=200)
        ax.scatter(
            track["X"],
            track["Y"],
            marker="o",
            s=40,
            linestyle="None",
            color=DATA_COLORS.BLUE,
            zorder=1,
        )
        for distance, location in track.iterrows():
            percentage = round(distance / len(track) * 100, 1)
            if distance % 10 == 0:
                ax.annotate(
                    percentage,
                    (location["X"], location["Y"]),
                    fontsize=3,
                    ha="center",
                    va="center",
                    color="blue",
                )

        ax.margins(x=0.02, y=0.02)

        lap = add_track_locations(enhance_telemetry(session.laps.pick_fastest())) 

        partly_on_throttle = track.loc[
            lap.telemetry[lap.telemetry["Throttle"] < 95]["Location"]
        ]
        ax.scatter(
            partly_on_throttle["X"],
            partly_on_throttle["Y"],
            marker="o",
            s=4,
            linestyle="None",
            color=DATA_COLORS.GREEN,
            zorder=1,
        )
        braking = track.loc[lap.telemetry[lap.telemetry["Brake"] > 0]["Location"]]
        ax.scatter(
            braking["X"],
            braking["Y"],
            marker="o",
            s=4,
            linestyle="None",
            color=DATA_COLORS.RED,
            zorder=1,
        )

        ax.set_aspect("equal")

        fig.tight_layout()
        fig.savefig("tests/Track.png")

@cache_dataset("Session_Section_Times")
def get_section_times(season):
    laps_sections = []
    # for session in get_all_testing_sessions(season) + get_all_practice_sessions(season) + get_all_qualifying_sessions(season) + get_all_sprint_sessions(season) + get_all_race_sessions(season):
    # for session in get_all_qualifying_sessions(season, selected_rounds=[1]):
    # for session in get_all_testing_sessions(season):
    # for session in get_all_qualifying_sessions(season):
    for session in [get_session(season, "Saudi Arabian Grand Prix", "Practice 2")]:
        for lap_index, lap in session.laps[session.laps["IsAccurate"]].iterrows():
            # print(lap.telemetry[["Distance", "Speed", "Location", "Section", "SectionChanges"]].to_string())
            try:
                lap = enhance_telemetry(lap)
            except:
                print("Lap telemetry not available")
                continue
            lap = add_track_locations(lap)
            lap.telemetry["SectionChanges"] = (lap.telemetry["Section"] != lap.telemetry["Section"].shift()).cumsum()
            section_times = dict()
            # print(lap.telemetry["SectionChanges"].unique())
            for _, data in lap.telemetry.groupby("SectionChanges"):
                section_name = data.iloc[0]["Section"]
                section_time = data.iloc[-1]["TimeInSeconds"] - data.iloc[0]["TimeInSeconds"]
                section_times[section_name] = section_times.get(section_name, 0) + section_time
            for index, (section_name, section_time) in enumerate(section_times.items()):
                laps_sections.append(dict(
                    Meeting=session.info["Meeting"],
                    Session=session.info["Session"],
                    LapNumber=lap["LapNumber"],
                    LapIndex=lap_index,
                    Driver=lap["Driver"],
                    SectionNumber=index,
                    SectionName=section_name,
                    Time=section_time,
                ))

        print(len(laps_sections), "entries")
    return pd.DataFrame(laps_sections)

def get_brakings(season, meeting, lap, turn):
    session = get_session(season, meeting, "R")
    track_cache_path = os.path.join(
        cache_directory,
        "tracks",
        session.cache_name + "_Track.pkl",
    )
    aggregate_track = pd.read_pickle(track_cache_path)
    fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(16, 9), dpi=150)
    ax1.plot(aggregate_track["X"], aggregate_track["Y"], linewidth=15, alpha=0.8)

    braking_points = pd.DataFrame()
    for driver_identifier, laps in laps_per_driver(session):
        try:
            lap = enhance_telemetry(laps.pick_fastest())
        except:
            continue

        acceleration = pd.Series(
            savgol_filter(
                np.gradient(lap.telemetry["Speed"]), window_length=15, polyorder=1
            )
        )
        lap.telemetry["IsBraking"] = acceleration < -0.1
        braking_zones = lap.telemetry[lap.telemetry["IsBraking"] == True]
        # print(lap.telemetry["IsBraking"])

        first_sample_braking = braking_zones.iloc[0]
        closest_sample = cdist(
            [(first_sample_braking["X"], first_sample_braking["Y"])], aggregate_track
        ).argmin()
        closest_coordinates = aggregate_track[closest_sample]
        ax1.plot(
            [aggregate_track.loc[closest_sample, "X"]],
            [aggregate_track.loc[closest_sample, "Y"]],
            marker="o",
            markersize=10,
            color=get_driver_color(season, driver_identifier),
        )
        ax1.annotate(
            driver_identifier,
            (closest_coordinates[0], closest_coordinates[1]),
            ha="center",
            va="center",
            fontsize=6,
        )
        print(
            driver_identifier,
            "first braking",
            first_sample_braking[["TimeInSeconds", "Distance", "Speed", "Brake"]],
        )
        braking_points = braking_points.append(
            dict(
                Driver=driver_identifier,
                BrakingLocation=closest_sample,
                FromSpeed=first_sample_braking["Speed"],
                X=closest_coordinates[0],
                Y=closest_coordinates[1],
                Color=get_driver_color(season, driver_identifier),
            ),
            ignore_index=True,
        )

    ax1.plot(
        [braking_points["X"].median()],
        [braking_points["Y"].median()],
        marker="o",
        markersize=200,
        color=LIGHT_COLOR,
        alpha=0.2,
    )
    ax1.set_xlim(
        braking_points["X"].median() - 1000, braking_points["X"].median() + 1000
    )
    ax1.set_ylim(
        braking_points["Y"].median() - 1000, braking_points["Y"].median() + 1000
    )

    braking_points = braking_points.sort_values("BrakingLocation").reset_index(
        drop=True
    )
    print(braking_points)
    ax2.barh(
        braking_points.index,
        braking_points["BrakingLocation"],
        color=braking_points["Color"],
        alpha=1 / 2,
    )
    ax2.set_yticks(braking_points.index.to_list(), braking_points["Driver"])
    ax2.set_xlim(
        braking_points["BrakingLocation"].median() - 50,
        braking_points["BrakingLocation"].median() + 50,
    )

    ax1.margins(x=0.02, y=0.02)
    ax1.grid()
    ax2.margins(x=0.02)
    ax2.grid()

    fig.tight_layout()
    fig.savefig("test.png")

def rotate_track(lap, degrees=90):
    x, y = lap.telemetry["X"], lap.telemetry["Y"]
    lap.telemetry["X"], lap.telemetry["Y"] = [
        x * math.cos(math.radians(90)) - y * math.sin(math.radians(90))
        for x, y in zip(x, y)
    ], [
        x * math.sin(math.radians(90)) - y * math.cos(math.radians(90))
        for x, y in zip(x, y)
    ]