from views import *


class PreSeasonSandbaggingAnalysis(Aggregation):
    def __init__(self, season, grouped_by):
        self.grouped_by = grouped_by
        self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
            self.grouped_by
        ]

        super().__init__(
            grouped_by,
            season,
            title=f"{self.grouped_by.upper()}S Sandbagging",
            xlabel=["Improvement from Pre-Season Testing to Round 1 Qualifying", "s"],
            subtitle=f"{season} Formula 1 Season",
            description=f"[Improvement from best laptime set in pre-season testing to best laptime in qualifying of the first round. Ordered by {self.grouped_by.upper()} median.]",
            xlimits=[-2, 2],
            locators=(0.5, 0.25),
        )
        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()
        self.export(
            os.path.join(
                analysis_directory,
                "aggregating",
                f"{self.season}_{self.grouped_by}s_Pre-Season_Sandbagging.png",
            )
        )

    def prepare_data(self):
        self.df = get_pre_season_improvements(self.season)
        self.df.sort_values("LapTimeImprovement", ascending=True, inplace=True)
        self.df = self.df.groupby(self.grouped_by, sort=False)

    def plot_data(self):
        self.twins = []
        for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
            competitor_color = self.color_getter(self.season, competitor_name)
            ax.barh(
                y=[0],
                width=[-competitor_data.iloc[0]["LapTimeImprovement"]],
                color=competitor_color,
                height=1,
                align="edge",
                alpha=1 / 4,
            )
            ax.axvline(x=0, c=LIGHT_COLOR, alpha=0.5)


class Q1SessionImprovement(Aggregation):
    def __init__(self, season, grouped_by):
        self.grouped_by = grouped_by
        self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
            self.grouped_by
        ]
        super().__init__(
            grouped_by,
            season,
            title=f"{self.grouped_by.upper()}S Q1 Improvement",
            xlabel=["Improvement from first Q1 Effort to Eventual Q1 Laptime", "s"],
            subtitle=f"{season} Formula 1 Season",
            description=f"[Improvement from first laptime set in Q1 to best laptime set at the end of Q1. Ordered by {self.grouped_by.upper()} median.]",
            xlimits=[0, 1.15],
            locators=(0.5, 0.1),
        )
        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()
        self.export(
            os.path.join(
                analysis_directory,
                "aggregating",
                f"{self.season}_{self.grouped_by}s_Q1_Improvement.png",
            )
        )

    def prepare_data(self):
        self.df = get_Q1_improvements(self.season)
        print(self.df.sort_values("Driver").to_string())
        self.df["MedianImprovement"] = self.df.groupby(self.grouped_by)[
            "Improvement"
        ].transform("median")
        self.df.sort_values("MedianImprovement", ascending=True, inplace=True)
        self.df = self.df.groupby(self.grouped_by, sort=False)

    def plot_data(self):
        for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
            competitor_color = self.color_getter(self.season, competitor_name)
            ax.barh(
                y=[0],
                width=[competitor_data.iloc[0]["MedianImprovement"]],
                color=competitor_color,
                height=1,
                align="edge",
                alpha=1 / 4,
            )

            ax.scatter(
                x=competitor_data["Improvement"],
                y=[1 / 2] * len(competitor_data),
                s=dict(Driver=100, Team=200)[self.grouped_by],
                c=competitor_color,
                alpha=1 / 6,
            )


class TimeOnTrackPattern(Aggregation):
    pass


class SpinsAnalysis(Aggregation):
    def __init__(self, season, grouped_by):
        self.grouped_by = grouped_by
        self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
            self.grouped_by
        ]
        self.sorting_order = "count"

        super().__init__(
            grouped_by,
            season,
            title=f"{self.grouped_by}s Spin Award",
            xlabel=["Spins Noted by Race Control", "#"],
            subtitle=f"{season} Formula 1 Season",
            description=f"[Number of spins reported by Race Control across Free Practice, Qualifying, F1 Sprints and Grands Prix of the season for each {self.grouped_by}.]",
            xlimits=dict(Driver=[0, 15], Team=[0, 19])[self.grouped_by],
            locators=dict(Driver=[2, 1], Team=[5, 1])[self.grouped_by],
        )
        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()
        self.export(
            os.path.join(
                analysis_directory,
                "aggregating",
                f"{self.season}_{self.grouped_by}s_Spins.png",
            )
        )

    def prepare_data(self):
        self.df = get_all_race_control_messages(self.season)

        self.df.fillna(value=np.nan, inplace=True)

        self.df = self.df[~self.df["Driver"].isna()]
        self.df = self.df[self.df["Driver"].isin(DRIVER_IDENTIFIER[self.season].keys())]
        self.df["Team"] = self.df["Driver"].apply(
            lambda driver: get_team(self.season, driver)
        )

        self.df = self.df[self.df["Message"].str.contains("SPUN")]

        self.sorting_column_name = "AmountSpins"
        self.df[self.sorting_column_name] = self.df.groupby(self.grouped_by)[
            "Message"
        ].transform(self.sorting_order)

        self.df = self.df.sort_values(self.sorting_column_name, ascending=False)
        for driver in DRIVER_IDENTIFIER[self.season].keys():
            if driver not in self.df["Driver"].unique():
                self.df = self.df.append(
                    {"Driver": driver, self.sorting_column_name: "0"}, ignore_index=True
                )
        self.df = self.df.groupby(self.grouped_by, sort=False)

    def plot_data(self):
        for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
            competitor_color = self.color_getter(self.season, competitor_name)
            competitor_data["Meeting"] = pd.Categorical(
                competitor_data["Meeting"],
                [round.name for round in CALENDAR[self.season]],
            )
            sorted_by_race = competitor_data.sort_values("Meeting")
            per_weekend = sorted_by_race.groupby("Meeting", sort=False)
            bottom = 0
            for index, (weekend, spins) in enumerate(per_weekend, start=1):
                amount_spins_in_weekend = len(spins)
                (bar,) = ax.barh(
                    y=[0],
                    width=[amount_spins_in_weekend],
                    left=bottom,
                    color=competitor_color,
                    height=1,
                    align="edge",
                    alpha=1 / 3 if index % 2 else 1 / 4,
                )
                if amount_spins_in_weekend > 0:
                    round_number = [
                        round.round_number
                        for round in CALENDAR[self.season]
                        if round.name == weekend
                    ][0]
                    ax.annotate(
                        text=f"R{round_number}",
                        xy=(
                            bottom + 0.05,
                            0.02,
                        ),
                        color=LIGHT_COLOR,
                        alpha=1 / 4,
                        fontsize=6,
                        fontweight="bold",
                        ha="left",
                        va="bottom",
                    )
                bottom += amount_spins_in_weekend


