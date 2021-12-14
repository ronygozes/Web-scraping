from configs import clean_data_config


def split_magnitude(df):
    """
    The function receives a dataframe as an argument,
    performs split of column magnitude to two separate columns - value and units.
    The function returns new dataframe.
    """
    df[['magnitude', 'magnitude_units']] = df['Magnitude'].str.split(' ', expand=True)
    df = df.drop('Magnitude', axis=clean_data_config.COLS)

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


def latitude(loc):
    """
    The function receives latitude details with degree ('°') and S/N sign, removes degrees sign, N/S sign and
    adds minus ("-") sign for latitude located in South. This will enable use this  parameter as float number.
    returns data with digits and decimal point only.
    """
    return '-' + loc[:clean_data_config.TWO_LAST_MEMBERS] if loc[clean_data_config.LAST_MEMBER] == 'S' \
        else loc[:clean_data_config.TWO_LAST_MEMBERS]


def longitude(loc):
    """
    The function receives longitude details with degree ('°') and W/E sign, removes degrees sign, E/W sign and
    adds minus ("-") sign for longitude located in West. This will enable use this  parameter as float number.
    Returns data with digits and decimal point only.
    """
    return '-' + loc[:clean_data_config.TWO_LAST_MEMBERS] if loc[clean_data_config.LAST_MEMBER] == 'W' \
        else loc[:clean_data_config.TWO_LAST_MEMBERS]


def remove_units_from_values(df_event_mod):
    """
    The function receive dataframe as argument and performs removal of units from values.
    The function returns updated dataframe.
    """
    df_event_mod['event_key'] = df_event_mod['catalog'].str.split(' ').str[2]
    col_list = ['location_uncertainty_km', 'depth_km', 'travel_time_residual_sec', 'minimum_distance_km',
                'contributor', 'catalog']
    for col in col_list:
        df_event_mod[col] = df_event_mod[col].str.split(' ').str[0]

    df_event_mod['azimuthal_gap_deg'] = df_event_mod['azimuthal_gap_deg'].str.replace('°', '')
    df_event_mod[['location_latitude', 'location_longitude']] = df_event_mod['location'].str.split('  ', expand=True)
    df_event_mod.drop('location', axis=1, inplace=True)
    df_event_mod['location_latitude'] = df_event_mod['location_latitude'].apply(latitude)
    df_event_mod['location_longitude'] = df_event_mod['location_longitude'].apply(longitude)
    df_event_mod['fe_region'] = df_event_mod['fe_region'].str.replace('\'', '')
    df_event_mod = df_event_mod.drop(['url', 'Location Source', 'Magnitude Source'], axis=clean_data_config.COLS)
    cols = df_event_mod.columns.tolist()
    cols = cols[clean_data_config.LAST_MEMBER:] + cols[:clean_data_config.LAST_MEMBER]
    df_event_mod = df_event_mod[cols]

    return df_event_mod


def clean_dataframe(dataframe):
    """
    The function receives dataframe as argument and calls different functions to perform data cleaning and labeling.
    The function returns new dataframe.
    """
    event_dataframe = split_magnitude(dataframe)
    updated_df = rename_column(event_dataframe)
    df_event_mod = remove_units_from_values(updated_df)

    return df_event_mod

