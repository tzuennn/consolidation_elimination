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

    # Create a normalized key: (A, B) is same as (B, A)
    internal_df['Key'] = internal_df.apply(
        lambda row: f"{min(row['Company'], row['Counterparty'])}|{max(row['Company'], row['Counterparty'])}|{row['AccountType']}",
        axis=1
    )
    # Group by Key and check for mismatches
    grouped = internal_df.groupby('Key')['Amount'].sum().reset_index()
    mismatches = grouped[grouped['Amount'].abs() > 1e-2]  # Allow tiny float errors

    return mismatches

def compute_consolidated(df):
    external_df = df[~df['Is_Internal']]
    revenue = external_df[external_df['AccountType'] == 'Revenue']['Amount'].sum()
    expense = external_df[external_df['AccountType'] == 'Expense']['Amount'].sum()
    profit = revenue + expense
    return revenue, expense, profit

def main():
    transactions_csv = 'data/transactions.csv'
    group_config_txt = 'config/group_companies.txt'

    df, group_companies = load_data(transactions_csv, group_config_txt)
    df = tag_internal_transactions(df, group_companies)

    mismatches = check_internal_mismatches(df)
    if not mismatches.empty:
        print("\n⚠️ Internal Transaction Mismatches Detected:")
        print(mismatches.to_string(index=False))
        print("❗ These should be reviewed and adjusted before consolidation.\n")
    else:
        print("\n✅ All internal transactions are matched correctly.")

    revenue, expense, profit = compute_consolidated(df)

    print("\n✅ Consolidated Financial Summary:")
    print(f"  - Revenue: {revenue:,.0f}")
    print(f"  - Expense: {expense:,.0f}")
    print(f"  - Net Profit: {profit:,.0f}")

    # Optional: save tagged version for audit
    output_file = 'data/tagged_transactions.csv'
    df.to_csv(output_file, index=False)
    print(f"\n Tagged transactions saved to: {output_file}")

if __name__ == "__main__":
    main()
