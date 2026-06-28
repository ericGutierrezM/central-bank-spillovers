import os

import numpy as np
import pandas as pd
import statsmodels.api as sm


BANKS = ['fed', 'ecb', 'boe']
LEFT_MODEL = 'gemini25flash'
RIGHT_MODEL = 'mistrallarge_or'
MAX_H = 20
REPORT_HORIZONS = [0, 5, 10, 20]

MARKETS = {
    'US': {'index_col': 'S&P 500', 'vix_col': 'VIX', 'shift_fed': False},
    'EU': {'index_col': 'Euro Stoxx 50', 'vix_col': 'VIX', 'shift_fed': True},
    'UK': {'index_col': 'FTSE 100', 'vix_col': 'VIX', 'shift_fed': True},
}

MARKET_LABELS = {'US': 'US', 'EU': 'EU', 'UK': 'UK'}
SHOCK_LABELS = {'fed': 'Fed', 'ecb': 'ECB', 'boe': 'BoE'}


def as_scalar(value):
    return float(np.asarray(value).squeeze())


def stars(pvalue):
    if pvalue < 0.01:
        return '***'
    if pvalue < 0.05:
        return '**'
    if pvalue < 0.1:
        return '*'
    return ''


def fmt(coef, low, high, pvalue):
    return f"{coef:.3f}{stars(pvalue)} [{low:.3f}, {high:.3f}] p={pvalue:.3f}"


def load_market_base():
    df_base = pd.read_csv('data/controls/global_indices_daily.csv')
    vix = pd.read_csv('data/controls/vix_daily.csv')

    df_base = df_base.set_index('Date').join(vix.set_index('Date'), how='inner').reset_index(drop=False)
    df_base['Date'] = pd.to_datetime(df_base['Date'])
    df_base = df_base.sort_values('Date').reset_index(drop=True)

    df_base['S&P 500'] = np.log(df_base['S&P 500']) * 100
    df_base['Euro Stoxx 50'] = np.log(df_base['Euro Stoxx 50']) * 100
    df_base['FTSE 100'] = np.log(df_base['FTSE 100']) * 100
    df_base[['S&P 500', 'Euro Stoxx 50', 'FTSE 100', 'VIX']] = (
        df_base[['S&P 500', 'Euro Stoxx 50', 'FTSE 100', 'VIX']].ffill(limit=3)
    )
    return df_base


def load_model_shocks(model_key, suffix=''):
    shocks = {}
    for bank in BANKS:
        filepath = f'output/causal-machinery/residuals/{bank}_{model_key}_residuals.csv'
        if not os.path.exists(filepath):
            raise FileNotFoundError(f'Missing residual file: {filepath}')

        col_name = f'{bank}_{suffix}shock' if suffix else f'{bank}_shock'
        bank_df = pd.read_csv(filepath).rename(columns={'date': 'Date', 'shock': col_name})
        bank_df = bank_df[['Date', col_name]]
        bank_df['Date'] = pd.to_datetime(bank_df['Date'])
        shocks[bank] = bank_df
    return shocks


def add_controls(df, idx_col, vix_col):
    out = df.copy()
    out['market_lag1'] = out[idx_col].shift(1)
    out['market_lag2'] = out[idx_col].shift(2)
    out['vix_lag1'] = out[vix_col].shift(1)
    out['vix_lag2'] = out[vix_col].shift(2)
    return out


