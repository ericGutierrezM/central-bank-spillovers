import os
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from statsmodels.stats.stattools import durbin_watson

# ==========================================
# 1. Configuration
# ==========================================
BANKS = ['fed', 'ecb', 'boe']
LLMS  = ['deepseekv3', 'gemini25flash', 'gpt-4o', 'llama33', 'mistrallarge_or', 'qwen25_72b']

CLUSTER = {
    'deepseekv3':      'high-neutral',
    'qwen25_72b':      'high-neutral',
    'gemini25flash':   'low-neutral',
    'gpt-4o':          'low-neutral',
    'llama33':         'low-neutral',
    'mistrallarge_or': 'low-neutral',
}
CLUSTER_COLORS = {'high-neutral': '#1a6faf', 'low-neutral': '#cc4444'}
CLUSTER_LABELS = {
    'high-neutral': 'High-Neutral (DeepSeek, Qwen)',
    'low-neutral':  'Low-Neutral (Gemini, GPT-4o, Llama, Mistral)',
}

max_h = 20
markets = {
    'US': {'index_col': 'S&P 500',       'vix_col': 'VIX', 'shift_fed': False},
    'EU': {'index_col': 'Euro Stoxx 50', 'vix_col': 'VIX', 'shift_fed': True},
    'UK': {'index_col': 'FTSE 100',      'vix_col': 'VIX', 'shift_fed': True},
}

os.makedirs('output/robustness', exist_ok=True)

# ==========================================
# 2. Pre-Process Market Data (identical to D)
# ==========================================
print("Loading market data...")
df_base = pd.read_csv('data/controls/global_indices_daily.csv')
vix     = pd.read_csv('data/controls/vix_daily.csv')

df_base = df_base.set_index('Date').join(vix.set_index('Date'), how='inner').reset_index(drop=False)
df_base['Date'] = pd.to_datetime(df_base['Date'])
df_base = df_base.sort_values('Date').reset_index(drop=True)

df_base['S&P 500']       = np.log(df_base['S&P 500']) * 100
df_base['Euro Stoxx 50'] = np.log(df_base['Euro Stoxx 50']) * 100
df_base['FTSE 100']      = np.log(df_base['FTSE 100']) * 100

df_base[['S&P 500', 'Euro Stoxx 50', 'FTSE 100', 'VIX']] = \
    df_base[['S&P 500', 'Euro Stoxx 50', 'FTSE 100', 'VIX']].ffill(limit=3)

# ==========================================
# 3. Run LP for All LLMs — Collect Full IRF Arrays
# ==========================================
print("Running local projections for all LLMs...")

# irf_all[llm][market][bank] = {'coef': [...h0..h20], 'ci_lower': [...], 'ci_upper': [...], 'pvalue': [...]}
irf_all = {}
h_vals  = list(range(max_h + 1))

for llm in LLMS:
    print(f"  -> {llm}")
    shocks_dict = {}
    missing = False

    for bank in BANKS:
        filepath = f'output/residuals/{bank}_{llm}_residuals.csv'
        if not os.path.exists(filepath):
            print(f"     Warning: {filepath} missing — skipping {llm}")
            missing = True
            break
        b_df = pd.read_csv(filepath).rename(columns={'date': 'Date', 'shock': f'{bank}_shock'})
        b_df = b_df[['Date', f'{bank}_shock']]
        b_df['Date'] = pd.to_datetime(b_df['Date'])
        shocks_dict[bank] = b_df

    if missing:
        continue

    df = df_base.copy()
    for bank in BANKS:
        df = df.set_index('Date').join(shocks_dict[bank].set_index('Date'), how='left').reset_index(drop=False)

    shock_cols = [f'{b}_shock' for b in BANKS]
    df[shock_cols] = df[shock_cols].fillna(0)

    irf_all[llm] = {m: {b: {'coef': [], 'ci_lower': [], 'ci_upper': [], 'pvalue': []}
                         for b in BANKS} for m in markets}

    for market_name, params in markets.items():
        idx_col = params['index_col']
        vix_col = params['vix_col']

        df['fed_shock_aligned'] = df['fed_shock'].shift(1).fillna(0) if params['shift_fed'] else df['fed_shock']
        df['ecb_shock_aligned'] = df['ecb_shock']
        df['boe_shock_aligned'] = df['boe_shock']

        df['market_lag1'] = df[idx_col].shift(1)
        df['market_lag2'] = df[idx_col].shift(2)
        df['vix_lag1']    = df[vix_col].shift(1)
        df['vix_lag2']    = df[vix_col].shift(2)

        for h in h_vals:
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
                se   = model.bse[shock_col]
                pval = model.pvalues[shock_col]

                irf_all[llm][market_name][bank]['coef'].append(coef)
                irf_all[llm][market_name][bank]['ci_lower'].append(coef - 1.96 * se)
                irf_all[llm][market_name][bank]['ci_upper'].append(coef + 1.96 * se)
                irf_all[llm][market_name][bank]['pvalue'].append(pval)

