import json
import numpy as np
import streamlit as st
from shapely.geometry import Point, Polygon

vertex_coor = [
    (15.4267204, 108.7915547),
    (15.4063642, 108.7754271),
    (15.3970962, 108.7963701),
    (15.3908484, 108.8004471),
    (15.3748027, 108.8102677),
    (15.3407027, 108.8229709),
    (15.3532012, 108.8506946),
    (15.4013178, 108.8334837),
    (15.4182808, 108.8193643),
    (15.4244037, 108.8037),
    (15.4267204, 108.7915547)
]

def is_point_inside_polygon(x, y, polygon_vertices):
    # Convert the numpy array to a list of tuples
    polygon_vertices_list = [tuple(point) for point in polygon_vertices]

    # Create a Shapely Point object for the given (x, y) coordinates
    point = Point(x, y)

    # Create a Shapely Polygon object for the given vertex coordinates
    polygon = Polygon(polygon_vertices_list)

    # Check if the point lies within the polygon
    return point.within(polygon)


def generate_header(max_lat, min_lat, max_lon, min_lon, nx, ny):
    # Lat represents the y-axis
    lat_range = max_lat - min_lat
                    
    # Lon represents the x-axis
    lon_range = max_lon - min_lon
    
    dy = lat_range / ny
    dx = lon_range / nx
    
    return [{
        "header": {
            "la1": min_lat,
            "la2": max_lat,
            "lo1": min_lon,
            "lo2": max_lon,
            "nx": nx,
            "ny": ny,
            "dx": dx,
            "dy": dy,
            "GRIB_ELEMENT": grib_element,
        },
    } for grib_element in ["UGRD", "VGRD"]]


def generate_data(header, vertices, out_of_polygon_ind="const", default_value=None, random_min=2, random_max=3):
    header_content = header["header"]
    data = (np.random.rand(header_content["nx"] * header_content["ny"]) * (random_max - random_min) + random_min).tolist()
    for i in range(header_content["nx"]):
        for j in range(header_content["ny"]):
            center_x = header_content["la1"] + (0.5 + i) * header_content["dy"]
            center_y = header_content["lo1"] + (0.5 + j) * header_content["dx"]
            
            if not is_point_inside_polygon(center_x, center_y, polygon_vertices=vertices):
                if out_of_polygon_ind == "value":
                    data[i * header_content["nx"] + j] = default_value
                elif out_of_polygon_ind == "None":
                    data[i * header_content["nx"] + j] = None
    header["data"] = data
    return header

def create_fake_data(
    vertices,
    max_lat=None,
    min_lat=None,
    max_lon=None,
    min_lon=None,
    nx=4,
    ny=4,
    out_of_polygon_ind="const",
    default_value=None,
    random_min=2,
    random_max=3
):
    
    headers = generate_header(max_lat, min_lat, max_lon, min_lon, nx, ny)
    headers = [generate_data(header, vertices, out_of_polygon_ind, default_value, random_min, random_max) for header in headers]
    return headers

def main():
    max_lat = max([v[0] for v in vertex_coor])
    min_lat = min([v[0] for v in vertex_coor])
    max_lon = max([v[1] for v in vertex_coor])
    min_lon = min([v[1] for v in vertex_coor])

    st.title("Data Generation")
    
    enable_edit_lat_lon = st.checkbox("Edit lat, lon area")
    hide_json_content = st.checkbox("Hide JSON content")

    # Input parameters
    col1, col2 = st.columns(2)

    with col1:
        min_lat = st.number_input("Min Latitude:", value=min_lat, disabled=not enable_edit_lat_lon)
        min_lon = st.number_input("Min Longitude:", value=min_lon, disabled=not enable_edit_lat_lon)
        nx = st.number_input("Number of points (nx):", value=5, step=1)
        out_of_polygon_ind = st.radio("Out of Polygon Indicator:", ["value", "None"])
        random_min = st.number_input("Data Random Minimum Value:", value=0.0)

    with col2:
        max_lat = st.number_input("Max Latitude:", value=max_lat, disabled=not enable_edit_lat_lon)
        max_lon = st.number_input("Max Longitude:", value=max_lon, disabled=not enable_edit_lat_lon)
        ny = st.number_input("Number of points (ny):", value=5, step=1)
        default_value = st.number_input("Default Value (if out of polygon indicator = value):", value=0.0)
        random_max = st.number_input("Data Random Maximum Value:", value=1.0)

    if st.button("Generate"):
        # Call the data generation function with the specified inputs
        data = create_fake_data(vertex_coor, max_lat, min_lat, max_lon, min_lon, nx, ny, out_of_polygon_ind, default_value, random_min, random_max)
        
        # Display the generated data
        st.write("Generated Data:")
        if not hide_json_content:
            st.json(data)
        else:
            st.write("JSON data is hidden, click on Download to get the full file.")
        
        # Download JSON button
        json_data_str = json.dumps(data, indent=2)
        st.download_button("Download JSON", data=json_data_str, file_name="generated_data.json")

if __name__ == "__main__":
    main()
