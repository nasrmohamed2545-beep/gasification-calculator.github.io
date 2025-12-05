# streamlit_app.py
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Gasification Energy Balance", layout="wide")

# Custom CSS to match website design
st.markdown("""
<style>
    /* Main container */
    .main {
        background-color: #f3f4f6;
    }
    
    /* Input section styling */
    .input-section {
        background-color: white;
        padding: 1.5rem;
        border-radius: 0.75rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Colored input groups */
    .fuel-params {
        background-color: #f0f9ff;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #3b82f6;
    }
    
    .syngas-params {
        background-color: #fff7ed;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #f97316;
    }
    
    .gas-comp {
        background-color: #f0fdf4;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #22c55e;
    }
    
    /* Result cards */
    .result-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-left: 4px solid #3b82f6;
    }
    
    .result-card.green {
        border-left-color: #22c55e;
    }
    
    .result-card.red {
        border-left-color: #ef4444;
    }
    
    /* Section headers */
    .section-title {
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        color: #1e40af;
        margin-bottom: 0.75rem;
    }
    
    .section-title.orange {
        color: #b45309;
    }
    
    .section-title.green {
        color: #166534;
    }
    
    /* Small text */
    .small-text {
        font-size: 0.75rem;
        color: #6b7280;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 style='text-align:center;color:#1e3a8a;margin-bottom:0.25rem;'>Biomass Gasification Energy Balance</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#6b7280;margin-bottom:2rem;'>Based on Modified Equation: Q<sub>loss</sub> = E<sub>in</sub> - (E<sub>chemical</sub> + E<sub>sensible</sub>)</p>", unsafe_allow_html=True)

# Constants
LHV_CO = 12.63
LHV_H2 = 10.78
LHV_CH4 = 35.88
CP_GAS = 1.35  # kJ/Nm3K

# Layout: left inputs, right results
left, right = st.columns([1, 2])

with left:
    st.markdown("<div class='input-section'>", unsafe_allow_html=True)
    st.markdown("<h2 style='font-size: 1.25rem; font-weight: bold; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e5e7eb;'>1. Process Inputs</h2>", unsafe_allow_html=True)
    
    # Fuel Parameters
    st.markdown("<div class='fuel-params'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Fuel Parameters</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        mass_flow = st.number_input("Mass Flow (kg/h)", value=6.4, step=0.1, format="%.2f", label_visibility="collapsed")
        st.caption("Mass Flow (kg/h)")
    with col2:
        fuel_lhv = st.number_input("Fuel LHV (MJ/kg)", value=15.8, step=0.1, format="%.2f", label_visibility="collapsed")
        st.caption("Fuel LHV (MJ/kg)")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Syngas Conditions
    st.markdown("<div class='syngas-params'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title orange'>Syngas Conditions</div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        gas_flow = st.number_input("Gas Flow (Nm³/h)", value=15.3, step=0.1, format="%.2f", label_visibility="collapsed")
        st.caption("Gas Flow (Nm³/h)")
    with col2:
        temp_out = st.number_input("Outlet Temp (°C)", value=320, step=1, label_visibility="collapsed")
        st.caption("Outlet Temp (°C)")
    temp_ref = st.number_input("Ref Temp (°C)", value=25, step=1, label_visibility="collapsed")
    st.caption("Ref Temp (°C)")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Gas Composition
    st.markdown("<div class='gas-comp'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title green'>Gas Composition (Vol %)</div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        vol_co = st.number_input("CO %", value=19.2, step=0.1, format="%.2f", label_visibility="collapsed")
        st.caption("CO %")
    with col2:
        vol_h2 = st.number_input("H2 %", value=14.1, step=0.1, format="%.2f", label_visibility="collapsed")
        st.caption("H2 %")
    with col3:
        vol_ch4 = st.number_input("CH4 %", value=2.1, step=0.1, format="%.2f", label_visibility="collapsed")
        st.caption("CH4 %")
    st.markdown("<div class='small-text'>*Balance is assumed to be N2/CO2</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    run = st.button("Run Calculation", use_container_width=True, key="calc_btn")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    # Placeholders for results
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    
    with kpi_col1:
        lhv_place = st.empty()
    with kpi_col2:
        eff_place = st.empty()
    with kpi_col3:
        loss_place = st.empty()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Detailed Energy Breakdown
    breakdown_container = st.container()
    
    # Energy breakdown table + chart
    energy_col1, energy_col2 = st.columns([1, 1])
    with energy_col1:
        breakdown_table = st.empty()
    with energy_col2:
        chart_place = st.empty()
    
    st.markdown("<br>", unsafe_allow_html=True)
    analysis_place = st.empty()

def compute_and_show():
    pct_co = vol_co / 100.0
    pct_h2 = vol_h2 / 100.0
    pct_ch4 = vol_ch4 / 100.0

    E_in = mass_flow * fuel_lhv
    LHV_gas = (pct_co * LHV_CO) + (pct_h2 * LHV_H2) + (pct_ch4 * LHV_CH4)
    E_chem = gas_flow * LHV_gas
    delta_T = temp_out - temp_ref
    E_sens_kJ = gas_flow * CP_GAS * delta_T
    E_sens = E_sens_kJ / 1000.0
    E_loss = E_in - (E_chem + E_sens)
    CGE = (E_chem / E_in) * 100 if E_in != 0 else 0.0

    # KPI Cards
    with lhv_place.container():
        st.markdown(f"""
        <div class='result-card'>
            <p style='font-size: 0.875rem; color: #6b7280; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;'>Syngas LHV</p>
            <h3 style='font-size: 2rem; font-weight: bold; color: #1f2937; margin: 0.5rem 0;'>{LHV_gas:.2f} <span style='font-size: 1rem; color: #9ca3af; font-weight: normal;'>MJ/Nm³</span></h3>
            <p style='font-size: 0.75rem; color: #9ca3af; margin-top: 0.5rem;'>Energy Density</p>
        </div>
        """, unsafe_allow_html=True)
    
    with eff_place.container():
        st.markdown(f"""
        <div class='result-card green'>
            <p style='font-size: 0.875rem; color: #6b7280; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;'>Cold Gas Efficiency</p>
            <h3 style='font-size: 2rem; font-weight: bold; color: #16a34a; margin: 0.5rem 0;'>{CGE:.1f}%</h3>
            <p style='font-size: 0.75rem; color: #9ca3af; margin-top: 0.5rem;'>Fuel to Gas Conversion</p>
        </div>
        """, unsafe_allow_html=True)
    
    with loss_place.container():
        st.markdown(f"""
        <div class='result-card red'>
            <p style='font-size: 0.875rem; color: #6b7280; font-weight: 600; text-transform: uppercase; margin-bottom: 0.5rem;'>System Losses</p>
            <h3 style='font-size: 2rem; font-weight: bold; color: #dc2626; margin: 0.5rem 0;'>{E_loss:.2f} <span style='font-size: 1rem; color: #9ca3af; font-weight: normal;'>MJ/h</span></h3>
            <p style='font-size: 0.75rem; color: #9ca3af; margin-top: 0.5rem;'>Wall Loss + Unburnt Char</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed Energy Breakdown
    with breakdown_table.container():
        st.markdown("""
        <div style='background: white; border-radius: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden;'>
            <div style='background-color: #f9fafb; padding: 1rem 1.5rem; border-bottom: 1px solid #e5e7eb;'>
                <h3 style='font-weight: bold; color: #374151; margin: 0;'>Detailed Energy Breakdown (Modified Equation)</h3>
            </div>
            <div style='padding: 1.5rem;'>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style='font-size: 0.875rem;'>
            <div style='display: flex; justify-content: space-between; align-items: center; padding-bottom: 0.5rem; border-bottom: 1px solid #f3f4f6;'>
                <span style='color: #4b5563;'>Total Input (H<sub>feed</sub>)</span>
                <span style='font-family: monospace; font-weight: bold; color: #2563eb;'>{E_in:.2f} MJ/h</span>
            </div>
            <div style='display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f3f4f6;'>
                <span style='color: #4b5563;'>Chemical Out (H<sub>chem</sub>)</span>
                <span style='font-family: monospace; font-weight: bold; color: #16a34a;'>{E_chem:.2f} MJ/h</span>
            </div>
            <div style='display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid #f3f4f6;'>
                <span style='color: #4b5563;'>Sensible Out (H<sub>sens</sub>)</span>
                <span style='font-family: monospace; font-weight: bold; color: #f97316;'>{E_sens:.2f} MJ/h</span>
            </div>
            <div style='display: flex; justify-content: space-between; align-items: center; padding-top: 0.5rem;'>
                <span style='font-weight: bold; color: #1f2937;'>Total Losses (Q<sub>loss</sub>)</span>
                <span style='font-family: monospace; font-weight: bold; color: #dc2626;'>{E_loss:.2f} MJ/h</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div></div>", unsafe_allow_html=True)
    
    # Energy Chart
    with chart_place.container():
        labels = ['Chemical Energy\n(Useful)', 'Sensible Heat\n(Hot Gas)', 'Losses\n(Wall/Char)']
        values = [max(E_chem, 0), max(E_sens, 0), max(E_loss, 0)]
        colors = ['#22c55e', '#f97316', '#ef4444']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            marker=dict(colors=colors),
            textinfo='label+percent',
            textposition='auto',
            hovertemplate='<b>%{label}</b><br>%{value:.2f} MJ/h<br>%{percent}<extra></extra>'
        )])
        fig.update_layout(
            height=300,
            margin=dict(t=10, b=10, l=10, r=10),
            showlegend=False,
            font=dict(size=11)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Analysis Box
    with analysis_place.container():
        st.markdown("""
        <div style='background: white; border-radius: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); padding: 1.5rem;'>
            <h3 style='font-weight: bold; color: #374151; margin-top: 0;'>💡 Analysis of Current Results</h3>
        """, unsafe_allow_html=True)
        
        analysis = ""
        if LHV_gas > 4.5:
            analysis += f"✅ **Good Gas Quality ({LHV_gas:.2f} MJ/Nm³):** Suitable for ICE power generation. "
        else:
            analysis += f"⚠️ **Low Gas Quality ({LHV_gas:.2f} MJ/Nm³):** Better for thermal applications. "
        if CGE > 70:
            analysis += f"**Efficiency is good ({CGE:.1f}%).**"
        else:
            analysis += f"**Efficiency is low ({CGE:.1f}%).**"
        
        st.markdown(analysis)
        st.markdown("</div>", unsafe_allow_html=True)

# Run calculations
compute_and_show()
if run:
    compute_and_show()
