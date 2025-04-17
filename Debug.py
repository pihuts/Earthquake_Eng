from handcalcs.decorator import handcalc
import numpy as np
import PLOTTER_APPROX as PLOTTER
import UTILITIES_APPROX as UTIL
import forallpeople


path = UTIL.create_folder("Factor Method")
testdata = {}
mode = False
# ForceList = np.insert(np.array([133.493, 212.375, 233.379]), 0, np.nan)  # bot to top
# BuildingHeightList = np.array([4, 3, 3])  # bot to top
# BuildingSpanList = np.array([6, 7, 5])  # left to right
# NanList = [(18, 10)]  # (x,y) coordinates of the NaN values

ForceList = np.insert(np.array([180.0, 120.0]), 0, np.nan)  # bot to top
BuildingHeightList = np.array([3.5, 3.5])  # bot to top
BuildingSpanList = np.array([7, 3.5, 5])  # left to right
NanList = None  # (x,y) coordinates of the NaN values


Array3d, LabelsDict = UTIL.RemoveNan(BuildingHeightList, BuildingSpanList, NanList)
ForceListCum = np.cumsum(ForceList[::-1])
mode = True
Col_Coord_List = UTIL.CreateColCoordList(Array3d)
Beam_Coord_List = UTIL.CreateBeamCoordList(Array3d)
CumSpan = np.insert(np.cumsum(BuildingSpanList), 0, 0)
path = UTIL.create_folder("FACTOR Pics")

Dtype = UTIL.Dtype
# Create the structured array
shear_canti_array = np.empty(shape=(0,), dtype=Dtype)
moment_canti_array = np.empty(shape=(0,), dtype=Dtype)
axial_canti_array = np.empty(shape=(0,), dtype=Dtype)


@handcalc(override="long", jupyter_display=False, precision=5)
def kl(b, h, length):
    I = (b * h**3) / 12
    k = I / (length)
    return k, 0


@handcalc(override="long", jupyter_display=False, precision=5)
def gfactor(k_col, k_girder):
    g = sum(k_col) / ((sum(k_col)) + sum(k_girder))
    c = 1 - g
    return g, c


@handcalc(override="long", jupyter_display=False, precision=5)
def gfactorhalfgirder(g_left, g_right):
    g_left_ = g_left + (g_right / 2)
    g_right_ = g_right + (g_left / 2)

    return g_left_, g_right_


@handcalc(override="long", jupyter_display=False, precision=5)
def gfactorhalfcol(c_bot, c_top):
    c_bot_ = c_bot + (c_top / 2)
    c_top_ = c_top + (c_bot / 2)
    return c_bot_, c_top_


@handcalc(override="long", jupyter_display=False, precision=5)
def momentfactorcol(c_bot, c_top, k):
    MomentFactor_bot = c_bot * k
    MomentFactor_top = c_top * k
    return MomentFactor_bot, MomentFactor_top


@handcalc(override="long", jupyter_display=False, precision=5)
def momentfactorBeam(g_left, g_right, k):
    MomentFactor_left = g_left * k
    MomentFactor_right = g_right * k
    return MomentFactor_left, MomentFactor_right


@handcalc(override="long", jupyter_display=False, precision=5)
def alp(Cm, f, h):
    alpha = (sum(f) * h) / sum(Cm)
    return alpha


@handcalc(override="long", jupyter_display=False, precision=5)
def MomentEndCol(MomentFactor_bot, MomentFactor_top, alpha):
    EndMoment_Bot = MomentFactor_bot * alpha
    EndMoment_Top = MomentFactor_top * alpha
    return EndMoment_Bot, EndMoment_Top


@handcalc(override="long", jupyter_display=False, precision=5)
def ShearBeam(Moment1, Moment2, Height):
    Shear = (Moment1 + Moment2) / Height
    return Shear, 0


@handcalc(override="long", jupyter_display=False, precision=5)
def ShearColumn(Moment1, Moment2, length):
    Shear = (Moment1 + Moment2) / length
    return Shear, 0


