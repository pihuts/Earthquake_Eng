import numpy as np
import os
import forallpeople
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
import math
from selenium.webdriver.chrome.options import Options
from itertools import islice
import PLOTTER_APPROX as PLOTTER

forallpeople.environment("structural", top_level=True)


ForceList = np.insert(np.array([133.493, 212.375, 233.379]), 0, np.nan)  # bot to top
BuildingHeightList = np.array([4, 3, 3])  # bot to top
BuildingSpanList = np.array([6, 7, 5])  # left to right
NanList = [(18, 10)]  # (x,y) coordinates of the NaN values


LatexData = {}
testdata = {}

Dtype = np.dtype(
    [
        ("X", np.float64),
        ("Y", np.float64),
        ("Loc", "U10"),
        ("Force", np.float64),
        ("ForceUnits", forallpeople.Physical),
        ("Type", "U10"),
    ]
)


# Create the ColCoordList
def CreateColCoordList(Array3d):
    # test = np.stack((Array3d[1:, 0:-1], Array3d[1:, 1:]), axis=1)

    test = np.array(
        [
            np.stack((Array3d[i], Array3d[i + 1]), axis=1)
            if i > 0
            else np.stack((Array3d[i], Array3d[i + 1]), axis=1)
            for i in range(Array3d.shape[0] - 1)
        ]
    )
    return test[::-1]


def CreateBeamCoordList(Array3d):
    test = np.stack((Array3d[1:, 0:-1], Array3d[1:, 1:]), axis=2)
    return test[::-1]


def UpdateDict(Dict, Key, Value):
    if Key in Dict:
        Dict[Key].append(Value)
    else:
        Dict[Key] = Value
    return Dict


def RemoveNan(BuildingHeightList, BuildingSpanList, NanList):
    """
    Remove NaN values from the given NodesArrayX and NodesArrayY based on the NanList.

    Args:
    NodesArrayY (np.array): Y-coordinate array
    NodesArrayX (np.array): X-coordinate array
    NanList (list): List of NaN values

    Returns:
    array3d (np.array): 3D array of NodesArrayX and NodesArrayY with NaN values removed
    """
    Coords = []
    CumSpan = np.insert(
        np.cumsum(BuildingSpanList), 0, 0
    )  # cumsum then insert 0 at beginning
    CumHeight = np.insert(
        np.cumsum(BuildingHeightList), 0, 0
    )  # cumsum then insert 0 at beginning
    # Loop through the NanList and find the indices in the NodesArrayX and NodesArrayY
    NodesArrayY = np.array(
        [[i] * (len(BuildingSpanList) + 1) for i in CumHeight], dtype=float
    )
    NodesArrayX = np.array([CumSpan for i, j in enumerate(CumHeight)], dtype=float)

    if NanList is not None:
        for j in NanList:
            asd, col_indices = np.where(NodesArrayX == j[0])
            row_indices, asd = np.where(NodesArrayY == j[1])
            Coords.append((row_indices[0], col_indices[0]))
        # Replace the found coordinates in the NodesArrayX and NodesArrayY with np.nan
        for j in Coords:
            NodesArrayY[tuple(j)] = np.nan
            NodesArrayX[tuple(j)] = np.nan

    # Stack the NodesArrayX and NodesArrayY into a 3D array
    array3d = np.stack((NodesArrayX, NodesArrayY), axis=2)

    XList, YList = array3d[:, :, 0].copy(), array3d[:, :, 1].copy()
    XListT, YListT = XList.T[:, 1:], YList.T[:, 1:]

    import string

    LabelsDict = {}
    letters = string.ascii_uppercase + string.ascii_lowercase

    node_count = 0
    for y, x in zip(YList[::-1].ravel(), XList[::-1].ravel()):
        arr1 = np.array((x, y))
        if not np.isnan(arr1).any():
            LabelsDict = UpdateDict(LabelsDict, tuple(arr1), letters[node_count])
            node_count += 1


    return array3d, LabelsDict


def create_folder(sub_folder):
    """
    Create a folder with the specified name if it does not already exist.

    Args:
    sub_folder (str): Name of the folder to be created

    Returns:
    path (str): Path of the created folder
    """
    path = os.path.join(os.getcwd(), sub_folder)
    if not os.path.exists(path):
        os.makedirs(path)
    return path


