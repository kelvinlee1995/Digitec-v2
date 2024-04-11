import pandas as pd
import streamlit as st
import json
import time
from main import updateZielbestand, getLagerStand, deleateZielbestand, addZielbestand, get_cookies

def load_settings():
    # load settings.json
    with open('settings.json') as f:
        settings = json.load(f)
    return settings

def save_settings(settings):
    # save settings.json
    with open('settings.json', 'w') as f:
        json.dump(settings, f)

def main():

    settings = load_settings()

    st.header("Digitec Galaxus - Filialzielbestand")
    
    # settings
    with st.sidebar:
        with st.expander("Excel data"):
            file = st.text_input("File", settings["filepath"])
            n = st.number_input("Shift", min_value=1, value=2, step=1)
            try:
                file = "data.csv"
                df = pd.read_csv(file, skiprows=n)
            except:
                st.error("Please enter a valid file path.")
                st.stop()

            columns = [col for col in df.columns.to_list() if not col.startswith("Unnamed")]
            product_id_name = st.selectbox("Product ID", columns, index=settings["product_id_name_index"])
            zielbestand_column = st.selectbox("Zielbestand", columns, index=settings["zielbestand_column_index"])
            bemerkungen_column = st.selectbox("Bemerkungen", columns, index=settings["bemerkungen_column_index"])
            bemerkungen_string_deutschweitz = st.text_input("Bemerkungen (Deutschweitz) str", value="Nur in Deutschschweiz")
            bemerkungen_string_franz = st.text_input("Bemerkungen (Franz) str (Startswith)", value="Franz nur in LA")
            start = st.date_input("Start", value=pd.to_datetime(settings["start"]))
            end = st.date_input("End", value=pd.to_datetime(settings["end"]))
            start_str = f"{start.day}.{start.month}.{start.year}"
            end_str = f"{end.day}.{end.month}.{end.year}"

        with st.expander("Strategy"):
            max_transfers_per_run = st.number_input("Max transfers per run", min_value=1, value=settings["max_trans_default_value"], step=1)

        cookies = get_cookies()

        if cookies:
            st.success("Cookies are valid!")
        else:
            st.error("Cookies are not valid. Please run the cookiesGrab.py.")

        button = st.button("Save")
        if button:
            settings["filepath"] = file
            settings["product_id_name_index"] = columns.index(product_id_name)
            settings["zielbestand_column_index"] = columns.index(zielbestand_column)
            settings["bemerkungen_column_index"] = columns.index(bemerkungen_column)
            settings["bemerkungen_string_deutschweitz"] = bemerkungen_string_deutschweitz
            settings["bemerkungen_string_franz"] = bemerkungen_string_franz
            settings["max_trans_default_value"] = max_transfers_per_run
            settings["start"] = f"{start.year}-{start.month}-{start.day}"
            settings["end"] = f"{end.year}-{end.month}-{end.day}"
            save_settings(settings)
            st.success("Settings saved!")

    with st.expander("Data"):
        st.write(df)

    run = st.button("Run")
    if run:
        if not cookies:
            st.error("Cookies are not valid. Please run the cookiesGrab.py.")
            st.stop()

        progress_bar = st.progress(0)

        current_transfer = {}

        max_quantity = 0

        for index, row in df.iterrows():
            progress_bar.progress(max_quantity/max_transfers_per_run)
            product = str(int(row["Product Id"]))
            zielbestand = int(row["Stück pro Filiale"])
            bemerkungen = row['Bemerkungen']

            st.write(product, zielbestand)

            updates = updateZielbestand(cookies, product, start_str, end_str, zielbestand)

            # Create a new "Transfered" column that stores the current date
            df.loc[index, "Transfered"] = True
            df.loc[index, "Date"] = time.strftime("%Y-%m-%d")
            
            st.write(updates)

            if index % 10 == 0 or True:
                st.subheader(f"Ran 10 rows out of {len(df)}, {index}/{len(df)}%")
                st.write(current_transfer)
                df.to_csv("transfered.csv", index=False)

            if max_transfers_per_run >= max_quantity:
                st.balloons()
                st.stop()
            break





            



main()