import os
import pandas as pd
import statsmodels.api as sm

# 1. Configuration
BANKS = ['fed', 'ecb', 'boe']
LLMS = ['deepseekv3', 'gemini25flash', 'gpt-4o', 'llama33', 'mistrallarge_or', 'qwen25_72b']

# Create a directory to save the final matrices
os.makedirs('output/causal-machinery/spillovers', exist_ok=True)

for llm in LLMS:
    print(f"\n{'='*50}")
    print(f"=== G3 TEXT-TO-TEXT SPILLOVER MATRIX: {llm.upper()} ===")
    print(f"{'='*50}\n")
    
    # 2. Load and prepare all three residual files for the current LLM
    dfs = {}
    missing_data = False
    
    for bank in BANKS:
        filepath = f'output/causal-machinery/residuals/{bank}_{llm}_residuals.csv'
        
        # Graceful skip if the LLM hasn't been run for a specific bank yet
        if not os.path.exists(filepath):
            print(f"  -> Missing file: {filepath}. Skipping {llm.upper()} analysis.")
            missing_data = True
            break 
            
        df = pd.read_csv(filepath)[['date', 'shock']]
        df['Date'] = pd.to_datetime(df['date'])
        df = df.rename(columns={'shock': f'{bank}_shock'})
        dfs[bank] = df[['Date', f'{bank}_shock']].sort_values('Date').dropna()
        
    if missing_data:
        continue # Skip to the next LLM if we are missing files

    # Initialize the matrix
    text_matrix = pd.DataFrame(index=BANKS, columns=BANKS)

    # 3. Loop through all combinations
    for target in BANKS:
        for origin in BANKS:
            if target == origin:
                text_matrix.loc[target, origin] = "-"
                continue
                
            target_df = dfs[target]
            origin_df = dfs[origin]
            
            # Match each target meeting with the most recent origin meeting BEFORE it
            merged = pd.merge_asof(target_df, origin_df, on='Date', direction='backward').dropna()
            
            # Regression: Target_Shock = alpha + beta * Origin_Shock
            X = sm.add_constant(merged[f'{origin}_shock'])
            Y = merged[f'{target}_shock']
            
            model = sm.OLS(Y, X).fit()
            
            coef = model.params[f'{origin}_shock']
            pval = model.pvalues[f'{origin}_shock']
            
            # Academic formatting: Add significance stars
            stars = '***' if pval < 0.01 else '**' if pval < 0.05 else '*' if pval < 0.1 else ''
            
            # Format for your table
            text_matrix.loc[target, origin] = f"{coef:.4f}{stars} (p={pval:.4f})"

    # 4. Display and Save the final result
    print("Rows: Target Bank (Y) | Columns: Prior Origin Bank (X)\n")
    print(text_matrix.to_markdown())
    
    # Save to CSV for easy copy-pasting into your thesis later
    out_path = f'output/causal-machinery/spillovers/text_matrix_{llm}.csv'
    text_matrix.to_csv(out_path)
    print(f"\n  -> Matrix saved to: {out_path}")