class BrakingPointAnalysis(Aggregation):
    def __init__(self, season, grouped_by, event, lap, turn):
        self.grouped_by = grouped_by
        self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
            self.grouped_by
        ]
        self.sorting_order = "median"

        super().__init__(
            grouped_by,
            season,
            title=f"{self.grouped_by}s Braking",
            xlabel=["Braking Phases", None],
            subtitle=f"{season} {event}",
            description=f"[. Ordered by {self.grouped_by} {self.sorting_order}.]",
            xlimits=[1.75, 4.75],
            locators=(0.5, 0.1),
        )
        self.prepare_data(event, lap, turn)
        # self.create_figure()
        # self.add_titles()
        # self.apply_logos()
        # self.plot_data()
        # self.refine_figure()
        # self.export(
        #     os.path.join(
        #         analysis_directory,
        #         "aggregating",
        #         f"{self.season}_{event}_{lap}_{turn}_{self.grouped_by}s_.png",
        #     )
        # )

    def prepare_data(self, event, lap, turn):
        self.df = get_brakings(self.season, event, lap, turn)

    # def plot_data(self):
    #     for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
    #         competitor_color = self.color_getter(self.season, competitor_name)
    #         ax.barh(
    #             y=[0],
    #             width=[competitor_data[self.metric_column].agg(self.sorting_order)],
    #             color=competitor_color,
    #             height=1,
    #             align="edge",
    #             alpha=1 / 4,
    #         )


class DownshiftRateAnalyis(Aggregation):
    def __init__(self, season, grouped_by):
        self.grouped_by = grouped_by
        self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
            self.grouped_by
        ]
        self.metric_column = "TimeTaken"
        self.sorting_order = "median"

        super().__init__(
            grouped_by,
            season,
            title=f"{self.grouped_by}s Downshift Rate",
            xlabel=["Time Between Downshifts", ("s")],
            subtitle=f"{season} Season",
            description=f"[. Ordered by {self.grouped_by} {self.sorting_order}.]",
            xlimits=[0, 0.35],
            locators=(0.1, 0.025),
        )
        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()
        self.export(
            os.path.join(
                analysis_directory,
                "aggregating",
                f"{self.season}_{self.grouped_by}s_Downshift_Rates.png",
            )
        )

    def prepare_data(self):
        self.df = get_downshift_rates(self.season)
        self.df[self.sorting_order] = self.df.groupby(self.grouped_by)[
            self.metric_column
        ].transform(self.sorting_order)

        self.df = self.df.sort_values(self.sorting_order, ascending=False)
        self.df = self.df.groupby(self.grouped_by, sort=False)

    def plot_data(self):
        for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
            competitor_color = self.color_getter(self.season, competitor_name)
            ax.barh(
                y=[0],
                width=[competitor_data[self.metric_column].agg(self.sorting_order)],
                color=competitor_color,
                height=1,
                align="edge",
                alpha=1 / 4,
            )
            ax.hist(
                competitor_data[self.metric_column],
                range=self.xlimits,
                bins=20,
                weights=np.ones(len(competitor_data)) / len(competitor_data) * 5,
                color=competitor_color,
                alpha=1 / 2,
            )


# class SafetyCarTimingAnalysis(Aggregation):
#     def __init__(self, season, grouped_by):
#         self.grouped_by = grouped_by
#         self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
#             self.grouped_by
#         ]
#         self.sorting_order = "median"

#         super().__init__(
#             grouped_by,
#             season,
#             title=f"{self.grouped_by}s Safety Car Timing",
#             xlabel=["Safety Car Probability", "#"],
#             subtitle=f"{season} Formula 1 Season",
#             description=f"[. Ordered by {self.grouped_by} {self.sorting_order}.]",
#             xlimits=[1.75, 4.75],
#             locators=(0.5, 0.1),
#         )
#         self.prepare_data()
#         self.create_figure()
#         self.add_titles()
#         self.apply_logos()
# self.plot_data()
# self.refine_figure()
# self.export(
#     os.path.join(
#         analysis_directory,
#         "aggregating",
#         f"{self.season}_{self.grouped_by}s_Safety_Car_Timing.png",
#     )
# )

# def prepare_data(self):
#     self.df = get_all_race_control_messages(self.season)

#     print(self.df)
#     on_track_events = self.df[self.df["Category"] == "CarEvent"]
#     print(on_track_events)
#     spins = on_track_events[on_track_events["Message"].str.contains("SPUN")]
#     print(spins)
#     print(spins.groupby("DriverNumber")["DriverNumber"].agg(len))

#     self.metric_column = "len"

#     self.sorting_column_name = (
#         f"{self.sorting_order.capitalize()}{self.metric_column.capitalize()}"
#     )
#     self.df[self.sorting_column_name] = self.df.groupby(
#         self.grouped_by, sort=False
#     )[self.metric_column].transform(self.sorting_order)

#     self.df = self.df.sort_values(self.sorting_column_name, ascending=True)
#     self.df = self.df.groupby(self.grouped_by, sort=False)

# def plot_data(self):
#     for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
#         competitor_color = self.color_getter(self.season, competitor_name)
#         ax.barh(
#             y=[0],
#             width=[competitor_data[self.metric_column].agg(self.sorting_order)],
#             color=competitor_color,
#             height=1,
#             align="edge",
#             alpha=1 / 4,
#         )


