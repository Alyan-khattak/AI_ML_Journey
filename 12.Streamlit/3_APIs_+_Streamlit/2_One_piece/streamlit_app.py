import streamlit as st
import requests

API_URL = "http://127.0.0.1:5000"

st.set_page_config(page_title="One Piece App", layout="wide")

st.title("🏴‍☠️ One Piece Character Manager")

# ---------------- Sidebar ----------------
page = st.sidebar.selectbox("Navigate", ["Create", "View All"])

# ---------------- CREATE ----------------
if page == "Create":

    st.subheader("Create Character")

    name = st.text_input("Name")
    power = st.slider("Power", 0, 100)
    crew = st.selectbox("Crew", ["Straw Hat", "Navy", "Revolutionary", "Pirate"])
    role = st.selectbox("Role", ["Captain", "Swordsman", "Sniper", "Cook", "Doctor"])
    bounty = st.number_input("Bounty", 0)

    if st.button("Create"):

        res = requests.post(
            f"{API_URL}/characters",
            json={
                "name": name,
                "power": power,
                "crew": crew,
                "role": role,
                "bounty": bounty
            }
        )

        data = res.json()

        if res.status_code != 201:
            st.error(data["error"])
        else:
            st.success(f"{data['name']} created!")
            st.json(data)


# ---------------- VIEW ----------------
elif page == "View All":

    st.subheader("All Characters")

    res = requests.get(f"{API_URL}/characters")

    data = res.json()

    if data:   # data is list of dicts [ {} , {} ] so char = data[0], data[1] mean dict 0 and dict 1 
        for char in data:
            with st.expander(f"{char['name']} ({char['rank']})"):
                st.write(f"Crew: {char['crew']}")
                st.write(f"Role: {char['role']}")
                st.write(f"Power: {char['power']}")
                st.write(f"Bounty: {char['bounty']}")

                if st.button(f"Delete {char['id']}"):
                    requests.delete(f"{API_URL}/characters/{char['id']}")
                    st.rerun()
    else:
        st.info("No characters yet")