import numpy as np
from bokeh.models import (
    ColumnDataSource,
    CrosshairTool,
    HoverTool,
    LinearAxis,
    NumeralTickFormatter,
    Range1d,
)
from bokeh.palettes import Category10 as palette
from bokeh.plotting import figure, output_file, save
from prettytable import PrettyTable

# --------------------------------------------------------------------------------------------------
# Constanten.
# --------------------------------------------------------------------------------------------------

# Box 1 belasting tarieven.
BOX1_TARIEF = 73031.0
BOX1_SCHIJF_1_PERC = 0.3693
BOX1_SCHIJF_2_PERC = 0.4950

# Algemene heffingskorting tarieven.
AH_TARIEF_1 = 22661.0
AH_TARIEF_2 = 73031.0
AH_KORTING = 3070.0
AH_PERC = 0.06095

# Arbeidskorting tarieven.
AK_TARIEF_1 = 10741.0
AK_TARIEF_2 = 23201.0
AK_TARIEF_3 = 37691.0
AK_TARIEF_4 = 115295.0
AK_SCHIJF_1_PERC = 0.08231
AK_SCHIJF_2_PERC = 0.29861
AK_SCHIJF_3_PERC = 0.03085
AK_SCHIJF_4_PERC = 0.06510
AK_KORTING_1 = 884.0
AK_KORTING_2 = 4605.0
AK_KORTING_3 = 5052.0

# --------------------------------------------------------------------------------------------------
# Functies.
# --------------------------------------------------------------------------------------------------


# Hulpfunctie die 1 van een getal af trekt om leesbaarheid te vergroten.
def min1(getal: float) -> float:
    return getal - 1


# Bereken het box 1 tarief gegeven een belastbaar inkomen.
def box1_tarief(inkomen: float) -> float:
    schijf1_bedrag = min(inkomen, BOX1_TARIEF)
    schijf2_bedrag = max(inkomen - BOX1_TARIEF, 0)

    tarief = schijf1_bedrag * BOX1_SCHIJF_1_PERC + schijf2_bedrag * BOX1_SCHIJF_2_PERC

    return tarief


# Bereken de algemene heffingskorting gegeven een belastbaar inkomen.
def algemene_heffingskorting(inkomen: float) -> float:
    if inkomen < AH_TARIEF_1:
        korting = AH_KORTING
    elif inkomen < AH_TARIEF_2:
        korting = AH_KORTING - AH_PERC * (inkomen - min1(AH_TARIEF_1))
    else:
        korting = 0.0

    return korting


# Bereken de arbeidskorting gegeven een arbeidsinkomen.
def arbeidskorting(inkomen: float) -> float:
    if inkomen < AK_TARIEF_1:
        korting = AK_SCHIJF_1_PERC * inkomen
    elif inkomen < AK_TARIEF_2:
        korting = AK_KORTING_1 + AK_SCHIJF_2_PERC * (inkomen - min1(AK_TARIEF_1))
    elif inkomen < AK_TARIEF_3:
        # Geen idee waarom nu opeens geen min 1 meer nodig is.
        korting = AK_KORTING_2 + AK_SCHIJF_3_PERC * (inkomen - AK_TARIEF_2)
    elif inkomen < AK_TARIEF_4:
        korting = AK_KORTING_3 - AK_SCHIJF_4_PERC * (inkomen - AK_TARIEF_3)
    else:
        korting = 0.0

    return korting


# Bereken de totale belasting gegeven een bruto inkomen, rekening houdend met heffingskortingen.
def belasting(bruto: float) -> float:
    bedrag = (
        box1_tarief(bruto) - algemene_heffingskorting(bruto) - arbeidskorting(bruto)
    )

    return max(bedrag, 0.0)


# Bereken het netto inkomen gegeven een bruto inkomen, rekening houdend met heffingskortingen.
def netto(bruto: float) -> float:
    return bruto - belasting(bruto)


# Bereken het marginaal belasting percentage gegeven een bruto inkomen.
def marginale_belasting(bruto: float) -> float:
    return belasting(bruto + 1) - belasting(bruto)


# --------------------------------------------------------------------------------------------------
# Voorbeelden.
# --------------------------------------------------------------------------------------------------