def run_standalone_lp(df_base, model_key):
    shocks = load_model_shocks(model_key)
    df = df_base.copy()

    for bank in BANKS:
        df = df.set_index('Date').join(shocks[bank].set_index('Date'), how='left').reset_index(drop=False)

    shock_cols = [f'{bank}_shock' for bank in BANKS]
    df[shock_cols] = df[shock_cols].fillna(0)

    rows = []
    for market_name, params in MARKETS.items():
        idx_col = params['index_col']
        vix_col = params['vix_col']

        work = df.copy()
        work['fed_shock_aligned'] = work['fed_shock'].shift(1).fillna(0) if params['shift_fed'] else work['fed_shock']
        work['ecb_shock_aligned'] = work['ecb_shock']
        work['boe_shock_aligned'] = work['boe_shock']
        work = add_controls(work, idx_col, vix_col)

        regressors = [
            'fed_shock_aligned',
            'ecb_shock_aligned',
            'boe_shock_aligned',
            'market_lag1',
            'market_lag2',
            'vix_lag1',
            'vix_lag2',
        ]

        for h in range(MAX_H + 1):
            col_name = f'delta_y_h{h}'
            work[col_name] = work[idx_col].shift(-h) - work[idx_col].shift(1)
            temp_df = work[[col_name] + regressors].dropna()

            y = temp_df[col_name]
            x = sm.add_constant(temp_df[regressors])
            model = sm.OLS(y, x).fit(cov_type='HAC', cov_kwds={'maxlags': h + 1})

            for bank in BANKS:
                shock_col = f'{bank}_shock_aligned'
                coef = model.params[shock_col]
                se = model.bse[shock_col]
                pvalue = model.pvalues[shock_col]
                rows.append(
                    {
                        'market': market_name,
                        'shock_bank': bank,
                        'horizon': h,
                        'coef': coef,
                        'se': se,
                        'pvalue': pvalue,
                        'ci_lower': coef - 1.96 * se,
                        'ci_upper': coef + 1.96 * se,
                    }
                )

    return pd.DataFrame(rows)


def run_joint_lp(df_base, left_model, right_model):
    left_shocks = load_model_shocks(left_model, suffix=f'{left_model}_')
    right_shocks = load_model_shocks(right_model, suffix=f'{right_model}_')
    df = df_base.copy()

    for bank in BANKS:
        df = df.set_index('Date').join(left_shocks[bank].set_index('Date'), how='left').reset_index(drop=False)
        df = df.set_index('Date').join(right_shocks[bank].set_index('Date'), how='left').reset_index(drop=False)

    shock_cols = []
    for bank in BANKS:
        shock_cols.extend([f'{bank}_{left_model}_shock', f'{bank}_{right_model}_shock'])
    df[shock_cols] = df[shock_cols].fillna(0)

    rows = []
    for market_name, params in MARKETS.items():
        idx_col = params['index_col']
        vix_col = params['vix_col']

        work = df.copy()
        for model_key in [left_model, right_model]:
            fed_raw = f'fed_{model_key}_shock'
            work[f'fed_{model_key}_aligned'] = work[fed_raw].shift(1).fillna(0) if params['shift_fed'] else work[fed_raw]
            work[f'ecb_{model_key}_aligned'] = work[f'ecb_{model_key}_shock']
            work[f'boe_{model_key}_aligned'] = work[f'boe_{model_key}_shock']

        work = add_controls(work, idx_col, vix_col)
        regressors = [
            f'{bank}_{model_key}_aligned'
            for model_key in [left_model, right_model]
            for bank in BANKS
        ] + ['market_lag1', 'market_lag2', 'vix_lag1', 'vix_lag2']

        for h in range(MAX_H + 1):
            col_name = f'delta_y_h{h}'
            work[col_name] = work[idx_col].shift(-h) - work[idx_col].shift(1)
            temp_df = work[[col_name] + regressors].dropna()

            y = temp_df[col_name]
            x = sm.add_constant(temp_df[regressors])
            model = sm.OLS(y, x).fit(cov_type='HAC', cov_kwds={'maxlags': h + 1})

            for bank in BANKS:
                left_col = f'{bank}_{left_model}_aligned'
                right_col = f'{bank}_{right_model}_aligned'
                test = model.t_test(f'{left_col} - {right_col} = 0')
                ci_low, ci_high = np.asarray(test.conf_int(alpha=0.05)).squeeze()

                left_coef = model.params[left_col]
                right_coef = model.params[right_col]
                left_se = model.bse[left_col]
                right_se = model.bse[right_col]

                rows.append(
                    {
                        'market': market_name,
                        'shock_bank': bank,
                        'horizon': h,
                        'joint_left_coef': left_coef,
                        'joint_left_se': left_se,
                        'joint_left_pvalue': model.pvalues[left_col],
                        'joint_left_ci_lower': left_coef - 1.96 * left_se,
                        'joint_left_ci_upper': left_coef + 1.96 * left_se,
                        'joint_right_coef': right_coef,
                        'joint_right_se': right_se,
                        'joint_right_pvalue': model.pvalues[right_col],
                        'joint_right_ci_lower': right_coef - 1.96 * right_se,
                        'joint_right_ci_upper': right_coef + 1.96 * right_se,
                        'diff_coef': as_scalar(test.effect),
                        'diff_se': as_scalar(test.sd),
                        'diff_pvalue': as_scalar(test.pvalue),
                        'diff_ci_lower': as_scalar(ci_low),
                        'diff_ci_upper': as_scalar(ci_high),
                    }
                )

    return pd.DataFrame(rows)