class SlowPitStopsAnalysis(Aggregation):
    def __init__(self, season, grouped_by):
        self.grouped_by = grouped_by
        self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
            self.grouped_by
        ]
        self.metric_column = "Time"
        self.sorting_order = "count"
        self.threshold_time = 5

        super().__init__(
            grouped_by,
            season,
            title=f"{self.grouped_by}s Slow Pit Stops",
            xlabel=[f"Pit Stops Slower than {self.threshold_time} seconds", "#"],
            subtitle=f"{season} Formula 1 Season",
            description=f"[Number of Pit Stops taking in excess of {self.threshold_time} seconds for Drivers and Teams across the 22 Races of the {season} season.]",
            xlimits=dict(Driver=[0, 6], Team=[0, 10])[self.grouped_by],
            locators=dict(Driver=[1, 1], Team=[2, 1])[self.grouped_by],
        )
        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()
        self.export(
            os.path.join(
                analysis_directory,
                "aggregating",
                f"{self.season}_{self.grouped_by}s_Slow_Pit_Stops.png",
            )
        )

    def prepare_data(self):
        self.df = get_all_pitstop_times(self.season)
        season_race_control_messages = get_all_race_control_messages(self.season)
        # print(season_race_control_messages[season_race_control_messages["Message"].str.contains("PENALTY")])
        penalty_messages = season_race_control_messages[
            season_race_control_messages["Message"].str.contains("PENALTY")
        ].copy()
        penalty_messages["PenaltyType"] = penalty_messages["Message"].str.extract(
            "\d+ SECOND (\S+)"
        )
        penalty_messages["PenaltySeconds"] = (
            penalty_messages["Message"].str.extract("(\d+) SECOND").astype(int)
        )
        servable_time_penalties = penalty_messages[
            penalty_messages["PenaltyType"].isin(["TIME", "STOP/GO"])
        ]

        pit_stop_times_penalties_removed = pd.DataFrame()
        for round in CALENDAR[self.season]:
            race_pit_stops = self.df[
                self.df["Round"] == round.round_number
            ].sort_values("Lap", ascending=True)
            race_penalties = servable_time_penalties[
                servable_time_penalties["Meeting"] == round.name
            ]

            def func(stops):
                driver_penalties = race_penalties[
                    race_penalties["Message"].str.contains(f"\({stops.name}\)")
                ]
                for index, stop in stops.iterrows():
                    penalties_before_stop = driver_penalties[
                        driver_penalties["Lap"] <= stop["Lap"]
                    ]
                    if len(penalties_before_stop) > 1:
                        print("MULTIPLE PENALTIES")
                        import sys

                        sys.exit(1)
                    if len(penalties_before_stop) == 1:
                        penalty_to_serve = penalties_before_stop.iloc[0]
                        driver_penalties.drop(penalty_to_serve.name, inplace=True)
                        if penalty_to_serve["PenaltyType"] == "STOP/GO":
                            stops.drop(index, inplace=True)
                            continue
                        if penalty_to_serve["PenaltyType"] == "TIME":
                            stops.loc[index, "Time"] -= penalty_to_serve[
                                "PenaltySeconds"
                            ]
                            # print(stop["Time"], penalty_to_serve["PenaltySeconds"])
                            if stop["Time"] - penalty_to_serve["PenaltySeconds"] < 1.5:
                                print("PENALTY NOT SERVED")
                return stops

            pit_stop_times_penalties_removed = pd.concat(
                [
                    pit_stop_times_penalties_removed,
                    race_pit_stops.groupby("Driver").apply(func).reset_index(drop=True),
                ],
                ignore_index=True,
            )

        self.df = pit_stop_times_penalties_removed

        self.sorting_column_name = f"CountBy{self.grouped_by}"
        self.df = (
            self.df.groupby(self.grouped_by)
            .apply(lambda group: group[group[self.metric_column] > self.threshold_time])
            .reset_index(drop=True)
        )

        self.df[self.sorting_column_name] = self.df.groupby(self.grouped_by)[
            self.metric_column
        ].transform(self.sorting_order)

        self.competitor_order = (
            self.df.groupby(self.grouped_by)[self.metric_column]
            .agg(self.sorting_order)
            .reset_index(name=self.sorting_order)
            .sort_values(self.sorting_order, ascending=False)[self.grouped_by]
            .values
        )
        self.df[self.grouped_by] = pd.Categorical(
            self.df[self.grouped_by], self.competitor_order
        )
        self.df.sort_values(self.grouped_by, inplace=True)

        for driver in DRIVER_IDENTIFIER[self.season].keys():
            if driver not in self.df["Driver"].unique():
                self.df = self.df.append(
                    {"Driver": driver, self.sorting_column_name: "0"}, ignore_index=True
                )
        print(self.df.sort_values("Round").to_string())
        self.df = self.df.groupby(self.grouped_by, sort=False)

    def plot_data(self):
        for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
            competitor_color = self.color_getter(self.season, competitor_name)
            total_slow_stops = competitor_data[self.metric_column].agg(
                self.sorting_order
            )
            ax.barh(
                y=[0],
                width=[total_slow_stops],
                color=competitor_color,
                height=1,
                align="edge",
                alpha=1 / 3,
            )
            # competitor_data["Meeting"] = pd.Categorical(competitor_data["Meeting"], [round.name for round in CALENDAR[self.season]])
            # sorted_by_race = competitor_data.sort_values("Meeting")
            # if total_slow_stops > 0:
            #     for index, stop in sorted_by_race.reset_index().iterrows():
            #         ax.barh(
            #             y=[0],
            #             width=[1],
            #             left=index,
            #             color=competitor_color,
            #             height=1,
            #             align="edge",
            #             alpha=1 / 3 if index % 2 else 1 / 4,
            #         )
            #         event = [round for round in CALENDAR[self.season] if round.round_number == stop["Round"]][0]
            #         ax.annotate(
            #             text=f"""{event.shortened_name} {round(stop["Time"], 1)}s""",
            #             xy=(
            #                 index + 0.05,
            #                 0.05,
            #             ),
            #             color=LIGHT_COLOR,
            #             alpha=1 / 4,
            #             fontsize=6,
            #             fontweight="bold",
            #             # rotation="vertical",
            #             ha="left",
            #             va="bottom",
            #             ma="center",
            #         )