def print_table(inkomen: float) -> None:
    table = PrettyTable()
    table.field_names = ["Label", "Value"]
    table.header = False
    table.align["Label"] = "l"
    table.align["Value"] = "r"

    table.add_row(["Inkomen", f"€ {inkomen:10,.2f}"])
    table.add_row(["Box 1 tarief", f"€ {box1_tarief(inkomen):10,.2f}"])
    table.add_row(
        [
            "Algemene heffingskorting",
            f"€ {algemene_heffingskorting(inkomen):10,.2f}",
        ]
    )
    table.add_row(["Arbeidskorting", f"€ {arbeidskorting(inkomen):10,.2f}"])
    table.add_row(["Effectieve belasting", f"€ {belasting(inkomen):10,.2f}"])
    table.add_row(["Netto inkomen", f"€ {netto(inkomen):10,.2f}"])
    table.add_row(
        ["Marginale belasting", f"% {100*marginale_belasting(inkomen):10.2f}"]
    )

    print(table)


print_table(0)
print_table(10000)
print_table(50000)
print_table(100000)
print_table(150000)

# --------------------------------------------------------------------------------------------------
# Bereid de data voor.
# --------------------------------------------------------------------------------------------------

x = np.linspace(0, 150000, 1501)

data = {
    "Bruto inkomen": x,
    "Netto inkomen": np.array([netto(i) for i in x]),
    "Box 1 tarief": np.array([box1_tarief(i) for i in x]),
    "Algemene heffingskorting": np.array([algemene_heffingskorting(i) for i in x]),
    "Arbeidskorting": np.array([arbeidskorting(i) for i in x]),
    "Effectieve belasting": np.array([belasting(i) for i in x]),
    "Marginale belasting": np.array([marginale_belasting(i) for i in x]),
}

source = ColumnDataSource(data=data)

# --------------------------------------------------------------------------------------------------
# Plot grafieken.
# --------------------------------------------------------------------------------------------------

p = figure(
    title="Inkomstenbelasting 2023",
    width=1200,
    height=800,
    x_range=(0, np.max(data["Bruto inkomen"])),
    y_range=(0, np.max(data["Netto inkomen"])),
)

p.xaxis.axis_label = "Bruto inkomen (€)"
p.yaxis.axis_label = "€"
p.xaxis.formatter = NumeralTickFormatter(format="0[.]000a")
p.yaxis.formatter = NumeralTickFormatter(format="0[.]000a")

# Secundaire verticale as.
p.extra_y_ranges["percentage"] = Range1d(0, 1)  # type: ignore
ax2 = LinearAxis(y_range_name="percentage")
ax2.formatter = NumeralTickFormatter(format="0 %")  # type: ignore

bruto_line = p.line(
    x="Bruto inkomen",
    y="Netto inkomen",
    source=source,
    line_width=4,
    line_color=palette[10][0],
    legend_label="Netto inkomen",
)
p.line(
    x="Bruto inkomen",
    y="Box 1 tarief",
    source=source,
    line_width=2,
    line_color=palette[10][1],
    legend_label="Box 1 tarief",
)
p.line(
    x="Bruto inkomen",
    y="Algemene heffingskorting",
    source=source,
    line_width=2,
    line_color=palette[10][2],
    legend_label="Algemene heffingskorting",
)
p.line(
    x="Bruto inkomen",
    y="Arbeidskorting",
    source=source,
    line_width=2,
    line_color=palette[10][3],
    legend_label="Arbeidskorting",
)
p.line(
    x="Bruto inkomen",
    y="Effectieve belasting",
    source=source,
    line_width=2,
    line_color=palette[10][4],
    legend_label="Effectieve belasting",
)
p.line(
    x="Bruto inkomen",
    y="Marginale belasting",
    source=source,
    line_width=2,
    line_color=palette[10][5],
    legend_label="Marginale belasting",
    y_range_name="percentage",
)

p.add_layout(ax2, "right")
p.legend.location = "top_left"
p.legend.click_policy = "hide"

hover_tool = HoverTool(
    tooltips=[
        ("Bruto inkomen", "€ @{Bruto inkomen}{0,0}"),
        ("Netto inkomen", "€ @{Netto inkomen}{0,0}"),
        ("Box 1 tarief", "€ @{Box 1 tarief}{0,0}"),
        ("Algemene heffingskorting", "€ @{Algemene heffingskorting}{0,0}"),
        ("Arbeidskorting", "€ @{Arbeidskorting}{0,0}"),
        ("Effectieve belasting", "€ @{Effectieve belasting}{0,0}"),
        ("Marginale belasting", "@{Marginale belasting}{0.00 %}"),
    ],
    mode="vline",
    renderers=[bruto_line],
)

crosshair_tool = CrosshairTool(
    dimensions="height",
    line_alpha=0.5,
)

p.add_tools(hover_tool)
p.add_tools(crosshair_tool)

output_file("index.html")
save(p)
