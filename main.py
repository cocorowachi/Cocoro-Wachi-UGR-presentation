import streamlit as st
import numpy as np
from Data import Data
from Autocalibrate import Autocalibrate
import plotly.graph_objects as go

st.set_page_config(
    page_title="MSOE Wachi Sewer Dashboard",
    page_icon="graphics/msoe_icon.png",
    layout="wide"
)

if "_init_" not in st.session_state:
    st.session_state._init_ = False
    st.session_state.page = "dashboard"
# Header
title_cols = st.columns([1,10])
with title_cols[0]:
    st.image("graphics/msoe_logo.png", width=100)
with title_cols[1]:
    st.header("Breaking Apart Wet Weather Flow Signals Allows Streamlined Auto-calibration of Sewer Hydrology Models")
    st.write("Dr. William Gonwa P.E., Cocoro Wachi Undergraduate")
topbutton_cols = st.columns([2,2,2])
with topbutton_cols[0]:
    if st.button("Dashboard", type="primary" if st.session_state.page == "dashboard" else "secondary", disabled=not st.session_state._init_, width="stretch"):
        st.session_state.page = "dashboard"
        st.rerun()
with topbutton_cols[1]:
    if st.button("Poster", type="primary" if st.session_state.page == "poster" else "secondary", disabled=not st.session_state._init_, width="stretch"):
        st.session_state.page = "poster"
        st.rerun()
with topbutton_cols[2]:
    if st.button("Authors/About the Project", type="primary" if st.session_state.page == "authors" else "secondary", disabled=not st.session_state._init_, width="stretch"):
        st.session_state.page = "authors"
        st.rerun()
st.write("---")
if not st.session_state._init_:
    path = "Data/"
    temp = "Temperature.csv"
    sewer = "MMSD Sewer Flow Data.csv"
    precip = "MMSD Precipitation Raw Data.csv"

    temperature_df = Data(path + temp)
    sewer_df = Data(path + sewer)
    precip_df = Data(path + precip)
    st.session_state.acali = Autocalibrate(np.datetime64("2015-06-01T00:00"), np.datetime64("2020-01-31T23:00"), 64, sewer_df.read('MS0208 FlowMGD'), temperature_df.read("Temperature (F)"), precip_df.read("WS1201 Precip HourlyInches"))
    with st.spinner("Initializing Model"):
        st.session_state.acali.optimize()
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
datetime, diurnal, sim_fast, sim_slow, sim_seasonal = acali.get_sim_flow()
s, e = 11200, 26700
# datetime = datetime[s:e]