class BestPitStopTimesAnalysis(Aggregation):
    def __init__(self, season, grouped_by):
        self.grouped_by = grouped_by
        self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
            self.grouped_by
        ]
        self.metric_column = "Time"
        self.sorting_order = "mean"
        self.n_best = 15

        super().__init__(
            grouped_by,
            season,
            title=f"{self.grouped_by}s Pit Stop Times",
            xlabel=["Pit Stop Time", "s"],
            subtitle=f"{season} Formula 1 Season",
            description=f"[{self.n_best} Best/Quickest Pit Stop Times for Drivers and Teams across the Grands Prix of the {season} season. Ordered by {self.grouped_by} {self.sorting_order}.]",
            xlimits=dict(Driver=[1.75, 3.75], Team=[1.75, 3.25])[self.grouped_by],
            locators=(0.5, 0.1),
        )
        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()
        self.export(
            os.path.join(
                analysis_directory,
                "aggregating",
                f"{self.season}_{self.grouped_by}s_Pit_Stop_Times.png",
            )
        )

    def prepare_data(self):
        self.df = get_all_pitstop_times(self.season)

        self.sorting_column_name = (
            f"{self.sorting_order.capitalize()}{self.metric_column.capitalize()}"
        )
        fifteen_best = (
            self.df.groupby(self.grouped_by, sort=False)
            .apply(lambda group: group.nsmallest(self.n_best, [self.metric_column]))
            .reset_index(drop=True)
        )

        self.df = fifteen_best

        self.df[self.sorting_column_name] = self.df.groupby(
            self.grouped_by, sort=False
        )[self.metric_column].transform(self.sorting_order)

        self.df = self.df.sort_values(self.sorting_column_name, ascending=True)
        self.df = self.df.groupby(self.grouped_by, sort=False)

    def plot_data(self):
        for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
            competitor_color = self.color_getter(self.season, competitor_name)
            ax.barh(
                y=[0],
                width=[competitor_data[self.metric_column].agg(self.sorting_order)],
                color=competitor_color,
                height=1,
                align="edge",
                alpha=1 / 4,
            )

            violin_parts = ax.violinplot(
                competitor_data[self.metric_column],
                [0.5],
                vert=False,
                widths=0.85,
                showextrema=False,
                bw_method=lambda _: 0.2,
            )
            for part in violin_parts["bodies"]:
                part.set_facecolor(competitor_color)
                part.set_alpha(1 / 3)
            ax.scatter(
                x=competitor_data[self.metric_column],
                y=[0.5] * len(competitor_data),
                s=dict(Driver=100, Team=200)[self.grouped_by],
                c=competitor_color,
                alpha=1 / 6,
            )
            # x_range = np.arange(*self.xlimits, 0.02)
            # in_range_values = sorted(
            #     competitor_data[
            #         competitor_data[self.metric_column].between(*self.xlimits)
            #     ][self.metric_column]
            # )
            # densities = stats.gaussian_kde(in_range_values, bw_method=lambda _: 0.2)(
            #     x_range
            # )
            # densities_scaled = densities * (0.8 / max(densities))
            # ax.fill_between(
            #     x_range, densities_scaled, color=competitor_color, alpha=1 / 2
            # )


class TimeInPitlaneAnalysis(Aggregation):
    def __init__(self, season, grouped_by):
        self.grouped_by = grouped_by
        self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
            self.grouped_by
        ]
        self.sorting_order = "median"
        self.metric_column = "TimeInPitlane"

        super().__init__(
            grouped_by,
            season,
            title=f"{self.grouped_by}s Pitlane Times",
            xlabel=["Time in Pitlane", "s"],
            subtitle=f"{season} Formula 1 Season",
            description=f"[KDE of Time from Pit Entry to Exit in Pit Stops at all Grands Prix except Monaco. Corrected for pitlane length. Ordered by {self.grouped_by} {self.sorting_order}.]",
            xlimits=[21.5, 27.5],
            locators=(1, 0.25),
        )
        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()
        self.export(
            os.path.join(
                analysis_directory,
                "aggregating",
                f"{self.season}_{self.grouped_by}s_Pitlane_Times.png",
            )
        )

    def prepare_data(self):
        self.df = get_all_pitstop_laps(self.season)
        self.df = self.df[self.df["Meeting"] != "Monaco Grand Prix"]
        self.sorting_column_name = (
            f"{self.sorting_order.capitalize()}{self.metric_column.capitalize()}"
        )
        races_pitlane_distance = dict()
        for race, data in self.df.groupby("Meeting"):
            races_pitlane_distance[race] = data["PitlaneDistance"].median()
        pitlane_distance_median = self.df["PitlaneDistance"].agg(self.sorting_order)
        self.df[self.metric_column] = self.df.apply(
            lambda row: row[self.metric_column]
            - 0.045 * (row["PitlaneDistance"] - pitlane_distance_median),
            axis=1,
        )
        self.df = self.df[self.df["TimeInPitlane"] > 20]

        self.df[self.sorting_column_name] = self.df.groupby(
            self.grouped_by, sort=False
        )[self.metric_column].transform(self.sorting_order)
        self.df = self.df.sort_values(self.sorting_column_name, ascending=True)
        self.df = self.df.groupby(self.grouped_by, sort=False)

    def plot_data(self):
        for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
            competitor_color = self.color_getter(self.season, competitor_name)
            ax.barh(
                y=[0],
                width=[competitor_data[self.metric_column].agg(self.sorting_order)],
                color=competitor_color,
                height=1,
                align="edge",
                alpha=1 / 4,
            )
            x_range = np.arange(*self.xlimits, 0.1)
            in_range_values = competitor_data[
                competitor_data[self.metric_column].between(*self.xlimits)
            ][self.metric_column]
            densities = stats.gaussian_kde(in_range_values, bw_method=lambda _: 0.15)(
                x_range
            )
            densities_scaled = densities * (0.8 / max(densities))
            ax.fill_between(
                x_range, densities_scaled, color=competitor_color, alpha=1 / 2
            )


