from handcalcs.decorator import handcalc
import numpy as np
import PLOTTER_APPROX as PLOTTER
import UTILITIES_APPROX as UTIL
import forallpeople

forallpeople.environment("structural", top_level=True)


@handcalc(override="long", jupyter_display=False, precision=5)
def ColAxialCanti(ColList, Col_Number, Force, ForceHeight, SpanCum):
    X_bar = sum(ColList) / Col_Number  # Since Same Section
    ColCoefficient = (X_bar - ColList) / X_bar
    Moment = sum(Force * ForceHeight) / sum(ColCoefficient * SpanCum)  # Moment of Leftmost Column
    ColAxialArray = ColCoefficient * Moment
    return ColAxialArray


@handcalc(override="long", jupyter_display=False, precision=2)
def BeamShearMoment(ColAxial_Bot, ColAxial_Top, length, BeamShear):
    Shear = sum(ColAxial_Bot) + sum(BeamShear) - sum(ColAxial_Top)
    Moment = Shear * length / 2
    return Shear, Moment


@handcalc(override="long", jupyter_display=False, precision=2)
def ColMomentShear(BeamMoment, Height, ColMoment=[0]):
    Moment = sum(BeamMoment) - sum(ColMoment)
    Shear = (Moment * 2) / Height
    return Moment, Shear


@handcalc(override="long", jupyter_display=False, precision=2)
def BeamAxial(BeamAxial, ColShear, LateralForce=0):
    BeamAxial = LateralForce - sum(ColShear) + sum(BeamAxial)
    return BeamAxial, 0

@handcalc(override="long", jupyter_display=False, precision=2)
def AxialBeam(Col_Shear, Beam_Axial, Lateral_Force):
    Axial_Beam = sum(Lateral_Force) - sum(Col_Shear) - Beam_Axial
    return Axial_Beam, 0


