import os
import altair as alt
from matplotlib import image, patches, animation, pyplot as plt
from matplotlib.text import Annotation
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
from matplotlib.offsetbox import (
    AnnotationBbox,
    HPacker,
    VPacker,
    TextArea,
    OffsetImage,
    DrawingArea,
)
from getters import *


class Aggregation:
    def __init__(
        self,
        grouped_by,
        season=None,
        title=None,
        subtitle=None,
        xlabel=None,
        description=None,
        xlimits=None,
        locators=None,
    ):
        self.grouped_by = grouped_by
        self.season = season
        self.title = title
        self.subtitle = subtitle
        self.description = description
        self.xlabel = xlabel
        self.xlimits = xlimits
        self.locators = locators
        if locators:
            self.major_locator, self.minor_locator = self.locators

    def create_figure(self):
        self.insets = dict(
            left=0.15 - 0.002 * len(self.df),
            right=0.9,
            bottom=0.09,
            top=0.78 + 0.003 * len(self.df),
        )
        self.pixel_dimensions = self.pixel_width, self.pixel_height = (2160, 2680)
        self.figure, self.axes = plt.subplots(
            nrows=len(self.df),
            figsize=(
                self.pixel_width / plt.rcParams["figure.dpi"],
                self.pixel_height / plt.rcParams["figure.dpi"],
            ),
            gridspec_kw=dict(**self.insets, hspace=1 - 0.04 * len(self.df)),
        )
        self.bottom_axes = self.figure.add_axes(
            [
                self.insets["left"],
                0.075,
                self.insets["right"] - self.insets["left"],
                0.01,
            ]
        )

    def refine_figure(self):
        amount_competitors = len(self.df)
        for index, (competitor_name, competitor_data) in enumerate(self.df):
            ax = self.axes[index]
            ax.add_artist(
                AnnotationBbox(
                    OffsetImage(
                        image.imread(
                            os.path.join(
                                package_directory,
                                "assets",
                                "images",
                                f"position_{index + 1}.png",
                            )
                        ),
                        zoom=0.07 - 0.0017 * amount_competitors,
                    ),
                    xy=(self.title_x_pos, 0.5),
                    xycoords=("figure fraction", "axes fraction"),
                    frameon=False,
                    box_alignment=(0, 0.5),
                )
            )

            identifier_bar_width = 0.021 - 0.0003 * amount_competitors
            self.figure.add_artist(
                patches.Rectangle(
                    (-identifier_bar_width, 0),
                    identifier_bar_width,
                    1,
                    facecolor=self.color_getter(self.season, competitor_name),
                    clip_on=False,
                    transform=ax.transAxes,
                )
            )

            ax.add_artist(
                Annotation(
                    competitor_name.upper(),
                    fontsize=9,
                    ha="left",
                    va="center",
                    fontweight="black",
                    xy=(
                        identifier_bar_width * 1.1,
                        0.48,
                    ),
                    xycoords=("axes fraction", "axes fraction"),
                ),
            )

        # setting params
        for ax in self.axes:
            ax.set_frame_on(False)
            ax.tick_params(
                axis="x", which="both", bottom=False, labelbottom=False, length=0
            )
            ax.tick_params(
                axis="y",
                which="both",
                left=False,
                labelleft=False,
                direction="in",
                length=0,
            )
            ax.grid(True, axis="x", which="major", alpha=2 / 3)
            ax.set_ylim(0, 1)
            if self.xlimits:
                ax.set_xlim(self.xlimits)
            if self.locators:
                ax.xaxis.set_major_locator(MultipleLocator(self.major_locator))
                ax.xaxis.set_minor_locator(MultipleLocator(self.minor_locator))

        self.bottom_axes.set_frame_on(False)
        self.bottom_axes.tick_params(axis="x", which="both", labelsize=8, bottom=True)
        self.bottom_axes.tick_params(axis="y", which="both", left=False)
        self.bottom_axes.set_yticks([])
        if self.xlimits:
            self.bottom_axes.set_xlim(self.xlimits)
        if self.locators:
            self.bottom_axes.xaxis.set_major_locator(
                MultipleLocator(self.major_locator)
            )
            self.bottom_axes.xaxis.set_minor_locator(
                MultipleLocator(self.minor_locator)
            )

        # adding xlabel
        xlabel, unit = self.xlabel[0], self.xlabel[1]
        self.figure.add_artist(
            AnnotationBbox(
                HPacker(
                    children=[
                        TextArea(
                            xlabel,
                            textprops=dict(
                                fontsize=10, fontweight="black", ha="center"
                            ),
                        ),
                    ]
                    + (
                        [
                            TextArea(
                                f"({unit})",
                                textprops=dict(fontsize=8, ha="center"),
                            ),
                        ]
                        if unit is not None
                        else []
                    ),
                    pad=0,
                    sep=2,
                ),
                xy=(0.5, 0.03),
                xycoords="figure fraction",
                frameon=False,
            )
        )

    def add_titles(self):
        self.title_x_pos = 0.05
        self.title_y_pos = 0.89
        self.figure.add_artist(
            AnnotationBbox(
                VPacker(
                    children=[
                        TextArea(
                            self.subtitle.upper(),
                            textprops=dict(fontsize=10, fontweight="black"),
                        ),
                        TextArea(
                            self.title.upper(),
                            textprops=dict(fontsize=30, fontweight="black"),
                        ),
                    ],
                    pad=0,
                    sep=2,
                ),
                xy=(self.title_x_pos, self.title_y_pos),
                xycoords="figure fraction",
                box_alignment=(0, 0),
                frameon=False,
            )
        )

        self.figure.add_artist(
            Annotation(
                self.description.upper(),
                fontsize=5,
                ha="left",
                va="center",
                fontweight="black",
                xy=(
                    self.title_x_pos,
                    self.title_y_pos - 0.01,
                ),
                xycoords="figure fraction",
            ),
        )

    def apply_logos(self):
        alpha = 0.95
        self.figure.add_artist(
            AnnotationBbox(
                OffsetImage(
                    image.imread(signature),
                    zoom=0.14,
                    alpha=alpha,
                ),
                xy=(1 - self.title_x_pos, self.title_y_pos + 0.005),
                xycoords="figure fraction",
                box_alignment=(1, 0),
                frameon=False,
            )
        )

        self.figure.add_artist(
            Annotation(
                "@DrivenByData_".upper(),
                fontsize=7,
                va="top",
                ha="right",
                fontweight="black",
                color="w",
                alpha=alpha,
                xy=(
                    1 - self.title_x_pos - 0.02,
                    self.title_y_pos - 0.005,
                ),
                xycoords="figure fraction",
            ),
        )
        self.figure.add_artist(
            AnnotationBbox(
                OffsetImage(
                    image.imread(d_logo_path),
                    zoom=0.3,
                    alpha=D_LOGO_ALPHA,
                ),
                xy=(1.5, -0.05),
                xycoords="figure fraction",
                box_alignment=(1, 0),
                frameon=False,
            )
        )

    def export(self, path):
        self.figure.savefig(path, dpi=300)