class DRSActivationAnalysis(Aggregation):
    def __init__(self, season, grouped_by):
        self.grouped_by = grouped_by
        self.color_getter = dict(
            Driver=get_driver_color, Team=get_team_color, Race=lambda x, y: "#DCDCDC"
        )[self.grouped_by]

        description = (
            f"[Shows total number of DRS Activations for each of the season's Grands Prix. Note: the number of DRS-zones varies between tracks.]"
            if self.grouped_by == "Meeting"
            else f"[Shows total number of DRS Activations for each {self.grouped_by} throughout the season's 22 Grands Prix.\nBars are stacked, one for each race, in championship order, alternating in opacity.]"
        )
        super().__init__(
            grouped_by,
            season,
            # title=f"{self.grouped_by}s DRS Activations",
            title=f"{self.grouped_by} DRS Activations",
            xlabel=["Number of DRS Activations", None],
            subtitle=f"{season} Formula 1 Season",
            description=description,
            xlimits=[0, dict(Driver=545, Team=1090, Race=880)[self.grouped_by]],
            locators=dict(Driver=(100, 25), Team=(200, 50), Race=(200, 50))[
                self.grouped_by
            ],
        )
        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()
        self.export(
            os.path.join(
                analysis_directory,
                "aggregating",
                f"{self.season}_{self.grouped_by}s_DRS_Activations.png",
            )
        )

    def prepare_data(self):
        self.df = get_DRS_activations(self.season)
        self.df["TotalDRSActivations"] = self.df.groupby(self.grouped_by, sort=False)[
            "AmountDRSActivations"
        ].transform(sum)
        self.df = self.df.sort_values("TotalDRSActivations", ascending=False)
        if (
            self.grouped_by == "Meeting"
        ):  # add entries for the two weekends of the Belgian- and Turkish Grand Prix in which DRS was never allowed
            races_included = [
                name for name, group in self.df.groupby(self.grouped_by, sort=False)
            ]
            for race in TRACK_LENGTHS.keys():
                if race not in races_included:
                    self.df = self.df.append(
                        dict(Race=race, AmountDRSActivations=0), ignore_index=True
                    )
        self.df["RaceFullName"] = self.df["Meeting"]
        # self.df["Meeting"] = self.df["Meeting"].apply(lambda race_name: race_name.replace("Grand Prix", "GP")) # shortening race names
        self.df = self.df.groupby(self.grouped_by, sort=False)

    def plot_data(self):
        for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
            competitor_color = self.color_getter(self.season, competitor_name)
            total_activations = competitor_data["AmountDRSActivations"].agg(sum)
            rolling_sum = 0
            competitor_data["RaceRank"] = competitor_data["RaceFullName"].map(
                {race: rank + 1 for rank, race in enumerate(TRACK_LENGTHS)}
            )
            competitor_data.sort_values("RaceRank", inplace=True)
            if self.grouped_by == "Meeting":
                ax.barh(
                    y=[0],
                    width=[total_activations],
                    color=competitor_color,
                    height=1,
                    align="edge",
                    alpha=1 / 4,
                )
            else:
                for index, (race_name, race_data) in enumerate(
                    competitor_data.groupby("Meeting", sort=False)
                ):
                    race_activations = race_data["AmountDRSActivations"].agg(sum)

                    ax.barh(
                        y=[0],
                        width=[race_activations],
                        left=rolling_sum,
                        color=competitor_color,
                        height=1,
                        align="edge",
                        alpha=1 / 4 if index % 2 else 1 / 3,
                    )
                    rolling_sum += race_activations


class RPMDistributionAnalysis(Aggregation):
    def __init__(self, season, grouped_by):
        self.grouped_by = grouped_by
        self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
            self.grouped_by
        ]

        self.sorting_order = "median"
        self.metric_column = "TimeInPitlane"

        super().__init__(
            grouped_by,
            season,
            title=f"{self.grouped_by}s Engine RPM",
            xlabel=["Engine RPM", None],
            subtitle=f"{season} Formula 1 Season",
            description=f"[Running Engine RPM prior during all of the season's Grands Prix. Ordered by {self.grouped_by} median.]",
            xlimits=[8750, 12750],
            locators=(500, 125),
        )
        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()
        self.export(
            os.path.join(
                analysis_directory,
                "aggregating",
                f"{self.season}_{self.grouped_by}s_Engine_RPM_Distribution.png",
            )
        )

    def prepare_data(self):
        self.df = get_all_engine_data(self.season)
        self.df[self.sorting_order] = self.df.groupby(self.grouped_by)["RPM"].transform(
            self.sorting_order
        )
        self.df.sort_values(self.sorting_order, ascending=False, inplace=True)
        self.df = self.df.groupby(self.grouped_by, sort=False)

    def plot_data(self):
        for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
            competitor_color = self.color_getter(self.season, competitor_name)
            ax.barh(
                y=[0],
                width=[competitor_data.iloc[0][self.sorting_order]],
                color=competitor_color,
                height=1,
                align="edge",
                alpha=1 / 4,
            )
            ax.hist(
                competitor_data["RPM"],
                range=self.xlimits,
                bins=100,
                weights=np.ones(len(competitor_data)) / len(competitor_data) * 40,
                color=competitor_color,
                alpha=1 / 2,
            )


class SectionTimesAnalysis(Aggregation):
    def __init__(self, season, grouped_by, meeting, selected_session, turns):
        self.grouped_by = grouped_by
        self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
            self.grouped_by
        ]

        super().__init__(
            grouped_by,
            season,
            title=f"{self.grouped_by}s Turn {min(turns)}"
            + (f"-{max(turns)}" if len(turns) > 1 else ""),
            xlabel=["Approx. laptime loss", "s"],
            subtitle=f"{season} {meeting} - {selected_session}",
            description=f"""[Fastest time through the highlighted section, spanning turn{"s" if len(turns) > 1 else ""} {turns[0]}{"-" + str(turns[-1]) if len(turns) > 1 else ""}.\nOrdered by fastest run through the section, not neccesesarily occuring in a driver's fastest lap of the session.]""",
        )
        self.prepare_data(meeting, selected_session, turns)
        self.create_figure()

        example_lap = add_track_locations(
            enhance_telemetry(
                get_session(season, meeting, selected_session).laps.pick_fastest()
            )
        )
        # rotate track map if its width is greater than its height
        if (
            example_lap.telemetry["X"].abs().max()
            > example_lap.telemetry["Y"].abs().max()
        ):
            rotate_track(example_lap, degrees=90)
        trackmap_axis = self.figure.add_axes(
            [
                0.5,
                0.35,
                0.5,
                0.5,
            ],
            zorder=-1,
        )
        trackmap_axis.plot(
            example_lap.telemetry["X"],
            example_lap.telemetry["Y"],
            color=GRAY_DARK,
            linewidth=10,
        )
        in_section = example_lap.telemetry[
            example_lap.telemetry["Section"]
            .str.slice(start=1)
            .isin([str(turn) for turn in turns])
        ]
        trackmap_axis.plot(
            in_section["X"], in_section["Y"], color=MUTED_COLOR, linewidth=10
        )
        trackmap_axis.set_aspect("equal")
        trackmap_axis.set_axis_off()
        trackmap_axis.margins(x=0.1, y=0.1)

        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()
        fastest, slowest = self.axes[0].dataLim.x1, self.axes[-1].dataLim.x1
        for ax in list(self.axes) + [self.bottom_axes]:
            ax.set_xlim(fastest, slowest * 1.1)
        self.bottom_axes.xaxis.set_minor_locator(AutoMinorLocator(n=5))
        self.export(
            os.path.join(
                analysis_directory,
                "aggregating",
                f"{self.season}_{meeting}_{selected_session}_{self.grouped_by}s_Section_Times-T{min(turns)}-T{max(turns)}.png",
            )
        )

    def prepare_data(self, meeting, selected_session, turns):
        self.df = get_section_times(self.season)
        print(self.df)
        # self.df = self.df[
        # (self.df["Meeting"] == meeting) & (self.df["Session"] == selected_session)
        # ]
        print(self.df)
        self.df = self.df[
            self.df["SectionName"]
            .str.slice(start=1)
            .isin([str(turn) for turn in turns])
        ]
        groupers = (
            ["Driver", "LapNumber"]
            if self.grouped_by == "Driver"
            else ["Driver", "LapNumber"]
        )
        self.df = (
            self.df.groupby(groupers)
            .agg(dict(Time="sum"))
            .reset_index()
            .sort_values("Time", ascending=True)
        )
        self.df["Team"] = self.df["Driver"].apply(
            lambda val: get_team(self.season, val)
        )
        self.df["Time"] = self.df["Time"] - self.df["Time"].min()
        self.df = self.df.groupby(self.grouped_by, sort=False)

    def plot_data(self):
        for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
            competitor_color = self.color_getter(self.season, competitor_name)
            ax.barh(
                y=[0],
                width=[competitor_data["Time"].min()],
                color=competitor_color,
                height=1,
                align="edge",
                alpha=1 / 4,
            )


