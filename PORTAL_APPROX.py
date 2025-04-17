from handcalcs.decorator import handcalc
import numpy as np
import PLOTTER_APPROX as PLOTTER
import UTILITIES_APPROX as UTIL
import forallpeople

forallpeople.environment("structural", top_level=True)


# Define the Col() function to calculate Shear and EndMoment
@handcalc(jupyter_display=False, precision=2)
def ColShearMoment(length, Force, Side, NumberCol):
    V = Force / NumberCol
    if Side == "Exterior":
        Shear = V
    elif Side == "Interior":
        Shear = 2 * V
    EndMoment = Shear * (length) / 2
    return Shear, EndMoment


@handcalc(override="long", jupyter_display=False, precision=2)
def BeamShearMoment(ColMoment, Length, BeamMoment=[0]):
    EndMoment = sum(ColMoment) - sum(BeamMoment)
    Shear = (EndMoment * 2) / Length
    return Shear, EndMoment


@handcalc(override="long", jupyter_display=False, precision=2)
def AxialCol(BeamShear_right, BeamShear_left, ColAxial=[0]):
    axial_col = sum(BeamShear_right) + sum(ColAxial) - sum(BeamShear_left)

    return axial_col, 0


@handcalc(override="long", jupyter_display=False, precision=2)
def AxialBeam(Col_Shear, Beam_Axial, Lateral_Force):
    Axial_Beam = sum(Lateral_Force) - sum(Col_Shear) - Beam_Axial
    return Axial_Beam, 0


def UpdateDict(Dict, Key, Value):
    if Key in Dict:
        Dict[Key].append(Value)
    else:
        Dict[Key] = [Value]
    return Dict


