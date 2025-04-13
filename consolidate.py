import pandas as pd

def load_data(transactions_csv, group_config_txt):
    df = pd.read_csv(transactions_csv)
    with open(group_config_txt, 'r') as f:
        group_companies = {line.strip() for line in f if line.strip()}
    return df, group_companies

def tag_internal_transactions(df, group_companies):
    df['Is_Internal'] = df.apply(
        lambda row: row['Company'] in group_companies and row['Counterparty'] in group_companies,
        axis=1
    )
    return df

def check_internal_mismatches(df):
    internal_df = df[df['Is_Internal']].copy()

    # Normalize entity pairs regardless of direction
    internal_df['EntityPair'] = internal_df.apply(
        lambda row: '|'.join(sorted([row['Company'], row['Counterparty']])), axis=1
    )

    # Group by pair and account type
    summary = (
        internal_df.groupby(['EntityPair', 'AccountType'])['Amount']
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )

    # Compute net: Revenue + Expense (since Expense is negative)
    summary['Net_Internal'] = summary.get('Revenue', 0) + summary.get('Expense', 0)
    mismatches = summary[summary['Net_Internal'].abs() > 1e-2]

    return mismatches[['EntityPair', 'Revenue', 'Expense', 'Net_Internal']]

def compute_consolidated(df):
    external_df = df[~df['Is_Internal']]
    revenue = external_df[external_df['AccountType'] == 'Revenue']['Amount'].sum()
    expense = external_df[external_df['AccountType'] == 'Expense']['Amount'].sum()
    profit = revenue + expense
    return revenue, expense, profit

def main():
    transactions_csv = 'data/transactions.csv'
    group_config_txt = 'config/group_companies.txt'

    try:
        df, group_companies = load_data(transactions_csv, group_config_txt)
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return

    # Check columns
    required_columns = {'Company', 'Counterparty', 'AccountType', 'Amount'}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        print(f"Missing required columns in CSV: {missing}")
        return

    df = tag_internal_transactions(df, group_companies)

    # Step 1: Check for internal mismatches
    mismatches = check_internal_mismatches(df)
    if not mismatches.empty:
        print("\nInternal Transaction Mismatches Detected — Consolidation aborted:")
        print(mismatches.to_string(index=False))
        print("❗ Please review and resolve these issues before proceeding.\n")
        return
    else:
        print("\n✅ All internal transactions are matched correctly.")

    # Step 2: Compute consolidated financials
    revenue, expense, profit = compute_consolidated(df)
    print("\n✅ Consolidated Financial Summary:")
    print(f"  - Revenue: {revenue:,.0f}")
    print(f"  - Expense: {expense:,.0f}")
    print(f"  - Net Profit: {profit:,.0f}")

    # Step 3: Save tagged file
    output_file = 'data/tagged_transactions.csv'
    df.to_csv(output_file, index=False)
    print(f"\n📁 Tagged transactions saved to: {output_file}")

if __name__ == "__main__":
    main()
