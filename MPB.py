import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Mandatory Pension Booster", page_icon=":bar_chart:",layout="wide")


df = pd.read_excel(
    io= 'MPB_DataSet.xlsx',
    engine= 'openpyxl',
    sheet_name= 'MPB_DataSet',
    skiprows= 1,
    usecols= 'A:I',
    nrows= 18602)
    

st.dataframe(df)

#--------SIDEBAR------------#

st.sidebar.header("Please select Starting Age, 2023 MSC, and 2025 MSC")

starting_age = st.sidebar.selectbox(
    "Select Starting Age:",
    options=df["Age"].unique()
)

MSC_2023 = st.sidebar.selectbox(
    "Select MSC in 2023:",
    options=df["MSC1"].unique()
)

MSC_2025 = st.sidebar.selectbox(
    "Select MSC in 2025:",
    options=df["MSC2"].unique()
)


df_selection = df.query(
    "Age == @starting_age & MSC1 == @MSC_2023 & MSC2 == @MSC_2025"
)



#---------MAINPAGE---------#
st.title(":bar_chart: Mandatory Pension Dashboard")
st.markdown("##")

#TOP KPI's
start_age = int(df_selection["Age"])
total_months = int(df_selection["No. Months until Retirement"])
Contri_2023 = int(df_selection["Contri 1"])
Contri_2025 = int(df_selection["Contri 2"])
potential_income = int(df_selection["Potential Income"])
total_fee = int(df_selection["Total Management fee"])
TAAV =  int(df_selection["TAAV"])

column1, column2, column3, column4, column5, column6, column7= st.columns(7)
with column1:
    st.subheader("Starting Age")
    st.subheader(f"{start_age}")
with column2:
    st.subheader("Number of Months until Retirement")
    st.subheader(f"{total_months}")
with column3:
    st.subheader("Contribution from 2023 to 2024")
    st.subheader(f"₱ {Contri_2023:,.2f}")
with column4:
    st.subheader("Contribution from 2025")
    st.subheader(f"₱ {Contri_2025:,.2f}")
with column5:
    st.subheader("Potential Income")
    st.subheader(f"₱ {potential_income:,.2f}")
with column6:
    st.subheader("Total Management Fee")
    st.subheader(f"₱ {total_fee:,.2f}")
with column7:
    st.subheader("Total Accumulated Account Value at Retirement")
    st.subheader(f"₱ {TAAV:,.2f}")
st.markdown("----")

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
WISP_MSC = []  # List to store WISP_MSC values for each month (p)
WISP_Contribution = []  # List to store WISP_Contribution values for each month (p)
for p in range(1, max + 1):  # Loop from 1 to Max (inclusive)
    if p <= 24:  # Months for 2023-2024
        excess_MSC = MSC1 - MSC_limit
        WISP_MSC.append(excess_MSC)
        WISP_Contribution.append(excess_MSC * PC)
    else:  # Months for 2025 onwards
        PC = 0.15  # Update contribution rate
        excess_MSC = MSC2 - MSC_limit
        WISP_MSC.append(excess_MSC)
        WISP_Contribution.append(excess_MSC * PC)


# Loop 4: Calculate Income, Account Value, and Fees

ROI=pow(1.06, 1/12) - 1 #return of investment
MF= pow(1.01, 1/12) - 1 #management fee
            

Income = [0] *max# Initialize Income list with zeros (length Max + 1)
AV = [0] *max# Initialize AV list with zeros (length Max + 1)
AVMF = [0] *max# Initialize AVMF list with zeros (length Max + 1)
Fee = [0] *max # Initialize Fee list with zeros (length Max + 1)

for j in range(0, max):  # Loop from 1 to Max (inclusive)
    if j == 0:
        Income[j]=0
        AV[j] = WISP_Contribution[j] + Income[j]
        Fee[j] = MF * AV[j]
        AVMF[j] = AV[j] - Fee[j]
    else:
        Income[j] = ROI * AVMF[j - 1]
        AV[j] = WISP_Contribution[j] + AVMF[j - 1] + Income[j]
        Fee[j] = MF * AV[j]
        AVMF[j] = AV[j] - Fee[j]

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
    template = "plotly_white"

)
fig_TAAV.update_layout(
    xaxis=dict(
        title="Ages",  # Set x-axis title
        showgrid=True,  # Enable gridlines on the x-axis
        tickmode="linear"
    ),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(
        title="Total Accumulated Account Value",
        showgrid = True
    )
)
st.plotly_chart(fig_TAAV)

# ---- HIDE STREAMLIT STYLE ----
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
