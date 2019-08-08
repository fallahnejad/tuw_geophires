# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 15:26:32 2019

@author: Mostafa
"""
from datetime import datetime
import os
import geopandas as gpd
import pandas as pd
import numpy as np
os.chdir(os.path.dirname(os.path.abspath(__file__)))
cwd = os.getcwd()
from tuw_geophires import run_tuw_geophires
from rem_mk_dir import rm_mk_dir
#from pprint import pprint as pp
#from line_profiler import LineProfiler

# %%
output_column_headers = ["Accrued financing during construction (%)",
"Annual Thermal Drawdown (%/year)",
"Annualized capital costs (M.USD)",
"Average annual heat production (GWh/yr)",
"Average Annual Net Electricity Generation (GWh/yr)",
"Average annual pumping costs (M.USD/yr)",
"Average buoyancy correction (kPa)",
"Average Direct-Use Heat Production (MWth)",
"Average direct-use heat production (MWth)",
"Average injection well pressure drop (kPa)",
"Average injection well pump pressure drop (kPa)",
"Average Net Electricity Production (MWe)",
"Average net power generation (MWe)",
"Average production well pressure drop (kPa)",
"Average production well pump pressure drop (kPa)",
"Average production well temperature drop (deg.C)",
"Average reservoir pressure drop (kPa)",
"Average total geofluid pressure drop (kPa)",
"Bottom-hole temperature (deg.C)",
"Capacity factor (%)",
"Constant production well temperature drop (deg.C)",
"Direct-Use heat breakeven price ($/MMBTU)",
"Drilling and completion costs (for redrilling) (M.USD)",
"Drilling and completion costs (M.USD)",
"Drilling and completion costs per redrilled well (M.USD)",
"Drilling and completion costs per well (M.USD)",
"Economic Model",
"Electricity breakeven price (cents/kWh)",
"End-Use Option",
"Exploration costs (M.USD)",
"Field gathering system costs (M.USD)",
"Fixed Charge Rate (FCR) (%)",
"Flowrate per production well (kg/s)",
"Fracture area (m^2)",
"fracture diameter (m)",
"Fracture model",
"Fracture separation (m)",
"Fracture width (m)",
"Geothermal gradient (deg.C/km)",
"Initial direct-use heat production (MWth)",
"Initial geofluid availability (MWe/(kg/s))",
"Initial net power generation (MWe)",
"Initial pumping power/net installed power (%)",
"Injection temperature (deg.C)",
"Injection well casing ID (inches)",
"Injectivity Index (kg/s/bar)",
"Interest Rate (%)",
"m/A Drawdown Parameter (kg/s/m^2)",
"Maximum reservoir temperature (deg.C)",
"Number of fractures",
"Number of injection wells",
"Number of production wells",
"Number of segments",
"Number of times redrilling",
"Plant outlet pressure (kPa)",
"Power plant maintenance costs (M.USD/yr)",
"Power plant type",
"Produciton well casing ID (inches)",
"Production wellhead pressure (kPa)",
"Productivity Index (kg/s/bar)",
"Project lifetime (years)",
"Pump efficiency (%)",
"Reservoir density (kg/m^3)",
"Reservoir heat capacity (J/kg/K)",
"Reservoir hydrostatic pressure (kPa)",
"Reservoir impedance (GPa/m^3/s)",
"Reservoir Model",
"Reservoir permeability (m^2)",
"Reservoir porosity (%)",
"Reservoir thermal conductivity (W/m/K)",
"Reservoir thickness (m)",
"Reservoir volume (m^3)",
"Reservoir width (m)",
"Segment 1 geothermal gradient (deg.C/km)",
"Segment 1 thickness (km)",
"Segment 2 geothermal gradient (deg.C/km)",
"Segment 2 thickness (km)",
"Segment 3 geothermal gradient (deg.C/km)",
"Segment 3 thickness (km)",
"Segment 4 geothermal gradient (deg.C/km)",
"Stimulation costs (for redrilling) (M.USD)",
"Stimulation costs (M.USD)",
"Surface power plant costs (M.USD)",
"Total capital costs (M.USD)",
"Total operating and maintenance costs (M.USD/yr)",
"Total surface equipment costs (M.USD)",
"Transmission pipeline cost (M.USD)",
"Water costs (M.USD/yr)",
"Water loss rate (%)",
"Well depth (m)",
"Well seperation = fracture diameter (m)",
"Well seperation = fracture height (m)",
"Wellfield maintenance costs (M.USD/yr)",
]


# %%
def rm_file(file, *args):
    if os.path.exists(file):
        os.remove(file)
    for arg in args:
        if os.path.exists(arg):
            os.remove(arg)


# %%
def call_tuw_geophires(output_path, uploaded_json_file, uploaded_reservoir_output_file="",
                       max_nr_feature=1000):
    """
    input_json_file: filled template with geojson format (or json generated by ArcMap)
    temp_text_file: used to save results in loops and will be deleted at the end of the process
    output_text_file: Sent to the user as output
    output_json_file: json file with results written in it (with geometries)
    output_csv: json file with results written in it (without geometries)
    uploaded_reservoir_output_file: required if the reservoir model 5 is selected
    max_nr_feature: limited to 1000 entries to avoid
    
    """
    rm_mk_dir(output_path)
    temp_text_file = output_path + '/temp.txt'
    output_text_file = output_path + '/output_summary.txt'
    output_json_file = output_path + '/output_layer.geojson'
    output_csv = output_path + '/output_data.csv'
    start = str(datetime.now())
    with open(output_text_file, "w", encoding='utf-8') as f:
        f.write("The calculation results are for: %s\n" %start)
    f.close()
    gdf = gpd.read_file(uploaded_json_file, dtype='object', na_values='nan', encoding="utf-8")
    model_par = []
    units = []
    # in case of arc map users, the headers should be modified to the known
    # headers for Geophires.
    modified_col = []
    for item in gdf.columns:
        temp = item
        temp = temp.replace("_O_M_", "_O&M_")
        temp = temp.replace("__", " (")
        temp = temp.replace("_", " ")
        temp = temp.strip()
        temp = temp.replace("End Use", "End-Use")
        modified_col.append(temp)
    # apply the headers if there is a necessity
    if len(modified_col) > 0:
        gdf.columns = modified_col
    column_headers = gdf.columns
    # model_par: includes all the fields within the input shapefile regardless
    # of whether they are accepted in Geophires or not.
    for item in column_headers:
        if " (" in item:
            par, unit = item.split(" (")
            model_par.append(par)
            units.append("(" + unit)
        elif "(" in item:
            par, unit = item.split("(")
            model_par.append(par)
            units.append("(" + unit)
        else:
            model_par.append(item)
            units.append("")

    nr_features =  gdf.shape[0]
    if nr_features > max_nr_feature:
        raise Exception('The number of features should not exceed from %s.' %max_nr_feature)

    gdf2 = gpd.GeoDataFrame(np.array([[""]*len(output_column_headers)]*gdf.shape[0]).astype('<U60'), columns=output_column_headers, index=gdf.index, geometry=gdf['geometry'])
    if uploaded_reservoir_output_file != "":
        df_reservoir_output = pd.read_csv(uploaded_reservoir_output_file)
    # index of used headers
    used_header_indices = []
    failure_object_ids = []
    failure_flag = 0
    for row in range(nr_features):
        obj_id = row + 1
        print("OBJECT ID: ", obj_id)
        input_text = []
        entry = gdf.iloc[row]
        # last element of entry is geometry which is not passed to the next
        # function
        for i, item in enumerate(model_par):
            input_text.append(item + ', ' + str(entry[i]) + ',\n')
        # if reservoir model type 5 selected, create reservoir output
        contentprodtemp = []
        if entry[0] == 5:
            if uploaded_reservoir_output_file == "":
                failure_flag = 1
                failure_object_ids.append(row)
                print('Error: TUW-GEOPHIRES could not read reservoir output file.')
                continue
            else:
                try:
                    temp_df_res = df_reservoir_output.loc[df_reservoir_output['OBJECTID'] == obj_id].values
                    for row in enumerate(temp_df_res.shape[0]):
                        contentprodtemp.append(str(temp_df_res[row, 1]) + ', ' + str(temp_df_res[row, 2]) + ',\n')
                    temp_df_res = None
                except:
                    failure_flag = 1
                    failure_object_ids.append(row)
                    print('Error: TUW-GEOPHIRES could not find column OBJECTID.')
                    continue
        par, val = run_tuw_geophires(input_text, contentprodtemp, row+1,
                                     output_text_file, temp_text_file)
        if par == [] and val == []:
            failure_flag = 1
            failure_object_ids.append(row)
            continue
        par_lowercase = [item.lower() for item in par]
        # remove duplicates
        par_set = list(set(par_lowercase))
        par_unique = np.array([par[par_lowercase.index(k)] for k in par_set])
        val_unique = np.array([val[par_lowercase.index(k)] for k in par_set])
        val_ind = []
        for item in par_unique:
            if item in output_column_headers:
                val_ind.append(output_column_headers.index(item))
            elif item + " (M.USD)" in output_column_headers:
                val_ind.append(output_column_headers.index(item + " (M.USD)"))
            elif item + " (M.USD/yr)" in output_column_headers:
                val_ind.append(output_column_headers.index(item + " (M.USD/yr)"))
            else:
                print(item)
                raise Exception("the parameter was not found!")
        # while the indices of different features in the loop may different,
        # the headers should be saved.
        used_header_indices = list(set(used_header_indices + val_ind))
        col_to_write = [output_column_headers[j] for j in val_ind]
        # val_unique should have the same type as of gdf2
        gdf2.loc[row, col_to_write] = val_unique
    if failure_flag:
        print(("#"*90+"\n")*3)
        print("WARNING: The follwoing OBJECT IDs were skipped:")
        for id in failure_object_ids:
            print('OBJECT ID %s' %(id+1))
        print(("#"*90+"\n")*3)
    rm_file(temp_text_file)    
    not_used_header_indices = list(set(list(range(len(output_column_headers)))) - set(used_header_indices))
    not_used_columns = gdf2.columns[not_used_header_indices]
    gdf2 = gdf2.drop(columns=not_used_columns)
    
    gdf2_headers_lowercase = [item.lower() for item in gdf2.columns]
    gdf_headers_lowercase = [item.lower() for item in gdf.columns]
    common_headers = list(set(gdf_headers_lowercase) & set(gdf2_headers_lowercase))
    # remove headers from gdf and not from gdff2 in order to keep the default values from Geophires
    index_for_delete = [gdf_headers_lowercase.index(item) for item in common_headers]
    gdf = gdf.drop(columns=gdf.columns[index_for_delete])
    gdf = pd.concat([gdf, gdf2], axis=1).pipe(gpd.GeoDataFrame)
    gdf.to_file(output_json_file, driver='GeoJSON', encoding="utf-8")
    column_list = gdf.columns
    csv_headers = []
    for col in column_list:
        col_splitted = col.split(" (")
        if len(col_splitted) > 1:
            # -2 for " ("
            par = col[:-len(col_splitted[-1])-2]
        else:
            par = col
        par = par.strip()
        par_len = len(par)
        temp = ""
        for i, char in enumerate(par):
            if char.isalnum():
                temp = temp + char
            else:
                if i == par_len-1:
                    pass
                else:
                    temp = temp + "_"
        csv_headers.append(temp)
    gdf.columns = csv_headers
    df = pd.DataFrame()
    for header in gdf.columns:
        if header != 'geometry':
            df[header] = gdf[header]
    df.to_csv(output_csv, index=False)
    gdf = None
    df = None


if __name__ == "__main__":
    upload_path = cwd + "/uploads"
    output_path = cwd + "/outputs"
    uploaded_json_file = upload_path + '/egs2000.geojson'
    uploaded_reservoir_output_file = upload_path + '/uploaded_reservoir_output.csv'
    call_tuw_geophires(output_path, uploaded_json_file, uploaded_reservoir_output_file)
