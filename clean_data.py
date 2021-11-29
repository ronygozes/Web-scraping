import pandas as pd

from configs import clean_data_config


def split_magnitude(df):
    """
    The function receives a dataframe as an argument,
    performs split of column magnitude to two separate columns - value and units.
    The function returns new dataframe.
    """
    df[['magnitude', 'magnitude_units']] = df['Magnitude'].str.split(' ', expand=True)
    df = df.drop('Magnitude', axis=1)

    return df


def rename_column(event_dataframe):
    """
    The function receives a dataframe as an argument,
    performs manual update of column names to fit column names in sql main table 'earthquakes_events'.
    The new names include also units where possible to remove units from the values
    The function returns new dataframe.
    """
    df_event_mod = event_dataframe.rename(columns=clean_data_config.COLUMNS)

    return df_event_mod


def remove_units_from_values(df_event_mod):
    """
    The function receive dataframe as argument and performs removal of units from values.
    The function returns updated dataframe.
    """
    df_event_mod['location_uncertainty_km'] = df_event_mod['location_uncertainty_km'].str.replace(' km', '')
    df_event_mod['depth_km'] = df_event_mod['depth_km'].str.replace(' km', '')
    df_event_mod['travel_time_residual_sec'] = df_event_mod['travel_time_residual_sec'].str.replace(' s', '')
    df_event_mod['azimuthal_gap_deg'] = df_event_mod['azimuthal_gap_deg'].str.replace('°', '')
    df_event_mod['minimum_distance_km'] = df_event_mod['minimum_distance_km'].str.replace(' km', '').str. \
        replace(' (.+)', '')
    df_event_mod = df_event_mod.drop(['url', 'Location Source', 'Magnitude Source'], axis=1)
    df_event_mod['contributor'] = df_event_mod['contributor'].str.replace(' 1', '')
    df_event_mod['event_key'] = df_event_mod['catalog'].str.split(' ').str[2]
    df_event_mod['catalog'] = df_event_mod['catalog'].str.split(' ').str[0]
    cols = df_event_mod.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df_event_mod = df_event_mod[cols]

    return df_event_mod


def convert_datatype(df_event_mod):
    """
    The function receive dataframe as argument and assigns datatype to numerical columns.
    The function returns updated dataframe.
    """
    df_event_mod['magnitude'] = df_event_mod['magnitude'].astype('float')
    df_event_mod['magnitude_uncertainty'] = df_event_mod['magnitude_uncertainty'].astype('float')
    df_event_mod['location_uncertainty_km'] = df_event_mod['location_uncertainty_km'].astype('float')
    df_event_mod['depth_km'] = round(pd.to_numeric(df_event_mod['depth_km'], errors='coerce'), 3)
    df_event_mod['depth_uncertainty_km'] = round(pd.to_numeric(df_event_mod['depth_uncertainty_km'],
                                                               errors='coerce'), 3)
    df_event_mod['travel_time_residual_sec'] = pd.to_numeric(df_event_mod['travel_time_residual_sec'],
                                                             errors='coerce')
    df_event_mod['num_of_stations'] = pd.to_numeric(df_event_mod['num_of_stations'], downcast='integer',
                                                    errors='coerce')
    df_event_mod['origin_time'] = pd.to_datetime(df_event_mod['origin_time'])
    df_event_mod['azimuthal_gap_deg'] = pd.to_numeric(df_event_mod['azimuthal_gap_deg'],
                                                      errors='coerce')
    df_event_mod['num_of_phases'] = pd.to_numeric(df_event_mod['num_of_phases'], downcast='integer',
                                                  errors='coerce')

    return df_event_mod


def clean_dataframe(dataframe):
    """
    The function receives dataframe as argument and calls different function to perform data cleaning and labeling.
    The function returns new dataframe.
    """
    event_dataframe = split_magnitude(dataframe)
    updated_df = rename_column(event_dataframe)
    updated_df1 = remove_units_from_values(updated_df)
    df_event_mod = convert_datatype(updated_df1)

    return df_event_mod
