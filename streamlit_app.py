# streamlit_app.py
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Gasification Energy Balance", layout="wide")

st.markdown("<h1 style='text-align:center;color:#0f172a'>Biomass Gasification Energy Balance</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#374151'>Based on Modified Equation: Q<sub>loss</sub> = E<sub>in</sub> - (E<sub>chemical</sub> + E<sub>sensible</sub>)</p>", unsafe_allow_html=True)

# Constants (same as your HTML)
LHV_CO = 12.63
LHV_H2 = 10.78
LHV_CH4 = 35.88
CP_GAS = 1.35  # kJ/Nm3K

# Layout: left inputs, right results
left, right = st.columns([1, 2])

with left:
    st.subheader("1. Process Inputs")
    mass_flow = st.number_input("Mass Flow (kg/h)", value=6.4, step=0.1, format="%.2f")
    fuel_lhv = st.number_input("Fuel LHV (MJ/kg)", value=15.8, step=0.1, format="%.2f")
    st.markdown("---")
    gas_flow = st.number_input("Gas Flow (Nm³/h)", value=15.3, step=0.1, format="%.2f")
    temp_out = st.number_input("Outlet Temp (°C)", value=320, step=1)
    temp_ref = st.number_input("Ref Temp (°C)", value=25, step=1)
    st.markdown("---")
    vol_co = st.number_input("CO %", value=19.2, step=0.1, format="%.2f")
    vol_h2 = st.number_input("H2 %", value=14.1, step=0.1, format="%.2f")
    vol_ch4 = st.number_input("CH4 %", value=2.1, step=0.1, format="%.2f")

    run = st.button("Run Calculation")

with right:
    st.subheader("Results")
    # placeholders / metrics
    lhv_metric = st.empty()
    eff_metric = st.empty()
    loss_metric = st.empty()
    st.write("---")
    val_in = st.empty()
    val_chem = st.empty()
    val_sens = st.empty()
    val_loss = st.empty()
    chart_place = st.empty()
    analysis_place = st.empty()

def compute_and_show():
    pct_co = vol_co / 100.0
    pct_h2 = vol_h2 / 100.0
    pct_ch4 = vol_ch4 / 100.0

    E_in = mass_flow * fuel_lhv                        # MJ/h
    LHV_gas = (pct_co * LHV_CO) + (pct_h2 * LHV_H2) + (pct_ch4 * LHV_CH4)  # MJ/Nm3
    E_chem = gas_flow * LHV_gas                        # MJ/h
    delta_T = temp_out - temp_ref
    E_sens_kJ = gas_flow * CP_GAS * delta_T
    E_sens = E_sens_kJ / 1000.0                        # MJ/h
    E_loss = E_in - (E_chem + E_sens)
    CGE = (E_chem / E_in) * 100 if E_in != 0 else 0.0

    # show metrics
    lhv_metric.metric("Syngas LHV", f"{LHV_gas:.2f} MJ/Nm³")
    eff_metric.metric("Cold Gas Efficiency", f"{CGE:.1f} %")
    loss_metric.metric("System Losses", f"{E_loss:.2f} MJ/h")

    val_in.markdown(f"**Total Input (H<sub>feed</sub>)**: `{E_in:.2f} MJ/h`")
    val_chem.markdown(f"**Chemical Out (H<sub>chem</sub>)**: `{E_chem:.2f} MJ/h`")
    val_sens.markdown(f"**Sensible Out (H<sub>sens</sub>)**: `{E_sens:.2f} MJ/h`")
    val_loss.markdown(f"**Total Losses (Q<sub>loss</sub>)**: `{E_loss:.2f} MJ/h`")

    # doughnut chart (plotly)
    labels = ['Chemical Energy (Useful)', 'Sensible Heat (Hot Gas)', 'Losses (Wall/Char)']
    values = [max(E_chem, 0), max(E_sens, 0), max(E_loss, 0)]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5, textinfo='label+percent')])
    fig.update_layout(height=350, margin=dict(t=10,b=10,l=10,r=10))
    chart_place.plotly_chart(fig, use_container_width=True)

    # analysis text
    analysis = ""
    if LHV_gas > 4.5:
        analysis += f"✅ **Good Gas Quality ({LHV_gas:.2f} MJ/Nm³):** Suitable for ICE power generation. "
    else:
        analysis += f"⚠️ **Low Gas Quality ({LHV_gas:.2f} MJ/Nm³):** Better for thermal applications. "
    if CGE > 70:
        analysis += f"Efficiency is **good ({CGE:.1f}%)**."
    else:
        analysis += f"Efficiency is **low ({CGE:.1f}%)**. Check for heat leaks or incomplete carbon conversion."
    analysis_place.markdown(analysis)

# run on load and when user clicks the button
compute_and_show()
if run:
    compute_and_show()
