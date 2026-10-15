import os
import pandas as pd
import requests
import streamlit as st

st.set_page_config(
    page_title="California House Valuation",
    page_icon="🏡",
    layout="wide",
)

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

# Preset profiles for quick testing
PRESETS = {
    "Custom Input": None,
    "San Francisco Bay Area (High-End)": {
        "MedInc": 9.5,
        "HouseAge": 32.0,
        "AveRooms": 6.8,
        "AveBedrms": 1.05,
        "Population": 1100.0,
        "AveOccup": 2.6,
        "Latitude": 37.77,
        "Longitude": -122.42,
    },
    "Los Angeles Suburban": {
        "MedInc": 5.2,
        "HouseAge": 24.0,
        "AveRooms": 5.9,
        "AveBedrms": 1.1,
        "Population": 1450.0,
        "AveOccup": 3.1,
        "Latitude": 34.05,
        "Longitude": -118.25,
    },
    "San Diego Coastal": {
        "MedInc": 6.4,
        "HouseAge": 19.0,
        "AveRooms": 6.1,
        "AveBedrms": 1.08,
        "Population": 1250.0,
        "AveOccup": 2.8,
        "Latitude": 32.72,
        "Longitude": -117.16,
    },
    "Central Valley (Affordable)": {
        "MedInc": 2.8,
        "HouseAge": 28.0,
        "AveRooms": 5.1,
        "AveBedrms": 1.06,
        "Population": 1800.0,
        "AveOccup": 3.4,
        "Latitude": 36.74,
        "Longitude": -119.78,
    },
}


def check_backend_health() -> bool:
    try:
        resp = requests.get(f"{API_URL}/health", timeout=3)
        return resp.ok
    except requests.RequestException:
        return False


# Header & Status
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🏡 California Housing Price Predictor")
    st.caption("Machine Learning powered real-estate appraisal service trained on California census data.")

with col_h2:
    is_healthy = check_backend_health()
    if is_healthy:
        st.success("🟢 API Connected", icon="✅")
    else:
        st.error("🔴 API Offline", icon="⚠️")
        st.caption(f"Run backend at `{API_URL}`: `python -m uvicorn app.main:app --reload`")

tab_predict, tab_history, tab_docs = st.tabs(["📊 Value Predictor", "📜 Prediction History", "ℹ️ Dataset Info"])