def AppendStructuredArray(Array, Value, dtype):
    if type(Value) == "list":
        for j in Value:
            child_array = np.array([j], dtype=dtype)
            father_array = np.append(Array, child_array)
    else:
        child_array = np.array([Value], dtype=dtype)
        father_array = np.append(Array, child_array)
    return father_array


def add_latex_data(key, values, description, test=False):
    """
    Add LaTeX data to the corresponding dictionary (LatexData or testdata).

    Args:
    key (str): Key for the data
    values (list): List of values
    description (str): Description of the data
    test (bool, optional): Flag to indicate if data should be added to testdata (True) or LatexData (False)
    """
    target_dict = testdata if test else LatexData

    if key not in target_dict:
        target_dict[key] = [[values, description]]
    else:
        target_dict[key].append

        target_dict[key].append([values, description])


def chunks(data, SIZE=10000):
    """
    Split a dictionary into chunks of a given size.

    Args:
    data (dict): Dictionary to be split
    SIZE (int, optional): Maximum size of each chunk

    Yields:
    chunk (dict): Dictionary chunk of the specified size
    """
    it = iter(data)
    for i in range(0, len(data), SIZE):
        yield {k: data[k] for k in islice(it, SIZE)}


def selenium_screenshot(test=False, subfolder="Solutions"):
    """
    Take screenshots of web elements using Selenium and save them to the specified folder.

    Args:
    test (bool, optional): Flag to indicate if test data should be used (True) or LatexData (False)
    """
    data = testdata if test else LatexData
    new_data = chunks(data, min(10, len(data)))

    for i, j in enumerate(new_data):
        data_chunk_no = i
        data1 = j
        path_latex = create_folder(subfolder)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--window-size=3200x20800")
        driver = webdriver.Chrome("chromedriver.exe", options=chrome_options)
        path = create_folder("Beams")
        driver.get(f"{path}\\{data_chunk_no}.html")
        time.sleep(5)
        for keys in data1.keys():
            element = driver.find_element(By.ID, keys)
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            element.screenshot(f"{path_latex}\\{keys}.png")
            time.sleep(0.2)


def html_makerl(cols=3, test=False):
    """
    Create an HTML file containing a table with the given LaTeX data.

    Args:
    test (bool, optional): Flag to indicate if test data should be used (True) or LatexData (False)
    """
    shear_Table = ""
    shear_th = []
    data1 = testdata if test else LatexData

    # Chunks the data into multiple pieces for easier browsing loading later
    chunk_data = chunks(data1, min(10, len(data1)))

    for data_chunk_no, data2 in enumerate(chunk_data):
        shear_Table = ""

        for keys in data2.keys():
            shear_th = []
            shear_tr = []
            ValueList = data2[keys]

            for i, j in enumerate(ValueList):
                Key = f"{keys}-{math.ceil(i/3)}"
                Value = j[0]
                Description = j[1]
                shear_th.append(
                    f"<td><h2>{Description}</h2><p style='font-size:10px;'>{Value}</p></td>"
                )
                if len(shear_th) > cols:
                    shear_tr.append(f"<tr>{''.join(shear_th)}</tr>")
                    shear_th = []
                # shear_th += f"<td><h2>{Description}</h2><p style='font-size:10px;'>{Value}</p></td>"

            shear_tr.append(f"<tr>{''.join(shear_th)}</tr>")
            shear_Table += (
                f"""<div ><table id= "{keys}" >{''.join(shear_tr)}</table></div>"""
            )

        div = (
            """<!DOCTYPE html>
  <html>
    <head>
      <meta charset="UTF-8">
      <title>MathJax Example</title>
      <style>
        body {
          font-family: sans-serif;
        }
        
        /* Add borders to tables */
        table {
          border-collapse: collapse;
          border: 2px solid black;
          margin: 10px 0;
        }
        
        th, td {
          border: 1px solid black;
          padding: 5px;
          vertical-align: top;
        }
      </style>
      <script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML"></script>
    </head>
    <body>
  %s
    </body>
  </html>

      """
            % shear_Table
        )
        path = create_folder("Beams")

        if not test:
            with open(f"{path}\\{data_chunk_no}.html", "w", encoding="utf-8") as file:
                file.write(div)
        else:
            with open(
                f"{path}\\test-{data_chunk_no}.html", "w", encoding="utf-8"
            ) as file:
                file.write(div)