available_llms = list(irf_all.keys())
print(f"\nAvailable LLMs for plotting: {available_llms}")

# ==========================================
# Layer 1: Fan Chart — 6 IRF Lines + Cluster Envelopes
# ==========================================
print("\nLayer 1: Fan chart...")

row_labels = ['US Market (SP500)', 'EU Market (EUROSTOXX50)', 'UK Market (FTSE100)']
col_labels  = ['FED Shock', 'ECB Shock', 'BoE Shock']

plt.style.use('seaborn-v0_8-whitegrid')
fig, axes = plt.subplots(3, 3, figsize=(18, 12), sharex=True)

for i, market in enumerate(['US', 'EU', 'UK']):
    for j, bank in enumerate(BANKS):
        ax = axes[i, j]
        ax.axhline(0, color='black', linestyle='--', linewidth=1)

        cluster_coefs = {'high-neutral': [], 'low-neutral': []}

        for llm in available_llms:
            coefs   = irf_all[llm][market][bank]['coef']
            cluster = CLUSTER[llm]
            color   = CLUSTER_COLORS[cluster]
            ax.plot(h_vals, coefs, color=color, linewidth=1.2, alpha=0.65)
            cluster_coefs[cluster].append(coefs)

        # Within-cluster envelope
        for cluster, coef_list in cluster_coefs.items():
            if len(coef_list) > 1:
                arr = np.array(coef_list)
                ax.fill_between(h_vals, arr.min(axis=0), arr.max(axis=0),
                                color=CLUSTER_COLORS[cluster], alpha=0.12)

        # Median across all LLMs as the majority-vote line
        all_coefs = np.array([irf_all[llm][market][bank]['coef'] for llm in available_llms])
        ax.plot(h_vals, np.median(all_coefs, axis=0),
                color='black', linestyle='--', linewidth=2)

        if i == 0:
            ax.set_title(col_labels[j], fontsize=13, fontweight='bold')
        if j == 0:
            ax.set_ylabel(f"{row_labels[i]}\n$\\Delta$ Index", fontsize=11, fontweight='bold')
        if i == 2:
            ax.set_xlabel('Horizon ($h$ days)', fontsize=11)

legend_handles = [
    mpatches.Patch(color=CLUSTER_COLORS['high-neutral'], label=CLUSTER_LABELS['high-neutral']),
    mpatches.Patch(color=CLUSTER_COLORS['low-neutral'],  label=CLUSTER_LABELS['low-neutral']),
    plt.Line2D([0], [0], color='black', linestyle='--', linewidth=2, label='Median (all LLMs)'),
]
fig.legend(handles=legend_handles, loc='lower center', ncol=3, fontsize=11,
           bbox_to_anchor=(0.5, -0.03), frameon=True)

plt.suptitle('IRF Fan Chart by LLM Cluster: Global Market Spillovers',
             fontsize=16, fontweight='bold', y=1.01)
plt.tight_layout()
plt.savefig('output/robustness/layer1_fan_chart.png', dpi=500, bbox_inches='tight')
plt.close()
print("  -> Saved: output/robustness/layer1_fan_chart.png")

# ==========================================
# Layer 2: Sensitivity — Max–Min Range + Sign Flips
# ==========================================
print("\nLayer 2: Sensitivity analysis...")

fig, axes = plt.subplots(3, 3, figsize=(18, 12), sharex=True)

sign_flip_summary = []