@handcalc(override="long", jupyter_display=False, precision=5)
def Shear(
    Factor_left,
    Factor_right,
    ColEndMoments,
):
    beta = sum(ColEndMoments) / (Factor_left + Factor_right)
    MomentEnd_Left = Factor_left * beta
    MomentEnd_Right = Factor_right * beta
    return MomentEnd_Left, MomentEnd_Right


@handcalc(override="long", jupyter_display=False, precision=5)
def MomentEndBeam(
    Factor_left,
    Factor_right,
    ColEndMoments,
):
    beta = sum(ColEndMoments) / (Factor_left + Factor_right)
    MomentEnd_Left = Factor_left * beta
    MomentEnd_Right = Factor_right * beta
    return MomentEnd_Left, MomentEnd_Right


@handcalc(override="long", jupyter_display=False, precision=5)
def AxialFactor(Axial, ShearBeam):
    Axial = sum(Axial) - sum(ShearBeam)

    return Axial, 0


def magic(liasd):
    asfv = []
    for i, j in enumerate(liasd):
        if i < 2:
            pass
        else:
            j * -1
        asfv.append(j)
    return asfv


keyfactor0_Fig, keyfactor0_Ax, asd = PLOTTER.Frame(Array3d, ForceList, "Moment Diagram")
k_factor0_col = np.empty(shape=(0,), dtype=Dtype)
for i, j in enumerate(Col_Coord_List[::-1]):
    j = j[~np.isnan(j).any(axis=(1, 2))]

    for i1, j1 in enumerate(j):
        if not np.isnan(j1).any():
            ColName = (
                f"COLUMN-{LabelsDict.get(tuple(j1[0]))}-{LabelsDict.get(tuple(j1[1]))}"
            )
            member_type = "Col"
            bot = tuple(j1[0])
            top = tuple(j1[1])
            
            offsety = 0.1
            offsetx = 0.1
            scale = 1
            height = int(j1[1][1]) - int(j1[0][1])
            b = 0.4
            h = 0.4
            latexk0, asd = kl(b, h, height)
            UTIL.add_latex_data(f"Factor-k-{i}", latexk0, ColName, mode)
            # k_factor0_col.update({tuple(j1[0]): [asd[0]]}) if k_factor0_col.get(
            #     tuple(j1[0])
            # ) is None else k_factor0_col.get(tuple(j1[0])).append(asd[0])
            # k_factor0_col.update({tuple(j1[1]): [asd[0]]}) if k_factor0_col.get(
            #     tuple(j1[1])
            # ) is None else k_factor0_col.get(tuple(j1[1])).append(asd[0])
            ktext = format(asd[0], ".2e")
            keyfactor0_Ax.text(bot[0], bot[1] + (height / 2), ktext, color="green")

# k_factor0_beam = {}
# for i, j in enumerate(Beam_Coord_List[::-1]):
#     for i1, j1 in enumerate(j):
#         if not np.isnan(j1).any():
#             BeamName = (
#                 f"BEAM-{LabelsDict.get(tuple(j1[0]))}-{LabelsDict.get(tuple(j1[1]))}"
#             )
#             x = int(j1[0][0])
#             y = int(j1[0][1])
#             offsety = 0.1
#             offsetx = 0.1
#             scale = 1
#             b = 0.3
#             h = 0.6
#             height = j1[1][0] - j1[0][0]
#             latexk0, asd = kl(b, h, height)
#             UTIL.add_latex_data(f"Factor-k-g-{i}", latexk0, BeamName, mode)
#             ktext = format(asd[0], ".2e")
#             k_factor0_beam.update({tuple(j1[0]): [asd[0]]}) if k_factor0_beam.get(
#                 tuple(j1[0])
#             ) is None else k_factor0_beam.get(tuple(j1[0])).append(asd[0])
#             k_factor0_beam.update({tuple(j1[1]): [asd[0]]}) if k_factor0_beam.get(
#                 tuple(j1[1])
#             ) is None else k_factor0_beam.get(tuple(j1[1])).append(asd[0])

