import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Ensure output directory exists
os.makedirs('output/aggregated', exist_ok=True)

stance_folder = 'output/stance'

files_info = [(f.name[17:-4], f.path) for f in os.scandir(stance_folder) if f.is_file()]

# Hardcoded BoE dates
date_dict = {
    "201502": "20150212",
    "201505": "20150513",
    "201508": "20150806",
    "201511": "20151105",
    "201602": "20160204",
    "201605": "20160512",
    "201608": "20160804",
    "201611": "20161103",
    "201702": "20170202",
    "201705": "20170511",
    "201711": "20171102",
    "201802": "20180208",
    "201805": "20180510",
    "201808": "20180802",
    "201811": "20181101",
    "201902": "20190207",
    "201905": "20190502",
    "201908": "20190801",
    "201911": "20191107",
    "202003": "20200311",
    "202005": "20200507",
    "202008": "20200806",
    "202011": "20201105",
    "202102": "20210204",
    "202105": "20210506",
    "202108": "20210805",
    "202111": "20211104",
    "202202": "20220203",
    "202205": "20220505",
    "202208": "20220804",
    "202211": "20221103",
    "202302": "20230202",
    "202305": "20230511",
    "202308": "20230803",
    "202311": "20231102",
    "202402": "20240201",
    "202405": "20240509",
    "202408": "20240801",
    "202411": "20241107",
    "202502": "20250206",
    "202505": "20250508",
    "202508": "20250807",
    "202511": "20251106",
    "202602": "2026"
}

for name, path in files_info:
    print(name)
    # 1. Load Data
    data_chunks = pd.read_csv(path, index_col='doc_id')
    
    # 2. Fix the Dates safely (Force strings so dictionary matching works!)
    data_chunks['date'] = data_chunks['date'].astype(str)
    date_dict_str = {str(k): str(v) for k, v in date_dict.items()} # Ensure dict is string:string
    
    is_boe = data_chunks['bank'] == 'BoE'
    data_chunks.loc[is_boe, 'date'] = data_chunks.loc[is_boe, 'date'].replace(date_dict_str)

    # Convert to datetime (if some are STILL YYYYMM, let pandas infer it)
    data_chunks['date'] = pd.to_datetime(data_chunks['date'], format='mixed')

    # 3. Calculate Counts
    counts = data_chunks.reset_index().groupby(['doc_id', 'bank', 'label', 'date']).size().unstack(level='label', fill_value=0)

    # 4. Calculate Stance (THE MATH FIX)
    total = counts.sum(axis=1)

    # .get() safely looks for the column. If it doesn't exist, it defaults to 0.
    # This allows you to safely ADD them together if a document has both!
    hawk = counts.get('hawkish', 0) + (counts.get('mostly hawkish', 0) * 0.5)
    dove = counts.get('dovish', 0) + (counts.get('mostly dovish', 0) * 0.5)
    
    # (Optional: what about 'neutral'? If 'neutral' shouldn't skew the stance heavily, 
    # dividing by `total` is fine, but just be aware that total includes neutral sentences)
    counts['stance'] = (hawk - dove) / total

    # 5. Plot Combined Histogram
    plt.figure(figsize=(10, 6))
    plot_data = counts.reset_index()

    sns.histplot(
        data=plot_data,
        x='stance',
        hue='bank',
        stat='density',
        bins=20,
        kde=True,
        element='step',      
        common_norm=False,   
        alpha=0.3,           
        palette=['#1f77b4', '#ff7f0e', '#2ca02c'] 
    )

    plt.title('Stance Distribution Comparison (Fed vs ECB vs BoE)', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel(r'Net Stance $(negative = dovish, positive = hawkish)$ ', fontsize=12)
    plt.ylabel('Density', fontsize=12)

    # Save Plot
    plt.tight_layout()
    plt.savefig(f'output/aggregated/hist_stance_combined_{name}.png', dpi=500)
    plt.show()

    # 6. Save separate CSVs
    counts.xs('Fed', level='bank').sort_values(by='date', ascending=True).to_csv(f'output/aggregated/fed_{name}.csv')
    counts.xs('ECB', level='bank').sort_values(by='date', ascending=True).to_csv(f'output/aggregated/ecb_{name}.csv')
    counts.xs('BoE', level='bank').sort_values(by='date', ascending=True).to_csv(f'output/aggregated/boe_{name}.csv')