def CANTICALCULATION(
    Name,
    BuildingHeightList,
    BuildingSpanList,
    NanList,
    ForceList,
    screenshot=False,
    plot=False,
    subfolder="Portal",
):
    Array3d, LabelsDict = UTIL.RemoveNan(BuildingHeightList, BuildingSpanList, NanList)
    ForceListCum = np.cumsum(ForceList[::-1])
    mode = True
    Col_Coord_List = UTIL.CreateColCoordList(Array3d)
    Beam_Coord_List = UTIL.CreateBeamCoordList(Array3d)
    CumSpanReverse = np.insert(np.cumsum(BuildingSpanList[::-1]), 0, 0)
    path = UTIL.create_folder("Canti Pics")

    Dtype = UTIL.Dtype
    # Create the structured array
    shear_array = np.empty(shape=(0,), dtype=Dtype)
    moment_array = np.empty(shape=(0,), dtype=Dtype)
    axial_array = np.empty(shape=(0,), dtype=Dtype)

    ColPerFloor = Col_Coord_List[:, :, -1, 0]
    for i, ColList in enumerate(ColPerFloor):
        member_type = "Col"
        Floor = f"Floor-{len(BuildingHeightList)-i}"
        SpanCum = CumSpanReverse[~np.isnan(ColList)][::-1]
        ColList = ColList[~np.isnan(ColList)]
        Col_Number = len(ColList)
        ForceReverse = ForceList[::-1]
        HeightReverse = BuildingHeightList[::-1]
        LateralForce = ForceReverse[: i + 1]
        HeightArray = np.cumsum(
            (HeightReverse[: i + 1].copy()).astype(np.float64)[::-1]
        )[::-1]
        HeightArray = HeightArray - HeightArray[-1] / 2
        latexAxialCanti, AxialCol = ColAxialCanti(
            ColList, Col_Number, LateralForce, HeightArray, SpanCum
        )
        UTIL.add_latex_data(f"Canti-ColAxial-{i}", latexAxialCanti, Floor)
        for i2, asd in enumerate(AxialCol):
            j1 = Col_Coord_List[i][i2]
            bot = j1[0]
            top = j1[1]
            axial_value = [
                (bot[0], bot[1], "Top", asd, asd, member_type),
                (top[0], top[1], "Bot", asd, asd, member_type),
            ]
            axial_array = UTIL.AppendStructuredArray(axial_array, axial_value, Dtype)

    for i, j in enumerate(Beam_Coord_List):
        for i1, j1 in enumerate(j):
            if not np.isnan(j1).any():
                member_type = "Beam"
                left = tuple(j1[0])
                right = tuple(j1[1])
                BeamName = f"BEAM-{LabelsDict.get(left)}-{LabelsDict.get(right)}"
                length = j1[1][0] - j1[0][0]

                conditionX_moment = axial_array["X"] == left[0]
                conditionY_moment = axial_array["Y"] == left[1]

                conditionX_shear = shear_array["X"] == left[0]
                conditionY_shear = shear_array["Y"] == left[1]

                condition_col = axial_array["Type"] == "Col"
                condition_beam = shear_array["Type"] == "Beam"

                condition_top = axial_array["Loc"] == "Top"
                condition_bot = axial_array["Loc"] == "Bot"

                col_axial_top = axial_array[
                    conditionX_moment
                    & conditionY_moment
                    & condition_col
                    & condition_top
                ]["ForceUnits"]
                col_axial_bot = axial_array[
                    conditionX_moment
                    & conditionY_moment
                    & condition_col
                    & condition_bot
                ]["ForceUnits"]
                beam_shear = shear_array[
                    conditionX_shear & conditionY_shear & condition_beam
                ]["ForceUnits"]

                LatexBeamAxial, asd = BeamShearMoment(
                    col_axial_bot, col_axial_top, length, beam_shear
                )
                shear, moment = asd
                UTIL.add_latex_data(f"Canti-Beam-{i}", LatexBeamAxial, BeamName)
                shear_value = [
                    (left[0], left[1], "Right", shear, shear, member_type),
                    (right[0], right[1], "Left", shear, shear, member_type),
                ]
                moment_value = [
                    (left[0], left[1], "Right", moment, moment, member_type),
                    (right[0], right[1], "Left", moment, moment, member_type),
                ]

                shear_array = UTIL.AppendStructuredArray(
                    shear_array, shear_value, Dtype
                )
                moment_array = UTIL.AppendStructuredArray(
                    moment_array, moment_value, Dtype
                )

    ColMomentCanti = {}
    ColShearCanti = {}
    for i, j in enumerate(Col_Coord_List):
        j = j[~np.isnan(j).any(axis=(1, 2))]
        for i1, j1 in enumerate(j):
            if not np.isnan(j1).any():
                member_type = "Col"
                bot = j1[0]
                top = j1[1]
                ColName = f"COLUMN-{LabelsDict.get(tuple(j1[0]))}-{LabelsDict.get(tuple(j1[1]))}"
                height = int(j1[1][1]) - int(j1[0][1])
                # BeamList = BeamShear.get(tuple(j1[0]))
                conditionX_moment = moment_array["X"] == top[0]
                conditionY_moment = moment_array["Y"] == top[1]
                condition_col = moment_array["Type"] == "Col"
                condition_beam = moment_array["Type"] == "Beam"

                col_moment = moment_array[
                    conditionX_moment & conditionY_moment & condition_col
                ]["ForceUnits"]
                beam_moment = moment_array[
                    conditionX_moment & conditionY_moment & condition_beam
                ]["ForceUnits"]
                LatexColAxial, asd = ColMomentShear(beam_moment, height, col_moment)
                UTIL.add_latex_data(f"Canti-ColMoment-{i}", LatexColAxial, ColName)
                moment, shear = asd
                moment_value = [
                    (bot[0], bot[1], "Top", moment, moment, member_type),
                    (top[0], top[1], "Bot", moment, moment, member_type),
                ]
                shear_value = [
                    (bot[0], bot[1], "Top", shear, shear, member_type),
                    (top[0], top[1], "Bot", shear, shear, member_type),
                ]

                moment_array = UTIL.AppendStructuredArray(
                    moment_array, moment_value, Dtype
                )
                shear_array = UTIL.AppendStructuredArray(
                    shear_array, shear_value, Dtype
                )
    UTIL.html_makerl()
    for i, j in enumerate(Beam_Coord_List):
        for i1, j1 in enumerate(j):
            if not np.isnan(j1).any():
                BeamName = f"BEAM-{LabelsDict.get(tuple(j1[0]))}-{LabelsDict.get(tuple(j1[1]))}"
                left = j1[0]
                right = j1[1]
                length = j1[1][0] - j1[0][0]
                # BeamList = BeamShear.get(tuple(j1[0]))
                conditionX_left_axial = axial_array["X"] == left[0]
                conditionY_left_axial = axial_array["Y"] == left[1]
                conditionX_right_axial = axial_array["X"] == right[0]
                conditionY_right_axial = axial_array["Y"] == right[1]
                condition_beam_axial = axial_array["Type"] == "Beam"
                condition_left_axial = axial_array["Loc"] == "Left"
                condition_right_axial = axial_array["Loc"] == "Left"

                conditionX_left_shear = shear_array["X"] == left[0]
                conditionY_left_shear = shear_array["Y"] == left[1]
                conditionX_right_shear = shear_array["X"] == right[0]
                conditionY_right_shear = shear_array["Y"] == right[1]
                condition_beam_shear = shear_array["Type"] == "Col"
                condition_left_shear = shear_array["Loc"] == "Left"
                condition_right_shear = shear_array["Loc"] == "Right"
                try:
                    axial_beam_right = axial_array[
                        conditionX_left_axial
                        & conditionY_left_axial
                        & condition_beam_axial
                        & condition_right_axial
                    ]["Force"][0]
                except:
                    axial_beam_right = 0
                shear_col = shear_array[
                    conditionX_left_shear & conditionY_left_shear & condition_beam_shear
                ]["Force"]
                print(shear_col)
                lateral_force = ForceList[::-1][: i + 1] if i1 == 0 else [0]

                LatexBeamAxial, asd = AxialBeam(
                    shear_col, axial_beam_right, lateral_force
                )
                axial_value = asd[0]

                UTIL.add_latex_data(
                    f"Axial-Beam-Factor{i}", LatexBeamAxial, BeamName, mode
                )
                member_type = "Beam"
                axial_array_value = [
                    (left[0], left[1], "Right", axial_value, axial_value, member_type),
                    (right[0], right[1], "Left", axial_value, axial_value, member_type),
                ]
                axial_array = UTIL.AppendStructuredArray(
                    axial_array,
                    axial_array_value,
                    Dtype,
                )
    import pandas as pd
    import dataframe_image as dfi

    path_dataframe = UTIL.create_folder(f"Canti dataframe- {Name}")
    moment_array_pd = pd.DataFrame(moment_array)
    moment_array_pd = moment_array_pd.rename(columns={"Force": "Moment"})
    moment_array_pd = moment_array_pd.drop("ForceUnits", axis=1)
    shear_array_pd = pd.DataFrame(shear_array)
    shear_array_pd = shear_array_pd.rename(columns={"Force": "Shear"})
    shear_array_pd = shear_array_pd.drop("ForceUnits", axis=1)
    axial_array_pd = pd.DataFrame(axial_array)
    axial_array_pd = axial_array_pd.rename(columns={"Force": "Axial"})
    axial_array_pd = axial_array_pd.drop("ForceUnits", axis=1)
    moment_array_pd.to_csv(f"{path_dataframe}/moment.csv")
    shear_array_pd.to_csv(f"{path_dataframe}/shear.csv")
    axial_array_pd.to_csv(f"{path_dataframe}/axial.csv")


    if plot:
        ColShear_Fig, ColMoment_Fig, ColAxial_Fig = PLOTTER.PortalPlot(
            Array3d,
            BuildingSpanList,
            BuildingHeightList,
            ForceList,
            Col_Coord_List,
            Beam_Coord_List,
            moment_array,
            shear_array,
            axial_array,
            subfolder=f"Canti Pictures - {Name}",
        )
    if screenshot:
        UTIL.selenium_screenshot(subfolder=f"Canti Solutions- {Name}")
