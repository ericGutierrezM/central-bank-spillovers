import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

BANKS = ['fed', 'ecb', 'boe']
LLMS = ['deepseekv3', 'gemini25flash', 'gpt-4o', 'llama33', 'mistrallarge_or', 'qwen25_72b']

max_h = 20
horizons_to_report = [0, 5, 10, 20]

os.makedirs('output/spillovers', exist_ok=True)

# Define Market Dictionary
markets = {
    'US':  {'index_col': 'S&P 500',       'vix_col': 'VIX', 'shift_fed': False}, 
    'EU':  {'index_col': 'Euro Stoxx 50', 'vix_col': 'VIX', 'shift_fed': True},  
    'UK':  {'index_col': 'FTSE 100',      'vix_col': 'VIX', 'shift_fed': True}   
}

all_llm_results = {}
final_terminal_tables = {}

global_ymin = float('inf')
global_ymax = float('-inf')

# Pre-Process Market Data
print("Loading and transforming base market data...")
df_base = pd.read_csv('data/controls/global_indices_daily.csv')
vix = pd.read_csv('data/controls/vix_daily.csv')

df_base = df_base.set_index('Date').join(vix.set_index('Date'), how='inner').reset_index(drop=False)
df_base['Date'] = pd.to_datetime(df_base['Date'])
df_base = df_base.sort_values('Date').reset_index(drop=True)

df_base['S&P 500'] = np.log(df_base['S&P 500']) * 100
df_base['Euro Stoxx 50'] = np.log(df_base['Euro Stoxx 50']) * 100
df_base['FTSE 100'] = np.log(df_base['FTSE 100']) * 100

df_base[['S&P 500', 'Euro Stoxx 50', 'FTSE 100', 'VIX']] = df_base[['S&P 500', 'Euro Stoxx 50', 'FTSE 100', 'VIX']].ffill(limit=3)

print("\n--- PASS 1: Calculating Regressions and tracking scales ---")
for llm in LLMS:
    missing_data = False
    shocks_dict = {}
    
    for bank in BANKS:
        filepath = f'output/residuals/{bank}_{llm}_residuals.csv'
        if not os.path.exists(filepath):
            print(f"  -> Missing file: {filepath}. Skipping {llm.upper()}.")
            missing_data = True
            break
            
        b_df = pd.read_csv(filepath)
        b_df = b_df.rename(columns={'date': 'Date', 'shock': f'{bank}_shock'})[['Date', f'{bank}_shock']]
        b_df['Date'] = pd.to_datetime(b_df['Date'])
        shocks_dict[bank] = b_df
        
    if missing_data:
        continue

    df = df_base.copy()
    for bank in BANKS:
        df = df.set_index('Date').join(shocks_dict[bank].set_index('Date'), how='left').reset_index(drop=False)
        
    shock_cols = [f'{b}_shock' for b in BANKS]
    df[shock_cols] = df[shock_cols].fillna(0)

    irf_results = {market: {bank: {'h': [], 'coef': [], 'ci_lower': [], 'ci_upper': [], 'pvalue': []} 
                            for bank in BANKS} for market in markets}

    for market_name, params in markets.items():
        idx_col = params['index_col']
        vix_col = params['vix_col']
        
        df['fed_shock_aligned'] = df['fed_shock'].shift(1).fillna(0) if params['shift_fed'] else df['fed_shock']
        df['ecb_shock_aligned'] = df['ecb_shock'] 
        df['boe_shock_aligned'] = df['boe_shock'] 
        
        df['market_lag1'] = df[idx_col].shift(1)
        df['market_lag2'] = df[idx_col].shift(2)
        df['vix_lag1'] = df[vix_col].shift(1)
        df['vix_lag2'] = df[vix_col].shift(2)
        
        for h in range(max_h + 1):
            col_name = f'delta_y_h{h}'
            df[col_name] = df[idx_col].shift(-h) - df[idx_col].shift(1)
            
            temp_df = df[[col_name, 'fed_shock_aligned', 'ecb_shock_aligned', 'boe_shock_aligned', 
                          'market_lag1', 'market_lag2', 'vix_lag1', 'vix_lag2']].dropna()
            
            Y = temp_df[col_name]
            X = sm.add_constant(temp_df[['fed_shock_aligned', 'ecb_shock_aligned', 'boe_shock_aligned', 
                                         'market_lag1', 'market_lag2', 'vix_lag1', 'vix_lag2']])
            
            model = sm.OLS(Y, X).fit(cov_type='HAC', cov_kwds={'maxlags': h + 1})
            
            for bank in BANKS:
                shock_col = f'{bank}_shock_aligned'
                coef = model.params[shock_col]
                se = model.bse[shock_col]
                pval = model.pvalues[shock_col]
                
                ci_l = coef - 1.96 * se
                ci_u = coef + 1.96 * se
                
                irf_results[market_name][bank]['h'].append(h)
                irf_results[market_name][bank]['coef'].append(coef)
                irf_results[market_name][bank]['ci_lower'].append(ci_l)
                irf_results[market_name][bank]['ci_upper'].append(ci_u)
                irf_results[market_name][bank]['pvalue'].append(pval)
                
                if ci_l < global_ymin: global_ymin = ci_l
                if ci_u > global_ymax: global_ymax = ci_u

    all_llm_results[llm] = irf_results

