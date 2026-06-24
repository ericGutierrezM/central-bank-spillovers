import pandas as pd

'''
For the first regression, we only need the controls for the
time periods with a meeting.
'''

# List of the continuous variables that need standardization
cols_to_standardize = ['unemployment', 'inflation', 'rate_change', 'vix', 'bond_yields']

# Function to apply Z-score standardization
def standardize_controls(df, cols):
    df_standardized = df.copy()
    for col in cols:
        df_standardized[col] = (df[col] - df[col].mean()) / df[col].std()
    return df_standardized

# ======= FED ======= #

fed = pd.read_csv('output/causal-machinery/aggregated/fed_gemini25flash.csv')
fed_dates = fed['date'].sort_values(ascending=True)

unemploy_fed = pd.read_csv('data/controls/us_unemployment_vintages.csv')
unemploy_fixed_fed = []

inflation_fed = pd.read_csv('data/controls/us_cpi_vintages.csv')
inflation_fixed_fed = []

rate_fed = pd.read_csv('data/controls/fed_rate_vintages.csv')
rate_fixed_fed = []

vix = pd.read_csv('data/controls/vix_daily.csv').reset_index(drop=False)
vix_fixed_fed = []

yield_us = pd.read_csv('data/controls/us_yield.csv').reset_index(drop=False)
yield_fixed_us = []

governor_fed = []


for date in fed_dates:
    # Unemployment (from latest available data)
    valid_dates_unemploy = unemploy_fed[unemploy_fed['Initial_Release_Date']<date]
    unemploy_fixed_fed.append(valid_dates_unemploy.sort_values(by='Initial_Release_Date', ascending=False).iloc[0]['Initial_Value'])

    # Inflation (from latest available data)
    valid_dates_inflation = inflation_fed[inflation_fed['Initial_Release_Date']<date]
    inflation_fixed_fed.append(valid_dates_inflation.sort_values(by='Initial_Release_Date', ascending=False).iloc[0]['Initial_Value'])

    # Rate changes
    valid_dates_rate = rate_fed[rate_fed['Initial_Release_Date']==date]
    if(len(valid_dates_rate)!=0):
        if(len(valid_dates_rate)>1):
            rate = max(valid_dates_rate.sort_values(by='Initial_Release_Date', ascending=False)['Initial_Value'].to_list())
        elif(len(valid_dates_rate)==1):
            rate = valid_dates_rate['Initial_Value'].to_list()[0]
    else:
        rate = None
    rate_fixed_fed.append(rate)

    # VIX (from the previous day)
    valid_dates_vix = vix[vix['Date']<date]
    vix_fixed_fed.append(valid_dates_vix.sort_values(by='Date', ascending=False).iloc[0]['VIX'])

    # US Bond Yields
    valid_dates_yields = yield_us[yield_us['Observation_Month']<date]
    yield_fixed_us.append(valid_dates_yields.sort_values(by='Observation_Month', ascending=False).iloc[0]['Value'])

    # Governor dummy
    if(date<'2018-02-04'):
        gov = 'Yellen'
    else:
        gov = 'Powell'
    governor_fed.append(gov)



# Fill NaN and Compute Rate Change
rate_fixed_fed = pd.Series(rate_fixed_fed).ffill()
rate_fixed_fed = (rate_fixed_fed-rate_fixed_fed.shift(1)).to_numpy().copy()

# Manually set the first rate change to 0 
# (it is the case for all three banks)
rate_fixed_fed[0] = 0

fed_controls = pd.DataFrame({
    "date": fed_dates,
    "unemployment": unemploy_fixed_fed,
    "inflation": inflation_fixed_fed,
    "rate_change": rate_fixed_fed,
    "vix": vix_fixed_fed,
    "bond_yields": yield_fixed_us,
    'governor': governor_fed
})

fed_controls_std = standardize_controls(fed_controls, cols_to_standardize)
fed_controls_std.to_csv('data/controls/FED_CONTROLS.csv')


# ======= ECB ======= #

# Get Fed dates
ecb = pd.read_csv('output/causal-machinery/aggregated/ecb_gemini25flash.csv')
ecb_dates = ecb['date'].sort_values(ascending=True)

unemploy_ecb = pd.read_csv('data/controls/unemployment_eur.csv')
unemploy_ecb = unemploy_ecb[unemploy_ecb['geo']=='EA21']
unemploy_ecb = unemploy_ecb[['TIME_PERIOD', 'OBS_VALUE']]
unemploy_ecb['TIME_PERIOD'] = pd.to_datetime(unemploy_ecb['TIME_PERIOD'])
unemploy_fixed_ecb = []

inflation_ecb = pd.read_csv('data/controls/inflation_eur.csv')
inflation_ecb = inflation_ecb[inflation_ecb['geo']=='EA21']
inflation_ecb = inflation_ecb[['TIME_PERIOD', 'OBS_VALUE']]
inflation_ecb['TIME_PERIOD'] = pd.to_datetime(inflation_ecb['TIME_PERIOD'])
inflation_fixed_ecb = []

rate_ecb = pd.read_csv('data/controls/ecb_rate_vintages.csv')
rate_fixed_ecb = []

vix_fixed_ecb= []

yield_de = pd.read_csv('data/controls/de_yield.csv').reset_index(drop=False)
yield_fixed_de = []

governor_ecb = []


