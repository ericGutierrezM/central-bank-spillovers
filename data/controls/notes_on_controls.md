# Notes on Controls

### Global Indices

### VIX
- Concern: it tracks volatility in the US market.
- Maybe we can consider using EconAI's EPU, or EUR and UK's specific indices: VSTOXX and VFTSE, respectively.

### Inflation
- Source: Federal Reserve Economic Data (FRED)
- European data for the Euro Area (19). In the time series, the UK left the EU but was never in the Euro Area, so no effect. However, Croatia joined in 2023. We have to double check, but I believe that the FRED mantians the EU19 throughout the time series, not including Croatia.
- FRED time series codes: CP0000USM086NEST, CPALTT01GBM659N, CP0000EZM086NEST.

### Unemployment
- Source: Federal Reserve Economic Data (FRED) for US and UK data, Eurostat for Euro Area data.
- European data is retreived both for EU27 and EA21 (Euro Area 19 + Croatia and Bulgaria). We are likely interested in EA21 for cohesiveness sake, but we must mention that EA19 and EA21 are not exactly the same. The European data from FRED was EA19, but the series stops at 2023.
- FRED time series codes: LRHUTTTTUSM156S, LRHUTTTTGBM156S.
- Eurostat time series code: une_rt_m.