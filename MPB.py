#---PRELIMINARIES---#
import pandas as pd
import json
import requests
import plotly.express as px
import streamlit as st
import plotly.graph_objects as go
from streamlit_lottie import st_lottie

st.set_page_config(page_title="Mandatory MySSS Pension Booster", page_icon=":chart_with_upwards_trend:",layout="wide")

#Allows pandas to scan the excel file containing the data set for all combinations needed for the MPB Dashboard
df = pd.read_excel(
    io= 'MPB_DataSet.xlsx',
    engine= 'openpyxl',
    sheet_name= 'MPB_DataSet',
    skiprows= 1,
    usecols= 'A:J',
    nrows= 18602)

#--------SIDEBAR------------#
st.logo("MANDATORY PENSION BOOSTER CALCULATOR.png")
st.sidebar.header("Please select Starting Age, 2023 MSC, and 2025 MSC")

starting_age = st.sidebar.selectbox(
    "Starting Age:",
    options=df["Age"].unique()
)
MSC_2023 = st.sidebar.selectbox(
    "MSC in 2023:",
    options=df["MSC1"].unique()
)

MSC_2025 = st.sidebar.selectbox(
    "MSC in 2025:",
    options=df["MSC2"].unique()
)


df_selection = df.query(
    "Age == @starting_age & MSC1 == @MSC_2023 & MSC2 == @MSC_2025"
)



#---------MAINPAGE---------#
#st.image("ssspension.png", width=800)
#animation:
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load a Lottie animation
lottie_Investment = load_lottieurl("https://lottie.host/11bb6ee9-4005-4e22-bbb8-caa1f82a19e9/RDv8waetES.json")


colm1, colm2 = st.columns((4, 1))
with colm1:
    st.title(":chart_with_upwards_trend: Mandatory MySSS Pension Booster Dashboard")

with colm2:
    st_lottie(
        lottie_Investment,
        speed = 1,
        reverse = False,
        loop = True,
        quality= "high",
        width=150,
        key="animation"
    )

#Values to be displayed in the mainpage
total_months = int(df_selection["No. Months until Retirement"])
Total_Contri = f"₱ {round(float(df_selection['Total Contri']),2):,.2f}"
Total_Contri1= round(float(df_selection['Total Contri']),2)
potential_income = f"₱ {round(float(df_selection['Potential Income']),2):,.2f}"
potential_income1= round(float(df_selection['Potential Income']),2)
total_fee = f"₱ {round(float(df_selection['Total Management fee']),2):,.2f}"
total_fee1= round(float(df_selection['Total Management fee']),2)
AAV =  f"₱ {round(float(df_selection['TAAV']),2):,.2f}"
AAV1 = round(float(df_selection['TAAV']),2)

#Displays by column:
col1, col2, col3, col4, col5= st.columns(5)
col1.metric("No. of Months Until Retirement", value = total_months, delta= None, delta_color="normal", help=None, label_visibility="visible")
col2.metric("Total Contribution", value = Total_Contri, delta= None, delta_color="normal", help=None, label_visibility="visible")
col3.metric("Potential Income", value = potential_income, delta= None, delta_color="normal", help=None, label_visibility="visible")
col4.metric("Total Management Fee", value = total_fee, delta= None, delta_color="normal", help=None, label_visibility="visible")
col5.metric("Total Accumulated Account Value at Retirement", value = AAV, delta= None, delta_color="normal", help=None, label_visibility="visible")

st.markdown("----")#separator between the values and the graph/charts

#---CALCULATIONS---#
SA = starting_age
RA = 60
max = (RA - SA)*12

Ages = []
for i in range(max):  # Loop from 0 to max (exclusive)
    age = SA + i / 12  # Calculate age for each month (fractional for the first month)
    Ages.append(age)

