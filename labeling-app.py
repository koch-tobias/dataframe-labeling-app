import streamlit as st
import pandas as pd
import numpy as np
import os 
from datetime import datetime
from shutil import copy2

# initialize labels
labels = {0: "Label 1", 1: "Label 2", 2: "Label 3", 3: "Label 4", 4: "Label 5"}
labels_keys = labels.keys()

# create sidebar to upload the csv file and display the possible labels
st.title("Data Labeling Tool")
col1, col2 = st.columns(2)
st.sidebar.write("## CSV-Datei hochladen")
uploaded_file = st.sidebar.file_uploader("# CSV-Datei hochladen", type="csv")

# CSS, to display the text centered
st.sidebar.markdown(
    """
    <style>
    .centered-bold {
        text-align: center;
        font-weight: bold;
    }

    </style>
    """,
    unsafe_allow_html=True
)

st.sidebar.write("## Mögliche Labels:")
col1, col2 = st.sidebar.columns((1, 1))
for i in range(len(labels)):
    with col1:
        st.write(f"<div class='centered-bold'>{i}:</div>", unsafe_allow_html=True)
    with col2:
        st.write(f"<div class='centered-bold'>{labels[i]}</div>", unsafe_allow_html=True)


# define all paths
filename = "dataset" # file name for the uploaded dataset
labeled_data_folder = "data_labeled" # folder to store the uploaded dataset
archive_folder = "data_archive"  # folder for archiving the combined dataset before each merge
filename_combined_dataset = "data.csv" # name of the combined dataset

# get the execution date
date = datetime.now().strftime("%Y-%m-%d-%H-%M")

# get the number of files in the folder
num_files = len([name for name in os.listdir(labeled_data_folder) if os.path.isfile(os.path.join(labeled_data_folder, name))])

# add 1 to the number of files
num_files += 1

# create the filename with the name, date, time and number of files
filename_with_date_and_num_files = f"{filename}_{num_files}_{date}.csv"

# if file is uploaded
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file,sep=";")

    # add column "Label"
    df["Label"] = np.nan
    
    # show editable dataframe in app and store the new data in df_update
    df_update = st.experimental_data_editor(df, num_rows='dynamic')
        
    # if the button "Speichern" is pressed
    if st.button("Speichern"):

        # check if column 'Label' contains null values if "yes" print warning else continue
        if df_update['Label'].isnull().any():
            st.warning('Bitte weisen Sie vor der Speicherung jedem Sample ein Label zu.')
        elif ~df_update['Label'].isin(labels_keys).any():
            st.warning('Bitte verwenden Sie nur gültige Labels. (siehe Sidebar)')
        else:        
            # Convert the Label column to integer data type 
            df_update['Label'] = df_update['Label'].astype(int)

            # store the uploaded dataset as csv
            path_new_data = os.path.join(labeled_data_folder, filename_with_date_and_num_files)
            df_update.to_csv(path_new_data, index=False)
            
            # Load the current combined dataset
            old_df = pd.read_csv(filename_combined_dataset, sep=';')

            # make a copy of the current data and save it in the archive folder
            if not os.path.exists(archive_folder):
                os.makedirs(archive_folder)
            
            num_files_in_archive = len([name for name in os.listdir(archive_folder) if os.path.isfile(os.path.join(archive_folder, name))])
            archive_filename = os.path.basename(f"{filename_combined_dataset[:-4]}_{num_files_in_archive+1}_{date}.csv")
            archive_filepath = os.path.join(archive_folder, archive_filename)
            copy2(filename_combined_dataset, archive_filepath)

            # merge the new data to the current dataset
            merged_df = pd.concat([old_df, df_update], ignore_index=True)

            # overwrite the current combined dataset with the merged DataFrame
            merged_df.to_csv(filename_combined_dataset, index=False)

            # print information that dataset is stored
            st.write("CSV-Datei wurde gespeichert.")
    