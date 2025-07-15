import streamlit as st
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import numpy as np

    # 페이지 설정
    st.set_page_config(page_title="Exoplanet Explorer", layout="wide")

    # 데이터 로드
    @st.cache_data
    def load_data():
        try:
            df = pd.read_csv("data/exoplanets.csv")
            return df
        except FileNotFoundError:
            st.error("Data file 'data/exoplanets.csv' not found. Showing demo mode.")
            return pd.DataFrame()

    # 통과법 시뮬레이션 함수
    def simulate_transit(planet_radius, orbital_period, star_brightness):
        time = np.linspace(0, orbital_period, 100)
        brightness = np.ones_like(time) * star_brightness
        transit_duration = orbital_period * 0.1  # 통과 시간은 주기의 10%
        transit_start = orbital_period * 0.4
        transit_end = transit_start + transit_duration
        brightness[(time >= transit_start) & (time <= transit_end)] *= (1 - (planet_radius / 10) ** 2)
        return time, brightness

    # 메인 앱
    st.title("Exoplanet Explorer")
    st.markdown("Explore exoplanetary systems and simulate transit events with NASA Exoplanet Archive data.")

    # 사이드바: 사용자 입력
    st.sidebar.header("행성 매개변수 조정")
    planet_radius = st.sidebar.slider("행성 반지름 (지구 반지름 단위)", 0.5, 10.0, 2.0, step=0.1)
    orbital_radius = st.sidebar.slider("궤도 반경 (AU)", 0.01, 2.0, 0.1, step=0.01)
    orbital_period = st.sidebar.slider("궤도 주기 (일)", 1.0, 100.0, 10.0, step=0.1)
    star_brightness = st.sidebar.slider("항성 밝기 (상대값)", 0.8, 1.2, 1.0, step=0.01)
    selected_system = st.sidebar.selectbox("행성계 선택", ["All", "TRAPPIST-1", "Kepler-452", "Proxima Centauri"])

    # 데이터 로드
    df = load_data()
    if not df.empty:
        if selected_system != "All":
            system_data = df[df["pl_name"].str.contains(selected_system, na=False, case=False)]
        else:
            system_data = df
    else:
        system_data = pd.DataFrame()

    # 행성계 맵
    st.header("행성계 맵")
    st.markdown("선택한 행성계의 궤도를 시각화합니다. 슬라이더로 반지름과 궤도를 조정하세요.")
    fig_map = go.Figure()
    fig_map.add_trace(go.Scatter(
        x=[0], y=[0], mode="markers", marker=dict(size=20, color="yellow"), name="항성"
    ))
    if not system_data.empty:
        for _, row in system_data.iterrows():
            radius = row["pl_orbsmax"] if not pd.isna(row["pl_orbsmax"]) else orbital_radius
            angle = np.linspace(0, 2 * np.pi, 100)
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            fig_map.add_trace(go.Scatter(
                x=x, y=y, mode="lines", name=row["pl_name"], line=dict(color="blue")
            ))
            fig_map.add_trace(go.Scatter(
                x=[radius], y=[0], mode="markers", marker=dict(size=planet_radius * 5), name=f"{row['pl_name']} (조정됨)"
            ))
    else:
        angle = np.linspace(0, 2 * np.pi, 100)
        x = orbital_radius * np.cos(angle)
        y = orbital_radius * np.sin(angle)
        fig_map.add_trace(go.Scatter(
            x=x, y=y, mode="lines", name="샘플 행성", line=dict(color="blue")
        ))
        fig_map.add_trace(go.Scatter(
            x=[orbital_radius], y=[0], mode="markers", marker=dict(size=planet_radius * 5), name="샘플 행성"
        ))
    fig_map.update_layout(
        title="궤도 맵", xaxis_title="X (AU)", yaxis_title="Y (AU)",
        showlegend=True, width=600, height=600
    )
    st.plotly_chart(fig_map)

    # 통과법 시뮬레이션
    st.header("통과법 시뮬레이션")
    st.markdown("행성이 항성을 가릴 때 밝기 변화를 시뮬레이션합니다. 매개변수를 조정하여 변화를 확인하세요.")
    time, brightness = simulate_transit(planet_radius, orbital_period, star_brightness)
    fig_transit = go.Figure()
    fig_transit.add_trace(go.Scatter(
        x=time, y=brightness, mode="lines", name="밝기 곡선", line=dict(color="blue")
    ))
    fig_transit.update_layout(
        title="통과법 밝기 곡선", xaxis_title="시간 (일)", yaxis_title="상대 밝기",
        showlegend=True, width=600, height=400
    )
    st.plotly_chart(fig_transit)

    # 통계적 분포
    if not df.empty:
        st.header("외계 행성 통계")
        st.markdown("궤도 주기와 행성 반지름의 분포를 확인하세요.")
        fig_stats = px.scatter(
            system_data, x="pl_orbper", y="pl_rade", color="st_spectype",
            labels={"pl_orbper": "궤도 주기 (일)", "pl_rade": "행성 반지름 (지구 반지름 단위)"},
            title="외계 행성 분포"
        )
        st.plotly_chart(fig_stats)
