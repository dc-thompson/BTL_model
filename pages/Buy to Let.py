import streamlit as st
import numpy as np
import numpy_financial as npf
import matplotlib.pyplot as plt
import json
from numpy.linalg import LinAlgError
import pandas as pd
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Load Lottie animation
def load_lottie(source):
    if source.startswith('http'):
        # If the source is a URL
        r = requests.get(source)
        if r.status_code != 200:
            return None
        return r.json()
    else:
        # If the source is a local file path
        with open(source, 'r') as f:
            return json.load(f)

lottie_house = load_lottie("1725915498155.json")

# Setup page
st.set_page_config(
    page_title="Buy to Let Model",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f0f2f6;
    }
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stAlert {
        background-color: #e8f4f8;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3498db;
    }
    .stTabs {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .bold-text, .bold-text span {
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.title('🏠 Buy to Let Model')
    st.markdown("""
    Welcome to our advanced Buy-to-Let property financial modelling tool. 
    This app is designed to help you make informed decisions about property investments, 
    whether you're considering purchasing as an individual or through a limited company.
    """)

with col2:
    if lottie_house is not None:
        st_lottie(lottie_house, speed=1, height=200, key="house_animation")
    else:
        st.warning("Failed to load house animation.")

# Sidebar
with st.sidebar:
    st.subheader("Model Parameters")
    tax_treatment = st.radio("Tax Treatment", ["Limited company", "Personal"])

    tabs = st.tabs(["🏡 House", "💰 Income", "💸 Costs", "🏦 Mortgage", "📈 Growth"])
    
    with tabs[0]:
        houseprice = st.number_input('House price (£)', value=100000, step=10000)
        deposit = st.number_input('Deposit (£)', value=10000, step=1000)
        postcode = st.text_input('Postcode')
    
    with tabs[1]:
        rent = st.number_input('Expected rental income (PCM) (£)')
        if tax_treatment == "Limited company":
            incometax = st.number_input('Rate of Corporation tax (%)', value=19)
        else:
            incometax = st.selectbox("Income Tax Band", ("Personal Allowance (0%)", "Basic (20%)", "Higher (40%)", "Additional (45%)"))
            incometax = {"Personal Allowance (0%)": 0, "Basic (20%)": 0.2, "Higher (40%)": 0.4, "Additional (45%)": 0.45}[incometax]
    
    with tabs[2]:
        service_charge = st.number_input('Service Charge (£)')
        management_charge_percent = st.number_input('Management Charge (%)')
        maintenance_cost = st.number_input('Maintenance Costs (£)')
        landlord_insurance = st.number_input('Landlord Insurance (£)')
        building_insurance = st.number_input('Buildings Insurance (£)')
        accountancy_cost = st.number_input('Accountancy Fees (£)')
    
    with tabs[3]:
        interest_rate = st.number_input("Interest Rate (%)")
        length_of_mortgage = st.number_input("Length of Mortgage (years)")
    
    with tabs[4]:
        annual_capital_growth = st.number_input("Predicted Annual Capital Growth (%)")

# Function Definitions
def get_mortgage_details():
    mort_req = houseprice - deposit
    interest_rate_monthly = (interest_rate / 100) / 12
    length_of_mortgage_monthly = length_of_mortgage * 12
    mortgage_principle_sum = npf.ppmt(interest_rate_monthly, 1, length_of_mortgage_monthly, mort_req)
    mortgage_interest = npf.ipmt(interest_rate_monthly, 1, length_of_mortgage_monthly, mort_req)
    total_monthly_repay = npf.pmt(interest_rate_monthly, length_of_mortgage_monthly, mort_req)
    return abs(mortgage_principle_sum), abs(mortgage_interest), abs(total_monthly_repay)

def ltv(deposit, houseprice):
    return (houseprice - deposit)/houseprice

def stamp_duty(houseprice):
    if houseprice <= 250000:
        return 0
    elif 250000 < houseprice <= 925000:
        return (houseprice - 250000) * 0.05
    elif 925000 < houseprice <= 1500000:
        return (houseprice - 925000) * 0.1 + 33750
    else:
        return (houseprice - 1500000) * 0.12 + 91250
    
def stamp_duty_additional(houseprice):
        if houseprice <= 250000:
            return houseprice * 0.03
        elif 250000 < houseprice <= 925000:
            return (houseprice - 250000) * 0.08 + 7500
        elif 925000 < houseprice <= 1500000:
            return (houseprice - 925000) * 0.13 + 61500
        else:
            return (houseprice - 1500000) * 0.15 + 136250

def total_costs(rent_val):
    return service_charge + (rent_val * (management_charge_percent / 100)) + maintenance_cost + landlord_insurance + building_insurance + accountancy_cost

def tax_credit(interest):
    tax_credit_sum = float(interest * 0.2)
    return tax_credit_sum

def EBIT(rent_val):
    if tax_treatment == "Personal":
        return rent_val - total_costs(rent_val)
    elif tax_treatment == "Limited company":
        return rent_val - (total_costs(rent_val) + mort_interest)

def NOPAT(rent_val, interest):
    if tax_treatment == "Personal":
        return (EBIT(rent_val) - (EBIT(rent_val) * (incometax))) + tax_credit(interest)
    elif tax_treatment == "Limited company":
        return (EBIT(rent_val) - (EBIT(rent_val) * (incometax/100)))

def net_inc(rent_val, interest, mortgage_repay):
    if tax_treatment == "Personal":
        return NOPAT(rent_val, interest) - mortgage_repay
    elif tax_treatment == "Limited company":
        return NOPAT(rent_val, interest) - mort_principle

def culm_growth_func(years):
    capital_growth_float = (annual_capital_growth / 100)
    return (houseprice * (pow(1 + capital_growth_float, years))) - houseprice

def save():
    calculations = {'deposit': deposit, 'houseprice': houseprice}
    json_object = json.dumps(calculations, indent=4)
    with open("calculations.json", "w") as outfile:
        outfile.write(json_object)
    st.download_button(
        label="Download JSON",
        data=json_object,
        file_name='calculations.json',
        mime='application/json'
    )
    st.write(calculations)


# Main Calculations and Display
st.header("Mortgage Details")
if houseprice > 0 and deposit > 0 and interest_rate > 0 and length_of_mortgage > 0:
    mort_principle, mort_interest, mort_repay = get_mortgage_details()
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Mortgage Required", f"£{houseprice - deposit:,.0f}")
    col2.metric("Loan to Value", f"{ltv(deposit,houseprice):.2%}")
    col3.metric("Total Monthly Repayment", f"£{mort_repay:,.2f}")
    
    st.info(f"""
    📊 Monthly Breakdown:
    - Interest Repayment: £{mort_interest:,.2f}
    - Capital Repayment: £{mort_principle:,.2f}
    """)
else:
    st.warning("Please enter all mortgage details to calculate repayments.")

# Net Income Graph
st.header("Net Income Analysis")
if rent > 0 and houseprice > 0:
    try:
        x = np.linspace(rent * 0.5, rent * 1.5, 100)
        y = [net_inc(i, mort_interest, mort_repay) for i in x]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Net Income'))
        fig.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Cost Neutral")
        
        fig.update_layout(
            title='Net Monthly Income vs Rent',
            xaxis_title='Monthly Rent (£)',
            yaxis_title='Net Monthly Income (£)',
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        model = np.polyfit(x, y, 1)
        x_intercept = -model[1] / model[0]
        st.success(f"📌 Rent required for cost-neutrality after tax: £{x_intercept:,.2f}")
        
    except Exception as e:
        st.error(f"An error occurred when generating the net income graph: {e}")
else:
    st.warning("Please enter a valid rent and house price to generate the net income graph.")

# Capital Growth Visualization
st.header("Capital Growth Projection")
years = st.slider("Select the number of years for capital growth visualization:", 1, 30, 10)

if years > 0 and houseprice > 0:
    x_years = np.arange(1, years + 1)
    y_growth = np.array([culm_growth_func(year) for year in x_years])
    y_valuation = houseprice + y_growth

    fig_growth = go.Figure()
    fig_growth.add_trace(go.Scatter(x=x_years, y=y_valuation, mode='lines+markers', name='Capital Valuation'))
    fig_growth.update_layout(
        title='Capital Growth Over Time',
        xaxis_title='Years',
        yaxis_title='Capital Valuation (£)',
        hovermode='x unified',
        xaxis=dict(tickmode='linear', dtick=1)
    )
    st.plotly_chart(fig_growth, use_container_width=True)

    data = {
        "Year": range(1, years + 1),
        "Capital Valuation": ["£{:,.0f}".format(houseprice + culm_growth_func(i)) for i in range(1, years + 1)]
    }
    culm_growth_func_table = pd.DataFrame(data)
    st.table(culm_growth_func_table)

# Capital Requirements
st.header("Capital Requirements")

if tax_treatment == "Limited company":
    stamp_duty_val = stamp_duty_additional(houseprice)
else:
    property_type = st.radio("Property Type:", ["Main Residence", "Additional Property"])
    if property_type == "Main Residence":
        stamp_duty_val = stamp_duty(houseprice)
    else:
        stamp_duty_val = stamp_duty_additional(houseprice)

total = deposit + stamp_duty_val
capital_requirements = pd.DataFrame({
    "Capital": ["Deposit", "Stamp Duty", "Total"],
    "Amount": [deposit, stamp_duty_val, total]
})

# Format the 'Amount' column as currency
capital_requirements['Amount'] = capital_requirements['Amount'].apply(lambda x: f"£{x:,.0f}")

# Create a styled DataFrame
styled_df = capital_requirements.style.set_properties(**{'font-weight': 'bold'}, subset=pd.IndexSlice[2, :])
styled_df = styled_df.set_properties(**{'text-align': 'left'}, subset=['Capital'])
styled_df = styled_df.set_properties(**{'text-align': 'right'}, subset=['Amount'])
styled_df = styled_df.hide(axis="index")

# Display the styled table
st.write(styled_df.to_html(), unsafe_allow_html=True)

# Add a summary of the capital requirements
st.info(f"""
💰 Capital Requirements Summary:
- Total capital required: {capital_requirements.loc[2, 'Amount']}
- This includes a deposit of {capital_requirements.loc[0, 'Amount']} and stamp duty of {capital_requirements.loc[1, 'Amount']}
""")

# Save functionality
if st.button("Save Calculations"):
    calculations = {'deposit': deposit, 'houseprice': houseprice}
    json_object = json.dumps(calculations, indent=4)
    st.download_button(
        label="Download JSON",
        data=json_object,
        file_name='calculations.json',
        mime='application/json'
    )
    st.write(calculations)