class AnimationViewer:
    def __init__(
        self,
        title,
        subtitle,
        laps,
        cap_delta=False,
    ):
        self.title = title
        self.subtitle = subtitle
        self.laps = laps

        self.cap_delta = cap_delta

        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()

    def create_figure(self):
        self.insets = dict(left=0.03, right=0.6, bottom=0.05, top=0.86)
        spacer_height = 0.02
        subplot_heights = [
            0.42,
            spacer_height,
            0.18,
            spacer_height,
            0.18,
            spacer_height / 2,
        ]
        self.pixel_dimensions = self.pixel_width, self.pixel_height = (3840, 2160)
        self.figure, self.axes = plt.subplots(
            nrows=len(subplot_heights),
            sharex=True,
            figsize=(
                self.pixel_width / plt.rcParams["figure.dpi"],
                self.pixel_height / plt.rcParams["figure.dpi"],
            ),
            gridspec_kw=dict(**self.insets, hspace=0, height_ratios=subplot_heights),
        )

        (
            self.speed_axis,
            _,
            self.throttle_axis,
            _,
            self.delta_axis,
            _,
        ) = self.axes

        self.plotting_axes = (
            self.speed_axis,
            self.throttle_axis,
            self.delta_axis,
        )
        self.spacer_axes = (
            self.axes[1],
            self.axes[3],
            self.axes[5],
        )

        self.position_tracker_axis = self.axes[-1]
        self.axes = self.axes[:-1]

        self.trackmap_axis = self.figure.add_axes(
            [self.insets["right"] + 0.08, 0.1, 0.32, 0.5],
            zorder=-1,
        )

        self.plotting_axes_lookup = dict(
            Speed=self.speed_axis,
            Throttle=self.throttle_axis,
            Delta=self.delta_axis,
        )
        self.channel_labels = [
            "GPS Speed",
            "Throttle",
            "Laptime Diff.",
        ]
        self.channel_units = ["KM/H", "%", "SEC."]

        self.labels_fontdict = dict(
            fontsize=11,
            fontweight="black",
            alpha=0.9,
        )
        self.units_fontdict = dict(
            fontsize=8,
            fontweight="bold",
            alpha=0.7,
        )

        self.legend_fontdicts = dict(
            small=dict(
                fontsize=11,
                fontweight="black",
            ),
            medium=dict(
                fontsize=20,
                fontweight="black",
            ),
            large=dict(
                fontsize=34,
                fontweight="black",
            ),
        )
        self.marker_dimensions = dict(
            medium=(3, 15),
        )

    def refine_figure(self):
        tick_label_size = 6

        for ax in self.spacer_axes:
            ax.margins(x=0, y=0)
            ax.set_axis_off()

        ticklabel_color = (
            f"""{LIGHT_COLOR}{int(self.labels_fontdict["alpha"] * 255):x}"""
        )
        for ax in self.plotting_axes:
            ax.margins(x=0, y=0.005)
            ax.grid(True, axis="x", which="major", color=GRID_COLOR)
            ax.grid(True, axis="y", which="both", color=GRID_COLOR)
            ax.tick_params(axis="x", which="both", bottom=False)
            ax.tick_params(
                axis="y",
                which="both",
                direction="in",
                left=False,
                labelleft=False,
                right=False,
                labelright=False,
                labelsize=tick_label_size,
                labelcolor=ticklabel_color,
            )

        # delta axis
        self.delta_axis.tick_params(
            axis="x",
            which="both",
            bottom=True,
            labelbottom=False,
            direction="in",
            labelsize=tick_label_size,
            labelcolor=ticklabel_color,
        )
        self.delta_axis.margins(x=0, y=0.1)

        # trackmap axis
        self.trackmap_axis.axis("equal")
        self.trackmap_axis.margins(x=0.2, y=0.01)
        self.trackmap_axis.set_axis_off()

        lap_legends = []
        for lap in self.laps:
            marker_area = DrawingArea(*self.marker_dimensions["medium"])
            marker = patches.Rectangle(
                (0, 0), *self.marker_dimensions["medium"], color=lap.info["Color"]
            )
            marker_area.add_artist(marker)
            lap_legends.append(
                HPacker(
                    children=[
                        marker_area,
                        TextArea(
                            lap.info["Driver"],
                            textprops=self.legend_fontdicts["medium"],
                        ),
                        TextArea(
                            lap.info["ReadableLapTime"],
                            textprops=self.legend_fontdicts["medium"]
                            | dict(fontsize=15, fontweight="bold"),
                        ),
                        TextArea(
                            lap.info.get("Description", ""),
                            textprops=dict(
                                fontsize=8,
                                fontweight="bold",
                                alpha=0.85,
                            ),
                        ),
                    ],
                    pad=0,
                    sep=6,
                ),
            )
        lap_legends.insert(
            1,
            TextArea(
                "VS.",
                textprops=self.labels_fontdict,
            ),
        )

        self.speed_axis.add_artist(
            AnnotationBbox(
                VPacker(
                    children=lap_legends,
                    pad=0,
                    sep=5,
                ),
                xy=(1.02, self.insets["top"] - 0.07),
                box_alignment=(0, 1),
                xycoords=("axes fraction", "figure fraction"),
                frameon=False,
            )
        )

        self.speed_axis.yaxis.set_major_locator(MultipleLocator(50))
        self.speed_axis.yaxis.set_minor_locator(MultipleLocator(10))
        self.speed_axis.set_ylim(
            bottom=max(
                self.reference_lap.telemetry["Speed"].min() - 15,
                self.speed_axis.get_ylim()[0],
            )
        )
        self.throttle_axis.set_yticks([0, 100])
        self.throttle_axis.set_yticklabels(["0", "100"])
        self.throttle_axis.yaxis.set_major_locator(MultipleLocator(100))
        self.throttle_axis.yaxis.set_minor_locator(MultipleLocator(20))
        self.delta_axis.xaxis.set_major_locator(MultipleLocator(500))
        self.delta_axis.xaxis.set_minor_locator(MultipleLocator(100))
        if self.cap_delta:
            self.delta_axis.set_ylim(
                bottom=max(-1, self.delta_axis.get_ylim()[0]),
                top=min(1, self.delta_axis.get_ylim()[1]),
            )

        self.apply_logos()

    def get_legend_box(self, channel_label, channel_unit):
        lap_value_legends = []
        for lap in self.laps:
            marker_area = DrawingArea(*self.marker_dimensions["medium"])
            marker = patches.Rectangle(
                (0, 0), *self.marker_dimensions["medium"], color=lap.info["Color"]
            )
            marker_area.add_artist(marker)
            lap_value_legends.append(
                HPacker(
                    children=[
                        marker_area,
                        TextArea(
                            "100",
                            textprops=self.legend_fontdicts["medium"]
                            | dict(fontweight="bold"),
                        ),
                    ],
                    pad=0,
                    sep=5,
                )
            )
        return AnnotationBbox(
            VPacker(
                children=[
                    HPacker(
                        children=[
                            TextArea(
                                channel_label.upper(),
                                textprops=self.labels_fontdict,
                            ),
                            TextArea(
                                channel_unit.upper(),
                                textprops=self.units_fontdict,
                            ),
                        ],
                        pad=0,
                        sep=2,
                    ),
                    HPacker(
                        children=[
                            VPacker(
                                children=lap_value_legends,
                                pad=0,
                                sep=2,
                            ),
                            VPacker(
                                children=[
                                    TextArea(
                                        "",
                                        textprops=self.legend_fontdicts["medium"],
                                    ),
                                    TextArea(
                                        "",
                                        textprops=self.legend_fontdicts["medium"],
                                    ),
                                ],
                                pad=0,
                                sep=2,
                            ),
                        ],
                        pad=1,
                        sep=4,
                    ),
                ],
                align="left",
                pad=0,
                sep=2,
            ),
            xy=(1.02, 15),
            box_alignment=(0, 0),
            xycoords=("axes fraction", "axes points"),
            frameon=False,
            clip_on=False,
        )

    def add_titles(self):
        self.figure.add_artist(
            AnnotationBbox(
                HPacker(
                    children=[
                        TextArea(
                            "F1 TELEMETRY",
                            textprops=self.legend_fontdicts["large"],
                        ),
                        TextArea(
                            "LAP ANALYSIS",
                            textprops=self.legend_fontdicts["large"]
                            | dict(fontweight="bold"),
                        ),
                    ],
                    pad=0,
                    sep=10,
                    align="top",
                ),
                xy=(self.insets["left"], self.insets["top"] + 0.03),
                xycoords="figure fraction",
                box_alignment=(0, 0),
                frameon=False,
            )
        )
        self.speed_axis.add_artist(
            AnnotationBbox(
                VPacker(
                    children=[
                        TextArea(
                            self.subtitle.upper(),
                            textprops=self.legend_fontdicts["small"]
                            | dict(fontweight="regular", alpha=0.9),
                        ),
                        TextArea(
                            self.title.upper(),
                            textprops=self.legend_fontdicts["medium"]
                            | dict(fontsize=18),
                        ),
                    ],
                    pad=0,
                    sep=2,
                ),
                xy=(1.02, self.insets["top"]),
                xycoords=("axes fraction", "figure fraction"),
                box_alignment=(0, 1),
                frameon=False,
            )
        )

    def apply_logos(self):
        alpha = 0.95
        self.figure.add_artist(
            AnnotationBbox(
                OffsetImage(
                    image.imread(signature),
                    zoom=0.14,
                    alpha=alpha,
                ),
                xy=(0.985, 0.045),
                xycoords="figure fraction",
                box_alignment=(1, 0),
                frameon=False,
            )
        )
        self.figure.add_artist(
            Annotation(
                "@DrivenByData_".upper(),
                fontsize=7,
                va="top",
                ha="left",
                fontweight="black",
                color="w",
                alpha=alpha,
                xy=(0.9, 0.045 - 0.005),
                xycoords="figure fraction",
            ),
        )

    def prepare_data(self):
        self.laps.sort(
            key=lambda lap: pd.Timedelta(seconds=500)
            if pd.isna(lap.info["LapTime"])
            else lap.info["LapTime"]
        )

        self.reference_lap, self.comparison_lap = self.laps

        self.reference_lap_index = 0
        self.reference_lap = self.laps[self.reference_lap_index]
        self.reference_lap.telemetry
        self.reference_lap.telemetry["Delta"] = 0
        self.comparison_lap.telemetry["Delta"] = (
            self.comparison_lap.telemetry["TimeInSeconds"]
            - self.reference_lap.telemetry["TimeInSeconds"]
        ).interpolate()

        # rotate track map if its width is greater than its height
        if (
            self.reference_lap.telemetry["X"].abs().max()
            > self.reference_lap.telemetry["Y"].abs().max()
        ):
            rotate_track(self.reference_lap, degrees=90)

    def plot_data(self):
        for lap in self.laps:
            lap.plot(self.plotting_axes_lookup)

        self.legends = []
        for ax, channel_label, channel_unit in zip(
            self.plotting_axes, self.channel_labels, self.channel_units
        ):
            legend = self.get_legend_box(channel_label, channel_unit)
            ax.add_artist(legend)
            self.legends.append(legend)

        for ax in self.axes:
            ax.live_line = ax.axvline(
                0,
                color=LIGHT_COLOR,
                linewidth=TRACE_THICKNESS,
                alpha=0.9,
            )

        self.position_tracker = self.position_tracker_axis.add_artist(
            AnnotationBbox(
                TextArea(
                    "",
                    textprops=self.legend_fontdicts["medium"],
                ),
                xy=(0, 0),
                box_alignment=(0.5, 1),
                xycoords=("data", "axes fraction"),
                frameon=False,
            )
        )

        self.trackmap_axis.plot(
            self.reference_lap.telemetry["X"],
            self.reference_lap.telemetry["Y"],
            color=GRAY_DARK,
            linewidth=4,
            zorder=1,
        )

        (self.live_track_position,) = self.trackmap_axis.plot(
            self.reference_lap.telemetry.iloc[0]["X"],
            self.reference_lap.telemetry.iloc[0]["Y"],
            marker="o",
            markersize=15,
            markeredgecolor=LIGHT_COLOR,
            markerfacecolor=BACKGROUND_COLOR,
            zorder=3,
            clip_on=False,
        )

    def show(self):
        self.current_distance = 1
        max_distance = round(self.delta_axis.get_xlim()[1])

        def move(event):
            print(event.key)
            if event.key == "right":
                self.current_distance = min(max_distance, self.current_distance + 10)
            elif event.key == "left":
                self.current_distance = max(0, self.current_distance - 10)
            self.update(self.current_distance)
            self.figure.canvas.draw()

        self.figure.canvas.mpl_connect("key_press_event", move)
        plt.show()

    def update(self, current_distance):
        updated_artists = []

        self.reference_lap.current_sample = (
            self.reference_lap.telemetry.iloc[current_distance]
            if len(self.reference_lap.telemetry) > current_distance
            else self.reference_lap.telemetry.iloc[-1]
        )
        self.comparison_lap.current_sample = (
            self.comparison_lap.telemetry.iloc[current_distance]
            if len(self.comparison_lap.telemetry) > current_distance
            else self.comparison_lap.telemetry.iloc[-1]
        )

        self.trackmap_axis.plot(
            self.reference_lap.telemetry.loc[
                : self.reference_lap.current_sample.name, "X"
            ],
            self.reference_lap.telemetry.loc[
                : self.reference_lap.current_sample.name, "Y"
            ],
            color=LIGHT_COLOR,
            linewidth=4,
            zorder=2,
        )
        self.live_track_position.set_data(
            self.reference_lap.current_sample["X"],
            self.reference_lap.current_sample["Y"],
        )
        updated_artists.append(self.live_track_position)

        self.position_tracker.get_children()[0].set_text(
            self.reference_lap.current_sample["Section"].upper().replace("T", "TURN ")
        )
        self.position_tracker.xybox = (current_distance, self.position_tracker.xy[1])
        updated_artists.append(self.position_tracker)

        for ax in self.axes:
            ax.live_line.set_xdata(self.reference_lap.current_sample["Distance"])
            ax.set_xlim(
                max(0, current_distance) - 500,
                min(self.reference_lap.telemetry["Distance"].max(), current_distance)
                + 500,
            )
            updated_artists.append(ax.live_line)

        for lap_index, lap in enumerate(self.laps):
            for (channel_name, ax), legend in zip(
                self.plotting_axes_lookup.items(),
                self.legends,
            ):
                current_value = lap.current_sample[channel_name]

                value_string = dict(
                    Speed=lambda val: str(round(val)),
                    Throttle=lambda val: str(round(val)),
                    Delta=lambda val: ""
                    if lap_index == self.reference_lap_index
                    else f"{round(val, 2):+}",
                )[channel_name](current_value)
                value_textarea = (
                    legend.get_children()[0]
                    .get_children()[1]
                    .get_children()[0]
                    .get_children()[lap_index]
                    .get_children()[1]
                )
                value_textarea.set_text(value_string)

                if lap_index == 0 and channel_name in [
                    "Speed",
                    "Throttle",
                ]:
                    ref_lap_diff_textarea = (
                        legend.get_children()[0]
                        .get_children()[1]
                        .get_children()[1]
                        .get_children()[0]
                    )
                    comp_lap_diff_textarea = (
                        legend.get_children()[0]
                        .get_children()[1]
                        .get_children()[1]
                        .get_children()[1]
                    )
                    diff = round(
                        lap.current_sample[channel_name]
                        - self.comparison_lap.current_sample[channel_name]
                    )
                    diff_text = r"$\blacktriangle$ " + str(abs(diff))
                    if diff > 0:  # if reference lap has higher value
                        ref_lap_diff_textarea.set_text(diff_text)
                        comp_lap_diff_textarea.set_text("")
                    elif diff < 0:
                        ref_lap_diff_textarea.set_text("")
                        comp_lap_diff_textarea.set_text(diff_text)
                    else:
                        ref_lap_diff_textarea.set_text("")
                        comp_lap_diff_textarea.set_text("")

                updated_artists.append(legend)

        return updated_artists

    def export(self):
        export_name = f"""{self.title}_{self.subtitle}_{"_vs_".join([lap.info["Driver"] for lap in self.laps])}""".replace(
            " ", "_"
        )
        export_path = os.path.join(
            "tests",
            "gifs",
            export_name + ".mp4",
        )
        print("exporting", export_path)

        def get_frame_sequence():
            frame_sequence = []
            distance = 1
            while distance < len(self.reference_lap.telemetry):
                frame_sequence.append(distance)
                distance += 2 + round(
                    (1 / 30) * self.reference_lap.telemetry.iloc[distance]["Speed"]
                )

            frame_sequence += [
                frame_sequence[-1]
            ] * 5  # repeat last frame when lap is completed

            print(len(frame_sequence), "frames")
            # return frame_sequence[:60]
            return frame_sequence

        anim = animation.FuncAnimation(
            self.figure,
            self.update,
            frames=get_frame_sequence(),
        )
        anim.save(
            export_path,
            writer=animation.FFMpegWriter(
                fps=10,
                metadata=dict(artist="DrivenByData_"),
            ),
        )


