
# Consolidation Accounting Automation

This project automates the process of preparing consolidated simple financial statements from multiple company transaction records using Python.

---

## Folder Structure

```
consolidation_project/
├── consolidate.py               # Main script (Python code)
├── data/
│   └── transactions.csv         # Input transaction data
|   └── tagged_transactions.csv  # Auto-generated: tagged and cleaned dataset   
├── config/
    └── group_companies.txt      # List of companies in the group
   
```

---

## Input Files

### 1. `transactions.csv`

This file contains all the accounting transactions for various companies. Each row represents one side of a transaction.

| Column         | Description                                                                 |
|----------------|-----------------------------------------------------------------------------|
| `TransactionID`| Unique ID per transaction (for traceability)                                |
| `Company`      | The reporting company                                                       |
| `Counterparty` | The party on the other side of the transaction                              |
| `AccountType`  | Type of transaction: `Revenue` or `Expense`                                 |
| `Amount`       | Amount (positive for revenue, negative for expense)                         |
| `Description`  | Free text explanation of the transaction                                    |

#### 📌 Example:

```csv
TransactionID,Company,Counterparty,AccountType,Amount,Description
TXN001,A,X,Revenue,600000,External sale by A
TXN002,A,X,Expense,-200000,External expense A
TXN007,A,B,Revenue,70000,Internal sale A → B
TXN008,B,A,Expense,-70000,Internal purchase B ← A
.
.
.
```

### 2. `group_companies.txt`

Plain text file listing group companies — one per line.

```txt
A
B
C
```

---

## ▶️ How to Run

```bash
python consolidate.py
```

---

## ⚙️ What the Script Does

1. Loads the transactions and group config
2. Tags each transaction as internal or external
3. Validates that internal transactions are properly matched between group entities
4. Aborts if mismatches are found
5. Computes consolidated revenue, expense, and net profit from external transactions
6. Outputs a tagged copy to `data/tagged_transactions.csv`

---

## 📊 Sample Output

```
✅ All internal transactions are matched correctly.

✅ Consolidated Financial Summary:
  - Revenue: 1,400,000
  - Expense: -600,000
  - Net Profit: 800,000

📁 Tagged transactions saved to: data/tagged_transactions.csv
```

If mismatches are found:

```
Internal Transaction Mismatches Detected — Consolidation aborted:
EntityPair  Revenue  Expense  Net_Internal
A|B         70,000   -60,000        10,000
```

---

## Why It Works

This approach ensures:

- Internal revenue/expenses are eliminated for accurate group performance
- Only external transactions contribute to reported profit
- Errors from data entry mismatches are detected early

---

## 🔧 Future Improvements

- Export mismatch reports to CSV or Excel
- Allow filtering by date or year
- Add CLI flags to control output