class UpshiftRPMAnalyis(Aggregation):
    def __init__(self, season, grouped_by, session_selection):
        self.grouped_by = grouped_by
        self.session_selection = session_selection
        self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
            self.grouped_by
        ]

        super().__init__(
            grouped_by,
            season,
            title=f"{self.grouped_by.upper()}S UPSHIFT RPM",
            xlabel=["Engine RPM at Upshift", None],
            subtitle=f"{season} Bahrain Grand Prix",
            description=f"""[Engine RPM prior to upshifts made during the 2022 Bahrain Grand Prix. Ordered by {self.grouped_by} median.]""",
            xlimits=[10250, 12250],
            locators=(500, 100),
        )
        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()
        self.export(
            os.path.join(
                analysis_directory,
                "aggregating",
                f"{self.season}_{self.grouped_by}s_Upshift_RPM.png",
            )
        )

    def prepare_data(self):
        self.df = get_all_upshifts(self.season)
        self.df["MedianUpshiftRPM"] = self.df.groupby(self.grouped_by)["RPM"].transform(
            "median"
        )
        self.df.sort_values("MedianUpshiftRPM", ascending=False, inplace=True)
        self.df = self.df.groupby(self.grouped_by, sort=False)

    def plot_data(self):
        for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
            competitor_color = self.color_getter(self.season, competitor_name)
            ax.barh(
                y=[0],
                width=[competitor_data.iloc[0]["MedianUpshiftRPM"]],
                color=competitor_color,
                height=1,
                align="edge",
                alpha=1 / 4,
            )
            ax.hist(
                competitor_data["RPM"],
                range=self.xlimits,
                bins=100,
                weights=np.ones(len(competitor_data)) / len(competitor_data) * 17,
                color=competitor_color,
                alpha=1 / 2,
            )


class SingleRaceUpshiftRPMAnalyis(Aggregation):
    def __init__(self, season, grouped_by, selected_race):
        self.grouped_by = grouped_by
        self.selected_race = selected_race
        self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
            self.grouped_by
        ]

        super().__init__(
            grouped_by,
            season,
            title=f"{self.grouped_by.upper()}S UPSHIFT RPM",
            xlabel=["Engine RPM at Upshift", None],
            subtitle=f"{season} {self.selected_race}",
            description=f"""[Engine RPM prior to upshifts made at the {season} {self.selected_race}. Wet tire laps excluded. Ordered by {self.grouped_by} median.]""",
            xlimits=[10750, 12750],
            locators=(500, 100),
        )
        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()
        self.export(
            os.path.join(
                analysis_directory,
                "aggregating",
                f"""{self.season}_{self.selected_race.replace(" ", "_")}_{self.grouped_by}s_Upshift_RPM.png""",
            )
        )

    def prepare_data(self):
        self.df = get_all_upshifts(self.season, self.selected_race)
        self.df = self.df[self.df["Meeting"] == self.selected_race]
        self.df["MedianUpshiftRPM"] = self.df.groupby(self.grouped_by)["RPM"].transform(
            "median"
        )
        self.df.sort_values("MedianUpshiftRPM", ascending=False, inplace=True)
        self.df = self.df.groupby(self.grouped_by, sort=False)

    def plot_data(self):
        for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
            competitor_color = self.color_getter(self.season, competitor_name)
            ax.barh(
                y=[0],
                width=[competitor_data.iloc[0]["MedianUpshiftRPM"]],
                color=competitor_color,
                height=1,
                align="edge",
                alpha=1 / 4,
            )
            ax.hist(
                competitor_data["RPM"],
                range=self.xlimits,
                bins=100,
                weights=np.ones(len(competitor_data)) / len(competitor_data) * 17,
                color=competitor_color,
                alpha=1 / 2,
            )


class StintPaceAnalysis(Aggregation):
    def __init__(self, season, grouped_by, meeting, session):
        self.grouped_by = grouped_by
        self.meeting = meeting
        self.session = session
        self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
            self.grouped_by
        ]

        super().__init__(
            grouped_by,
            season,
            title=f"""{self.grouped_by}s Stint Pace""",
            xlabel=["Median Laptime", "sec."],
            subtitle=f"{season} {self.meeting}",
            description=f"""[Median laptime on high-fuel stints during {season} {self.selected_meeting} {self.selected_session}. Ordered by {self.grouped_by} median.]""",
            xlimits=[285, 325],
            locators=(1, 0.2),
        )
        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()
        self.export(
            os.path.join(
                analysis_directory,
                "aggregating",
                f"""{self.season}_{self.selected_meeting.replace(" ", "_")}_{self.grouped_by}s_StintPace.png""",
            )
        )

    def prepare_data(self):
        session = get_session(2022, self.selected_meeting, self.selected_session)
        self.df = session.laps

        self.df["Day"] = (
            self.df["LapStartDate"]
            .dt.day.fillna(0)
            .apply(lambda day_of_month: {10: 1, 11: 2, 12: 3}.get(int(day_of_month), 0))
        )
        self.df["TimeOfDay"] = (
            source["Time"]
            .dt.total_seconds()
            .apply(
                lambda secs: f"{int(secs // 3600):02d}:{int(secs % 3600) // 60:02d}:{int(secs % 3600) % 60:02d}"
            )
        )
        self.df["Time"] = self.df["Time"].dt.total_seconds()
        self.df["LapTime"] = self.df["LapTime"].dt.total_seconds()
        self.df["Compound"] = self.df["Compound"].str.capitalize()
        # self.df = self.df[self.df["IsAccurate"]]
        self.df["Stint"] = self.df.groupby("Driver")["PitOutTime"].transform(
            lambda group: (~group.isnull()).cumsum()
        )
        source = (
            self.df.groupby(["Driver", "Stint"])
            .apply(lambda group: group.iloc[1:-1])
            .reset_index(drop=True)
        )
        source["StintLength"] = (
            self.df.groupby(["Driver", "Stint"])["LapNumber"].transform(len).fillna(1)
        )
        min_stint_length_for_long_run = 8
        self.df = self.df[(self.df["StintLength"] - 3) > min_stint_length_for_long_run]
        self.df["Label"] = self.df.apply(
            lambda row: f"""{row["Driver"]} R{int(row["Stint"])} {row["Compound"]} ({int(row["StintLength"])})""",
            axis=1,
        )
        self.df["LapNumber"] = self.df.groupby("Label")["LapNumber"].transform(
            lambda group: group - group.min()
        )

        ordering_function = lambda row: self.df[
            self.df[self.grouped_by] == row[self.grouped_by]
        ][self.speed_channel].median()
        self.df["MedianSpeed"] = self.df.apply(ordering_function, axis=1)
        self.df.sort_values("MedianSpeed", ascending=False, inplace=True)
        self.df = self.df.groupby(self.grouped_by, sort=False)

    def plot_data(self):
        for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
            competitor_color = self.color_getter(self.season, competitor_name)
            print(competitor_name, len(competitor_data))

            ax.barh(
                y=[0],
                width=[competitor_data.iloc[0]["MedianLapTime"]],
                color=competitor_color,
                height=1,
                align="edge",
                alpha=1 / 4,
            )