#             keyfactor0_Ax.text(x + (length / 2), y, ktext, color="red")
# keyfactor0_Ax.set_xlim(min(CumSpan) - 5, max(CumSpan) + 5)
# keyfactor0_Fig.savefig(f"{path}\\kfactor0.png", dpi=300)


# gfactor0_Fig, gfactor0_Ax, asd = PLOTTER.Frame(Array3d, ForceList, "G,C Factor")
# g_factor = {}
# c_factor = {}
# for i, j in enumerate(Beam_Coord_List[::-1]):
#     for i1, j1 in enumerate(j):
#         if not np.isnan(j1).any():
#             BeamName = f"NODE-{LabelsDict.get(tuple(j1[0]))}"
#             x = int(j1[0][0])
#             y = int(j1[0][1])
#             offsety = 0.2
#             offsetx = 1
#             scale = 1
#             b = 0.3
#             h = 0.6
#             height = j1[1][0] - j1[0][0]

#             col = (
#                 [0]
#                 if k_factor0_col.get(tuple(j1[0])) is None
#                 else k_factor0_col.get(tuple(j1[0]))
#             )
#             beam = (
#                 [0]
#                 if k_factor0_beam.get(tuple(j1[0])) is None
#                 else k_factor0_beam.get(tuple(j1[0]))
#             )

#             latexk0, asd = gfactor(col, beam)

#             UTIL.add_latex_data(f"Factor-g-{i}", latexk0, BeamName, mode)
#             g_factor.update({tuple(j1[0]): asd[0]}) if g_factor.get(
#                 tuple(j1[0])
#             ) is None else g_factor.get(tuple(j1[0])).append(asd[0])
#             c_factor.update({tuple(j1[0]): asd[1]}) if c_factor.get(
#                 tuple(j1[0])
#             ) is None else c_factor.get(tuple(j1[0])).append(asd[1])
#             ktext = round(asd[0], 2)
#             gfactor0_Ax.text(x, y - offsety, ktext, color="red")
#             gfactor0_Ax.text(x - offsetx, y + offsety, ktext, color="red")

#             cfactortext = round(asd[1], 2)
#             gfactor0_Ax.text(x, y + offsety, cfactortext, color="green")
#             gfactor0_Ax.text(x - offsetx, y - offsety, cfactortext, color="green")
#     BeamName = f"NODE-{LabelsDict.get(tuple(j1[1]))}"
#     if not np.isnan(j1).any():
#         x = int(j1[1][0])
#         y = int(j1[1][1])
#         asfas = 1
#     else:
#         x = int(j1[0][0])
#         y = int(j1[0][1])
#         asfas = 0
#     offsety = 0.2
#     offsetx = 1
#     scale = 1
#     b = 0.3
#     h = 0.6
#     height = j1[1][0] - j1[0][0]

#     col = (
#         [0]
#         if k_factor0_col.get(tuple(j1[asfas])) is None
#         else k_factor0_col.get(tuple(j1[asfas]))
#     )
#     beam = (
#         [0]
#         if k_factor0_beam.get(tuple(j1[asfas])) is None
#         else k_factor0_beam.get(tuple(j1[asfas]))
#     )

#     latexk0, asd = gfactor(col, beam)
#     UTIL.add_latex_data(f"Factor-g-{i}", latexk0, BeamName, mode)
#     g_factor.update({tuple(j1[asfas]): asd[0]}) if g_factor.get(
#         tuple(j1[asfas])
#     ) is None else g_factor.get(tuple(j1[asfas])).append(asd[0])
#     c_factor.update({tuple(j1[asfas]): asd[1]}) if c_factor.get(
#         tuple(j1[asfas])
#     ) is None else c_factor.get(tuple(j1[asfas])).append(asd[1])
#     ktext = round(asd[0], 2)
#     gfactor0_Ax.text(x, y - offsety, ktext, color="red")
#     gfactor0_Ax.text(x - offsetx, y + offsety, ktext, color="red")
#     cfactortext = round(asd[1], 2)
#     gfactor0_Ax.text(x, y + offsety, cfactortext, color="green")
#     gfactor0_Ax.text(x - offsetx, y - offsety, cfactortext, color="green")
# gfactor0_Ax.set_xlim(min(CumSpan) - 5, max(CumSpan) + 5)
# gfactor0_Fig.savefig(f"{path}\\gfactor0.png", dpi=300)