class LapViewer:
    def __init__(
        self,
        title,
        subtitle,
        laps,
    ):
        self.title = title
        self.subtitle = subtitle
        self.laps = laps

        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()

    def create_figure(self):
        self.insets = dict(left=0.02, right=0.97, bottom=0.03, top=0.9)
        spacer_height = 0.02
        subplot_heights = [
            0.69,
            spacer_height,
            0.15,
            spacer_height,
            0.12,
        ]
        self.pixel_dimensions = self.pixel_width, self.pixel_height = (3840, 2160)
        self.figure, self.axes = plt.subplots(
            nrows=len(subplot_heights),
            sharex=True,
            figsize=(
                self.pixel_width / plt.rcParams["figure.dpi"],
                self.pixel_height / plt.rcParams["figure.dpi"],
            ),
            gridspec_kw=dict(**self.insets, hspace=0, height_ratios=subplot_heights),
        )

        (
            self.speed_axis,
            _,
            self.throttle_axis,
            _,
            self.delta_axis,
        ) = self.axes

        self.plotting_axes = (
            self.speed_axis,
            self.throttle_axis,
            self.delta_axis,
        )
        self.spacer_axes = (
            self.axes[1],
            self.axes[3],
        )

        self.plotting_axes_lookup = dict(
            Speed=self.speed_axis,
            Throttle=self.throttle_axis,
            Delta=self.delta_axis,
        )
        self.channel_labels = [
            "GPS Speed",
            "Throttle",
            "Diff.",
        ]
        self.channel_units = ["KM/H", "%", "SEC."]

        self.labels_fontdict = dict(
            fontsize=9,
            fontweight="black",
            alpha=0.9,
        )
        self.units_fontdict = dict(
            fontsize=7,
            fontweight="bold",
            alpha=0.7,
        )

        self.legend_fontdicts = dict(
            small=dict(
                fontsize=9,
                fontweight="black",
                ha="left",
            ),
            medium=dict(
                fontsize=13,
                fontweight="black",
                ha="left",
            ),
            large=dict(
                fontsize=21,
                fontweight="black",
                ha="left",
            ),
        )
        self.marker_dimensions = dict(
            small=(1, 7),
            medium=(2, 10),
            large=(4, 15),
        )

    def prepare_data(self):
        self.laps.sort(key=lambda lap: lap.info["LapTime"])

        self.reference_lap = self.laps[0]

        self.reference_lap.telemetry["Delta"] = 0
        for comparison_lap in self.laps[1:]:
            comparison_lap.telemetry["Delta"] = (
                comparison_lap.telemetry["TimeInSeconds"]
                - self.reference_lap.telemetry["TimeInSeconds"]
            ).interpolate()

        # correct_distance_offset(self.laps)

    def plot_data(self):
        for lap in self.laps:
            lap.plot(self.plotting_axes_lookup)


        self.legends = []
        for ax, channel_label, channel_unit in zip(
            self.plotting_axes, self.channel_labels, self.channel_units
        ):
            legend = self.get_legend_box(channel_label, channel_unit)
            ax.add_artist(legend)
            self.legends.append(legend)

    def refine_figure(self):
        tick_label_size = 6

        for ax in self.spacer_axes:
            ax.margins(x=0, y=0)
            ax.set_axis_off()

        ticklabel_color = (
            f"""{LIGHT_COLOR}{int(self.labels_fontdict["alpha"] * 255):x}"""
        )
        for ax in self.plotting_axes:
            ax.margins(x=0, y=0.005)
            ax.grid(True, axis="x", which="major", color=GRID_COLOR)
            ax.grid(True, axis="y", which="both", color=GRID_COLOR)
            ax.tick_params(axis="x", which="both", bottom=False)
            ax.tick_params(
                axis="y",
                which="both",
                left=False,
                labelleft=False,
                right=False,
                labelright=False,
                labelsize=tick_label_size,
                labelcolor=ticklabel_color,
            )

        # delta axis
        self.delta_axis.tick_params(
            axis="x",
            which="both",
            bottom=True,
            labelbottom=False,
            labelsize=tick_label_size,
            labelcolor=ticklabel_color,
        )
        self.delta_axis.margins(x=0, y=0.1)

        self.delta_axis.xaxis.set_major_locator(MultipleLocator(500))
        self.delta_axis.xaxis.set_minor_locator(MultipleLocator(100))

        lap_legends = []
        for lap in self.laps:
            marker_area = DrawingArea(*self.marker_dimensions["large"])
            marker = patches.Rectangle(
                (0, 0), *self.marker_dimensions["large"], color=lap.info["Color"]
            )
            marker_area.add_artist(marker)
            lap_legends.append(
                VPacker(
                    children=[
                        TextArea(
                            lap.info.get("Description", ""),
                            textprops=dict(
                                fontsize=7,
                                fontweight="bold",
                                alpha=0.85,
                            ),
                        ),
                        HPacker(
                            children=[
                                marker_area,
                                TextArea(
                                    lap.info["Label"],
                                    textprops=self.legend_fontdicts["large"],
                                ),
                            ],
                            pad=0,
                            sep=5,
                        ),
                    ],
                    pad=0,
                    sep=2,
                    align="right",
                )
            )

        self.figure.add_artist(
            AnnotationBbox(
                HPacker(
                    children=lap_legends,
                    pad=0,
                    sep=15,
                ),
                xy=(self.insets["right"], self.title_y_pos),
                box_alignment=(1, 0),
                xycoords="figure fraction",
                frameon=False,
            )
        )

        self.speed_axis.yaxis.set_major_locator(MultipleLocator(50))
        self.speed_axis.yaxis.set_minor_locator(MultipleLocator(10))
        self.speed_axis.set_ylim(
            bottom=max(
                self.reference_lap.telemetry["Speed"].min() - 15,
                self.speed_axis.get_ylim()[0],
            )
        )
        self.throttle_axis.set_yticks([0, 100])
        self.throttle_axis.set_yticklabels(["0", "100"])
        self.throttle_axis.yaxis.set_major_locator(MultipleLocator(100))
        self.throttle_axis.yaxis.set_minor_locator(MultipleLocator(20))

        self.apply_logos()

    def get_legend_box(self, channel_label, channel_unit):
        return AnnotationBbox(
            VPacker(
                children=[
                    TextArea(
                        channel_label.upper(),
                        textprops=self.labels_fontdict | dict(rotation=-90),
                    ),
                    TextArea(
                        channel_unit.upper(),
                        textprops=self.units_fontdict | dict(rotation=-90),
                    ),
                ],
                pad=0,
                sep=2,
                align="left",
            ),
            xy=(1.005, 1),
            box_alignment=(0, 1),
            xycoords="axes fraction",
            frameon=False,
        )

    def add_titles(self):
        self.title_x_pos = self.insets["left"]
        self.title_y_pos = 0.91
        self.figure.add_artist(
            AnnotationBbox(
                VPacker(
                    children=[
                        TextArea(
                            self.subtitle.upper(),
                            textprops=self.legend_fontdicts["small"],
                        ),
                        TextArea(
                            self.title.upper(),
                            textprops=self.legend_fontdicts["large"],
                        ),
                    ],
                    pad=0,
                    sep=2,
                ),
                xy=(self.title_x_pos, self.title_y_pos),
                xycoords="figure fraction",
                box_alignment=(0, 0),
                frameon=False,
            )
        )

    def apply_logos(self):
        self.figure.add_artist(
            AnnotationBbox(
                OffsetImage(
                    image.imread(d_logo_path),
                    zoom=0.35,
                    alpha=D_LOGO_ALPHA,
                ),
                xy=(0.25, -0.2),
                xycoords="figure fraction",
                box_alignment=(0, 0),
                frameon=False,
            )
        )

    def show(self):
        self.cursors = []
        for ax in self.plotting_axes:
            self.cursors.append(ax.axvline(x=0, color=LIGHT_COLOR, linewidth=0.5))

        self.legends = []
        for ax in self.plotting_axes:
            lap_value_legends = []
            for lap in self.laps:
                marker_area = DrawingArea(*self.marker_dimensions["small"])
                marker = patches.Rectangle(
                    (0, 0), *self.marker_dimensions["small"], color=lap.info["Color"]
                )
                marker_area.add_artist(marker)
                lap_value_legends.append(
                    HPacker(
                        children=[
                            marker_area,
                            TextArea(
                                "    ",
                                textprops=self.legend_fontdicts["small"],
                            ),
                        ],
                        pad=2,
                        sep=3,
                    )
                )
            legend = AnnotationBbox(
                VPacker(
                    children=lap_value_legends,
                    pad=2,
                    sep=2,
                ),
                xy=(0.999, 1),
                box_alignment=(1, 1),
                xycoords="axes fraction",
                pad=0,
                frameon=True,
                bboxprops=dict(
                    facecolor=BACKGROUND_COLOR,
                    edgecolor="none",
                    alpha=0.5,
                ),
                clip_on=False,
            )
            ax.add_artist(legend)
            self.legends.append(legend)

        def on_move(event):
            distance = int(event.xdata)
            for cursor, legend, channel_name in zip(
                self.cursors, self.legends, self.plotting_axes_lookup.keys()
            ):
                cursor.set_xdata(distance)
                for index, lap in enumerate(self.laps):
                    value = lap.telemetry[channel_name].loc[distance] 
                    value_text = round(value, 2) if channel_name == "Delta" else round(value)
                    legend.get_children()[0].get_children()[index].get_children()[
                        1
                    ].set_text(value_text)
            self.figure.canvas.draw()

        self.figure.canvas.mpl_connect("motion_notify_event", on_move)
        plt.show()

    def export(self):
        export_name = f"""{self.title}_{self.subtitle}_{"_vs_".join([lap.info["Driver"] for lap in self.laps])}""".replace(
            " ", "_"
        )

        for lap in self.laps:
            lap.telemetry["Label"] =  lap.info["Label"]

        export_path = os.path.join(
            analysis_directory, "lapcomparisons", export_name + ".png"
        )
        print("exporting", export_path)
        self.figure.savefig(export_path)


