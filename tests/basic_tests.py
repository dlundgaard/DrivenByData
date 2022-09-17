from turtle import width
import unittest
import pickle
import pandas
import numpy
from sklearn.linear_model import LinearRegression
from sklearn import preprocessing
from scipy import optimize
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator, NullLocator

from getters import *

class TestGetters(unittest.TestCase):
    def test_aston_martin_error(self):
        self.assertNotEqual(sum([1, 2, 3]), 5, "Should be 6")

# if __name__ == "__main__":
    # unittest.main()

# fill_local_cache()

# rpms, gears = None, None
# with open("caches/rpm_data.pkl", "rb") as f:
#     rpms = pickle.load(f)
# with open("caches/gear_data.pkl", "rb") as f:
#     gears = pickle.load(f)
# plt.hist(rpms, range=(9000, 13000), bins=40)
# plt.show()
# df = get_all_racing_laps(2021, selected_rounds=[19])
# df["GapToDriverAhead"] = df["GapToDriverAhead"].apply(lambda time: time.total_seconds())
# gap_ahead_max = 2
# df = df[df["GapToDriverAhead"] < gap_ahead_max]
# df = df[df["SpeedAtFinishLine"] > 290]
# df = df.sort_values(["Team", "GapToDriverAhead"])
# print(list(df["GapToDriverAhead"].apply(lambda time: time.total_seconds()).unique()))
# df = df.dropna(subset=["SpeedAtFinishLine", "GapToDriverAhead"])

# without_DRS = df[df["UsedDRSAtFinishLine"] == False]
# with_DRS = df[df["UsedDRSAtFinishLine"] == True]

# subset = without_DRS[without_DRS["Team"].isin(["Alfa Romeo", "McLaren"])]
# fig, axes = plt.subplots(5, 2, figsize=(3840 / 300, 3840 / 300))
# fig.subplots_adjust(left=0.05, right=0.95, bottom=0.05, top=0.95, wspace=0.1, hspace=0.25)

# for index, (team, subset) in enumerate(df.groupby("Team", sort=False)):
#     ax = fig.axes[index]
#     ax.text(0.5, 0.8, team, fontdict=dict(fontsize=12, weight="black"), transform=ax.transAxes, ha="center")

#     # for a, b in zip(subset["GapToDriverAhead"], y):
#     #     print(a, "->", b)
#     # reg = LinearRegression().fit(x, y)
#     # print(f"{reg.coef_[0]}x + {reg.intercept_}")
#     # print("R^2", reg.score(x, y))
#     # x, y = subset["GapToDriverAhead"].values.reshape(-1, 1), subset["SpeedAtFinishLine"]
#     # scaler = preprocessing.StandardScaler().fit(x)
#     # x = scaler.transform(x).reshape(1, -1)[0]

#     legends = []
#     for DRS_used in [True, False]:
#         data = subset[subset["UsedDRSAtFinishLine"] == DRS_used]
#         data = data[data["GapToDriverAhead"] < (1.5 if DRS_used else gap_ahead_max)]

#         x, y = data["GapToDriverAhead"], data["SpeedAtFinishLine"]
#         exponential_func = lambda x, a, b: a*x + b
#         fit = optimize.curve_fit(exponential_func, x, y, maxfev=100000)
#         a, b = fit[0]
#         fitted_func = f"{round(a, 2)}^x + {round(b, 2)}"
#         # fitted_func = f"{round(a, 2)}*{round(b, 2)}^x + {round(b, 2)}"
#         legends.append(fitted_func)

#         team_color = get_team_color(2021, team)
#         curve = exponential_func(x, a, b)
#         if DRS_used:
#             ax.scatter(x, y, s=40, alpha=1 / 2, facecolor="None", edgecolor=team_color)
#             ax.plot(x, curve, color=team_color, linestyle="--")
#         else:
#             ax.scatter(x, y, s=20, alpha=1 / 2, color=team_color)
#             ax.plot(x, curve, color=team_color)

#     ax.set_xlim(0, gap_ahead_max)
#     ax.set_xticks(range(gap_ahead_max + 1))
#     ax.tick_params(axis="both", labelsize=8)
#     ax.set_ylim(295, 340)
#     ax.yaxis.set_major_locator(MultipleLocator(5))
#     ax.yaxis.set_minor_locator(MultipleLocator(1))
#     ax.legend(ax.get_lines(), legends, loc="upper right", fontsize=12)
#     ax.grid()

# fig.savefig("tests/2021_São_Paulo_Grand_Prix_Tow_Effect.png", dpi=300)

# def func(row):
#     recorded_speed = row["SpeedAtFinishLine"]
#     if row["GapToDriverAhead"] > 2:
#         return recorded_speed
#     # if row["UsedDRSAtFinishLine"]:
#         # recorded_speed -= 15
#     recorded_speed -= 5 * (2 - row["GapToDriverAhead"])
#     return recorded_speed
# df["TowAndDRSCorrectedSpeedAtFinishLine"] = df.apply(func, axis=1)
# print(df[["Driver", "UsedDRSAtFinishLine", "GapToDriverAhead", "SpeedAtFinishLine", "TowAndDRSCorrectedSpeedAtFinishLine"]])

# get_first_corner_braking_points(2021)
# get_laps_in_DRS(2021)
# get_all_racing_laps(2021)

# df = get_all_pitstops(2021)
# print(df)
# for driver, group in df.groupby("Driver"):
#     print(driver, len(group))

# df = get_all_gearshifts(2021)
# print(df)
    
# print("engine")
# df = get_all_engine_data(2021)
# print(len(df))
# print(df["Race"].unique())
# print(df["Driver"].unique())
# for name, group in df.groupby("Driver"):
#     print(name)
    
#     for race, race_group in group.groupby("Race"):
#         print(race, "median", race_group["RPM"].median(), "mean", race_group["RPM"].mean())
#         print(race_group.sort_values("RPM", ascending=False).head(10)["RPM"].values)

# print("launch")
# df = get_all_launches(2021)
# print(len(df))
# for name, group in df.groupby("Driver"):
#     print(name)
#     print(group.loc[group["RPM"].idxmax()])


# print("upshift")
# df = get_all_upshifts(2021, "R")
# print(len(df))
# print(df["Race"].unique())
# print(df["Driver"].unique())

# to_2nd = df[df["ToGear"] == 2]
# print(to_2nd)
# for name, group in df.groupby("Driver"):
#     print(name)
    
    # for race, race_group in group.groupby("Race"):
    #     print(race) 
    #     print("median", race_group["RPM"].median())
    #     print("mean", race_group["RPM"].mean())
    #     print(race_group.sort_values("RPM", ascending=False).head(10)["RPM"].values)