y_padding = (global_ymax - global_ymin) * 0.05
global_ymin -= y_padding
global_ymax += y_padding

print(f"Standardization Matrix Lock complete. Global Y-Axis Range set to: [{global_ymin:.2f}, {global_ymax:.2f}]")

print("\n--- PASS 2: Standardized Grid Generation ---")
row_labels = ['US Market (SP500)', 'EU Market (EUROSTOXX50)', 'UK Market (FTSE100)']
col_labels = ['FED Shock', 'ECB Shock', 'BoE Shock']
colors = {'fed': '#1f77b4', 'ecb': '#ff7f0e', 'boe': '#2ca02c'}

for llm, irf_results in all_llm_results.items():
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, axes = plt.subplots(3, 3, figsize=(18, 12), sharex=True, sharey=True)

    for i, market in enumerate(['US', 'EU', 'UK']):
        for j, bank in enumerate(BANKS):
            ax = axes[i, j]
            
            h_vals = irf_results[market][bank]['h']
            coefs = irf_results[market][bank]['coef']
            lower = irf_results[market][bank]['ci_lower']
            upper = irf_results[market][bank]['ci_upper']
            
            ax.axhline(0, color='black', linestyle='--', linewidth=1.5)
            ax.plot(h_vals, coefs, color=colors[bank], marker='o', markersize=4, linewidth=2)
            ax.fill_between(h_vals, lower, upper, color=colors[bank], alpha=0.2)
            
            ax.set_ylim(global_ymin, global_ymax)
            
            if i == 0:
                ax.set_title(col_labels[j], fontsize=14, fontweight='bold', pad=15)
            if j == 0:
                ax.set_ylabel(f"{row_labels[i]}\n$\Delta$ Index", fontsize=12, fontweight='bold')
            if i == 2:
                ax.set_xlabel('Horizon ($h$ days)', fontsize=12)

    plt.suptitle(f'Global Market Spillovers ({llm.upper()}) [Standardized Scale]', fontsize=18, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(f'output/spillovers/irf_3x3_{llm}.png', dpi=500, bbox_inches='tight')
    plt.close()
    print(f"  -> Saved Standardized IRF Grid: output/spillovers/irf_3x3_{llm}.png")

    for target_h in horizons_to_report:
        spillover_matrix = pd.DataFrame(index=row_labels, columns=col_labels)
        
        for i, market in enumerate(['US', 'EU', 'UK']):
            for j, bank in enumerate(BANKS):
                idx = target_h 
                coef = irf_results[market][bank]['coef'][idx]
                pval = irf_results[market][bank]['pvalue'][idx]
                
                stars = '***' if pval < 0.01 else '**' if pval < 0.05 else '*' if pval < 0.1 else ''
                spillover_matrix.iloc[i, j] = f"{coef:.4f}{stars} (p={pval:.4f})"
        
        matrix_path = f'output/spillovers/matrix_{llm}_h{target_h}.csv'
        spillover_matrix.to_csv(matrix_path)
        
        dict_key = f"{llm.upper()} - Horizon (h={target_h} days)"
        final_terminal_tables[dict_key] = spillover_matrix.to_markdown()

print("\n" * 3)
print("*" * 80)
print("*" * 24 + " FINAL RESULTS " + "*" * 24)
print("*" * 80)

for title, markdown_table in final_terminal_tables.items():
    print(f"\n=== {title} ===")
    print(markdown_table)
    print("\n" + "-" * 80)

print("\nScript Complete and Scales are Fully Standardized!")