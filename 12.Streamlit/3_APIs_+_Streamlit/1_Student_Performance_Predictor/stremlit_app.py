import streamlit as st
import requests

# ---------------- Page Config ----------------
st.set_page_config(page_title="AI Student Predictor", layout="wide")

st.title("🎯 AI Student Performance App")
st.markdown("Predict marks using Flask API + ML logic")

st.divider()

# ---------------- Sidebar ----------------
st.sidebar.header("⚙️ Controls")

show_details = st.sidebar.checkbox("Show Raw API Response")

# ---------------- Layout ----------------
col1, col2 = st.columns(2)

# ---------------- INPUT ----------------
with col1:
    st.subheader("📥 Input")

    hours = st.slider("Study Hours", 0, 12, 5)
    sleep = st.slider("Sleep Hours", 0, 12, 6)

    predict_btn = st.button("🚀 Predict")

# ---------------- OUTPUT ----------------
with col2:
    st.subheader("📊 Output")

    if predict_btn:
        try:
            # Call Flask API   # sending post request at url with data
            response = requests.post(  # requests.post(url, json={...})
                "http://127.0.0.1:5000/predict",
                json={
                    "hours": hours,
                    "sleep": sleep
                }
            )

            # Stream lit recieves response
            data = response.json() # Converts JSON → Python dict

            # Handle error
            if response.status_code != 200:
                st.error(data.get("error"))
            else:
                # Display results
                st.success(f"Marks: {data['marks']}")

                st.metric("Grade", data["grade"])
                st.metric("Status", data["status"])

                st.progress(data["marks"])

                if show_details:
                    st.json(data)

        except Exception as e:
            st.error("API not running or connection failed")

# ---------------- Expander ----------------
with st.expander("📘 How this works"):
    st.write("""
    - Flask API handles validation and logic
    - Streamlit sends input as JSON
    - Model calculates marks
    - API returns structured response
    """)