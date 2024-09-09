import streamlit as st
import numpy_financial as npf
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_lottie import st_lottie
import requests
import json

# Helper functions
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


def convert_cost_to_annual(cost, period):
    return cost * 12 if period == 'Monthly' else cost

def ltv(deposit, houseprice):
    return (houseprice - deposit)/houseprice


# Set up the page
st.set_page_config(page_title="BTL Tax Comparison", layout="wide", page_icon="🏠")

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
    
    /* New CSS for sidebar */
    [data-testid="stSidebar"] {
        min-height: 100vh;
    }
    [data-testid="stSidebar"] > div:first-child {
        height: 100vh;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# Load the Lottie animation
lottie_house = load_lottie("/Users/dan/Documents/Coding/BTL_model/Streamlit/1725915498155.json")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.title('🏠 Buy to Let Tax Treatment Comparison')
    st.markdown("""
    This tool helps you compare the tax implications of owning a buy-to-let property 
    as an individual versus through a limited company. Enter your property details 
    and see the financial breakdown for both scenarios.
    """)

with col2:
    if lottie_house is not None:
        st_lottie(lottie_house, speed=1, height=200, key="house_animation")
    else:
        st.warning("Failed to load house animation.")

# Property Details
st.header("📊 Property Details")
col1, col2, col3 = st.columns(3)
with col1:
    current_market_value = st.number_input(
        "Current Market Value (£)", 
        value=250000, 
        step=1000, 
        key='market_value',
        help="The estimated value of the property if sold today."
    )
with col2:
    purchase_price = st.number_input(
        "Original Purchase Price (£)", 
        value=200000, 
        step=1000, 
        key='purchase_price',
        help="The price at which the property was initially bought."
    )
with col3:
    mort_remaining = st.number_input(
        'Mortgage amount remaining (£)', 
        value=50000, 
        step=5000,
        help="The outstanding balance on the mortgage."
    )

rent = st.number_input(
    'Expected Rental Income (PCM £)', 
    value=1000, 
    step=100,
    help="The monthly rent you expect to receive from tenants."
)

# General Costs
st.header("💰 General Costs")
col1, col2 = st.columns(2)
with col1:
    management_charge_percent = st.number_input(
        "Management Charge (%)", 
        value=10, 
        step=1,
        help="The percentage fee charged by a property management company."
    )
    maintenance_cost = st.number_input(
        "Maintenance Costs", 
        value=100, 
        step=10,
        help="Estimated costs for repairs and upkeep of the property."
    )
    maintenance_period = st.selectbox(
        "Maintenance Cost Period", 
        ['Monthly', 'Annually'], 
        key='maintenance_period'
    )
    maintenance_cost_annual = convert_cost_to_annual(maintenance_cost, maintenance_period)
    
    landlord_insurance = st.number_input(
        "Landlord Insurance", 
        value=150, 
        step=10,
        help="Insurance that covers risks associated with renting out property."
    )
    landlord_insurance_period = st.selectbox(
        "Landlord Insurance Period", 
        ['Monthly', 'Annually'], 
        key='landlord_insurance_period'
    )
    landlord_insurance_annual = convert_cost_to_annual(landlord_insurance, landlord_insurance_period)

with col2:
    building_insurance = st.number_input(
        "Building Insurance", 
        value=200, 
        step=10,
        help="Insurance that covers the structure of the property."
    )
    building_insurance_period = st.selectbox(
        "Building Insurance Period", 
        ['Monthly', 'Annually'], 
        key='building_insurance_period'
    )
    building_insurance_annual = convert_cost_to_annual(building_insurance, building_insurance_period)
    
    service_charge = st.number_input(
        "Service Charge", 
        value=100, 
        step=10,
        help="Fees for maintenance of common areas in leasehold properties."
    )
    service_charge_period = st.selectbox(
        "Service Charge Period", 
        ['Monthly', 'Annually'], 
        key='service_charge_period'
    )
    service_charge_annual = convert_cost_to_annual(service_charge, service_charge_period)

# Display annual costs for verification
st.info(f"""
Annual Costs Summary:
- Maintenance: £{maintenance_cost_annual:,.2f}
- Landlord Insurance: £{landlord_insurance_annual:,.2f}
- Building Insurance: £{building_insurance_annual:,.2f}
- Service Charge: £{service_charge_annual:,.2f}
""")

# Personal vs Limited Company Comparison
st.header("🔍 Personal vs Limited Company Comparison")
col1, col2 = st.columns(2)

with col1:
    st.subheader("👤 Personal")
    accountancy_cost_per = st.number_input(
        "Accountancy Fees",
        value=30, 
        step=10,
        help="Costs for managing personal tax returns related to the property."
    )
    accountancy_period_per = st.selectbox(
        "Accountancy Fees Period", 
        ['Monthly', 'Annually'], 
        key='personal_accountancy_period'
    )
    accountancy_cost_annual_per = convert_cost_to_annual(accountancy_cost_per, accountancy_period_per)

    st.markdown("---")
    st.subheader("Mortgage Details")
    interest_rate_per = st.number_input(
        "Interest Rate (%)", 
        value=3.5, 
        step=0.1, 
        key='personal_interest_rate',
        help="The annual interest rate on the mortgage."
    )
    length_of_mortgage_per = st.number_input(
        "Length of Mortgage (Years)", 
        value=25, 
        step=1, 
        key='personal_length_of_mortgage',
        help="The total duration of the mortgage."
    )
    mort_arrangement_fee_personal = st.number_input(
    "Mortgage arrangement fee (£)", 
    value=1000, 
    step=100, 
    key='mort_arrangement_fee_personal',
    help="Fee charged by the lender for setting up the new mortgage."
)

    st.markdown("---")
    st.subheader("Personal Tax Details")
    incometax = st.selectbox(
        "Income Tax Band",
        ("Personal Allowance (0%)", "Basic (20%)", "Higher (40%)", "Additional (45%)"),
        help="The tax band based on your total income, including from other sources."
    )
    incometax = {"Personal Allowance (0%)": 0, "Basic (20%)": 0.2, "Higher (40%)": 0.4, "Additional (45%)": 0.45}[incometax]
with col2:
    st.subheader("🏢 Limited Company")
    accountancy_cost_ltd = st.number_input(
        "Accountancy Fees",
        value=60, 
        step=10,
        help="Costs for managing company accounts and tax returns."
    )
    accountancy_period_ltd = st.selectbox(
        "Accountancy Fees Period", 
        ['Monthly', 'Annually'], 
        key='company_accountancy_period'
    )
    accountancy_cost_annual_ltd = convert_cost_to_annual(accountancy_cost_ltd, accountancy_period_ltd)

    st.markdown("---")
    st.subheader("Mortgage Details")
    interest_rate_ltd = st.number_input(
        "Interest Rate (%)", 
        value=3.5, 
        step=0.1, 
        key='company_interest_rate',
        help="The annual interest rate on the mortgage."
    )
    length_of_mortgage_ltd = st.number_input(
        "Length of Mortgage (Years)", 
        value=25, 
        step=1, 
        key='company_length_of_mortgage',
        help="The total duration of the mortgage."
    )
    mort_arrangement_fee_ltd = st.number_input(
    "Mortgage arrangement fee (£)", 
    value=1000, 
    step=100, 
    key='mort_arrangement_fee_ltd',
    help="Fee charged by the lender for setting up the new mortgage."
)
    st.markdown("---")
    st.subheader("Corporation Tax Details")
    corptax = st.number_input(
        'Rate of Corporation tax (%)', 
        value=19,
        help="The current rate of corporation tax applied to company profits."
    )
# Function definitions for calculations
def get_mortgage_details_per():
    mort_req = purchase_price - (purchase_price - mort_remaining)
    interest_rate_monthly = (interest_rate_per / 100) / 12
    length_of_mortgage_monthly = length_of_mortgage_per * 12
    mortgage_principle_sum = npf.ppmt(interest_rate_monthly, 1, length_of_mortgage_monthly, mort_req)
    mortgage_interest = npf.ipmt(interest_rate_monthly, 1, length_of_mortgage_monthly, mort_req)
    total_monthly_repay = npf.pmt(interest_rate_monthly, length_of_mortgage_monthly, mort_req)
    return abs(mortgage_principle_sum), abs(mortgage_interest), abs(total_monthly_repay)

def get_mortgage_details_ltd():
    mort_req = purchase_price - (purchase_price - mort_remaining)
    interest_rate_monthly = (interest_rate_ltd / 100) / 12
    length_of_mortgage_monthly = length_of_mortgage_ltd * 12
    mortgage_principle_sum = npf.ppmt(interest_rate_monthly, 1, length_of_mortgage_monthly, mort_req)
    mortgage_interest = npf.ipmt(interest_rate_monthly, 1, length_of_mortgage_monthly, mort_req)
    total_monthly_repay = npf.pmt(interest_rate_monthly, length_of_mortgage_monthly, mort_req)
    return abs(mortgage_principle_sum), abs(mortgage_interest), abs(total_monthly_repay)

def total_costs_per(rent_val):
    return (service_charge_annual/12) + (rent_val * (management_charge_percent / 100)) + \
        (maintenance_cost_annual/12) + (landlord_insurance_annual/12) + \
        (building_insurance_annual/12) + (accountancy_cost_annual_per/12)

def total_costs_ltd(rent_val):
    return (service_charge_annual/12) + (rent_val * (management_charge_percent / 100)) + \
        (maintenance_cost_annual/12) + (landlord_insurance_annual/12) + \
        (building_insurance_annual/12) + (accountancy_cost_annual_ltd/12)

def EBIT_per(rent_val):
    return rent_val - total_costs_per(rent_val)

def EBIT_ltd(rent_val):
    mort_principle, mort_interest, mort_repay = get_mortgage_details_ltd()
    return rent_val - (total_costs_ltd(rent_val) + mort_interest)

def tax_credit(interest):
    return float(interest * 0.2)

def NOPAT_per(rent_val, interest):
    return (EBIT_per(rent_val) - (EBIT_per(rent_val) * incometax)) + tax_credit(interest)

def NOPAT_ltd(rent_val):
    return (EBIT_ltd(rent_val) - (EBIT_ltd(rent_val) * (corptax/100)))

def net_inc_per(rent_val, interest):
    mort_principle, mort_interest, mort_repay = get_mortgage_details_per()
    return NOPAT_per(rent_val, interest) - mort_repay

def net_inc_ltd(rent_val):
    mort_principle, mort_interest, mort_repay = get_mortgage_details_ltd()
    return NOPAT_ltd(rent_val) - mort_principle

# Calculate financials
mort_principle_per, mort_interest_per, mort_repay_per = get_mortgage_details_per()
mort_principle_ltd, mort_interest_ltd, mort_repay_ltd = get_mortgage_details_ltd()

ebit_per = EBIT_per(rent)
nopat_per = NOPAT_per(rent, mort_interest_per)
net_inc_per_val = net_inc_per(rent, mort_interest_per)

ebit_ltd = EBIT_ltd(rent)
nopat_ltd = NOPAT_ltd(rent)
net_inc_ltd_val = net_inc_ltd(rent)

# Visualization: Compare Personal vs Limited Company
st.header("📊 Financial Comparison Visualization")

# Create a subplot with 2 rows and 1 column
fig = make_subplots(rows=2, cols=1, subplot_titles=("Monthly Financial Comparison", "Annual Financial Comparison"))

# Monthly comparison
monthly_data = {
    'Category': ['Mortgage Repayment', 'EBIT', 'NOPAT', 'Net Income'],
    'Personal': [mort_repay_per, ebit_per, nopat_per, net_inc_per_val],
    'Limited Company': [mort_repay_ltd, ebit_ltd, nopat_ltd, net_inc_ltd_val]
}

fig.add_trace(
    go.Bar(x=monthly_data['Category'], y=monthly_data['Personal'], name='Personal', marker_color='#3498db'),
    row=1, col=1
)
fig.add_trace(
    go.Bar(x=monthly_data['Category'], y=monthly_data['Limited Company'], name='Limited Company', marker_color='#e74c3c'),
    row=1, col=1
)

# Annual comparison (multiply monthly values by 12)
annual_data = {
    'Category': ['Mortgage Repayment', 'EBIT', 'NOPAT', 'Net Income'],
    'Personal': [mort_repay_per*12, ebit_per*12, nopat_per*12, net_inc_per_val*12],
    'Limited Company': [mort_repay_ltd*12, ebit_ltd*12, nopat_ltd*12, net_inc_ltd_val*12]
}

fig.add_trace(
    go.Bar(x=annual_data['Category'], y=annual_data['Personal'], name='Personal', marker_color='#3498db', showlegend=False),
    row=2, col=1
)
fig.add_trace(
    go.Bar(x=annual_data['Category'], y=annual_data['Limited Company'], name='Limited Company', marker_color='#e74c3c', showlegend=False),
    row=2, col=1
)

# Update layout
fig.update_layout(
    height=800, 
    title_text="Personal vs Limited Company Financial Comparison",
    barmode='group'
)

fig.update_yaxes(title_text="Amount (£)", row=1, col=1)
fig.update_yaxes(title_text="Amount (£)", row=2, col=1)

st.plotly_chart(fig, use_container_width=True)

# Visualization: Break-Even Analysis
st.header("📈 Break-Even Analysis")

# Calculate break-even points
x = np.linspace(rent * 0.5, rent * 1.5, 100)
y_personal = [net_inc_per(i, mort_interest_per) for i in x]
y_ltd = [net_inc_ltd(i) for i in x]

# Create break-even plot
fig_breakeven = go.Figure()

fig_breakeven.add_trace(go.Scatter(x=x, y=y_personal, mode='lines', name='Personal', line=dict(color='#3498db')))
fig_breakeven.add_trace(go.Scatter(x=x, y=y_ltd, mode='lines', name='Limited Company', line=dict(color='#e74c3c')))
fig_breakeven.add_hline(y=0, line_dash="dash", line_color="green", annotation_text="Break-even point")

fig_breakeven.update_layout(
    title='Break-Even Analysis: Personal vs Limited Company',
    xaxis_title='Monthly Rent (£)',
    yaxis_title='Net Monthly Income (£)',
    hovermode='x unified'
)

st.plotly_chart(fig_breakeven, use_container_width=True)

# Transfer to Company Costs
st.header("📈 Transfer to Company Costs")

# Capital Gains Tax
st.subheader("Capital Gains Tax")
capital_gains = max(current_market_value - purchase_price, 0)
capital_gains_tax_rate = st.number_input(
    "Capital Gains Tax Rate (%)", 
    value=24, 
    step=1, 
    key='cgt_rate',
    help="The rate at which any profit on the sale of the property is taxed."
) / 100
capital_gains_tax = capital_gains * capital_gains_tax_rate

# Display the calculated Capital Gains Tax
st.write(f"Estimated Capital Gains: £{capital_gains:,.2f}")
st.write(f"Estimated Capital Gains Tax: £{capital_gains_tax:,.2f}")

# Additional Stamp Duty
st.subheader("Additional Stamp Duty")
def stamp_duty_additional(houseprice):
    if houseprice <= 250000:
        return houseprice * 0.03
    elif 250000 < houseprice <= 925000:
        return (houseprice - 250000) * 0.08 + 7500
    elif 925000 < houseprice <= 1500000:
        return (houseprice - 925000) * 0.13 + 61500
    else:
        return (houseprice - 1500000) * 0.15 + 136250

additional_stamp_duty = stamp_duty_additional(current_market_value)
st.write(f"Additional Stamp Duty: £{additional_stamp_duty:,.2f}")

# Other costs
st.subheader("Other Costs")

st.write(f"Mortgage Arrangement Fee (Limited Company): £{mort_arrangement_fee_ltd:,.2f}")
legal_fees = st.number_input(
    "Legal Fees (£)", 
    value=1000, 
    step=100, 
    key='legal_fees',
    help="Costs for legal services required to transfer the property to a company."
)
# Total transfer cost
total_transfer_cost = capital_gains_tax + additional_stamp_duty + legal_fees + mort_arrangement_fee_ltd

# Display summary of transfer costs
st.success(f"""
Transfer Cost Summary:
- Capital Gains Tax: £{capital_gains_tax:,.2f}
- Additional Stamp Duty: £{additional_stamp_duty:,.2f}
- Mortgage Arrangement Fee: £{mort_arrangement_fee_ltd:,.2f}
- Legal Fees: £{legal_fees:,.2f}
- Total Transfer Cost: £{total_transfer_cost:,.2f}
""")

# Explanation of results
st.info("""
ℹ️ **Interpretation of Results:**

1. **Financial Comparison Visualisation**: This chart compares key financial metrics between personal and limited company ownership. Higher bars indicate better performance in that category.

2. **Break-Even Analysis**: This graph shows how net monthly income changes with varying rental income. The point where each line crosses the green dashed line (y=0) is the break-even point for that ownership structure.

3. **Transfer Costs**: These are the one-time costs associated with transferring the property from personal to company ownership. Consider these against the potential long-term tax benefits of company ownership.

Remember, this tool provides estimates based on the information you've entered. For personalised advice, please consult with a qualified tax professional or financial advisor.
""")

# Disclaimer
st.warning("""
**Disclaimer**: This tool is for informational purposes only and does not constitute financial or tax advice. 
The calculations are based on simplified models and may not account for all factors relevant to your specific situation. 
Always consult with a qualified professional before making financial decisions.
""")