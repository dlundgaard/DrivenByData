from matplotlib import pyplot as plt

TRACE_THICKNESS = 0.8

BACKGROUND_COLOR = "#050505"
GRID_COLOR = "#666666"
LIGHT_COLOR = "#DCDCDC"
MUTED_COLOR = "#707070"
GRAY_DARK = "#131515"
D_LOGO_ALPHA = 0.02

class DATA_COLORS:
    WHITE = "#DCDCDC"
    GREEN = "#37FF8B"
    PURPLE = "#EE03FF"
    RED = "#FF1053"
    BLUE = "#00ACED"
    YELLOW = "#FFFF00"

plt.rcParams["figure.dpi"] = 300
plt.rcParams["savefig.dpi"] = 200
plt.rcParams["animation.embed_limit"] = 1000
plt.rcParams["svg.fonttype"] = "none"
plt.rcParams["figure.frameon"] = False
plt.rcParams["figure.facecolor"] = BACKGROUND_COLOR
plt.rcParams["figure.titlesize"] = 22
plt.rcParams["axes.spines.left"] = True
plt.rcParams["axes.spines.bottom"] = False
plt.rcParams["axes.spines.right"] = True
plt.rcParams["axes.spines.top"] = False
plt.rcParams["axes.edgecolor"] = LIGHT_COLOR
plt.rcParams["axes.labelweight"] = "regular"
plt.rcParams["axes.labelcolor"] = LIGHT_COLOR
plt.rcParams["axes.facecolor"] = BACKGROUND_COLOR
plt.rcParams["axes.titlesize"] = "small"
plt.rcParams["axes.labelsize"] = "small"
plt.rcParams["axes.labelpad"] = 10
plt.rcParams["axes.titlepad"] = 10
plt.rcParams["axes.xmargin"] = 0
plt.rcParams["axes.ymargin"] = 0
plt.rcParams["grid.color"] = GRID_COLOR
plt.rcParams["grid.linewidth"] = 0.1
plt.rcParams["text.color"] = LIGHT_COLOR
plt.rcParams["font.family"] = "Roboto"
plt.rcParams["font.size"] = 8
plt.rcParams["font.weight"] = 700
plt.rcParams["xtick.color"] = LIGHT_COLOR
plt.rcParams["xtick.labelsize"] = "xx-small"
plt.rcParams["ytick.color"] = LIGHT_COLOR
plt.rcParams["ytick.labelsize"] = "xx-small"
plt.rcParams["legend.fontsize"] = "x-large"
plt.rcParams["legend.facecolor"] = BACKGROUND_COLOR
plt.rcParams["legend.edgecolor"] = BACKGROUND_COLOR
plt.rcParams["boxplot.boxprops.color"] = LIGHT_COLOR
plt.rcParams["boxplot.whiskerprops.color"] = LIGHT_COLOR
plt.rcParams["boxplot.capprops.color"] = LIGHT_COLOR
plt.rcParams["boxplot.medianprops.color"] = LIGHT_COLOR
plt.rcParams["boxplot.flierprops.markeredgecolor"] = LIGHT_COLOR
