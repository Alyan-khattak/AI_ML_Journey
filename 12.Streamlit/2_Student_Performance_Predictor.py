import streamlit as st

# ---------------- Page Config ----------------
st.set_page_config(page_title="AI Student Predictor", layout="wide")

# ---------------- Title ----------------
st.title("📊 AI Student Performance Predictor")
st.markdown("Predict marks based on study hours using a simple ML model")

st.divider()

# ---------------- Sidebar ----------------
st.sidebar.header("⚙️ Settings")

model_type = st.sidebar.radio(
    "Select Model",
    ["Simple Linear Model"]
)

show_formula = st.sidebar.checkbox("Show Model Formula")

# ---------------- Model Function ----------------
def predict_marks(hours):
    """
    Simple Linear Model:
    marks = 10 * hours + 20
    """
    return 10 * hours + 20

# ---------------- Main Layout ----------------
col1, col2 = st.columns(2)

# ---------------- Input Section ----------------
with col1:
    st.subheader("📝 Input")

    hours = st.slider("Study Hours", 0, 10, 5)

    if show_formula:
        st.info("Model: marks = 10 × hours + 20")

    predict_btn = st.button("Predict Marks")

# ---------------- Output Section ----------------
with col2:
    st.subheader("📈 Output")

    if predict_btn:
        marks = predict_marks(hours)

        # Clamp max marks to 100
        marks = min(marks, 100)

        # Grade logic
        if marks >= 85:
            grade = "A"
        elif marks >= 70:
            grade = "B"
        elif marks >= 50:
            grade = "C"
        else:
            grade = "F"

        status = "Pass" if marks >= 50 else "Fail"

        # Display results
        st.success(f"Predicted Marks: {marks}")

        st.metric("Grade", grade)
        st.metric("Status", status)

        # Progress bar
        st.progress(int(marks))

# ---------------- Expander ----------------
with st.expander("📘 How this model works"):
    st.write("""
    This app uses a simple Linear Regression concept:

    marks = 10 × hours + 20

    - More study hours → higher marks
    - This is a simplified ML model
    - Real models learn from data
    """)

# ---------------- Footer ----------------
st.divider()
st.caption("Built with Streamlit 🚀")