for i, market in enumerate(['US', 'EU', 'UK']):
    for j, bank in enumerate(BANKS):
        ax = axes[i, j]

        all_coefs  = np.array([irf_all[llm][market][bank]['coef'] for llm in available_llms])
        coef_range = all_coefs.max(axis=0) - all_coefs.min(axis=0)
        sign_flip  = (all_coefs.max(axis=0) > 0) & (all_coefs.min(axis=0) < 0)

        ax.plot(h_vals, coef_range, color='#555555', linewidth=2)
        ax.fill_between(h_vals, 0, coef_range, alpha=0.18, color='#555555')

        for h_idx, flip in enumerate(sign_flip):
            if flip:
                ax.axvline(h_idx, color='crimson', alpha=0.4, linewidth=1.5)

        ax.axhline(0, color='black', linewidth=0.8)

        if i == 0:
            ax.set_title(col_labels[j], fontsize=13, fontweight='bold')
        if j == 0:
            ax.set_ylabel(f"{row_labels[i]}\nCoefficient Range", fontsize=11, fontweight='bold')
        if i == 2:
            ax.set_xlabel('Horizon ($h$ days)', fontsize=11)

        flip_horizons = [h for h in h_vals if sign_flip[h]]
        if flip_horizons:
            sign_flip_summary.append(f"  {market} × {bank.upper()}: h = {flip_horizons}")

plt.suptitle(
    'Model Sensitivity: Max–Min IRF Range Across LLMs\n(Red lines = sign flip across models)',
    fontsize=15, fontweight='bold', y=1.01
)
plt.tight_layout()
plt.savefig('output/robustness/layer2_sensitivity.png', dpi=500, bbox_inches='tight')
plt.close()
print("  -> Saved: output/robustness/layer2_sensitivity.png")

print("\n  Sign-flip summary:")
if sign_flip_summary:
    for s in sign_flip_summary:
        print(s)
else:
    print("  None — LLMs agree on sign at all horizons.")

# ==========================================
# Layer 3: Cross-LLM Shock Spread × §1 Disagreement
# ==========================================
print("\nLayer 3: Linking shock spread to LLM disagreement...")

_LABEL_SCORE = {"dovish": -2, "mostly dovish": -1, "neutral": 0, "mostly hawkish": 1, "hawkish": 2}
_frames = []
for _llm in LLMS:
    _fp = f'output/stance/turn_predictions_{_llm}.csv'
    if not os.path.exists(_fp):
        continue
    _df = pd.read_csv(_fp, usecols=['bank', 'date', 'turn_uid', 'label'])
    _df['model_key'] = _llm
    _frames.append(_df)
_raw = pd.concat(_frames, ignore_index=True)
_raw['label']     = _raw['label'].str.strip().str.lower()
_raw['date_dt']   = pd.to_datetime(_raw['date'].astype(str).str[:6], format='%Y%m')
_raw['hawk_score'] = _raw['label'].map(_LABEL_SCORE)
_raw = _raw.dropna(subset=['hawk_score'])
_turn_agg = (
    _raw.groupby(['bank', 'date_dt', 'turn_uid'])['hawk_score']
    .agg(mean_score='mean', score_std='std')
    .reset_index()
)
disag = (
    _turn_agg.groupby(['bank', 'date_dt'])
    .agg(mean_stance=('mean_score', 'mean'), dispersion=('score_std', 'mean'), n_turns=('turn_uid', 'size'))
    .reset_index()
    .sort_values(['bank', 'date_dt'])
)
disag['date_dt']  = pd.to_datetime(disag['date_dt'])
disag['ym']       = disag['date_dt'].dt.to_period('M')
disag['bank_key'] = disag['bank'].str.lower()

rows = []
for bank in BANKS:
    llm_shocks = {}
    for llm in available_llms:
        filepath = f'output/residuals/{bank}_{llm}_residuals.csv'
        if not os.path.exists(filepath):
            continue
        df_r = pd.read_csv(filepath)
        df_r['date'] = pd.to_datetime(df_r['date'])
        llm_shocks[llm] = df_r.set_index('date')['shock']

    if len(llm_shocks) < 2:
        continue

    shock_df = pd.DataFrame(llm_shocks)
    shock_df['cross_llm_std']   = shock_df.std(axis=1)
    shock_df['cross_llm_range'] = shock_df.max(axis=1) - shock_df.min(axis=1)
    shock_df['bank'] = bank
    shock_df = shock_df.reset_index().rename(columns={'index': 'date'})
    shock_df['ym'] = pd.to_datetime(shock_df['date']).dt.to_period('M')
    rows.append(shock_df[['date', 'bank', 'ym', 'cross_llm_std', 'cross_llm_range']])

shock_spread = pd.concat(rows, ignore_index=True)

merged = shock_spread.merge(
    disag[['bank_key', 'ym', 'dispersion']],
    left_on=['bank', 'ym'],
    right_on=['bank_key', 'ym'],
    how='inner'
)

bank_colors = {'fed': '#1f77b4', 'ecb': '#ff7f0e', 'boe': '#2ca02c'}
bank_labels  = {'fed': 'FED', 'ecb': 'ECB', 'boe': 'BoE'}