class PaceAnalysis:
    def __init__(self, season, meeting, session):
        session = get_session(season, meeting, session)

        source = session.laps

        source["Day"] = (
            source["LapStartDate"]
            .dt.day.fillna(0)
            .apply(lambda day_of_month: {10: 1, 11: 2, 12: 3}.get(int(day_of_month), 0))
        )
        source["TimeOfDay"] = (
            source["Time"]
            .dt.total_seconds()
            .apply(
                lambda secs: f"{int(secs // 3600):02d}:{int(secs % 3600) // 60:02d}:{int(secs % 3600) % 60:02d}"
            )
        )
        source["Time"] = source["Time"].dt.total_seconds()
        source["LapTime"] = source["LapTime"].dt.total_seconds()
        source["Compound"] = source["Compound"].str.capitalize()
        # source = source[source["IsAccurate"]]
        source["Stint"] = source.groupby("Driver")["PitOutTime"].transform(
            lambda group: (~group.isnull()).cumsum()
        )
        source = (
            source.groupby(["Driver", "Stint"])
            .apply(lambda group: group.iloc[1:-1])
            .reset_index(drop=True)
        )
        source["StintLength"] = (
            source.groupby(["Driver", "Stint"])["LapNumber"].transform(len).fillna(1)
        )
        min_stint_length_for_long_run = 5
        source = source[(source["StintLength"] - 3) > min_stint_length_for_long_run]
        source["Label"] = source.apply(
            lambda row: f"""{row["Driver"]} R{int(row["Stint"])} {row["Compound"]} ({int(row["StintLength"])})""",
            axis=1,
        )
        source["LapNumber"] = source.groupby("Label")["LapNumber"].transform(
            lambda group: group - group.min()
        )
        source = source[
            [
                "Day",
                "TimeOfDay",
                "Time",
                "Driver",
                "LapNumber",
                "LapTime",
                "ReadableLapTime",
                "Color",
                "Compound",
                "TyreLife",
                "FreshTyre",
                "SpeedST",
                "Stint",
                "StintLength",
                "Label",
            ]
        ]
        # print(source[["Time", "LapNumber", "Driver", "ReadableLapTime", "Stint", "StintLength", "Label"]])

        # source["CumLapTime"] = source.groupby("Driver")["LapTime"].cumsum()
        # winner = source.loc[
        #     source[source["LapNumber"] == source["LapNumber"].max()]["Time"].idxmin()
        # ]["Driver"]
        # source["RaceTime"] = (
        #     source.groupby("LapNumber")
        #     .apply(lambda g: g["Time"] - g[g["Driver"] == winner].iloc[0]["Time"])
        #     .reset_index(level=0)[0]
        # )
        # source["ComparativeLapTime"] = (
        #     source.groupby("LapNumber")
        #     .apply(lambda g: g["LapTime"] - g["LapTime"].median())
        #     .reset_index(level=0)[0]
        # )

        group_by = "Label"

        # comparison_column = "RaceTime:Q"
        # comparison_column = "SpeedST:Q"
        comparison_column = "LapTime:Q"

        color_mapping = {
            label: get_driver_color(season, label[:3])
            for label in source["Label"].values
        }

        nearest_lap = alt.selection(
            type="single",
            nearest=True,
            on="mouseover",
            fields=["LapNumber"],
            empty="none",
        )
        driver_selection = alt.selection_multi(fields=[group_by], empty="none")

        colors = alt.condition(
            driver_selection,
            alt.Color(
                f"{group_by}:N",
                scale=alt.Scale(
                    domain=list(color_mapping.keys()),
                    range=list(color_mapping.values()),
                ),
                legend=None,
            ),
            alt.value(LIGHT_COLOR),
        )

        line = (
            alt.Chart(source)
            .mark_line(interpolate="monotone")
            .encode(
                x=alt.X("LapNumber:Q", scale=alt.Scale(padding=0, nice=False)),
                y=alt.Y(
                    comparison_column,
                    axis=alt.Axis(tickCount=15),
                    scale={
                        "LapTime:Q": alt.Scale(
                            zero=False,
                            domain=(
                                source["LapTime"].min(),
                                source["LapTime"].median() + 4,
                            ),
                            clamp=True,
                        ),
                        # "RaceTime:Q": alt.Scale(),
                        # "ComparativeLapTime:Q": alt.Scale(domain=(-5, 5), clamp=True),
                        # "SpeedST:Q": alt.Scale(
                        #     zero=False,
                        #     domain=(
                        #         source["SpeedST"].median() - 20,
                        #         source["SpeedST"].median() + 20,
                        #     ),
                        # ),
                    }[comparison_column],
                ),
                tooltip=[
                    "Day",
                    "TimeOfDay",
                    "LapNumber",
                    "Driver",
                    "ReadableLapTime",
                    "Compound",
                    "Stint",
                    "TyreLife",
                    "SpeedST",
                ],
                color=colors,
                opacity=alt.condition(driver_selection, alt.value(1.0), alt.value(0.1)),
            )
        )

        # Transparent selectors across the chart. This is what tells us the x-value of the cursor
        selectors = (
            alt.Chart(source)
            .mark_point()
            .encode(
                x=alt.X("LapNumber:Q", scale=alt.Scale(padding=0)),
                opacity=alt.value(0),
            )
            .add_selection(nearest_lap)
        )

        legend = (
            alt.Chart(source)
            .mark_point(size=100)
            .encode(x=alt.X(f"{group_by}:N", axis=alt.Axis(title="")), color=colors)
            .add_selection(driver_selection)
        )

        # Draw points on the line, and highlight based on selection
        points = line.mark_point().encode(
            opacity=alt.condition(
                driver_selection,
                alt.value(1),
                alt.value(0),
            )
        )

        # text = points.mark_text(align="left", dx=5, dy=-5).encode(
        #     text=alt.condition(nearest_lap, "ReadableLapTime", alt.value(" ")),
        # )

        # Draw a rule at the location of the selection
        rules = (
            alt.Chart(source)
            .mark_rule(color=LIGHT_COLOR)
            .encode(
                x="LapNumber:Q",
            )
            .transform_filter(nearest_lap)
        )

        # Put the five layers into a chart and bind the data
        chart = (
            alt.layer(
                line,
                selectors,
                points,
                rules,
            )
            .properties(
                title=f"""{session.info["Season"]} {session.info["Meeting"]} - Pace Overview""",
                width=2200,
                height=1220,
            )
            .interactive()
        )

        window = (
            alt.vconcat(
                chart,
                legend,
            )
            .configure(background=BACKGROUND_COLOR, padding=0, font="Roboto")
            .configure_axis(gridOpacity=0.15)
            .configure_view(strokeWidth=0)
        )

        alt.themes.enable("dark")
        # alt.renderers.enable("mimetype")

        # window.save("chart.html")
        window.show()


