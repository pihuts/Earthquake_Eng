import matplotlib.pyplot as plt
import numpy as np
import os
import string
import matplotlib.patches as patches


def create_folder(sub_folder):
    """
    Create a new folder with the given name in the current working directory.

    Args:
    sub_folder (str): The name of the folder to create.

    Returns:
    path (str): The path of the created folder.
    """
    path = os.getcwd() + f"\\{sub_folder}"
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
    return path


def Frame(Array3d, ForceList, Title="Building Visualization"):
    """
    Create a 2D building visualization plot.

    Args:
    Array3d (numpy.ndarray): A 3D array containing node coordinates.
    ForceList (list): List of forces applied to the structure.
    Title (str, optional): Title of the plot. Default is "Building Visualization".

    Returns:
    fig (matplotlib.figure.Figure): The figure object containing the plot.
    ax (matplotlib.axes.Axes): The axes object containing the plot elements.
    LabelsDict (dict): A dictionary containing the node labels.
    """
    # Plot initialization
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1)
    plt.title(Title, loc="center", fontsize=16, color="green")
    XList, YList = Array3d[:, :, 0].copy(), Array3d[:, :, 1].copy()
    XListT, YListT = XList.T[:, 1:], YList.T[:, 1:]

    # Plot lines
    ax.plot(
        XList,
        YList,
        label="Line",
        linestyle="-",
        linewidth=8,
        marker="s",
        markersize=10,
        color="gray",
    )
    ax.plot(
        XListT,
        YListT,
        label="Line",
        linestyle="-",
        linewidth=8,
        marker="s",
        markersize=10,
        color="gray",
    )

    # Label the nodes
    LabelsDict = {}
    letters = string.ascii_uppercase

    node_count = 0
    for y, x in zip(YList[::-1].ravel(), XList[::-1].ravel()):
        arr1 = np.array([y, x])
        if not np.isnan(arr1).any():
            ax.text(
                x,
                y,
                f"{letters[node_count]}",
                fontsize=10,
                verticalalignment="bottom",
                horizontalalignment="right",
            )
            node_count += 1

        if node_count == len(letters):
            break

    return fig, ax, LabelsDict


def Frame1(Array3d, ForceList):
    """
    Create a 2D building visualization plot with arrows indicating the applied forces.

    Args:
    Array3d (numpy.ndarray): A 3D array containing node coordinates.
    ForceList (list): List of forces applied to the structure.

    Returns:
    fig (matplotlib.figure.Figure): The figure object containing the plot.
    ax (matplotlib.axes.Axes): The axes object containing the plot elements.
    LabelsDict (dict): A dictionary containing the node labels.
    """
    # Plot initialization
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_subplot(1, 1, 1)
    plt.title("Building Visualization", loc="left", fontsize=16, color="green")
    XList, YList = Array3d[:, :, 0].copy(), Array3d[:, :, 1].copy()
    XListT, YListT = XList.T[:, 1:], YList.T[:, 1:]
    # Plot lines
    ax.plot(
        XList,
        YList,
        label="Line",
        linestyle="-",
        linewidth=8,
        marker="s",
        markersize=10,
        color="gray",
    )
    ax.plot(
        XListT,
        YListT,
        label="Line",
        linestyle="-",
        linewidth=8,
        marker="s",
        markersize=10,
        color="gray",
    )

    # Label the nodes
    LabelsDict = {}
    letters = string.ascii_uppercase

    node_count = 0
    for y, x in zip(YList[::-1].ravel(), XList[::-1].ravel()):
        arr1 = np.array([y, x])
        if not np.isnan(arr1).any():
            ax.text(
                x,
                y,
                f"{letters[node_count]}",
                fontsize=10,
                verticalalignment="bottom",
                horizontalalignment="right",
            )
            LabelsDict.update({(x, y): f"{letters[node_count]}"})
            node_count += 1

        if node_count == len(letters):
            break

    # Add arrows to the plot
    x_start = np.full_like(XList[:, 0], -5)
    y_start = YList[:, 0]
    y_start[y_start == 0] = np.nan
    dx = np.full_like(x_start, 1)  # Change in x (arrow length)
    dy = y_start * 0
    ax.quiver(x_start, y_start, dx, dy, color="blue", scale=8)

    # Add text to the middle of the arrow
    text_x = x_start + (dx / 2) + 2
    text_y = y_start + 0.3  # Slightly above the arrow
    for i, j in np.ndenumerate(ForceList):
        ax.text(
            text_x[i],
            text_y[i],
            j,
            fontsize=12,
            verticalalignment="center",
            horizontalalignment="center",
        )
    plt.show()

    return fig, ax, LabelsDict


