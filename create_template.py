# -*- coding: utf-8 -*-
"""
Created on Thu Jul  4 17:36:05 2019

@author: Mostafa
"""
import os
import sys
import numpy as np
import geopandas as gpd
import pandas as pd
#from pprint import pprint as pp
from zipfile import ZipFile
os.chdir(os.path.dirname(os.path.abspath(__file__)))
cwd = os.getcwd()
from rem_mk_dir import rm_mk_dir


def template_generator(warehouse, output_path, user_input, include_all_parameters=False):
    """
    user_input: is a numpy array for the key parameters
    """
    # remove and create output paths
    rm_mk_dir(output_path)
    # path to the data in the warehouse
    template_layer = warehouse + '/template_layer.geojson'
    par_list_csv = warehouse + '/inputs_TUW_geophires.csv'
    template_reservoir_output = warehouse + '/template_reservoir_output.csv'
    # path to output files
    output_template_geojson = output_path + '/template.geojson'
    output_template_header_csv = output_path + '/headers.csv'
    output_zip_file = output_path + '/outputs.zip'

    # start calculation
    gdf = gpd.read_file(template_layer)
    par_list = pd.read_csv(par_list_csv)
    par = par_list.values
    parameters = par_list['Parameter'].values
    par_with_unit = par_list['par_with_unit'].values
    key_par = par_list['key_par'].values
    default_val = par_list['default_val'].values

    # extract the relevant parameters
    headers_without_unit = []
    if include_all_parameters:
        for i, item in enumerate(par_with_unit):
            #gdf = gdf.join(pd.DataFrame({item: default_val[i]}))
            gdf[item] = default_val[i]
            headers_without_unit.append(parameters[i])
    else:
        for i, item in enumerate(par_with_unit):
            if key_par[i] == 1:
                gdf[item] = default_val[i]
                headers_without_unit.append(parameters[i])
            else:
                flag = 1
                row_values = par[i, 3:-1]
                cond_index = np.argwhere(row_values != -999)[:, 0]
                for index in cond_index:
                    if row_values[index] != user_input[index]:
                        flag = 0
                        break
                if flag:
                    gdf[item] = default_val[i]
                    headers_without_unit.append(parameters[i])
    gdf.to_file(output_template_geojson, driver='GeoJSON', encoding="utf-8")
    df = pd.DataFrame()
    for header in headers_without_unit:
        temp = ""
        for char in header:
            if char.isalnum():
                temp = temp + char
            else:
                temp = temp + "_"
        df[temp] = ""
    df.to_csv(output_template_header_csv, index=False, encoding="utf-8")
    zf = ZipFile(output_zip_file, 'w')
    try:
        zf.write(output_template_geojson)
        zf.write(output_template_header_csv)
        if user_input[0] == 5:
            zf.write(template_reservoir_output)
    finally:
        zf.close()
    return output_zip_file


if __name__ == "__main__":
    # note: default_inputs_path must not change in different runs. it uses 
    warehouse = cwd + "/data_warehouse"
    output_path = cwd + "/outputs"
    user_input = np.array([2, 1, 1, 3, 1, 2, 0, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    template_generator(warehouse, output_path, user_input)   