fig, axes = plt.subplots(1, 2, figsize=(14, 6))

for ax, y_col, y_label in zip(
    axes,
    ['cross_llm_std', 'cross_llm_range'],
    ['Cross-LLM Shock Std Dev', 'Cross-LLM Shock Range (Max–Min)'],
):
    for bank in BANKS:
        sub = merged[merged['bank'] == bank]
        ax.scatter(sub['dispersion'], sub[y_col],
                   color=bank_colors[bank], label=bank_labels[bank], alpha=0.6, s=40)

    # Pooled OLS regression line
    X_reg = sm.add_constant(merged['dispersion'])
    fit   = sm.OLS(merged[y_col], X_reg).fit()
    x_rng = np.linspace(merged['dispersion'].min(), merged['dispersion'].max(), 100)
    ax.plot(x_rng, fit.params['const'] + fit.params['dispersion'] * x_rng,
            color='black', linestyle='--', linewidth=2,
            label=f'OLS (β={fit.params["dispersion"]:.3f}, p={fit.pvalues["dispersion"]:.3f})')

    ax.set_xlabel('§1 LLM Disagreement (Dispersion)', fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.legend(fontsize=10, frameon=True)

plt.suptitle('Layer 3: §1 Disagreement vs. Cross-LLM Shock Spread',
             fontsize=15, fontweight='bold')
plt.tight_layout()
plt.savefig('output/robustness/layer3_disagreement_vs_shock_spread.png', dpi=500, bbox_inches='tight')
plt.close()
print("  -> Saved: output/robustness/layer3_disagreement_vs_shock_spread.png")

# ==========================================
# Layer 3b: DeBERTa Text-Predicted Disagreement vs. Cross-LLM Shock Spread
# ==========================================
print("\nLayer 3b: DeBERTa text-predicted disagreement vs. shock spread...")

_DEBERTA_PATH = r'C:\Users\sffra\Downloads\meeting_disagreement_for_var.csv'
_RUN_3B = os.path.exists(_DEBERTA_PATH)
if not _RUN_3B:
    print("  -> Skipping layer 3b: meeting_disagreement_for_var.csv not found.")

if _RUN_3B:
    deberta = pd.read_csv(_DEBERTA_PATH)
    deberta['bank_key'] = deberta['bank'].str.lower()
    deberta['ym']       = pd.to_datetime(deberta['meeting'], errors='coerce').dt.to_period('M')
    deberta = deberta.dropna(subset=['ym', 'pred_std3'])

if _RUN_3B:
    merged_b = shock_spread.merge(
        deberta[['bank_key', 'ym', 'pred_std3']],
        left_on=['bank', 'ym'],
        right_on=['bank_key', 'ym'],
        how='inner'
    )
    print(f"  -> Merged rows for layer3b: {len(merged_b)}")

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    for ax, y_col, y_label in zip(
        axes,
        ['cross_llm_std', 'cross_llm_range'],
        ['Cross-LLM Shock Std Dev', 'Cross-LLM Shock Range (Max–Min)'],
    ):
        for bank in BANKS:
            sub = merged_b[merged_b['bank'] == bank]
            ax.scatter(sub['pred_std3'], sub[y_col],
                       color=bank_colors[bank], label=bank_labels[bank], alpha=0.6, s=40)

        X_reg = sm.add_constant(merged_b['pred_std3'])
        fit   = sm.OLS(merged_b[y_col], X_reg).fit(cov_type='HAC', cov_kwds={'maxlags': 3})
        dw    = durbin_watson(fit.resid)
        x_rng = np.linspace(merged_b['pred_std3'].min(), merged_b['pred_std3'].max(), 100)
        ax.plot(x_rng, fit.params['const'] + fit.params['pred_std3'] * x_rng,
                color='black', linestyle='--', linewidth=2,
                label=f'OLS-HAC (β={fit.params["pred_std3"]:.3f}, p={fit.pvalues["pred_std3"]:.3f})\nDW={dw:.2f}')

        ax.set_xlabel('DeBERTa Text-Predicted Disagreement ($\\hat{d}$)', fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        ax.legend(fontsize=10, frameon=True)
        print(f"  [{y_col}] b={fit.params['pred_std3']:.4f}, p={fit.pvalues['pred_std3']:.4f}, DW={dw:.3f}")

    plt.suptitle('Layer 3b: Text-Predicted Disagreement (DeBERTa) vs. Cross-LLM Shock Spread',
                 fontsize=15, fontweight='bold')
    plt.tight_layout()
    plt.savefig('output/robustness/layer3b_deberta_vs_shock_spread.png', dpi=500, bbox_inches='tight')
    plt.close()
    print("  -> Saved: output/robustness/layer3b_deberta_vs_shock_spread.png")

# ==========================================
# Statistical Check: Cluster-Mean IRF Significance
# ==========================================
print("\n" + "=" * 60)
print("CLUSTER-MEAN IRF SIGNIFICANCE CHECK")
print("=" * 60)

CLUSTERS_DEF = {
    'high-neutral': [llm for llm in available_llms if CLUSTER[llm] == 'high-neutral'],
    'low-neutral':  [llm for llm in available_llms if CLUSTER[llm] == 'low-neutral'],
}
check_horizons = [0, 5, 10, 20]

for cluster_name, cluster_llms in CLUSTERS_DEF.items():
    print(f"\n  Cluster: {CLUSTER_LABELS[cluster_name]}")

    df_c = df_base.copy()

    for bank in BANKS:
        series_list = []
        for llm in cluster_llms:
            fp = f'output/residuals/{bank}_{llm}_residuals.csv'
            if not os.path.exists(fp):
                continue
            tmp = pd.read_csv(fp)
            tmp['date'] = pd.to_datetime(tmp['date'])
            series_list.append(tmp.set_index('date')['shock'].rename(llm))
        avg = pd.concat(series_list, axis=1).mean(axis=1).reset_index()
        avg.columns = ['Date', f'{bank}_shock']
        df_c = df_c.set_index('Date').join(avg.set_index('Date'), how='left').reset_index(drop=False)

    df_c[[f'{b}_shock' for b in BANKS]] = df_c[[f'{b}_shock' for b in BANKS]].fillna(0)

    for market_name, params in markets.items():
        idx_col = params['index_col']
        df_c['fed_shock_aligned'] = df_c['fed_shock'].shift(1).fillna(0) if params['shift_fed'] else df_c['fed_shock']
        df_c['ecb_shock_aligned'] = df_c['ecb_shock']
        df_c['boe_shock_aligned'] = df_c['boe_shock']
        df_c['market_lag1'] = df_c[idx_col].shift(1)
        df_c['market_lag2'] = df_c[idx_col].shift(2)
        df_c['vix_lag1']    = df_c['VIX'].shift(1)
        df_c['vix_lag2']    = df_c['VIX'].shift(2)

        for h in check_horizons:
            df_c[f'delta_y_h{h}'] = df_c[idx_col].shift(-h) - df_c[idx_col].shift(1)

        regressors = ['fed_shock_aligned', 'ecb_shock_aligned', 'boe_shock_aligned',
                      'market_lag1', 'market_lag2', 'vix_lag1', 'vix_lag2']

        print(f"\n    {market_name} Market | {'h=0':<18} {'h=5':<18} {'h=10':<18} {'h=20':<18}")
        print(f"    {'-'*80}")

        for bank in BANKS:
            cells = []
            for h in check_horizons:
                col  = f'delta_y_h{h}'
                tmp  = df_c[[col] + regressors].dropna()
                Y    = tmp[col]
                X    = sm.add_constant(tmp[regressors])
                mdl  = sm.OLS(Y, X).fit(cov_type='HAC', cov_kwds={'maxlags': h + 1})
                coef = mdl.params[f'{bank}_shock_aligned']
                pval = mdl.pvalues[f'{bank}_shock_aligned']
                stars = '***' if pval < 0.01 else '**' if pval < 0.05 else '*' if pval < 0.1 else '  '
                cells.append(f"{coef:>7.3f}{stars} (p={pval:.3f})")
            print(f"    {bank.upper():<6} " + " | ".join(cells))

# ==========================================
# Outlier Meeting Identification (Layer 3)
# ==========================================
print("\n" + "=" * 60)
print("OUTLIER MEETINGS — TOP 15 BY CROSS-LLM SHOCK RANGE")
print("=" * 60)
cols_to_show = ['bank', 'date', 'dispersion', 'cross_llm_std', 'cross_llm_range']
top_range = merged.sort_values('cross_llm_range', ascending=False).head(15)
print(top_range[cols_to_show].to_string(index=False))

print("\n  Top 10 by Std Dev:")
top_std = merged.sort_values('cross_llm_std', ascending=False).head(10)
print(top_std[cols_to_show].to_string(index=False))

print("\nScript E complete.")
