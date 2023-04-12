import streamlit as st
import pandas as pd
import os
import base64

def update_row_index(offset):
    st.session_state.row_index += offset
    st.experimental_rerun()


def get_radio_index(value):
    if value == "YES":
        return 0
    elif value == "NO":
        return 1
    else:
        return 2


def update_label(column, value):
    if original_index not in st.session_state.labels:
        st.session_state.labels[original_index] = {}
    st.session_state.labels[original_index][column] = value
    save_labels_to_csv(data, st.session_state.labels)



def create_download_link(file_path, filename="labeled_data.csv"):
    with open(file_path, "rb") as f:
        data = f.read()
    b64_data = base64.b64encode(data).decode()
    href = f'<a href="data:file/csv;base64,{b64_data}" download="{filename}" target="_blank">Download labeled CSV file</a>'
    return href

def save_labels_to_csv(data, labels):
    output_file = "labeled_data.csv"
    data_copy = data.copy()

    for index, label_dict in labels.items():
        for column, value in label_dict.items():
            data_copy.loc[index, column] = value

    data_copy.to_csv(output_file, index=False)
    return output_file


# Load the CSV file
def load_csv_file(file):
    df = pd.read_csv(file)
    if "label" not in df.columns:
        df["label"] = None
    return df

# Display a row from the CSV file
def display_row(filtered_data, row_index):
    row = filtered_data.iloc[row_index]
    original_index = row.name

    st.write(f"Index: {original_index}")

    for column in filtered_data.columns:
        st.subheader(column)
        st.write(row[column])

    if original_index in st.session_state.labels:
        st.write("Saved labels:")
        for k, v in st.session_state.labels[original_index].items():
            st.write(f"{k}: {v}")


# Filter the data based on the selected users
@st.cache_data 
def filter_data(data, selected_user_names):
    filtered_data = data[data["labeler"].isin(selected_user_names)]
    return filtered_data

# Create sidebar
sidebar = st.sidebar

# Add file uploader to the sidebar
csv_file = sidebar.file_uploader("Upload a CSV file", type=["csv"])

if csv_file is not None:
    data = load_csv_file(csv_file)
else:
    data = None

# Initialize row_index in session state if not present
if "row_index" not in st.session_state:
    st.session_state.row_index = 0

# Initialize labels in session state if not present
if "labels" not in st.session_state:
    st.session_state.labels = {}

# Display the row in the main area
if data is not None:
    unique_user_names = data["labeler"].unique()
    selected_user_names = sidebar.multiselect("Select user_name(s)", unique_user_names, default=unique_user_names)
    filtered_data = filter_data(data, selected_user_names)
else:
    filtered_data = None

if filtered_data is not None:

    col1, col2, col3 = st.columns(3)

    original_index = filtered_data.iloc[st.session_state.row_index].name

    with col1:
        st.write("QUESTION_CORRECT")
        question_value = st.selectbox(
            "",
            options=["YES", "NO", None],
            index=get_radio_index(st.session_state.labels.get(original_index, {}).get("QUESTION_CORRECT")),
            key=f"question_selectbox_{st.session_state.row_index}",
        )
        update_label("QUESTION_CORRECT", question_value)

    with col2:
        st.write("ORIGINAL_CORRECT")
        original_value = st.selectbox(
            "",
            options=["YES", "NO", None],
            index=get_radio_index(st.session_state.labels.get(original_index, {}).get("ORIGINAL_CORRECT")),
            key=f"original_selectbox_{st.session_state.row_index}",
        )
        update_label("ORIGINAL_CORRECT", original_value)

    with col3:
        st.write("MODEL_CORRECT")
        model_value = st.selectbox(
            "",
            options=["YES", "NO", None],
            index=get_radio_index(st.session_state.labels.get(original_index, {}).get("MODEL_CORRECT")),
            key=f"model_selectbox_{st.session_state.row_index}",
        )
        update_label("MODEL_CORRECT", model_value)



    display_row(filtered_data, st.session_state.row_index)


# Display progress bar in the sidebar
if filtered_data is not None:
    total_rows = len(filtered_data)
    current_index = st.session_state.row_index + 1
    progress_percentage = (current_index / total_rows) * 100

    sidebar.write(f"Reviewed: {current_index}/{total_rows} ({progress_percentage:.2f}%)")
    sidebar.progress(progress_percentage / 100)

# Add NEXT and PREVIOUS buttons to the sidebar for navigation
col1, col2 = sidebar.columns(2)

with col1:
    if st.button("PREVIOUS", key="previous_button"):
        update_row_index(-1)

with col2:
    if st.button("NEXT", key="next_button"):
        update_row_index(1)
            

if data is not None:
    output_file = "labeled_data.csv"
    sidebar.markdown(create_download_link(output_file), unsafe_allow_html=True)
