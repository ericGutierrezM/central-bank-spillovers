import os
import pandas as pd
import statsmodels.api as sm

BANKS = ['fed', 'ecb', 'boe']
LLMS = ['deepseekv3', 'gemini25flash', 'gpt-4o', 'llama33', 'mistrallarge_or', 'qwen25_72b']

os.makedirs('output/spillovers', exist_ok=True)

for llm in LLMS:
    print(f"\n{'='*50}")
    print(f"=== G3 TEXT-TO-TEXT SPILLOVER MATRIX: {llm.upper()} ===")
    print(f"{'='*50}\n")
    
    dfs = {}
    missing_data = False
    
    for bank in BANKS:
        filepath = f'output/residuals/{bank}_{llm}_residuals.csv'
        
        if not os.path.exists(filepath):
            print(f"  -> Missing file: {filepath}. Skipping {llm.upper()} analysis.")
            missing_data = True
            break 
            
        df = pd.read_csv(filepath)[['date', 'shock']]
        df['Date'] = pd.to_datetime(df['date'])
        df = df.rename(columns={'shock': f'{bank}_shock'})
        dfs[bank] = df[['Date', f'{bank}_shock']].sort_values('Date').dropna()
        
    if missing_data:
        continue

    # Initialize the matrix
    text_matrix = pd.DataFrame(index=BANKS, columns=BANKS)

    for target in BANKS:
        for origin in BANKS:
            if target == origin:
                text_matrix.loc[target, origin] = "-"
                continue
                
            target_df = dfs[target]
            origin_df = dfs[origin]
            
            merged = pd.merge_asof(target_df, origin_df, on='Date', direction='backward').dropna()
            
            # Regression: Target_Shock = alpha + beta * Origin_Shock
            X = sm.add_constant(merged[f'{origin}_shock'])
            Y = merged[f'{target}_shock']
            
            model = sm.OLS(Y, X).fit()
            
            coef = model.params[f'{origin}_shock']
            pval = model.pvalues[f'{origin}_shock']
            
            stars = '***' if pval < 0.01 else '**' if pval < 0.05 else '*' if pval < 0.1 else ''
            
            text_matrix.loc[target, origin] = f"{coef:.4f}{stars} (p={pval:.4f})"

    print("Rows: Target Bank (Y) | Columns: Prior Origin Bank (X)\n")
    print(text_matrix.to_markdown())
    
    out_path = f'output/spillovers/text_matrix_{llm}.csv'
    text_matrix.to_csv(out_path)
    print(f"\n  -> Matrix saved to: {out_path}")