def build_summary_table(combined, left_model, right_model):
    rows = []
    for market in MARKETS:
        for bank in BANKS:
            row = {
                'panel': f"{SHOCK_LABELS[bank]} x {MARKET_LABELS[market]}",
                'shock_bank': bank,
                'market': market,
            }
            for horizon in REPORT_HORIZONS:
                sub = combined[
                    (combined['market'] == market)
                    & (combined['shock_bank'] == bank)
                    & (combined['horizon'] == horizon)
                ].iloc[0]
                row[f'h{horizon}_{left_model}_standalone'] = fmt(
                    sub['standalone_left_coef'],
                    sub['standalone_left_ci_lower'],
                    sub['standalone_left_ci_upper'],
                    sub['standalone_left_pvalue'],
                )
                row[f'h{horizon}_{right_model}_standalone'] = fmt(
                    sub['standalone_right_coef'],
                    sub['standalone_right_ci_lower'],
                    sub['standalone_right_ci_upper'],
                    sub['standalone_right_pvalue'],
                )
                row[f'h{horizon}_{left_model}_joint'] = fmt(
                    sub['joint_left_coef'],
                    sub['joint_left_ci_lower'],
                    sub['joint_left_ci_upper'],
                    sub['joint_left_pvalue'],
                )
                row[f'h{horizon}_{right_model}_joint'] = fmt(
                    sub['joint_right_coef'],
                    sub['joint_right_ci_lower'],
                    sub['joint_right_ci_upper'],
                    sub['joint_right_pvalue'],
                )
                row[f'h{horizon}_diff'] = fmt(
                    sub['diff_coef'],
                    sub['diff_ci_lower'],
                    sub['diff_ci_upper'],
                    sub['diff_pvalue'],
                )
            rows.append(row)
    return pd.DataFrame(rows)


def main():
    os.makedirs('output/causal-machinery/robustness', exist_ok=True)

    print(f'Running standalone and joint LP comparison for {LEFT_MODEL} vs {RIGHT_MODEL}...')
    df_base = load_market_base()

    standalone_left = run_standalone_lp(df_base, LEFT_MODEL).rename(
        columns={
            'coef': 'standalone_left_coef',
            'se': 'standalone_left_se',
            'pvalue': 'standalone_left_pvalue',
            'ci_lower': 'standalone_left_ci_lower',
            'ci_upper': 'standalone_left_ci_upper',
        }
    )
    standalone_right = run_standalone_lp(df_base, RIGHT_MODEL).rename(
        columns={
            'coef': 'standalone_right_coef',
            'se': 'standalone_right_se',
            'pvalue': 'standalone_right_pvalue',
            'ci_lower': 'standalone_right_ci_lower',
            'ci_upper': 'standalone_right_ci_upper',
        }
    )
    joint = run_joint_lp(df_base, LEFT_MODEL, RIGHT_MODEL)

    merge_keys = ['market', 'shock_bank', 'horizon']
    combined = standalone_left.merge(
        standalone_right[merge_keys + [
            'standalone_right_coef',
            'standalone_right_se',
            'standalone_right_pvalue',
            'standalone_right_ci_lower',
            'standalone_right_ci_upper',
        ]],
        on=merge_keys,
        how='inner',
    ).merge(joint, on=merge_keys, how='inner')

    detailed_path = (
        f'output/causal-machinery/robustness/'
        f'{LEFT_MODEL}_vs_{RIGHT_MODEL}_standalone_and_joint_detailed.csv'
    )
    combined.to_csv(detailed_path, index=False)
    print(f'Saved detailed comparison: {detailed_path}')

    summary = build_summary_table(combined, LEFT_MODEL, RIGHT_MODEL)
    summary_path = (
        f'output/causal-machinery/robustness/'
        f'{LEFT_MODEL}_vs_{RIGHT_MODEL}_standalone_and_joint_summary.csv'
    )
    summary.to_csv(summary_path, index=False)
    print(f'Saved summary comparison: {summary_path}')

    print('\nSummary table')
    print('(Standalone columns = each model estimated separately; joint columns = both models in one regression; diff = left minus right)\n')
    print(summary.to_markdown(index=False))


if __name__ == '__main__':
    main()
