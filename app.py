import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import streamlit as st
import utils

st.title("Анализ исторических и текущих данных температуры")


file_uploader = st.file_uploader("""Загрузите файл с расширением .csv,
                        содержащий колонки city, season, temperature""",
                        type=["csv"])

df = None
cities = []

if file_uploader:
    df = pd.read_csv(file_uploader)

    assert 'city' in df.columns
    assert 'season' in df.columns
    assert 'temperature' in df.columns
    cities = sorted(df['city'].unique())

city = st.selectbox("Выберите город", options=["Default"] + cities)
api_key = st.text_input("Введите OpenWeather API Key", type="password")

if df is not None and city != "Default":
    st.subheader(f"Анализ данных и статистика {city}")
    city_df = df[df['city'] == city]
    city_df = utils.single_city_data_analysis(city_df)

    mean_temperature = city_df['temperature'].mean()
    min_temperature = city_df['temperature'].min()
    max_temperature = city_df['temperature'].max()

    st.write(f"Средняя температура за все время: {mean_temperature:.2f}")
    st.write(f"Минимальная температура за все время: {min_temperature:.2f}")
    st.write(f"Максимальная температура за все время: {max_temperature:.2f}")

    st.subheader("Скользящее среднее температур за все время")
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(city_df[['timestamp', 'moving_average']].dropna().set_index('timestamp'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate(rotation=45)
    st.pyplot(fig)

    st.subheader("Сезонные профили")
    season_profiles = city_df.groupby('season').first().reset_index()[['season', 'mean', 'std']]
    st.dataframe(season_profiles.rename(columns={'mean': 'Средняя температура', 'std': 'Стандартное отклонение'}))

    st.subheader("Аномалии в температуре")

    fig, ax = plt.subplots(figsize=(12, 6))
    colors = ['red' if anomaly else 'blue' for anomaly in city_df['anomaly']]
    ax.scatter(city_df['timestamp'], city_df['temperature'], s=10, c=colors)
    ax.set_xlabel('Дата')
    ax.set_ylabel('Температура')
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate(rotation=45)
    red_patch = plt.Line2D([0], [0], color='red', marker='o', linestyle='', markersize=5, label='Аномалия')
    blue_patch = plt.Line2D([0], [0], color='blue', marker='o', linestyle='', markersize=5, label='Нормальная температура')
    ax.legend(handles=[red_patch, blue_patch])
    st.pyplot(fig)

    if api_key:
        st.subheader("Данные по текущей температуре из OpenWeather API")
        try:
            curr_temperature, curr_season = utils.curr_temperature_sync(api_key, city)

            curr_season_mean = city_df[city_df['season'] == curr_season]['mean'].iloc[0]
            curr_season_std = city_df[city_df['season'] == curr_season]['std'].iloc[0]  
            anomaly = curr_temperature < (curr_season_mean - 2 * curr_season_std) or curr_temperature > (curr_season_mean + 2 * curr_season_std)

            st.write(f"Текущяя температура согласно OpenWeather: {curr_temperature:.2f} °C")
            st.write(f"Текущий сезон: {curr_season}")
            st.write(f"Эта температура считается в этом сезоне {'**АНОМАЛИЕЙ**' if anomaly else '**НОРМАЛЬНОЙ**'}")

        except Exception as e:
            st.error(f"Ошибка при получении текущей температуры: {e}")
