import os
import pandas as pd
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

# 1. Configuration: Define your banks and your LLMs here
BANKS = ['FED', 'ECB', 'BOE']
LLMS = ['deepseekv3', 'gemini25flash', 'gpt-4o', 'llama33', 'mistrallarge_or', 'qwen25_72b']

# Ensure output directory exists
os.makedirs('output/causal-machinery/residuals', exist_ok=True)

# The regression formula is constant across all runs
FORMULA = "stance ~ unemployment + inflation + rate_change + vix + bond_yields + C(governor)"

# 2. Main Execution Loop
for llm in LLMS:
    for bank in BANKS:
        bank_lower = bank.lower()
        print(f"\n[{bank} | {llm.upper()}] Processing orthogonalization...")

        # Construct file paths
        controls_path = f'data/controls/{bank}_CONTROLS.csv'
        sentiment_path = f'output/causal-machinery/aggregated/{bank_lower}_{llm}.csv'

        # Safety check: skip if the LLM hasn't generated predictions for this bank yet
        if not os.path.exists(sentiment_path):
            print(f"  -> Warning: {sentiment_path} not found. Skipping.")
            continue

        # Load data
        controls = pd.read_csv(controls_path)
        sentiment = pd.read_csv(sentiment_path)

        # Merge Controls and Y
        regression_data = pd.merge(
            left=controls, 
            right=sentiment[['date', 'stance']], 
            on='date', 
            how='left'
        )

        # Drop any NaNs before regression to prevent Statsmodels errors
        regression_data = regression_data.dropna(subset=['stance', 'unemployment', 'inflation', 'rate_change', 'vix', 'bond_yields', 'governor'])

        # Fit Stage 1 Regression
        stage1_model = smf.ols(formula=FORMULA, data=regression_data).fit()
        
        # Optional: Print summary (commented out to avoid terminal spam, but you can enable it)
        # print(stage1_model.summary())

        # Extract Residuals
        regression_data['shock'] = stage1_model.resid

        # Save the residuals to CSV (Now includes LLM in filename!)
        resid_csv_path = f'output/causal-machinery/residuals/{bank_lower}_{llm}_residuals.csv'
        regression_data[['date', 'shock']].to_csv(resid_csv_path, index=False)
        print(f"  -> Saved residuals: {resid_csv_path}")

        # ==========================================
        # Plot 1: Shocks Over Time
        # ==========================================
        fig, ax = plt.subplots(figsize=(12, 6))

        ax.plot(pd.to_datetime(regression_data['date']), regression_data['shock'], 
                marker='o', markersize=6, linestyle='-', linewidth=1.5, 
                color='#1f77b4', label='Identified Shock ($\epsilon_t$)')

        ax.axhline(0, color='crimson', linestyle='--', linewidth=2, label='Expected Stance (0)')

        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Dynamically inject Bank and LLM into the title
        ax.set_title(f'{bank} Communication Shocks Over Time ({llm.upper()})', fontsize=16, fontweight='bold', pad=15)
        ax.set_ylabel('Shock', fontsize=12)
        ax.set_xlabel('Meeting Date', fontsize=12)
        ax.legend(loc='upper right', frameon=True, facecolor='white', framealpha=0.9)

        plt.tight_layout()
        plt.savefig(f'output/causal-machinery/residuals/{bank_lower}_{llm}_shocks.png', dpi=500)
        plt.close() # Close figure to free up memory!

        # ==========================================
        # Plot 2: Distribution of Shocks
        # ==========================================
        fig, ax = plt.subplots(figsize=(8, 6))

        sns.histplot(data=regression_data, x='shock', kde=True, bins=15, 
                     color='steelblue', edgecolor='black', alpha=0.7, ax=ax)

        ax.axvline(0, color='crimson', linestyle='--', linewidth=2, label='Zero Mean')

        ax.set_title(f'Distribution of {bank} Shocks ({llm.upper()})', fontsize=16, fontweight='bold', pad=15)
        ax.set_xlabel('Shock Magnitude ($\epsilon_t$)', fontsize=12)
        ax.set_ylabel('Number of Meetings', fontsize=12)
        ax.legend(frameon=True, facecolor='white', framealpha=0.9)

        plt.tight_layout()
        plt.savefig(f'output/causal-machinery/residuals/{bank_lower}_{llm}_shocks_distribution.png', dpi=500)
        plt.close() # Close figure to free up memory!