def PORTALCALCULTATION(
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

    Dtype = UTIL.Dtype
    # Create the structured array
    shear_array = np.empty(shape=(0,), dtype=Dtype)
    moment_array = np.empty(shape=(0,), dtype=Dtype)
    axial_array = np.empty(shape=(0,), dtype=Dtype)
    # Iterate through the ColCoordList, calculate Shear and EndMoment, and store the results in the dictionaries

    for i, j in enumerate(Col_Coord_List):
        j = j[~np.isnan(j).any(axis=(1, 2))]
        for i1, j1 in enumerate(j):
            if not np.isnan(j1).any():
                title_calculation = f"Portal-Col-{i}"
                member_type = "Col"
                bot = tuple(j1[0])
                top = tuple(j1[1])
                Col_Name = f"COLUMN-{LabelsDict.get(top)}-{LabelsDict.get(bot)}"
                length = (j1[1][1] - j1[0][1]) * m
                Shear = (ForceListCum[i]) * kN
                Side = "Exterior" if i1 == 0 or i1 == len(j) - 1 else "Interior"
                NumberCol = len(j) * 2 - 2
                LatexCol, asd = ColShearMoment(length, Shear, Side, NumberCol)
                shear, moment = asd
                UTIL.add_latex_data(title_calculation, LatexCol, Col_Name)
                shear_value = [
                    (bot[0], bot[1], "Top", shear, shear, member_type),
                    (top[0], top[1], "Bot", shear, shear, member_type),
                ]

                moment_value = [
                    (bot[0], bot[1], "Top", moment, moment, member_type),
                    (top[0], top[1], "Bot", moment, moment, member_type),
                ]
                shear_array = UTIL.AppendStructuredArray(
                    shear_array,
                    shear_value,
                    Dtype,
                )

                moment_array = UTIL.AppendStructuredArray(
                    moment_array,
                    moment_value,
                    Dtype,
                )

    for i, j in enumerate(Beam_Coord_List):
        for i1, j1 in enumerate(j):
            if not np.isnan(j1).any():
                title_calculation = f"Portal-Beam-{i}"
                left = tuple(j1[0])
                right = tuple(j1[1])
                member_type = "Beam"
                Beam_Name = f"BEAM-{LabelsDict.get(right)}-{LabelsDict.get(left)}"
                length = j1[1][0] * m - j1[0][0] * m
                conditionX_moment = moment_array["X"] == left[0]
                conditionY_moment = moment_array["Y"] == left[1]
                condition_col = moment_array["Type"] == "Col"
                condition_beam = moment_array["Type"] == "Beam"

                col_moment = moment_array[
                    conditionX_moment & conditionY_moment & condition_col
                ]["ForceUnits"]
                beam_moment = moment_array[
                    conditionX_moment & conditionY_moment & condition_beam
                ]["ForceUnits"]
                latex_beam_moment_shear, asd = BeamShearMoment(
                    col_moment, length, beam_moment
                )
                shear, moment = asd
                UTIL.add_latex_data(
                    title_calculation, latex_beam_moment_shear, Beam_Name
                )

                shear_value = [
                    (left[0], left[1], "Right", shear, shear, member_type),
                    (right[0], right[1], "Left", shear, shear, member_type),
                ]
                moment_value = [
                    (left[0], left[1], "Right", moment, moment, member_type),
                    (right[0], right[1], "Left", moment, moment, member_type),
                ]
                shear_array = UTIL.AppendStructuredArray(
                    shear_array,
                    shear_value,
                    Dtype,
                )
                moment_array = UTIL.AppendStructuredArray(
                    moment_array,
                    moment_value,
                    Dtype,
                )

    for i, j in enumerate(Col_Coord_List):
        j = j[~np.isnan(j).any(axis=(1, 2))]
        for i1, j1 in enumerate(j):
            if not np.isnan(j1).any():
                title_calculation = f"Portal-Axial-{i}"
                member_type = "Col"
                bot = tuple(j1[0])
                top = tuple(j1[1])

                Col_Name = (
                    f"COLUMN-{LabelsDict.get(tuple(top))}-{LabelsDict.get(tuple(bot))}"
                )
                length = (j1[1][1] - j1[0][1]) * m
                conditionX_moment = axial_array["X"] == top[0]
                conditionY_moment = axial_array["Y"] == top[1]

                conditionX_shear = shear_array["X"] == top[0]
                conditionY_shear = shear_array["Y"] == top[1]

                condition_col = axial_array["Type"] == "Col"
                condition_beam = shear_array["Type"] == "Beam"

                condition_right = shear_array["Loc"] == "Right"
                condition_left = shear_array["Loc"] == "Left"

                col_axial = axial_array[
                    conditionX_moment & conditionY_moment & condition_col
                ]["ForceUnits"]
                beam_shear_right = shear_array[
                    conditionX_shear
                    & conditionY_shear
                    & condition_beam
                    & condition_right
                ]["ForceUnits"]
                beam_shear_left = shear_array[
                    conditionX_shear
                    & conditionY_shear
                    & condition_beam
                    & condition_left
                ]["ForceUnits"]
                LatexCol, asd = AxialCol(beam_shear_right, beam_shear_left, col_axial)
                axial, moment = asd
                UTIL.add_latex_data(title_calculation, LatexCol, Col_Name)
                axial_value = [
                    (bot[0], bot[1], "Top", axial, axial, member_type),
                    (top[0], top[1], "Bot", axial, axial, member_type),
                ]
                axial_array = UTIL.AppendStructuredArray(
                    axial_array,
                    axial_value,
                    Dtype,
                )
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

                lateral_force = ForceList[::-1][: i + 1] if i1 == 0 else [0]
                print(shear_col, axial_beam_right, lateral_force)
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

    path_dataframe = UTIL.create_folder(f"Portal dataframe-{Name}")
    moment_array_pd = pd.DataFrame(moment_array)
    moment_array_pd = moment_array_pd.rename(columns={"Force": "Moment"})
    moment_array_pd = moment_array_pd.drop("ForceUnits", axis=1)
    shear_array_pd = pd.DataFrame(shear_array)
    shear_array_pd = shear_array_pd.rename(columns={"Force": "Shear"})
    shear_array_pd = shear_array_pd.drop("ForceUnits", axis=1)
    axial_array_pd = pd.DataFrame(axial_array)
    axial_array_pd = axial_array_pd.rename(columns={"Force": "Axial"})
    axial_array_pd = axial_array_pd.drop("ForceUnits", axis=1)
    moment_array_pd.to_csv(f"{path_dataframe}//moment_array_pd.csv")
    shear_array_pd.to_csv(f"{path_dataframe}//shear_array_pd.csv")
    axial_array_pd.to_csv(f"{path_dataframe}//axial_array_pd.csv")

    # dfi.export(shear_array_pd, f"{path_dataframe}//shear_array_pd.png")
    # dfi.export(axial_array_pd, f"{path_dataframe}//axial_array_pd.png")
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
            subfolder=f"Portal Pictures-{Name}",
        )
    UTIL.html_makerl(4)
    if screenshot:
        UTIL.selenium_screenshot(subfolder=f"Portal Calculation-{Name}")