class Experimental:
    def __init__(
        self,
        title,
        subtitle,
        laps,
    ):
        self.title = title
        self.subtitle = subtitle
        self.laps = laps

        self.prepare_data()
        self.create_figure()
        self.add_titles()
        self.apply_logos()
        self.plot_data()
        self.refine_figure()

    def create_figure(self):
        self.insets = dict(left=0.03, right=0.75, bottom=0.03, top=0.85)
        spacer_height = 0.02
        subplot_heights = [
            0.61,
            spacer_height / 2,
        ]
        self.pixel_dimensions = self.pixel_width, self.pixel_height = (3840, 2160)
        self.figure, self.axes = plt.subplots(
            nrows=len(subplot_heights),
            sharex=True,
            figsize=(
                self.pixel_width / plt.rcParams["figure.dpi"],
                self.pixel_height / plt.rcParams["figure.dpi"],
            ),
            gridspec_kw=dict(**self.insets, hspace=0, height_ratios=subplot_heights),
        )

        (
            self.speed_axis,
            _,
        ) = self.axes

        self.plotting_axes = (self.speed_axis,)
        self.spacer_axes = (self.axes[1],)

        self.position_tracker_axis = self.axes[-1]
        self.axes = self.axes[:-1]

        self.trackmap_axis = self.figure.add_axes(
            [self.insets["right"], 0.04, 0.25, 0.4]
        )

        self.plotting_axes_lookup = dict(
            Speed=self.speed_axis,
        )

        self.labels_fontdict = dict(
            fontsize=9,
            fontweight="black",
            alpha=0.9,
        )
        self.units_fontdict = dict(
            fontsize=7,
            fontweight="bold",
            alpha=0.7,
        )

        self.legend_fontdicts = dict(
            small=dict(
                fontsize=10,
                fontweight="bold",
                alpha=0.95,
                ha="left",
            ),
            medium=dict(
                fontsize=18,
                fontweight="black",
                ha="left",
            ),
            large=dict(
                fontsize=30,
                fontweight="black",
                ha="left",
            ),
        )
        self.marker_dimensions = dict(
            medium=(2, 10),
            large=(4, 14),
        )

    def refine_figure(self):
        tick_label_size = 6

        for ax in self.spacer_axes:
            ax.margins(x=0, y=0)
            ax.set_axis_off()

        ticklabel_color = (
            f"""{LIGHT_COLOR}{int(self.labels_fontdict["alpha"] * 255):x}"""
        )
        for ax in self.plotting_axes:
            ax.margins(x=0, y=0.005)
            ax.grid(True, axis="x", which="major", color=GRID_COLOR)
            ax.grid(True, axis="y", which="both", color=GRID_COLOR)
            ax.tick_params(axis="x", which="both", bottom=False)
            ax.tick_params(
                axis="y",
                which="both",
                direction="in",
                left=False,
                labelleft=False,
                right=False,
                labelright=False,
                labelsize=tick_label_size,
                labelcolor=ticklabel_color,
            )

        # trackmap axis
        self.trackmap_axis.axis("equal")
        self.trackmap_axis.margins(x=0.2, y=0.01)
        self.trackmap_axis.set_axis_off()

        lap_legends = []
        for lap in self.laps:
            marker_area = DrawingArea(*self.marker_dimensions["large"])
            marker = patches.Rectangle(
                (0, 0), *self.marker_dimensions["large"], color=lap.info["Color"]
            )
            marker_area.add_artist(marker)
            lap_legends.append(
                VPacker(
                    children=[
                        HPacker(
                            children=[
                                marker_area,
                                TextArea(
                                    lap.info["Driver"],
                                    textprops=self.legend_fontdicts["medium"],
                                ),
                                HPacker(
                                    children=[
                                        TextArea(
                                            # int(lap.info["SpeedST"]),
                                            int(lap.telemetry["Speed"].max()),
                                            textprops=self.legend_fontdicts["medium"],
                                        ),
                                        TextArea(
                                            "KM/H",
                                            textprops=self.legend_fontdicts["small"],
                                        ),
                                    ],
                                    pad=0,
                                    sep=2,
                                ),
                            ],
                            pad=0,
                            sep=5,
                        ),
                    ],
                    pad=0,
                    sep=2,
                )
            )

        self.figure.add_artist(
            AnnotationBbox(
                VPacker(
                    children=[
                        TextArea(
                            "Top Speed on main straight".upper(),
                            textprops=self.legend_fontdicts["small"],
                        ),
                    ]
                    + lap_legends[::-1],
                    pad=0,
                    sep=12,
                ),
                xy=(self.insets["right"] + 0.01, self.title_y_pos),
                box_alignment=(0, 1),
                xycoords="figure fraction",
                frameon=False,
            )
        )

        self.speed_axis.yaxis.set_major_locator(MultipleLocator(50))
        self.speed_axis.yaxis.set_minor_locator(MultipleLocator(10))
        self.speed_axis.set_xlim(0, 550)
        self.speed_axis.set_ylim(bottom=self.reference_lap.telemetry.iloc[-1]["Speed"])

        self.apply_logos()

    def add_titles(self):
        self.title_x_pos = self.insets["left"]
        self.title_y_pos = self.insets["top"]
        self.figure.add_artist(
            AnnotationBbox(
                VPacker(
                    children=[
                        TextArea(
                            self.subtitle.upper(),
                            textprops=self.legend_fontdicts["small"],
                        ),
                        TextArea(
                            self.title.upper(),
                            textprops=self.legend_fontdicts["large"],
                        ),
                    ],
                    pad=0,
                    sep=2,
                ),
                xy=(self.title_x_pos, self.title_y_pos + 0.02),
                xycoords="figure fraction",
                box_alignment=(0, 0),
                frameon=False,
            )
        )

    def apply_logos(self):
        alpha = 0.95
        self.figure.add_artist(
            AnnotationBbox(
                OffsetImage(
                    image.imread(signature),
                    zoom=0.14,
                    alpha=alpha,
                ),
                xy=(1.001, self.title_y_pos),
                xycoords="figure fraction",
                box_alignment=(1, 0),
                frameon=False,
            )
        )
        self.figure.add_artist(
            Annotation(
                "@DrivenByData_".upper(),
                fontsize=7,
                va="top",
                ha="left",
                fontweight="black",
                color="w",
                alpha=alpha,
                xy=(0.917, self.title_y_pos - 0.005),
                xycoords="figure fraction",
            ),
        )

    def prepare_data(self):
        for lap in self.laps:
            lap.telemetry["Speed"] = savgol_filter(
                lap.telemetry["Speed"], window_length=99, polyorder=1
            )
        self.laps.sort(key=lambda lap: lap.info["SpeedST"])

        self.reference_lap = self.laps[0]

        # correct_distance_offset(*self.laps)

        # rotate track map if its width is greater than its height
        if (
            self.reference_lap.telemetry["Y"].abs().max()
            > self.reference_lap.telemetry["X"].abs().max()
        ):
            rotate_track(self.reference_lap, degrees=90)

    def plot_data(self):
        for lap in self.laps:
            lap.plot(self.plotting_axes_lookup)

        self.legends = []
        # for ax, channel_label, channel_unit in zip(
        #     self.plotting_axes, self.channel_labels, self.channel_units
        # ):
        #     legend = self.get_legend_box(channel_label, channel_unit)
        #     ax.add_artist(legend)
        #     self.legends.append(legend)

        self.trackmap_axis.plot(
            self.reference_lap.telemetry["X"],
            self.reference_lap.telemetry["Y"],
            color=LIGHT_COLOR,
            linewidth=8,
            alpha=0.3,
        )
        self.trackmap_axis.plot(
            self.reference_lap.telemetry.iloc[:550]["X"],
            self.reference_lap.telemetry.iloc[:550]["Y"],
            color=LIGHT_COLOR,
            linewidth=8,
            alpha=0.8,
        )

    def export(self):
        export_name = f"""{self.title}_{self.subtitle}""".replace(" ", "_")
        export_path = os.path.join(
            analysis_directory, "lapcomparisons", export_name + ".png"
        )
        print("exporting", export_path)
        self.figure.savefig(export_path)
