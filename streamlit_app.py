# streamlit_app.py
import streamlit as st
import plotly.graph_objects as go

st.set_page_config(page_title="Gasification Energy Balance", layout="wide")

# Custom CSS to match the HTML design exactly
st.markdown("""
<style>
    body { background-color: #f3f4f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .main { background-color: #f3f4f6; }
    
    /* Colored sections */
    .fuel-params { background-color: #eff6ff; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; border-left: 4px solid #3b82f6; }
    .syngas-params { background-color: #fef3c7; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; border-left: 4px solid #f97316; }
    .gas-comp { background-color: #f0fdf4; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem; border-left: 4px solid #22c55e; }
    
    /* Section titles */
    .section-title { font-weight: bold; font-size: 0.875rem; margin-bottom: 0.75rem; text-transform: uppercase; }
    .fuel-title { color: #1e40af; }
    .syngas-title { color: #b45309; }
    .gas-title { color: #166534; }
    
    /* Result cards */
    .result-card { background: white; padding: 1.5rem; border-radius: 0.5rem; border-left: 4px solid #2563eb; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .result-card.green { border-left-color: #22c55e; }
    .result-card.red { border-left-color: #dc2626; }
    
    /* Analysis box */
    .analysis-box { background-color: #eff6ff; border: 1px solid #bfdbfe; border-radius: 0.75rem; padding: 1.5rem; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div style='text-align: center; margin-bottom: 2rem;'>
    <h1 style='font-size: 1.875rem; font-weight: bold; color: #1e3a8a; margin: 0; margin-bottom: 0.5rem;'>Biomass Gasification Energy Balance</h1>
    <p style='color: #4b5563; margin: 0;'>Based on Modified Equation: Q<sub>loss</sub> = E<sub>in</sub> - (E<sub>chemical</sub> + E<sub>sensible</sub>)</p>
</div>
""", unsafe_allow_html=True)

# Constants
LHV_CO = 12.63
LHV_H2 = 10.78
LHV_CH4 = 35.88
CP_GAS = 1.35  # kJ/Nm3K

# Layout: left inputs, right results
left, right = st.columns([1, 2])

