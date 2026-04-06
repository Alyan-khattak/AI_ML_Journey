"""
Streamlit = Python library to build web apps (UI) using only Python

No HTML ❌
No CSS ❌
No JavaScript ❌

You just write Python → it becomes a web app

"""

import streamlit as st
import pandas as pd

st.title("Stream lit App")

st.write("This is me Learning Streamlit")
st.write(" st.write() Prints anything")
st.text(" st.text() prints only text")

## Inputs

name = st.text_input("Enter ur Name")
if name:
    st.write(f" Hello {name}")

age = st.number_input(" Enter ur age : ")
if age: 
    st.write(f" You are {age} years old")

Dob = st.date_input("Enter ur Date of Birth")
if Dob:
    st.write(f"U were Born in {Dob}")

marks = st.number_input("Enter ur Marks: ", min_value=0, max_value=100)

if st.button("check result"):
    if marks >= 85:
        grade = "A"
    elif marks >= 70:
        grade = "B"
    elif marks >= 50:
        grade = "C"
    else:
        grade = "F"

    status = "Pass" if marks >= 50 else "Fail"

    st.write(f"{name} got {marks} : {status}")

#===============================
### BUtton: st.button(label)
# ==================================

if st.button("CLick me"):
    st.write("Button clicked")

#===============================
### Radio BUtton: choice = st.radio("Label", options in list,  horizontal = True) : ( horizontal to show option horizontally)
# ==================================

radio1 = st.radio("Choose", ["A", "B", "c"])
st.write(radio1)

radio2 = st.radio("choose", ["Aroosa", "Alyan", "Sana"])
st.write(radio2)

radio3 = st.radio("Pick ", ["Yes", "No"], horizontal=True)
st.write(radio3)


#===============================
### Select Box : st.selectbox("Label", options in list)
# ==================================

options = st.selectbox("Choose", ["A", "B", "C"])
options2 = st.selectbox("Chooose", ["Nihha", "Nilla", "Nijja","Ninja"])



#===============================
### Check Box : chk Box = st.checkbox(Label) 
# ==================================

check = st.checkbox("Show Text")

a = st.checkbox("Python")
b = st.checkbox("AI")

st.write(a, b)


#===============================
### Slider : value = st.slider("Label", min, max, default_value)
# ==================================

value = st.slider("AGe", 2,100,5)
st.write(value)

temp = st.slider("Temperature : ", 0.0, 100.0, 25.00)
st.write(f"Current Temp: ", temp)



#===============================
### File Uploader : value = st.file_uploader("upload File")
# ==================================

file= st.file_uploader("upload")
if file:
    st.write(file.name)

csv = st.file_uploader("Upload Csv")
if csv:
    df = pd.read_csv(file)
    st.dataframe(df)



#===============================
### Side Bar : st.sidebar.<component>()
# ==================================

name = st.sidebar.text_input("Enter name")
age = st.sidebar.slider("Age", 0, 100)
opt = st.sidebar.radio("Selct Mode", ["easy", "Hard" ])
if st.sidebar.button("Button"):
    st.sidebar.write("clicked")




#===============================
### Expander: with st.expander("Title"):
#                  st.write("Content")
# ==================================


with st.expander("Lists"):
    st.write("this is one")
    st.write("thi sd")
    st.write("fdf")
    st.write("Noor")





#===============================
###  Coloums: col1, col2 = st.columns(2) : each column is like a sepraete page 
# ==================================

col1, col2 = st.columns(2)

with col1:

    st.write("Col 1")
    radio5 = st.radio("Gender", ["Female", "Male"])
    radio6 = st.radio("Choce", ["a", "b", "c"])

    s1 = st.selectbox("Ms", ["d","d","df"])
    val = st.slider("iop",2,90,2)


with col2:
    st.write("col 2")
    st.dataframe( pd.DataFrame(
        {
            "Age": [2,34,5],
            "Make": [3,54,76]
        }
    ))