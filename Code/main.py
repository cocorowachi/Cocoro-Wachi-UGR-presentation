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

    st.session_state.acali = Autocalibrate(np.datetime64("2015-06-01T00:00"), np.datetime64("2020-01-31T23:00"), 64, sewer_df.read('MS0311 FlowMGD'), temperature_df.read("Temperature (F)"), precip_df.read("WS1201 Precip HourlyInches"))
    st.session_state.acali.optimize()
acali=st.session_state.acali
datetime, diurnal, sim_fast, sim_slow = acali.get_sim_flow()

plot_config = {
    'displayModeBar': True,
    'scrollZoom': True
}

fig = go.Figure()
fig.add_trace(go.Scattergl(x=datetime, y=acali.diurnal, name="seasonal", mode="lines", yaxis='y1'))
fig.update_layout(
    title="Fast Response",
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

fig = go.Figure()
fig.add_trace(go.Scattergl(x=datetime, y=acali.obs_seasonal, name="seasonal", mode="lines", yaxis='y1'))
fig.add_trace(go.Scattergl(x=datetime, y=acali.obs_slow_flow+acali.obs_seasonal, name="slow", mode="lines", yaxis='y1'))
fig.add_trace(go.Scattergl(x=datetime, y=acali.obs_fast_flow+acali.obs_slow_flow+acali.obs_seasonal, name="fast", mode="lines", yaxis='y1'))
fig.update_layout(
    title="Responses",
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

st.write(acali.fast_param)
fig = go.Figure()
fig.add_trace(go.Scattergl(x=datetime, y=acali.obs_fast_flow, name="obs", mode="lines", yaxis='y1'))
fig.add_trace(go.Scattergl(x=datetime, y=sim_fast, name="sim", mode="lines", yaxis='y1'))
fig.update_layout(
    title="Fast Response",
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

st.write(acali.slow_param)
fig = go.Figure()
fig.add_trace(go.Scattergl(x=datetime, y=acali.obs_slow_flow, name="obs", mode="lines", yaxis='y1'))
fig.add_trace(go.Scattergl(x=datetime, y=sim_slow, name="sim", mode="lines", yaxis='y1'))
fig.update_layout(
    title="Slow Response",
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

fig = go.Figure()
fig.add_trace(go.Scattergl(x=datetime, y=acali.obs_fast_flow+acali.obs_slow_flow+acali.obs_seasonal, name="observed (LHS)", mode="lines", yaxis='y1'))
fig.add_trace(go.Scattergl(x=datetime, y=sim_fast+sim_slow+acali.obs_seasonal, name="simulated (RHS)", mode="lines", yaxis='y1'))

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