class SpeedTrapAnalysis(Aggregation):
    def __init__(
        self, season, grouped_by, selected_meeting, selected_session, include_DRS=None
    ):
        self.grouped_by = grouped_by
        self.selected_meeting = selected_meeting
        self.selected_session = selected_session
        self.include_DRS = include_DRS
        self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
            self.grouped_by
        ]

        super().__init__(
            grouped_by,
            season,
            title=f"""{self.grouped_by}s Top Speed (DRS)""",
            xlabel=["Maximum Velocity", "km/h"],
            subtitle=f"{season} {self.selected_meeting} - {self.selected_session}",
            description=f"""[Density distribution of top speeds measured on laps using DRS during {season} {self.selected_meeting} {self.selected_session}. Ordered by {self.grouped_by} median.]""",
            xlimits=[295, 335] if self.include_DRS else [275, 325],
            locators=(10, 2),
        )
        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()
        self.export(
            os.path.join(
                analysis_directory,
                "aggregating",
                f"""{self.season}_{self.selected_meeting.replace(" ", "_")}_{self.selected_session}_{self.grouped_by}s_SpeedTraps_{"With" if self.include_DRS else "No"}_DRS.png""",
            )
        )

    def prepare_data(self):
        self.speed_channel = "SpeedST"
        # self.speed_channel = "SpeedMax"
        self.DRS_channel = "UsedDRS"

        session = get_session(2022, self.selected_meeting, self.selected_session)
        self.df = session.laps[session.laps["IsAccurate"]]

        # self.df = self.df.head()
        # if self.selected_session == "FP1-2":
        #     session = get_session(2022, self.selected_meeting, "FP1")
        #     self.df = pd.concat([session.laps, get_session(2022, self.selected_meeting, "FP2").laps])

        def used_DRS(lap):
            telem = lap.get_telemetry()
            try:
                return telem.iloc[:200]["DRS"].isin([10, 12, 14]).sum() > 0 or telem.iloc[-200:]["DRS"].isin([10, 12, 14]).sum() > 0
            except:
                return False

        self.df[self.DRS_channel] = self.df.apply(used_DRS, axis=1)

        def max_speed(lap):
            telem = lap.get_telemetry()
            try:
                return telem["Speed"].max()
            except:
                return 0

        self.df[self.speed_channel] = self.df.apply(max_speed, axis=1)

        # def new_channels(lap):
        #     try:
        #         telem = lap.get_telemetry()
        #         return (
        #             telem["Speed"].max(),
        #             telem.iloc[:200]["DRS"].isin([10, 12, 14]).sum() > 0,
        #         )
        #     except:
        #         return (np.nan, False)

        # self.df[[self.speed_channel, self.DRS_channel]] = self.df.apply(
        #     new_channels, axis=1
        # )

        # self.df.to_pickle("test.pkl")
        # self.df = pd.read_pickle("test.pkl")

        self.df["Team"] = self.df["Driver"].apply(
            lambda driver: get_team(self.season, driver)
        )

        self.df.dropna(subset=self.speed_channel, inplace=True)

        self.df = self.df[self.df[self.speed_channel] > 280].pick_quicklaps(threshold=1.1)
        if self.include_DRS is True:
            self.df = self.df[self.df[self.DRS_channel]]
        elif self.include_DRS is False:
            self.df = self.df[~self.df[self.DRS_channel]]

        self.df["MedianSpeed"] = self.df.groupby(self.grouped_by)["SpeedST"].transform(
            np.median
        )
        print(self.df)
        self.df.sort_values("MedianSpeed", ascending=False, inplace=True)
        self.df = self.df.groupby(self.grouped_by, sort=False)

    def plot_data(self):
        for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
            competitor_color = self.color_getter(self.season, competitor_name)
            print(competitor_name, len(competitor_data))

            tail_length = 30
            # x_range = range(
            #     int(competitor_data[self.speed_channel].min()) - tail_length,
            #     int(competitor_data[self.speed_channel].max()) + tail_length,
            #     1,
            # )
            x_range = range(
                *self.xlimits,
                1,
            )
            densities = stats.gaussian_kde(
                competitor_data[self.speed_channel], bw_method=lambda _: 0.5
            )(x_range)
            densities_scaled = densities * (0.8 / max(densities))
            ax.fill_between(
                x_range, densities_scaled, color=competitor_color, alpha=1 / 2
            )
            ax.scatter(
                x=competitor_data[self.speed_channel],
                y=[1 / 2] * len(competitor_data),
                s=dict(Driver=100, Team=200)[self.grouped_by],
                c=competitor_color,
                alpha=1 / 4,
            )
            ax.barh(
                y=[0],
                width=[competitor_data.iloc[0]["MedianSpeed"]],
                color=competitor_color,
                height=1,
                align="edge",
                alpha=1 / 4,
            )


