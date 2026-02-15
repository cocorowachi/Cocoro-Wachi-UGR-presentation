import streamlit as st
import numpy as np
from Data import Data
from Autocalibrate import Autocalibrate
from AutocalibrateTrad import AutocalibrateTrad
import plotly.graph_objects as go
from model import moving_avg_numba
st.set_page_config(
    page_title="MSOE Wachi Sewer Dashboard",
    page_icon="graphics/msoe_icon.png",
    layout="wide"
)
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
# Header
title_cols = st.columns([1,10])
with title_cols[0]:
    st.image("graphics/msoe_logo.png", width=100)
with title_cols[1]:
    st.header("Breaking Apart Wet Weather Flow Signals Allows Streamlined Auto-calibration of Sewer Hydrology Models")
    st.write("Authors: Dr. William Gonwa P.E., Cocoro Wachi Undergraduate")
cols = st.columns(3)
with cols[0]:
    if st.button("Dashboard", type="primary" if st.session_state.page == "dashboard" else "secondary", disabled="_init_" not in st.session_state, width="stretch"):
        st.session_state.page = "dashboard"
        st.rerun()
with cols[1]:
    if st.button("Poster", type="primary" if st.session_state.page == "poster" else "secondary", disabled="_init_" not in st.session_state, width="stretch"):
        st.session_state.page = "poster"
        st.rerun()
with cols[2]:
    if st.button("Authors", type="primary" if st.session_state.page == "authors" else "secondary", disabled="_init_" not in st.session_state, width="stretch"):
        st.session_state.page = "authors"
        st.rerun()
st.write("---")
if "_init_" not in st.session_state:

    path = "Data/"
    temp = "Temperature.csv"
    sewer = "MMSD Sewer Flow Data.csv"
    precip = "MMSD Precipitation Raw Data.csv"

    temperature_df = Data(path + temp)
    sewer_df = Data(path + sewer)
    precip_df = Data(path + precip)

    st.session_state.acali = Autocalibrate(np.datetime64("2015-06-01T00:00"), np.datetime64("2020-01-31T23:00"), 64, sewer_df.read('MS0208 FlowMGD'), temperature_df.read("Temperature (F)"), precip_df.read("WS1201 Precip HourlyInches"))
    st.session_state.acaliT = AutocalibrateTrad(np.datetime64("2015-06-01T00:00"), np.datetime64("2020-01-31T23:00"), 64, sewer_df.read('MS0208 FlowMGD'), temperature_df.read("Temperature (F)"), precip_df.read("WS1201 Precip HourlyInches"))
    st.session_state.acali.optimize()
    st.session_state.acaliT.optimize()
    st.session_state._init_ = True
    st.rerun()

events = [(np.datetime64("2016-10-15T14:00"),np.datetime64("2016-10-18T14:00")),
          (np.datetime64("2016-10-25T14:00"),np.datetime64("2016-10-29T22:00")),
          (np.datetime64("2016-11-01T22:00"),np.datetime64("2016-11-04T07:00")),
          (np.datetime64("2016-11-27T12:00"),np.datetime64("2016-11-30T16:00")),
          (np.datetime64("2017-01-19T10:00"),np.datetime64("2017-01-19T22:00")),
          (np.datetime64("2017-02-23T09:00"),np.datetime64("2017-02-27T19:00")),
          (np.datetime64("2017-04-15T10:00"),np.datetime64("2017-04-19T08:00")),
          (np.datetime64("2017-04-29T17:00"),np.datetime64("2017-05-05T01:00")),
          (np.datetime64("2017-06-03T02:00"),np.datetime64("2017-06-06T14:00")),
          (np.datetime64("2017-06-16T19:00"),np.datetime64("2017-06-19T01:00")),
          (np.datetime64("2017-06-22T13:00"),np.datetime64("2017-06-27T13:00")),
          (np.datetime64("2017-06-28T04:00"),np.datetime64("2017-07-02T17:00")),
          (np.datetime64("2017-07-09T23:00"),np.datetime64("2017-07-16T08:00")),
          (np.datetime64("2017-10-10T04:00"),np.datetime64("2017-10-13T12:00")),
          (np.datetime64("2017-10-13T17:00"),np.datetime64("2017-10-17T10:00")),
          (np.datetime64("2018-01-21T20:00"),np.datetime64("2018-01-26T15:00")),
          (np.datetime64("2018-02-19T04:00"),np.datetime64("2018-02-24T07:00")),
          (np.datetime64("2018-04-13T04:00"),np.datetime64("2018-04-18T06:00")),
          (np.datetime64("2018-05-02T08:00"),np.datetime64("2018-05-06T18:00")),
          (np.datetime64("2018-05-08T15:00"),np.datetime64("2018-05-10T20:00")),
          (np.datetime64("2018-05-10T21:00"),np.datetime64("2018-05-19T02:00")),
          (np.datetime64("2018-05-20T06:00"),np.datetime64("2018-05-25T02:00")),
          (np.datetime64("2017-01-19T10:00"),np.datetime64("2017-01-19T22:00"))]