with left:
    st.markdown('<div style="background: white; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">', unsafe_allow_html=True)
    
    st.markdown("""
    <h2 style='font-size: 1.25rem; font-weight: bold; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e5e7eb; color: #374151;'>1. Process Inputs</h2>
    """, unsafe_allow_html=True)
    
    # Fuel Parameters
    st.markdown('<div class="fuel-params">', unsafe_allow_html=True)
    st.markdown('<div class="section-title fuel-title">Fuel Parameters</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        mass_flow = st.number_input("Mass Flow (kg/h)", value=6.4, step=0.1, format="%.1f", label_visibility="collapsed")
    with col2:
        fuel_lhv = st.number_input("Fuel LHV (MJ/kg)", value=15.8, step=0.1, format="%.1f", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Syngas Conditions
    st.markdown('<div class="syngas-params">', unsafe_allow_html=True)
    st.markdown('<div class="section-title syngas-title">Syngas Conditions</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        gas_flow = st.number_input("Gas Flow (Nm³/h)", value=15.3, step=0.1, format="%.1f", label_visibility="collapsed")
    with col2:
        temp_out = st.number_input("Outlet Temp (°C)", value=320, step=1, format="%d", label_visibility="collapsed")
    temp_ref = st.number_input("Ref Temp (°C)", value=25, step=1, format="%d", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Gas Composition
    st.markdown('<div class="gas-comp">', unsafe_allow_html=True)
    st.markdown('<div class="section-title gas-title">Gas Composition (Vol %)</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        vol_co = st.number_input("CO %", value=19.2, step=0.1, format="%.1f", label_visibility="collapsed")
    with col2:
        vol_h2 = st.number_input("H2 %", value=14.1, step=0.1, format="%.1f", label_visibility="collapsed")
    with col3:
        vol_ch4 = st.number_input("CH4 %", value=2.1, step=0.1, format="%.1f", label_visibility="collapsed")
    st.markdown('<p style="font-size: 0.75rem; color: #6b7280; margin-top: 0.5rem; margin-bottom: 0;">*Balance is assumed to be N2/CO2</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Run button
    run = st.button("Run Calculation", use_container_width=True, key="calc", type="primary")
    
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    # KPI Cards
    kpi1, kpi2, kpi3 = st.columns(3, gap="small")
    
    with kpi1:
        kpi1_place = st.empty()
    with kpi2:
        kpi2_place = st.empty()
    with kpi3:
        kpi3_place = st.empty()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Detailed Energy Breakdown
    breakdown_place = st.empty()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Analysis Box
    analysis_place = st.empty()


def compute_and_show():
    """Calculate energy balance and update results"""
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

    # KPI Card 1 - Syngas LHV
    with kpi1_place.container():
        st.markdown(f"""
        <div class="result-card">
            <p style='font-size: 0.875rem; color: #6b7280; font-weight: bold; text-transform: uppercase; margin-bottom: 0.5rem;'>Syngas LHV</p>
            <h3 style='font-size: 1.875rem; font-weight: bold; color: #1f2937; margin: 0.5rem 0;'>{LHV_gas:.2f} <span style='font-size: 1rem; color: #9ca3af; font-weight: normal;'>MJ/Nm³</span></h3>
            <p style='font-size: 0.75rem; color: #9ca3af; margin-top: 0.5rem;'>Energy Density</p>
        </div>
        """, unsafe_allow_html=True)

    # KPI Card 2 - Cold Gas Efficiency
    with kpi2_place.container():
        st.markdown(f"""
        <div class="result-card green">
            <p style='font-size: 0.875rem; color: #6b7280; font-weight: bold; text-transform: uppercase; margin-bottom: 0.5rem;'>Cold Gas Efficiency</p>
            <h3 style='font-size: 1.875rem; font-weight: bold; color: #16a34a; margin: 0.5rem 0;'>{CGE:.1f}%</h3>
            <p style='font-size: 0.75rem; color: #9ca3af; margin-top: 0.5rem;'>Fuel to Gas Conversion</p>
        </div>
        """, unsafe_allow_html=True)

    # KPI Card 3 - System Losses
    with kpi3_place.container():
        st.markdown(f"""
        <div class="result-card red">
            <p style='font-size: 0.875rem; color: #6b7280; font-weight: bold; text-transform: uppercase; margin-bottom: 0.5rem;'>System Losses</p>
            <h3 style='font-size: 1.875rem; font-weight: bold; color: #dc2626; margin: 0.5rem 0;'>{E_loss:.2f} <span style='font-size: 1rem; color: #9ca3af; font-weight: normal;'>MJ/h</span></h3>
            <p style='font-size: 0.75rem; color: #9ca3af; margin-top: 0.5rem;'>Wall Loss + Unburnt Char</p>
        </div>
        """, unsafe_allow_html=True)

    # Detailed Energy Breakdown
    with breakdown_place.container():
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown(f"""
            <div style='background: white; border-radius: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden;'>
                <div style='background-color: #f9fafb; padding: 1rem 1.5rem; border-bottom: 1px solid #e5e7eb;'>
                    <h3 style='font-weight: bold; color: #374151; margin: 0;'>Detailed Energy Breakdown (Modified Equation)</h3>
                </div>
                <div style='padding: 1.5rem;'>
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
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            labels = ['Chemical Energy\n(Useful)', 'Sensible Heat\n(Hot Gas)', 'Losses\n(Wall/Char)']
            values = [max(E_chem, 0), max(E_sens, 0), max(E_loss, 0)]
            colors = ['#16a34a', '#ea580c', '#dc2626']
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(colors=colors),
                textinfo='label+percent',
                textposition='outside',
                hovertemplate='<b>%{label}</b><br>%{value:.2f} MJ/h<br>%{percent}<extra></extra>'
            )])
            fig.update_layout(
                height=320,
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=True,
                font=dict(size=10),
                legend=dict(x=0.5, y=-0.15, orientation="h")
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Analysis Box
    with analysis_place.container():
        analysis = ""
        if LHV_gas > 4.5:
            analysis += f"✅ <b>Good Gas Quality ({LHV_gas:.2f} MJ/Nm³):</b> Suitable for ICE power generation. "
        else:
            analysis += f"⚠️ <b>Low Gas Quality ({LHV_gas:.2f} MJ/Nm³):</b> Better suited for thermal (heating) applications. "
        
        if CGE > 70:
            analysis += f"Efficiency is <b>good ({CGE:.1f}%)</b>."
        else:
            analysis += f"Efficiency is <b>low ({CGE:.1f}%)</b>. Check for heat leaks or incomplete carbon conversion."
        
        st.markdown(f"""
        <div class="analysis-box">
            <h3 style='color: #1e3a8a; font-weight: bold; margin-top: 0; margin-bottom: 0.5rem;'>💡 Analysis of Current Results</h3>
            <p style='color: #1e40af; font-size: 0.875rem; line-height: 1.5; margin: 0;'>{analysis}</p>
        </div>
        """, unsafe_allow_html=True)


# Initial calculation and on button click
compute_and_show()
if run:
    compute_and_show()
