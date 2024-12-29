import pandas as pd
import numpy as np
from functools import partial
from joblib import Parallel, delayed

def single_city_data_analysis(city_df):
    city_df = city_df.sort_values(by='timestamp')

    city_df['moving_average'] = list(city_df['temperature'].rolling(window=30).mean())
    season_profiles = city_df.groupby('season')['temperature'].agg(['mean', 'std']).reset_index()
    city_df = city_df.merge(season_profiles, on='season', how='left')

    city_df['anomaly'] = (city_df['temperature'] < (city_df['mean'] - 2 * city_df['std'])) | \
                              (city_df['temperature'] > (city_df['mean'] + 2 * city_df['std']))
    
    return city_df

def all_cities_data_analysis_sequential(df, cities):
    results = []
    for city in cities:
        city_df = df[df['city'] == city]
        city_df = single_city_data_analysis(city_df)
        results.append(city_df)
    return pd.concat(results)

def all_cities_data_analysis_parallel(df, cities):
    city_dfs = [df[df['city'] == city] for city in cities]
    results = Parallel(n_jobs=-1)(delayed(single_city_data_analysis)(city_df) for city_df in city_dfs)

    return pd.concat(results)