def PortalPlot(
    Array3d,
    BuildingSpanList,
    BuildingHeightList,
    ForceList,
    ColCoordList,
    BeamCoordList,
    MomentArray,
    ShearArray,
    AxialArray,
    subfolder="Portal Calculations",
):
    CumSpan = np.insert(
        np.cumsum(BuildingSpanList), 0, 0
    )  # cumsum then insert 0 at beginning
    ForceListCum = np.cumsum(ForceList[::-1])[::-1]
    path = create_folder(subfolder)
    ColShear_Fig, ColShear_Ax, asd = Frame(Array3d, ForceList, "Shear Diagram")
    for i, j in enumerate(ColCoordList):
        for i1, j1 in enumerate(j):
            if not np.isnan(j1).any():
                bot = j1[0]
                top = j1[1]
                x = bot[0]
                y = bot[1]
                scale = 1.5
                # shear = abs(ColShear.get(tuple(j1[1]))[0]) / kN
                conditionX = ShearArray["X"] == x
                conditionY = ShearArray["Y"] == y
                conditionType = ShearArray["Type"] == "Col"
                conditionLoc = ShearArray["Loc"] == "Top"
                print(x, y)
                shear = ShearArray[
                    conditionX & conditionY & conditionType & conditionLoc
                ]["Force"][0]
                width = -1 * (
                    min(
                        sum(BuildingSpanList) / len(BuildingSpanList),
                        min(BuildingSpanList),
                    )
                    * scale
                    * (shear / (np.nanmax(ForceListCum)))
                )
                height = int(j1[1][1]) - int(j1[0][1])
                ColShear_Ax.text(x, y + (height / 2), shear * kN)
                rect = patches.Rectangle(
                    (x, y),
                    width,
                    height,
                    linewidth=1,
                    edgecolor="r",
                    facecolor="green",
                    alpha=0.5,
                )
                ColShear_Ax.add_patch(rect)

    for i, j in enumerate(BeamCoordList):
        for i1, j1 in enumerate(j):
            if not np.isnan(j1).any():
                offsettext = 0.5
                x = int(j1[0][0])
                y = int(j1[0][1])
                scale = 1
                conditionX = ShearArray["X"] == x
                conditionY = ShearArray["Y"] == y
                conditionType = ShearArray["Type"] == "Beam"
                conditionLoc = ShearArray["Loc"] == "Right"
                shear = ShearArray[conditionX & conditionY & conditionType]["Force"][0]
                width = -1 * (
                    min(
                        sum(BuildingHeightList) / len(BuildingHeightList),
                        min(BuildingHeightList),
                    )
                    * scale
                    * (shear / (np.nanmax(ForceListCum)))
                )
                length = int(j1[1][0]) - int(j1[0][0])
                ColShear_Ax.text(
                    x + (length / 2) - offsettext, y, shear * kN, color="red"
                )
                rect = patches.Rectangle(
                    (x, y),
                    length,
                    width,
                    linewidth=1,
                    edgecolor="r",
                    facecolor="green",
                    alpha=0.5,
                )
                ColShear_Ax.add_patch(rect)
    ColShear_Ax.set_xlim(min(CumSpan) - 5, max(CumSpan) + 5)
    ColShear_Fig.savefig(f"{path}\\PortalShear.png", dpi=300)

    ColMoment_Fig, ColMoment_Ax, asd = Frame(Array3d, ForceList, "Moment Diagram")
    for i, j in enumerate(ColCoordList):
        for i1, j1 in enumerate(j):
            if not np.isnan(j1).any():
                x = int(j1[0][0])
                y = int(j1[0][1])
                offsety = 0.2
                offsetx = 0.8
                scale = 1
                conditionX = MomentArray["X"] == x
                conditionY = MomentArray["Y"] == y
                conditionType = MomentArray["Type"] == "Col"
                conditionLoc = MomentArray["Loc"] == "Top"
                Moment = MomentArray[
                    conditionX & conditionY & conditionType & conditionLoc
                ]["Force"][0]
                width = (
                    min(
                        sum(BuildingSpanList) / len(BuildingSpanList),
                        min(BuildingSpanList) / 2,
                    )
                    * scale
                    * (Moment / (np.nanmax(ForceListCum)))
                )
                height = int(j1[1][1]) - int(j1[0][1])
                ColMoment_Ax.text(
                    x - offsetx,
                    y + height - offsety,
                    round(Moment, 2) * kN * m,
                    color="green",
                )
                ColMoment_Ax.text(
                    x + offsetx, y + offsety, Moment * kN * m, color="green"
                )
                ColMoment_Ax.plot(
                    [x, x + width, x - width, x],
                    [y, y, y + height, y + height],
                    color="green",
                )

    for i, j in enumerate(BeamCoordList):
        for i1, j1 in enumerate(j):
            if not np.isnan(j1).any():
                x = int(j1[0][0])
                y = int(j1[0][1])
                offsety = 0.5
                offsetx = 0.3
                scale = 1
                conditionX = MomentArray["X"] == x
                conditionY = MomentArray["Y"] == y
                conditionType = MomentArray["Type"] == "Beam"
                conditionLoc = MomentArray["Loc"] == "Right"
                Moment = MomentArray[
                    conditionX & conditionY & conditionType & conditionLoc
                ]["Force"][0]
                width = (
                    min(
                        sum(BuildingHeightList) / len(BuildingHeightList),
                        min(BuildingHeightList) / 2,
                    )
                    * scale
                    * (Moment / (np.nanmax(ForceListCum)))
                )
                length = int(j1[1][0]) - int(j1[0][0])
                ColMoment_Ax.text(
                    x + length - offsetx,
                    y - offsety,
                    round(Moment, 2) * kN * m,
                    color="red",
                )
                ColMoment_Ax.text(
                    x + offsetx, y + offsety, Moment * kN * m, color="red"
                )
                ColMoment_Ax.plot(
                    [x, x, x + length, x + length],
                    [y, y + width, y - width, y],
                    color="red",
                )
    ColMoment_Ax.set_xlim(min(CumSpan) - 5, max(CumSpan) + 5)
    ColMoment_Fig.savefig(f"{path}\\PortalMoment.png", dpi=300)

    ColAxial_Fig, ColAxial_Ax, asd = Frame(Array3d, ForceList, "Axial Diagram")
    for i, j in enumerate(ColCoordList):
        for i1, j1 in enumerate(j):
            if not np.isnan(j1).any():
                x = int(j1[0][0])
                y = int(j1[0][1])
                offsety = 0.2
                offsetx = 0.8
                scale = 1
                height = int(j1[1][1]) - int(j1[0][1])

                conditionX = AxialArray["X"] == x
                conditionY = AxialArray["Y"] == y
                conditionType = AxialArray["Type"] == "Col"
                conditionLoc = AxialArray["Loc"] == "Top"
                Axial = AxialArray[
                    conditionX & conditionY & conditionType & conditionLoc
                ]["Force"][0]
                ColAxial_Ax.arrow(
                    x - offsetx,
                    y + height / 2 - offsety,
                    0,
                    -1,
                    color="red",
                    head_width=0.2,
                    head_length=1,
                ) if Axial > 0 else ColAxial_Ax.arrow(
                    x - offsetx,
                    y + height / 2 - offsety,
                    0,
                    1,
                    color="red",
                    head_width=0.2,
                    head_length=1,
                )

                ColAxial_Ax.text(
                    x - offsetx,
                    y + height / 2 - offsety,
                    round(Axial, 2) * kN,
                    color="green",
                )

    ColAxial_Ax.set_xlim(min(CumSpan) - 5, max(CumSpan) + 5)
    ColAxial_Fig.savefig(f"{path}\\PortalAxial.png", dpi=300)
    return ColShear_Fig, ColMoment_Fig, ColAxial_Fig