acali=st.session_state.acali
acaliT=st.session_state.acaliT
datetime, diurnal, sim_fast, sim_slow, sim_seasonal = acali.get_sim_flow()
s, e = 11200, 26700
# datetime = datetime[s:e]

plot_config = {
    'displayModeBar': True,
    'scrollZoom': True
}
if st.session_state.page == "dashboard":
    ########################################
    # model fast
    st.write(acali.fast_param)
    fig = go.Figure()
    # fig.add_trace(go.Scattergl(x=datetime[2:], y=acali.precip_signal[2:],   line_color="green", name="precip", mode="lines", yaxis='y2'))
    fig.add_trace(go.Scattergl(x=datetime[s:e], y=acali.obs_fast_flow[s:e],   line_color="blue", name="obs", mode="lines", yaxis='y1'))
    fig.add_trace(go.Scattergl(x=datetime[s:e], y=sim_fast[s:e],              line_color="red", name="sim", mode="lines", yaxis='y1'))
    fig.update_layout(
        title="Fast Response",
        xaxis=dict(title="Date Time",
                showgrid=True,
                fixedrange=True),
        yaxis=dict(title='Flow [MGD]',
                    side='left',
                    fixedrange=False),
        # yaxis2=dict(title='Flow [cfs]',
        #             side='right',
        #             showgrid=False,
        #             fixedrange=True,
        #             autorange="reversed"),
        template="plotly_dark",
        hovermode='x unified', 
        dragmode='pan'
    )
    st.plotly_chart(fig, config={'scrollZoom': True}, use_container_width=True)

    ###############################
    # Model slow
    st.write(acali.slow_param)
    fig = go.Figure()
    # fig.add_trace(go.Scattergl(x=datetime, y=acali.precip_signal,   line_color="green", name="precip", mode="lines", yaxis='y2'))
    fig.add_trace(go.Scattergl(x=datetime[s:e], y=acali.obs_slow_flow[s:e],   line_color="blue", name="obs", mode="lines", yaxis='y1'))
    fig.add_trace(go.Scattergl(x=datetime[s:e], y=sim_slow[s:e],              line_color="red", name="sim", mode="lines", yaxis='y1'))
    fig.update_layout(
        title="Slow Response",
        xaxis=dict(title="Date Time",
                showgrid=True,
                fixedrange=True),
        yaxis=dict(title='Flow [MGD]',
                    side='left',
                    fixedrange=False),
        # yaxis2=dict(title='Flow [cfs]',
        #             side='right',
        #             showgrid=False,
        #             fixedrange=True,
        #             autorange="reversed"),
        template="plotly_dark",
        hovermode='x unified', 
        dragmode='pan'
    )
    st.plotly_chart(fig, config={'scrollZoom': True}, use_container_width=True)

    ##############################
    # model seasonal
    st.write(acali.seasonal_param)
    fig = go.Figure()
    # fig.add_trace(go.Scattergl(x=datetime, y=acali.precip_signal,   line_color="green", name="precip", mode="lines", yaxis='y2'))
    fig.add_trace(go.Scattergl(x=datetime[s:e], y=acali.obs_seasonal[s:e],    line_color="blue", name="obs", mode="lines", yaxis='y1'))
    fig.add_trace(go.Scattergl(x=datetime[s:e], y=sim_seasonal[s:e],          line_color="red", name="sim", mode="lines", yaxis='y1'))
    fig.update_layout(
        title="Seasonal Response",
        xaxis=dict(title="Date Time",
                showgrid=True,
                fixedrange=True),
        yaxis=dict(title='Flow [MGD]',
                    side='left',
                    fixedrange=False),
        # yaxis2=dict(title='Flow [cfs]',
        #             side='right',
        #             showgrid=False,
        #             fixedrange=True,
        #             autorange="reversed"),
        template="plotly_dark",
        hovermode='x unified', 
        dragmode='pan'
    )
    st.plotly_chart(fig, config={'scrollZoom': True}, use_container_width=True)


    #############################3
    # combine
    fig = go.Figure()
    # fig.add_trace(go.Scattergl(x=datetime, y=acali.precip_signal,                                           line_color="green", name="precip", mode="lines", yaxis='y2'))
    fig.add_trace(go.Scattergl(x=datetime[s:e], y=acaliT.sim_rdii[s:e],                                                     line_color="green", name="observed", mode="lines", yaxis='y1'))
    fig.add_trace(go.Scattergl(x=datetime[s:e], y=(acali.obs_fast_flow+acali.obs_slow_flow+acali.obs_seasonal)[s:e],    line_color="blue", name="observed", mode="lines", yaxis='y1'))
    fig.add_trace(go.Scattergl(x=datetime[s:e], y=(sim_fast+sim_slow+sim_seasonal)[s:e],                          line_color="red", name="simulated", mode="lines", yaxis='y1'))

    fig.update_layout(
        title="combine Response",
        xaxis_title="Date Time",
        xaxis_showgrid=True,
        yaxis=dict(title='Flow [MGD]',
                    side='left',
                    fixedrange=True),
        # yaxis2=dict(title='Flow [cfs]',
        #             side='right',
        #             showgrid=False,
        #             fixedrange=True,
        #             autorange="reversed"),
        template="plotly_dark",
        hovermode='x unified', 
        dragmode='pan'
    )
    st.plotly_chart(fig, config={'scrollZoom': True}, use_container_width=True)


    #############################3
    # Onetoone
    fig = go.Figure()
    # fig.add_trace(go.Scattergl(x=datetime, y=acali.precip_signal,                                           line_color="green", name="precip", mode="lines", yaxis='y2'))
    fig.add_trace(go.Scattergl(x=(acali.obs_fast_flow+acali.obs_slow_flow+acali.obs_seasonal)[s:e], y=acaliT.sim_rdii[s:e],                    line_color="blue", name="observed", mode="markers", yaxis='y1'))
    fig.add_trace(go.Scattergl(x=(acali.obs_fast_flow+acali.obs_slow_flow+acali.obs_seasonal)[s:e], y=(sim_fast+sim_slow+sim_seasonal)[s:e],   line_color="green", name="observed", mode="markers", yaxis='y1'))

    fig.update_layout(
        title="combine Response",
        xaxis_title="Date Time",
        xaxis_showgrid=True,
        yaxis=dict(title='Flow [MGD]',
                    side='left'),
        # yaxis2=dict(title='Flow [cfs]',
        #             side='right',
        #             showgrid=False,
        #             fixedrange=True,
        #             autorange="reversed"),
        template="plotly_dark",
        dragmode='pan'
    )
    st.plotly_chart(fig, config={'scrollZoom': True}, use_container_width=True)

    ####################
    # Event OTO
    obs_rdii = (acali.obs_fast_flow+acali.obs_slow_flow+acali.obs_seasonal)
    sim_rdii = (sim_fast+sim_slow+sim_seasonal)
    simT_rdii = acaliT.sim_rdii

    obs_events = []
    sim_events = []
    simT_events = []

    for start, end in events:
        mask = (datetime >= start) & (datetime <= end)
        obs_events.append(obs_rdii[mask].sum())
        sim_events.append(sim_rdii[mask].sum())
        simT_events.append(simT_rdii[mask].sum())

    obs_events = np.array(obs_events)
    sim_events = np.array(sim_events)
    simT_events = np.array(simT_events)


    fig = go.Figure()
    # fig.add_trace(go.Scattergl(x=datetime, y=acali.precip_signal,                                           line_color="green", name="precip", mode="lines", yaxis='y2'))
    fig.add_trace(go.Scattergl(x=obs_events, y=sim_events, line_color="blue", name="observed", mode="markers", marker_size=20, yaxis='y1'))
    fig.add_trace(go.Scattergl(x=obs_events, y=simT_events, line_color="red", name="observed", mode="markers", marker_size=20, yaxis='y1'))


    m1, b1 = np.polyfit(obs_events, sim_events, 1)   # slope, intercept
    fig.add_trace(go.Scattergl(x=[0,max(obs_events)], y=[b1, m1*max(obs_events)+b1], line_color="blue", name="observed", mode="lines", yaxis='y1'))
    st.write("m1:",m1,", b1:",b1)
    m2, b2 = np.polyfit(obs_events, simT_events, 1)   # slope, intercept
    fig.add_trace(go.Scattergl(x=[0,max(obs_events)], y=[b2, m2*max(obs_events)+b2], line_color="red", name="observed", mode="lines", yaxis='y1'))
    st.write("m2:",m2,", b2:",b2)

    fig.add_trace(go.Scattergl(x=[0,max(obs_events)], y=[0, max(obs_events)], line_color="black", line_dash="dash", name="observed", mode="lines", yaxis='y1'))


    fig.update_layout(
        width=400, height=1000,
        title="combine Response",
        xaxis_title="Date Time",
        xaxis_showgrid=True,
        yaxis=dict(title='Flow [MGD]',
                    side='left'),
        template="plotly_dark",
        dragmode='pan'
    )
    st.plotly_chart(fig, config={'scrollZoom': True})


    ####################
    # peak vol oto
    obs_rdii = (acali.obs_fast_flow+acali.obs_slow_flow+acali.obs_seasonal)
    sim_rdii = (sim_fast+sim_slow+sim_seasonal)
    simT_rdii = acaliT.sim_rdii

    obs_top20 = []
    sim_top20 = []
    simT_top20 = []

    for start, end in events:
        mask = (datetime >= start) & (datetime <= end)
        obs_top20.append(max(obs_rdii[mask]))
        sim_top20.append(max(sim_rdii[mask]))
        simT_top20.append(max(simT_rdii[mask]))

    obs_top20 = np.array(obs_top20)
    sim_top20 = np.array(sim_top20)
    simT_top20 = np.array(simT_top20)

    fig = go.Figure()
    # fig.add_trace(go.Scattergl(x=datetime, y=acali.precip_signal,                                           line_color="green", name="precip", mode="lines", yaxis='y2'))
    fig.add_trace(go.Scattergl(x=obs_top20, y=sim_top20, line_color="blue", name="observed", mode="markers", marker_size=20, yaxis='y1'))
    fig.add_trace(go.Scattergl(x=obs_top20, y=simT_top20, line_color="red", name="observed", mode="markers", marker_size=20, yaxis='y1'))


    m1, b1 = np.polyfit(obs_top20, sim_top20, 1)   # slope, intercept
    fig.add_trace(go.Scattergl(x=[0,max(obs_top20)], y=[b1, m1*max(obs_top20)+b1], line_color="blue", name="observed", mode="lines", yaxis='y1'))
    st.write("m1:",m1,", b1:",b1)
    m2, b2 = np.polyfit(obs_top20, simT_top20, 1)   # slope, intercept
    fig.add_trace(go.Scattergl(x=[0,max(obs_top20)], y=[b2, m2*max(obs_top20)+b2], line_color="red", name="observed", mode="lines", yaxis='y1'))
    st.write("m2:",m2,", b2:",b2)

    fig.add_trace(go.Scattergl(x=[0,max(obs_top20)], y=[0, max(obs_top20)], line_dash="dash",line_color="black", name="observed", mode="lines", yaxis='y1'))


    fig.update_layout(
        width=400, height=1000,
        title="combine Response",
        xaxis_title="Date Time",
        xaxis_showgrid=True,
        yaxis=dict(title='Flow [MGD]',
                    side='left'),
        template="plotly_dark",
        dragmode='pan'
    )
    st.plotly_chart(fig, config={'scrollZoom': True}, use_container_width=True)






    st.button("reset")

    print(acaliT.sim_rdii)


    st.write("Trad",(((acali.obs_fast_flow+acali.obs_slow_flow+acali.obs_seasonal)[s:e] - acaliT.sim_rdii[s:e])**2).sum())
    st.write("new", (((acali.obs_fast_flow+acali.obs_slow_flow+acali.obs_seasonal)[s:e] - (sim_fast+sim_slow+sim_seasonal)[s:e])**2).sum())


