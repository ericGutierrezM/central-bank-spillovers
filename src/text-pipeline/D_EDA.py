import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")

files = {
    'Fed': 'data/corpus/Fed.csv', 
    'ECB': 'data/corpus/ECB.csv', 
    'BoE': 'data/corpus/BoE.csv'
}

dfs = []
for bank_name, file_path in files.items():
    try:
        df = pd.read_csv(file_path)
        df['Bank'] = bank_name
        
        # Ensure the date column is properly parsed as datetime
        df['date'] = pd.to_datetime(df['date'], format="%Y%m%d")
        
        # Calculate word count if missing
        if 'word_count' not in df.columns and 'text' in df.columns:
            df['word_count'] = df['text'].astype(str).apply(lambda x: len(x.split()))
            
        dfs.append(df)
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. Please check your path.")

corpus_df = pd.concat(dfs, ignore_index=True)

# ---------------------------------------------------------
# Figure 5: Time Coverage (Timeline Rectangles)
# ---------------------------------------------------------
plt.figure(figsize=(10, 4))

bank_y_mapping = {'BoE': 1, 'ECB': 2, 'Fed': 3}
corpus_df['y_val'] = corpus_df['Bank'].map(bank_y_mapping)

sns.scatterplot(
    data=corpus_df, 
    x='date', 
    y='y_val', 
    hue='Bank', 
    marker='|', 
    s=300,       
    linewidth=2,
    palette='muted', 
    legend=False, 
    alpha=0.6
)

plt.title('Time Coverage of Central Bank Communications', fontsize=14, fontweight='bold')
plt.xlabel('Date', fontsize=12)
plt.ylabel('')

plt.yticks(list(bank_y_mapping.values()), list(bank_y_mapping.keys()), fontsize=12)
plt.ylim(0.5, 3.5)
plt.tight_layout()
plt.savefig('output/aggregated/figure_5_time_coverage.png', dpi=300)
plt.close()

# ---------------------------------------------------------
# Figure 6: Word Count Over Time (Line Plot Only)
# ---------------------------------------------------------
plt.figure(figsize=(12, 5))

corpus_df = corpus_df.sort_values('date')

sns.lineplot(
    data=corpus_df, 
    x='date', 
    y='word_count', 
    hue='Bank', 
    palette='muted',
    linewidth=1.5,
    errorbar=None
)

plt.title('Word Count Over Time', fontsize=14, fontweight='bold')
plt.xlabel('Date', fontsize=12)
plt.ylabel('Word Count', fontsize=12)
plt.legend(title='Central Bank', loc='upper left')
plt.tight_layout()
plt.savefig('output/aggregated/figure_6_word_count_time.png', dpi=300)
plt.close()

# ---------------------------------------------------------
# Figure 7: Density Distributions of Communication Lengths
# ---------------------------------------------------------
plt.figure(figsize=(10, 5))
sns.kdeplot(data=corpus_df, x='word_count', hue='Bank', 
            fill=True, palette='muted', common_norm=False, alpha=0.4, linewidth=2)

plt.title('Density Distribution of Communication Lengths', fontsize=14, fontweight='bold')
plt.xlabel('Word Count per Document', fontsize=12)
plt.ylabel('Density', fontsize=12)
plt.tight_layout()
plt.savefig('output/aggregated/figure_7_density_distribution.png', dpi=300)
plt.close()