for date in ecb_dates:
    # Unemployment (from latest available data)
    valid_dates_unemploy = unemploy_ecb[(unemploy_ecb['TIME_PERIOD']<date) & (unemploy_ecb['TIME_PERIOD'].dt.month != pd.to_datetime(date))]
    unemploy_fixed_ecb.append(valid_dates_unemploy.sort_values(by='TIME_PERIOD', ascending=False).iloc[0]['OBS_VALUE'])

    # Inflation (from latest available data)
    valid_dates_inflation = inflation_ecb[inflation_ecb['TIME_PERIOD']<date]
    inflation_fixed_ecb.append(valid_dates_inflation.sort_values(by='TIME_PERIOD', ascending=False).iloc[0]['OBS_VALUE'])

    # Rate changes
    valid_dates_rate = rate_ecb[rate_ecb['Initial_Release_Date']==date]
    if(len(valid_dates_rate)!=0):
        if(len(valid_dates_rate)>1):
            rate = max(valid_dates_rate.sort_values(by='Initial_Release_Date', ascending=False)['Initial_Value'].to_list())
        elif(len(valid_dates_rate)==1):
            rate = valid_dates_rate['Initial_Value'].to_list()[0]
    else:
        rate = None
    rate_fixed_ecb.append(rate)

    # VIX (from the previous day)
    valid_dates_vix = vix[vix['Date']<date]
    vix_fixed_ecb.append(valid_dates_vix.sort_values(by='Date', ascending=False).iloc[0]['VIX'])

    # US Bond Yields
    valid_dates_yields = yield_de[yield_de['Observation_Month']<date]
    yield_fixed_de.append(valid_dates_yields.sort_values(by='Observation_Month', ascending=False).iloc[0]['Value'])

    # Governor dummy
    if(date<'2019-10-31'):
        gov = 'Draghi'
    else:
        gov = 'Lagarde'
    governor_ecb.append(gov)


# Fill NaN and Compute Rate Change
rate_fixed_ecb = pd.Series(rate_fixed_ecb).ffill()
rate_fixed_ecb = (rate_fixed_ecb-rate_fixed_ecb.shift(1)).to_numpy().copy()

# Manually set the first rate change to 0 
# (it is the case for all three banks)
rate_fixed_ecb[0] = 0

ecb_controls = pd.DataFrame({
    "date": ecb_dates,
    "unemployment": unemploy_fixed_ecb,
    "inflation": inflation_fixed_ecb,
    "rate_change": rate_fixed_ecb,
    "vix": vix_fixed_ecb,
    "bond_yields": yield_fixed_de,
    'governor': governor_ecb
})

ecb_controls_std = standardize_controls(ecb_controls, cols_to_standardize)
ecb_controls_std.to_csv('data/controls/ECB_CONTROLS.csv')


# ======= BoE ======= #

boe = pd.read_csv('output/causal-machinery/aggregated/boe_gemini25flash.csv')
boe_dates = boe['date'].sort_values(ascending=True)

unemploy_boe = pd.read_csv('data/controls/uk_unemployment_vintages.csv')
unemploy_fixed_boe = []

inflation_boe = pd.read_csv('data/controls/uk_cpi_vintages.csv')
inflation_fixed_boe = []

rate_boe = pd.read_csv('data/controls/boe_rate_vintages.csv')
rate_fixed_boe = []

vix_fixed_boe = []

yield_uk = pd.read_csv('data/controls/uk_yield.csv').reset_index(drop=False)
yield_fixed_uk = []

governor_boe = []


for date in boe_dates:
    # Unemployment (from latest available data)
    valid_dates_unemploy = unemploy_boe[unemploy_boe['Initial_Release_Date']<date]
    unemploy_fixed_boe.append(valid_dates_unemploy.sort_values(by='Initial_Release_Date', ascending=False).iloc[0]['Initial_Value'])

    # Inflation (from latest available data)
    valid_dates_inflation = inflation_boe[inflation_boe['Initial_Release_Date']<date]
    inflation_fixed_boe.append(valid_dates_inflation.sort_values(by='Initial_Release_Date', ascending=False).iloc[0]['Initial_Value'])

    # Rate changes
    valid_dates_rate = rate_boe[rate_boe['Initial_Release_Date']==date]
    if(len(valid_dates_rate)!=0):
        if(len(valid_dates_rate)>1):
            rate = max(valid_dates_rate.sort_values(by='Initial_Release_Date', ascending=False)['Initial_Value'].to_list())
        elif(len(valid_dates_rate)==1):
            rate = valid_dates_rate['Initial_Value'].to_list()[0]
    else:
        rate = None
    rate_fixed_boe.append(rate)

    # VIX (from the previous day)
    valid_dates_vix = vix[vix['Date']<date]
    vix_fixed_boe.append(valid_dates_vix.sort_values(by='Date', ascending=False).iloc[0]['VIX'])

    # US Bond Yields
    valid_dates_yields = yield_uk[yield_uk['Observation_Month']<date]
    yield_fixed_uk.append(valid_dates_yields.sort_values(by='Observation_Month', ascending=False).iloc[0]['Value'])

    # Governor dummy
    if(date<'2020-03-16'):
        gov = 'Carney'
    else:
        gov = 'Bailey'
    governor_boe.append(gov)



# Fill NaN and Compute Rate Change
rate_fixed_boe = pd.Series(rate_fixed_boe).ffill()
rate_fixed_boe = (rate_fixed_boe-rate_fixed_boe.shift(1)).to_numpy().copy()

# Manually set the first rate change to 0 
# (it is the case for all three banks)
rate_fixed_boe[0] = 0

boe_controls = pd.DataFrame({
    "date": boe_dates,
    "unemployment": unemploy_fixed_boe,
    "inflation": inflation_fixed_boe,
    "rate_change": rate_fixed_boe,
    "vix": vix_fixed_boe,
    "bond_yields": yield_fixed_uk,
    'governor': governor_boe
})

boe_controls_std = standardize_controls(boe_controls, cols_to_standardize)
boe_controls_std.to_csv('data/controls/BOE_CONTROLS.csv')

print("Done -- Controls harmonized for the Fed, ECB, and BoE.")