if st.session_state.page == "poster":
    poster_cols = st.columns([6,1])
    with poster_cols[0]:
        with st.container(border=True, width="stretch"):
            st.image("graphics/ICWMM_poster.png", width="stretch")
    with poster_cols[1]:
        with open("graphics/ICWMM_poster.pdf", "rb") as f:
            file_bytes = f.read()
        st.download_button("📥Download as PDF", data=file_bytes, file_name="Wachi_ICWMM2026_Poster.pdf")



if st.session_state.page == "authors":
    with st.container():
        gonwa_cols = st.columns([1,6])
        with gonwa_cols[0]:
            st.image("graphics/gonwa.jpg")
        with gonwa_cols[1]:
            st.header("Dr. William Gonwa P.E., Milwaukee School of Engineering.")
            st.write("Professor and Program Director for Civil Engineering.")
            st.write("Civil and Architectural Engineering and Construction Management.")
            st.write("Campus Center CC-27")
            st.write("+1(414)277-7320, gonwa@msoe.edu")
            st.markdown(
                '<a href="https://www.msoe.edu/directory/profile/william.gonwa/" target="_blank">Faculty Resume</a>',
                unsafe_allow_html=True
            )
    with st.container():
        wachi_cols = st.columns([1,6])
        with wachi_cols[0]:
            st.image("graphics/wachi.jpg")
        with wachi_cols[1]:
            st.header("Cocoro Wachi Undergraduate, Milwaukee School of Engineering.")
            st.write("B.S. Computer Science Major, Mathematics Minor, UX Design Minor.")
            st.write("Dwight & Dian Diercks School of Advanced Computing.")
            st.write("+1(224)345-1255, wachic@msoe.edu")
            with open("graphics/wachi_resume.pdf", "rb") as f:
                pdf_bytes = f.read()
            st.download_button("📥Download Resume", data=pdf_bytes, file_name="Cocoro Wachi Resume.pdf")
    st.write("---")
    with st.container():
        st.header("Acknowledgement")
        st.write("This undergraduate research and presentation at ICWMM2026 was made possible by the support of:")
        st.write("- Dwight & Dian Diercks School of Advanced Computing")
        st.write("- Civil and Architectural Engineering & Construction Management Department")
        st.write("of Milwaukee School of Engineering.")
