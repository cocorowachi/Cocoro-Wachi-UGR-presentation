import streamlit as st
import numpy as np
from Data import Data
from Autocalibrate import Autocalibrate
import plotly.graph_objects as go
st.set_page_config(
    page_title="Presentation Demo",
    page_icon="📊",
    layout="wide"
)

if "_init_" not in st.session_state:
    st.session_state._init_ = True

    path = "../Data/"
    temp = "Temperature.csv"
    sewer = "MMSD Sewer Flow Data.csv"
    precip = "MMSD Precipitation Raw Data.csv"

    temperature_df = Data(path + temp)
    sewer_df = Data(path + sewer)
    precip_df = Data(path + precip)

    st.session_state.acali = Autocalibrate(np.datetime64("2017-03-26T00:00"), np.datetime64("2017-05-14T23:00"), 64, sewer_df.read('MS0311 FlowMGD'), temperature_df.read("Temperature (F)"), precip_df.read("WS1201 Precip HourlyInches"))
    st.session_state.acali.optimize2()
acali=st.session_state.acali

plot_config = {
    'displayModeBar': True,
    'scrollZoom': True
}
##################################
datetime = acali.datetime
fig = go.Figure()
fig.add_trace(go.Scattergl(x=datetime, y=acali.flow, name="observed (LHS)", mode="lines", yaxis='y1'))
fig.add_trace(go.Scattergl(x=datetime, y=acali.obs_seasonal + acali.obs_slow_flow + acali.obs_fast_flow, name="simulated (RHS)", mode="lines", yaxis='y1'))

fig.update_layout(
    title="combine Response",
    xaxis_title="Date Time",
    yaxis=dict(title='Flow [MGD]',
                side='left',
                fixedrange=True),
    yaxis2=dict(title='Flow [cfs]',
                side='right',
                showgrid=False,
                fixedrange=True),
    template="plotly_dark",
    hovermode='x unified', 
    dragmode='pan'
)
st.plotly_chart(fig, config={'scrollZoom': True}, use_container_width=True)
###############################
#onetoone
fig = go.Figure()
x=acali.obs_seasonal + acali.obs_slow_flow + acali.obs_fast_flow
y=acali.flow
fig.add_trace(go.Scattergl(x=x, y=y, name="simulated (RHS)", mode="markers", yaxis='y1'))
m, b = np.polyfit(x, y, 1)
ss_res = np.sum((x - y)**2)
ss_tot = np.sum((x - np.mean(x))**2)

r2 = 1 - (ss_res / ss_tot)
st.write("m",m)
st.write("b",b)
st.write("r2",r2)
fig.add_trace(go.Scattergl(x=[0,max(x)], y=[0,m*max(x)+b], name="simulated (RHS)", mode="lines", yaxis='y1'))
fig.update_layout(
    title="combine Response",
    xaxis=dict(title="Date Time",
               fixedrange=False),
    yaxis=dict(title='Flow [MGD]',
                side='left',
                fixedrange=False),
    template="plotly_dark",
    hovermode='x unified', 
    dragmode='pan'
)
st.plotly_chart(fig, config={'scrollZoom': True}, use_container_width=True)
st.button("rerun")