with tab_predict:
    st.subheader("Property Characteristics & Location")

    selected_preset = st.selectbox(
        "Choose a Preset Profile (or select Custom Input):",
        options=list(PRESETS.keys()),
        index=0,
    )
    preset_data = PRESETS[selected_preset]

    with st.form("house_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("##### 📈 Socio-Economic & Property Attributes")
            med_inc = st.number_input(
                "Median Income ($10k blocks)",
                min_value=0.5,
                max_value=30.0,
                value=float(preset_data["MedInc"]) if preset_data else 5.0,
                step=0.1,
                help="Median income in block group (e.g., 5.0 = $50,000/year).",
            )
            house_age = st.number_input(
                "Median House Age (years)",
                min_value=1.0,
                max_value=100.0,
                value=float(preset_data["HouseAge"]) if preset_data else 20.0,
                step=1.0,
                help="Median age of houses in the block group.",
            )
            ave_rooms = st.number_input(
                "Average Rooms per Household",
                min_value=1.0,
                max_value=30.0,
                value=float(preset_data["AveRooms"]) if preset_data else 6.0,
                step=0.1,
            )
            ave_bedrms = st.number_input(
                "Average Bedrooms per Household",
                min_value=0.2,
                max_value=10.0,
                value=float(preset_data["AveBedrms"]) if preset_data else 1.0,
                step=0.05,
            )

        with col2:
            st.markdown("##### 📍 Block Population & Geographic Coordinates")
            population = st.number_input(
                "Block Population",
                min_value=10.0,
                max_value=40000.0,
                value=float(preset_data["Population"]) if preset_data else 1000.0,
                step=50.0,
            )
            ave_occup = st.number_input(
                "Average Occupancy (household size)",
                min_value=0.5,
                max_value=15.0,
                value=float(preset_data["AveOccup"]) if preset_data else 3.0,
                step=0.1,
            )
            latitude = st.number_input(
                "Latitude (California ~32.5° to 42.0°)",
                min_value=32.0,
                max_value=43.0,
                value=float(preset_data["Latitude"]) if preset_data else 34.05,
                step=0.01,
            )
            longitude = st.number_input(
                "Longitude (California ~-124.5° to -114.0°)",
                min_value=-125.0,
                max_value=-114.0,
                value=float(preset_data["Longitude"]) if preset_data else -118.25,
                step=0.01,
            )

        # Interactive Map showing coordinates
        st.markdown("##### 🗺️ Location Preview")
        map_df = pd.DataFrame([{"latitude": latitude, "longitude": longitude}])
        st.map(map_df, zoom=6)

        submitted = st.form_submit_button("💰 Estimate Property Value", use_container_width=True)

    if submitted:
        payload = {
            "MedInc": float(med_inc),
            "HouseAge": float(house_age),
            "AveRooms": float(ave_rooms),
            "AveBedrms": float(ave_bedrms),
            "Population": float(population),
            "AveOccup": float(ave_occup),
            "Latitude": float(latitude),
            "Longitude": float(longitude),
        }

        with st.spinner("Appraising property via ML inference engine..."):
            try:
                res = requests.post(f"{API_URL}/predict/", json=payload, timeout=15)
                if res.ok:
                    data = res.json()
                    st.success("Appraisal completed and logged to database!")

                    res_col1, res_col2, res_col3 = st.columns(3)
                    with res_col1:
                        st.metric("Estimated Price (USD)", f"${data['estimated_price_usd']:,.2f}")
                    with res_col2:
                        st.metric("Model Index ($100k Units)", f"{data['predicted_value']:.3f}")
                    with res_col3:
                        st.metric("Audit ID", f"#{data.get('prediction_id', 'N/A')}")
                else:
                    st.error(f"Prediction failed ({res.status_code}): {res.text}")
            except requests.RequestException as exc:
                st.error(f"Could not connect to API at {API_URL}: {exc}")

with tab_history:
    st.subheader("Historical Prediction Audits")
    c1, c2 = st.columns([1, 4])
    with c1:
        if st.button("🔄 Refresh History", use_container_width=True):
            st.rerun()

    try:
        h_resp = requests.get(f"{API_URL}/predict/history?limit=100", timeout=10)
        if h_resp.ok:
            h_data = h_resp.json()
            items = h_data.get("items", [])
            total = h_data.get("total", 0)

            if items:
                df_history = pd.DataFrame(items)
                # Format price column
                df_history["formatted_price"] = df_history["estimated_price_usd"].apply(
                    lambda x: f"${x:,.2f}"
                )

                metric_c1, metric_c2, metric_c3 = st.columns(3)
                metric_c1.metric("Total Predictions Saved", total)
                metric_c2.metric("Average Price", f"${df_history['estimated_price_usd'].mean():,.2f}")
                metric_c3.metric(
                    "Latest Appraisal",
                    f"${df_history.iloc[0]['estimated_price_usd']:,.2f}" if len(df_history) else "N/A",
                )

                display_cols = [
                    "id",
                    "created_at",
                    "formatted_price",
                    "predicted_value",
                    "MedInc",
                    "HouseAge",
                    "AveRooms",
                    "Population",
                    "Latitude",
                    "Longitude",
                ]
                available_cols = [c for c in display_cols if c in df_history.columns]
                st.dataframe(df_history[available_cols], use_container_width=True)

                csv = df_history.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "📥 Export History to CSV",
                    data=csv,
                    file_name="california_house_predictions.csv",
                    mime="text/csv",
                )
            else:
                st.info("No predictions recorded yet. Run a prediction from the first tab!")
        else:
            st.warning(f"Could not retrieve history: {h_resp.status_code}")
    except requests.RequestException as exc:
        st.warning(f"Backend unreachable to fetch history: {exc}")

with tab_docs:
    st.subheader("About the California Housing Model")
    st.markdown(
        """
        This appraisal model uses demographic and geographic features from the **California Housing Dataset** 
        (derived from the 1990 U.S. Census).

        - **MedInc**: Median income in block group (in tens of thousands of USD).
        - **HouseAge**: Median house age in block group.
        - **AveRooms**: Average number of rooms per household.
        - **AveBedrms**: Average number of bedrooms per household.
        - **Population**: Total population living in the block group.
        - **AveOccup**: Average number of household members.
        - **Latitude & Longitude**: Exact geographical coordinates.

        #### API Documentation
        - Interactive Swagger Docs: [`/docs`](http://127.0.0.1:8000/docs)
        - OpenAPI Schema: [`/openapi.json`](http://127.0.0.1:8000/openapi.json)
        """
    )
