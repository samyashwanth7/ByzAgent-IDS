"""Merge archive CSVs into thursday.csv and tuesday.csv"""
import pandas as pd
from pathlib import Path

raw = Path(r'C:\Users\sampa\Documents\vs code programs\Capstone\XFed-IDS\data\raw')
archive = raw / 'archive'

existing = [f.name for f in raw.glob('*.csv')]
print(f'Existing CSVs: {existing}')

# Thursday
thu_files = sorted(archive.glob('Thursday*.csv'))
if thu_files and 'thursday.csv' not in existing:
    print(f'Merging {len(thu_files)} Thursday files...')
    dfs = [pd.read_csv(f, low_memory=False) for f in thu_files]
    df = pd.concat(dfs, ignore_index=True)
    df.to_csv(raw / 'thursday.csv', index=False)
    print(f'  thursday.csv: {len(df)} rows')

# Tuesday
tue_files = sorted(archive.glob('Tuesday*.csv'))
if tue_files and 'tuesday.csv' not in existing:
    print(f'Merging {len(tue_files)} Tuesday files...')
    dfs = [pd.read_csv(f, low_memory=False) for f in tue_files]
    df = pd.concat(dfs, ignore_index=True)
    df.to_csv(raw / 'tuesday.csv', index=False)
    print(f'  tuesday.csv: {len(df)} rows')

print('Done!')
final = [f.name for f in raw.glob('*.csv')]
print(f'Final CSVs: {final}')
