import pandas as pd

files = [
    'products.csv', 'customers.csv', 'orders.csv', 'order_items.csv',
    'payments.csv', 'shipments.csv', 'returns.csv', 'reviews.csv',
    'inventory.csv', 'web_traffic.csv', 'promotions.csv', 'geography.csv'
]

for f in files:
    df = pd.read_csv(f'data/{f}', nrows=2)
    rows = sum(1 for _ in open(f'data/{f}')) - 1
    print(f'{f}: {rows} rows, cols={list(df.columns)}')
    print(f'  dtypes: {dict(df.dtypes)}')
    print()