plot_config = {
    'displayModeBar': True,
    'scrollZoom': True
}
if st.session_state.page == "dashboard":
    with st.container():
            
        ######################################
        # obs disagg 
        fig = go.Figure()
        # fig.add_trace(go.Scattergl(x=datetime, y=acali.precip_signal,                                                       name="precip", mode="lines", yaxis='y2'))
        fig.add_trace(go.Scattergl(x=datetime[s:e], y=(acali.obs_fast_flow+acali.obs_slow_flow+acali.obs_seasonal)[s:e],                line_color="blue", name="Seasonal+Slow+Fast Flow", mode="lines", yaxis='y1'))
        fig.add_trace(go.Scattergl(x=datetime[s:e], y=(acali.obs_slow_flow+acali.obs_seasonal)[s:e],                                    line_color="red", name="Seasonal+Slow Flow", mode="lines", yaxis='y1'))
        fig.add_trace(go.Scattergl(x=datetime[s:e], y=acali.obs_seasonal[s:e],                                                          line_color="green", name="Seasonal Flow", mode="lines", yaxis='y1'))
        # fig.add_trace(go.Scattergl(x=datetime[s:e], y=(acali.diurnal+acali.obs_fast_flow+acali.obs_slow_flow+acali.obs_seasonal)[s:e],  name="diurnal", mode="lines", yaxis='y1'))
        fig.update_layout(
            title="Disaggregated Signal (Diurnal Excluded)",
            xaxis=dict(title="Date Time",
                    showgrid=True,
                    fixedrange=False),
            yaxis=dict(title='Flow [MGD]',
                        side='left',
                        showgrid=True,
                        fixedrange=True),
            template="plotly_dark",
            hovermode='x unified', 
            dragmode='pan'
        )
        fig.update_yaxes(range=[-0.5, 4])
        st.plotly_chart(fig, config={'scrollZoom': True}, use_container_width=True)
        st.write("steps of disaggregation, put excel file here as well")
    with st.container():
            
        ########################################
        # model fast
        fig = go.Figure()
        # fig.add_trace(go.Scattergl(x=datetime[2:], y=acali.precip_signal[2:],   line_color="green", name="precip", mode="lines", yaxis='y2'))
        fig.add_trace(go.Scattergl(x=datetime[s:e], y=acali.obs_fast_flow[s:e],   line_color="blue", name="Observed Fast Flow", mode="lines", yaxis='y1'))
        fig.add_trace(go.Scattergl(x=datetime[s:e], y=sim_fast[s:e],              line_color="red", name="Simulated Fast Flow", mode="lines", yaxis='y1'))
        fig.update_layout(
            title="Fast Response Observed and Simulated Signal",
            xaxis=dict(title="Date Time",
                    showgrid=True,
                    fixedrange=False),
            yaxis=dict(title='Flow [MGD]',
                        side='left',
                        fixedrange=True),
            template="plotly_dark",
            hovermode='x unified', 
            dragmode='pan'
        )
        fig.update_yaxes(range=[-0.5, 4])
        st.plotly_chart(fig, config={'scrollZoom': True}, use_container_width=True)

    with st.container():
        ###############################
        # Model slow
        fig = go.Figure()
        # fig.add_trace(go.Scattergl(x=datetime, y=acali.precip_signal,   line_color="green", name="precip", mode="lines", yaxis='y2'))
        fig.add_trace(go.Scattergl(x=datetime[s:e], y=acali.obs_slow_flow[s:e],   line_color="blue", name="Observed Slow Flow", mode="lines", yaxis='y1'))
        fig.add_trace(go.Scattergl(x=datetime[s:e], y=sim_slow[s:e],              line_color="red", name="Simulated Slow Flow", mode="lines", yaxis='y1'))
        fig.update_layout(
            title="Slow Response Observed and Simulated Signal",
            xaxis=dict(title="Date Time",
                    showgrid=True,
                    fixedrange=False),
            yaxis=dict(title='Flow [MGD]',
                        side='left',
                        fixedrange=True),
            template="plotly_dark",
            hovermode='x unified', 
            dragmode='pan'
        )
        fig.update_yaxes(range=[-0.5, 4])
        st.plotly_chart(fig, config={'scrollZoom': True}, use_container_width=True)

    with st.container():
        ##############################
        # model seasonal
        fig = go.Figure()
        # fig.add_trace(go.Scattergl(x=datetime, y=acali.precip_signal,   line_color="green", name="precip", mode="lines", yaxis='y2'))
        fig.add_trace(go.Scattergl(x=datetime[s:e], y=acali.obs_seasonal[s:e],    line_color="blue", name="Observed Seasonal Flow", mode="lines", yaxis='y1'))
        fig.add_trace(go.Scattergl(x=datetime[s:e], y=sim_seasonal[s:e],          line_color="red", name="Simulated Seasonal Flow", mode="lines", yaxis='y1'))
        fig.update_layout(
            title="Seasonal Response Observed and Simulated Signal",
            xaxis=dict(title="Date Time",
                    showgrid=True,
                    fixedrange=False),
            yaxis=dict(title='Flow [MGD]',
                        side='left',
                        fixedrange=True),
            template="plotly_dark",
            hovermode='x unified', 
            dragmode='pan'
        )
        fig.update_yaxes(range=[-0.5, 4])
        st.plotly_chart(fig, config={'scrollZoom': True}, use_container_width=True)

    with st.container():
            
        #############################3
        # combine
        fig = go.Figure()
        # fig.add_trace(go.Scattergl(x=datetime, y=acali.precip_signal,                                           line_color="green", name="precip", mode="lines", yaxis='y2'))
        fig.add_trace(go.Scattergl(x=datetime[s:e], y=acali.sim_rdii[s:e],                                                     line_color="green", name="observed", mode="lines", yaxis='y1'))
        fig.add_trace(go.Scattergl(x=datetime[s:e], y=(acali.obs_fast_flow+acali.obs_slow_flow+acali.obs_seasonal)[s:e],    line_color="blue", name="Observed Flow", mode="lines", yaxis='y1'))
        fig.add_trace(go.Scattergl(x=datetime[s:e], y=(sim_fast+sim_slow+sim_seasonal)[s:e],                          line_color="red", name="Simulated Flow", mode="lines", yaxis='y1'))

        fig.update_layout(
            title="Aggregate Observed and Simulated Signal",
            xaxis_title="Date Time",
            xaxis_showgrid=True,
            yaxis=dict(title='Flow [MGD]',
                        side='left',
                        fixedrange=True),
            hovermode='x unified', 
            dragmode='pan'
        )
        
        fig.update_yaxes(range=[-0.5, 4])
        st.plotly_chart(fig, config={'scrollZoom': True}, use_container_width=True)

    ####################
    # Event OTO
    obs_rdii = (acali.obs_fast_flow+acali.obs_slow_flow+acali.obs_seasonal)
    sim_rdii = (sim_fast+sim_slow+sim_seasonal)
    simT_rdii = acali.sim_rdii

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
    fig.add_trace(go.Scattergl(x=obs_events, y=sim_events, line_color="blue", name="observed", mode="markers", marker_size=10, yaxis='y1'))
    fig.add_trace(go.Scattergl(x=obs_events, y=simT_events, line_color="red", name="observed", mode="markers", marker_size=10, yaxis='y1'))


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
    obs_rdii = (acali.obs_rdii)
    sim_rdii = (sim_fast+sim_slow+sim_seasonal)
    simT_rdii = acali.sim_rdii

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
    # fig.add_trace(go.Scattergl(x=datetime, y=acali.precip_signal, line_color="green", name="precip", mode="lines", yaxis='y2'))
    fig.add_trace(go.Scattergl(x=obs_top20, y=sim_top20, line_color="blue", name="observed", mode="markers", marker_size=10, yaxis='y1'))
    fig.add_trace(go.Scattergl(x=obs_top20, y=simT_top20, line_color="red", name="observed", mode="markers", marker_size=10, yaxis='y1'))


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
            st.image("graphics/wachi.JPG")
        with wachi_cols[1]:
            st.header("Cocoro Wachi Undergraduate, Milwaukee School of Engineering.")
            st.write("B.S. Computer Science Major, Mathematics Minor, UX Design Minor.")
            st.write("Dwight & Dian Diercks School of Advanced Computing.")
            st.write("+1(224)345-1255, wachic@msoe.edu")
            with open("graphics/wachi_resume.pdf", "rb") as f:
                pdf_bytes = f.read()
            st.download_button("Download Resume", data=pdf_bytes, file_name="Cocoro Wachi Resume.pdf")
    st.write("---")
    with st.container():
        st.header("Acknowledgement")
        st.write("This undergraduate research and presentation at ICWMM2026 was made possible by the support of:")
        st.write("- Dwight & Dian Diercks School of Advanced Computing")
        st.write("- Civil and Architectural Engineering & Construction Management Department")
        # st.write("of Milwaukee School of Engineering.")
        st.markdown(
            'of <a href="https://www.msoe.edu/" target="_blank">Milwaukee School of Engineering</a>',
            unsafe_allow_html=True
        )
    # used for export data for dr gonwa for excel useage
    # import pandas as pd
    # df = pd.DataFrame({
    #     "datetime": acali.datetime,
    #     "MS0208 Total Flow MGD": acali.target_flow
    # })
    # df.to_csv("hourly_MS0208_total.csv", index=False)

    # df = pd.DataFrame({
    #     "datetime": acali.datetime,
    #     "MS0208 RDII Flow MGD": acali.target_flow - acali.diurnal
    # })
    # df.to_csv("hourly_MS0208_rdii.csv", index=False)

    # x = acali.datetime
    # y = acali.target_flow
    # n_days = x.shape[0] // 24
    # x_daily = x[:n_days * 24].reshape(n_days, 24)[:, 0]
    # y_daily = y[:n_days * 24].reshape(n_days, 24)[:, 0]
    # df = pd.DataFrame({
    #     "datetime": x_daily,
    #     "MS0208 Total Flow MGD": y_daily
    # })
    # df.to_csv("daily_MS0208_total.csv", index=False)

    # x = acali.datetime
    # y = acali.target_flow - acali.diurnal
    # n_days = x.shape[0] // 24
    # x_daily = x[:n_days * 24].reshape(n_days, 24)[:, 0]
    # y_daily = y[:n_days * 24].reshape(n_days, 24)[:, 0]
    # df = pd.DataFrame({
    #     "datetime": x_daily,
    #     "MS0208 Total Flow MGD": y_daily
    # })
    # df.to_csv("daily_MS0208_rdii.csv", index=False)