class LaunchTimesAnalysis(Aggregation):
    def __init__(self, season, grouped_by):
        self.grouped_by = grouped_by
        self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
            self.grouped_by
        ]

        super().__init__(
            grouped_by,
            season,
            title=f"{self.grouped_by}s 0-200 Times",
            xlabel=["Time from 0 to 200 km/h", "s"],
            subtitle=f"{season} Formula 1 Season",
            description=f"[Times from 0-200 km/h at the race start of each Grand Prix. Wet tire laps excluded. Ordered by {self.grouped_by} median.]",
            xlimits=[4.4, 5.6],
            locators=(0.25, 0.0625),
        )
        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()
        self.export(
            os.path.join(
                analysis_directory,
                "aggregating",
                f"{self.season}_{self.grouped_by}s_Launch_Times.png",
            )
        )

    def prepare_data(self):
        self.df = get_all_launches(self.season)
        self.df["MedianTime"] = self.df.groupby(self.grouped_by)["Time"].transform(
            "median"
        )
        self.df.sort_values("MedianTime", ascending=True, inplace=True)
        self.df = self.df.groupby(self.grouped_by, sort=False)

    def plot_data(self):
        for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
            competitor_color = self.color_getter(self.season, competitor_name)
            ax.barh(
                y=[0],
                width=[competitor_data.iloc[0]["MedianTime"]],
                color=competitor_color,
                height=1,
                align="edge",
                alpha=1 / 4,
            )

            ax.scatter(
                x=competitor_data["Time"],
                y=[1 / 2] * len(competitor_data),
                s=dict(Driver=100, Team=200)[self.grouped_by],
                c=competitor_color,
                alpha=1 / 6,
            )


class LaunchRPMAnalyis(Aggregation):
    def __init__(self, season, grouped_by):
        self.grouped_by = grouped_by
        self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
            self.grouped_by
        ]

        super().__init__(
            grouped_by,
            season,
            title=f"{self.grouped_by}s Launch RPM",
            xlabel=["Engine RPM at Launch", None],
            subtitle=f"{season} Formula 1 Season",
            description=f"[Engine RPM prior to launch at the race start of each Grand Prix. Wet tire laps excluded. Ordered by {self.grouped_by} median.]",
            xlimits=[7750, 12250],
            locators=(500, 125),
        )
        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()
        self.export(
            os.path.join(
                analysis_directory,
                "aggregating",
                f"{self.season}_{self.grouped_by}s_Launch_RPM.png",
            )
        )

    def prepare_data(self):
        self.df = get_all_launches(self.season)
        self.df["MedianLaunchRPM"] = self.df.groupby(self.grouped_by)["RPM"].transform(
            "median"
        )
        self.df.sort_values("MedianLaunchRPM", ascending=True, inplace=True)
        self.df = self.df.groupby(self.grouped_by, sort=False)

    def plot_data(self):
        for ax, (competitor_name, competitor_data) in zip(self.axes, self.df):
            competitor_color = self.color_getter(self.season, competitor_name)
            ax.barh(
                y=[0],
                width=[competitor_data.iloc[0]["MedianLaunchRPM"]],
                color=competitor_color,
                height=1,
                align="edge",
                alpha=1 / 4,
            )
            ax.scatter(
                x=competitor_data["RPM"],
                y=[1 / 2] * len(competitor_data),
                s=dict(Driver=100, Team=200)[self.grouped_by],
                c=competitor_color,
                alpha=1 / 6,
            )


class PowerOutputAnalysis(Aggregation):
    def __init__(self, season, grouped_by):
        self.grouped_by = grouped_by
        self.color_getter = dict(Driver=get_driver_color, Team=get_team_color)[
            self.grouped_by
        ]

        super().__init__(
            grouped_by,
            season,
            title=f"{self.grouped_by}s Engine Power",
            xlabel=["", None],
            subtitle="",
            description=f"",
        )
        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.plot_data()
        self.export(
            os.path.join(
                "tests",
                "engine_output.png",
            )
        )

    def prepare_data(self):
        test = get_session(2021, "United States Grand Prix", "Q")
        selected = []
        for driver_identifier, laps in laps_per_driver(test):
            if not driver_identifier in ["HAM", "VER", "LEC"]:
                continue
            lap = enhance_telemetry(laps.pick_fastest())
            # lap.telemetry = lap.telemetry[lap.telemetry["Throttle"] > 99]
            lap.telemetry = lap.telemetry.iloc[2600:3550]
            # lap.telemetry["Acceleration"] = savgol_filter(
            #         np.gradient(lap.telemetry["Speed"]), window_length=149, polyorder=1
            #     )
            lap.telemetry["Acceleration"] = (
                savgol_filter(
                    np.gradient(lap.telemetry["Speed"])
                    / np.gradient(lap.telemetry["TimeInSeconds"]),
                    window_length=299,
                    polyorder=1,
                )
                / 9.81
            )
            # lap.telemetry = lap.telemetry[lap.telemetry["Acceleration"] > 0]
            # lap.telemetry["HorsePower"] = (lap.telemetry["Acceleration"] * 795 * lap.telemetry["Speed"])
            selected.append(lap)
            # sqrt((2*795*9.81)/(1.17*1.75))*3.6

        self.df = selected

    def plot_data(self):
        # ax = self.figure.add_subplot(projection="3d")
        ax = self.figure.add_axes([0.05, 0.05, 0.9, 0.8])
        # plt.ylim(-3, 1.5)
        for lap in self.df:
            # plt.plot(lap.telemetry["Distance"], lap.telemetry["Speed"], color=lap["Color"], linewidth=2, alpha=.5)
            # plt.plot(lap.telemetry["Distance"], lap.telemetry["Acceleration"], color=lap["Color"], linewidth=2, alpha=.5)
            # plt.hist(lap.telemetry["Acceleration"], bins=30, color=lap["Color"], linewidth=2, alpha=.4)
            plt.scatter(
                lap.telemetry["Distance"],
                lap.telemetry["Acceleration"],
                color=lap["Color"],
                s=2,
                alpha=0.2,
            )
            # plt.scatter(lap.telemetry["Speed"], lap.telemetry["HorsePower"], color=lap["Color"], s=2, alpha=.2)
            # plt.scatter(lap.telemetry["Distance"], lap.telemetry["Gear"], color=lap["Color"], s=2, alpha=.2)
            # plt.scatter(lap.telemetry["Distance"], lap.telemetry["RPM"], color=lap["Color"], s=2, alpha=.2)