PC = 0.14  # Initial contribution rate
MSC_limit = 20000  # Replace with the actual value for MSC_limit
MSC1= MSC_2023
MSC2= MSC_2025
MMPB_MSC = []  # List to store MMPB_MSC values for each month (p)
MMPB_Contribution = []  # List to store MMPB_Contribution values for each month (p)
for p in range(1, max + 1):  # Loop from 1 to Max (inclusive)
    if p <= 24:  # Months for 2023-2024
        excess_MSC = MSC1 - MSC_limit
        MMPB_MSC.append(excess_MSC)
        MMPB_Contribution.append(excess_MSC * PC)
    else:  # Months for 2025 onwards
        PC = 0.15  # Update contribution rate
        excess_MSC = MSC2 - MSC_limit
        MMPB_MSC.append(excess_MSC)
        MMPB_Contribution.append(excess_MSC * PC)



ROI=pow(1.06, 1/12) - 1 #return of investment
MF= pow(1.01, 1/12) - 1 #management fee
            

Income = [0] *max# Initialize Income list with zeros (length Max)
AV = [0] *max# Initialize AV list with zeros (length Max)
AVMF = [0] *max# Initialize AVMF list with zeros (length Max)
Fee = [0] *max # Initialize Fee list with zeros (length Max)

for j in range(0, max):  # Loop from 1 to Max (inclusive)
    if j == 0:
        Income[j]=0
        AV[j] = MMPB_Contribution[j] + Income[j]
        Fee[j] = MF * AV[j]
        AVMF[j] = AV[j] - Fee[j]
    else:
        Income[j] = ROI * AVMF[j - 1]
        AV[j] = MMPB_Contribution[j] + AVMF[j - 1] + Income[j]
        Fee[j] = MF * AV[j]
        AVMF[j] = AV[j] - Fee[j]

#----OUTPUT---#
FiveYear_AVMF = []
for i in range(0, max, 12):  # Loop in steps of 60 months (5 years)
    FiveYear_AVMF.append(AVMF[i])
FiveYear_AVMF.append(AVMF[max-1])

FiveYear_Ages = []
for age in range(SA, RA + 1, 1):  # Loop in steps of 5 years (inclusive)
    FiveYear_Ages.append(age)

    
fig_TAAV = px.line(
    x = FiveYear_Ages,
    y = FiveYear_AVMF,
    title ="<b>Growth of Total Accumulated Account Value</b>",
    markers=True
)

fig_TAAV.update_layout(
    
    xaxis=dict(
        title="<b>Age</b>",  # Set x-axis title
        showgrid=True,  # Enable gridlines on the x-axis
        tickmode="linear"
    ),
    title_x=0.4,
    titlefont_size=20,
    yaxis=dict(
        title="<b>Total Accumulated Account Value</b>",
        showgrid = True
    )
)
st.plotly_chart(fig_TAAV)

labels = ['Total Contribution', 'Management Fee', 'Potential Income']
values = [Total_Contri1, total_fee1, potential_income1]



#Monthly Pension
Option=['60-month Option', '120-Month Option', '180-Month Option']
y=[AAV1/60, AAV1/120, AAV1/180]
formatted_y = [f"<b>₱ {value:,.2f}</b>" for value in y]
# Use textposition='auto' for direct text
fig_MP = go.Figure(data=[go.Bar(
            x=Option, 
            y=y,
            text=formatted_y,
            textposition='auto',
            textfont_size=20
)])
fig_MP.update_layout( title="<b>Duration vs. Pension</b>", 
                    title_x=0.5,
                    titlefont_size=20 
)
#st.plotly_chart(fig_MP)

#TC vs PI vs MF
fig_TC = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])
fig_TC.update_layout(showlegend=True, 
                     plot_bgcolor="rgba(0,0,0,0)", 
                     title="<b>Investment Summary</b>", 
                     title_x=0.5,
                     titlefont_size=20,

)
#st.plotly_chart(fig_TC)

left_column, right_column = st.columns(2)
left_column.plotly_chart(fig_MP, use_container_width=True)
right_column.plotly_chart(fig_TC, use_container_width=True)
st.markdown("----")

# ---- HIDE STREAMLIT STYLE ----#
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