# print(c_factor)
# print(g_factor)
# ghalf_Fig, ghalf_Ax, asd = PLOTTER.Frame(Array3d, ForceList, "Distribute c,g")
# ghalf_col = {}
# for i, j in enumerate(Col_Coord_List[::-1]):
#     j = j[~np.isnan(j).any(axis=(1, 2))]
#     for i1, j1 in enumerate(j):
#         if not np.isnan(j1).any():
#             ColName = (
#                 f"COLUMN-{LabelsDict.get(tuple(j1[0]))}-{LabelsDict.get(tuple(j1[1]))}"
#             )
#             x = int(j1[0][0])
#             y = int(j1[0][1])
#             offsety = 0.3
#             offsetx = 0.3
#             scale = 1
#             length = int(j1[1][1]) - int(j1[0][1])

#             bot = (
#                 c_factor.get(tuple(j1[0])) if c_factor.get(tuple(j1[0])) != None else 1
#             )
#             top = (
#                 c_factor.get(tuple(j1[1])) if c_factor.get(tuple(j1[1])) != None else 1
#             )
#             latexk0, asd = gfactorhalfcol(bot, top)
#             UTIL.add_latex_data(f"g-halfcol-{i}", latexk0, ColName, mode)
#             ghalf_col.update({tuple(j1[0]): [asd[0]]}) if ghalf_col.get(
#                 tuple(j1[0])
#             ) is None else ghalf_col.get(tuple(j1[0])).append(asd[0])
#             ghalf_col.update({tuple(j1[1]): [asd[1]]}) if ghalf_col.get(
#                 tuple(j1[1])
#             ) is None else ghalf_col.get(tuple(j1[1])).append(asd[1])

#             ghalf_Ax.text(x, y + (length) - offsetx, round(asd[1], 2), color="green")
#             ghalf_Ax.text(x, y + offsetx, round(asd[0], 2), color="green")

# ghalf_beam = {}
# for i, j in enumerate(Beam_Coord_List[::-1]):
#     for i1, j1 in enumerate(j):
#         if not np.isnan(j1).any():
#             BeamName = (
#                 f"BEAM-{LabelsDict.get(tuple(j1[0]))}-{LabelsDict.get(tuple(j1[1]))}"
#             )
#             x = int(j1[0][0])
#             y = int(j1[0][1])
#             offsety = 0.3
#             offsetx = 0.3
#             scale = 1
#             b = 0.3
#             h = 0.6
#             height = j1[1][0] - j1[0][0]

#             left = (
#                 g_factor.get(tuple(j1[0])) if g_factor.get(tuple(j1[0])) != None else 1
#             )
#             right = (
#                 g_factor.get(tuple(j1[1])) if g_factor.get(tuple(j1[1])) != None else 1
#             )
#             latexk0, asd = gfactorhalfgirder(left, right)
#             UTIL.add_latex_data(f"ghalf-beam-{i}", latexk0, BeamName, mode)
#             ghalf_beam.update({tuple(j1[0]): [asd[0]]}) if ghalf_beam.get(
#                 tuple(j1[0])
#             ) is None else ghalf_beam.get(tuple(j1[0])).append(asd[0])
#             ghalf_beam.update({tuple(j1[1]): [asd[1]]}) if ghalf_beam.get(
#                 tuple(j1[1])
#             ) is None else ghalf_beam.get(tuple(j1[1])).append(asd[1])

#             ghalf_Ax.text(x + (length) - offsetx, y, round(asd[1], 2), color="red")
#             ghalf_Ax.text(x + offsetx, y, round(asd[0], 2), color="red")
# ghalf_Ax.set_xlim(min(CumSpan) - 5, max(CumSpan) + 5)
# ghalf_Fig.savefig(f"{path}\\ghalf.png", dpi=300)
