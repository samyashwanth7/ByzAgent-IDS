"""XFed-IDS Dataset Loading and Preprocessing"""
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import torch
from torch.utils.data import Dataset, DataLoader

import sys
sys.path.append(str(Path(__file__).parent.parent))
from config import RAW_DIR, PROCESSED_DIR, BATCH_SIZE, RANDOM_SEED, BINARY_CLASSIFICATION, ATTACK_CLASSES


class IDSDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.LongTensor(y)
    def __len__(self):
        return len(self.y)
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


def _map_label_to_class(label_str):
    """Map a CICIDS-2017 label string to one of our 8 consolidated classes."""
    label = str(label_str).strip()
    label_upper = label.upper()

    if label_upper == 'BENIGN':
        return 0  # BENIGN

    # DDoS / DoS variants
    ddos_keywords = ['DDOS', 'DOS HULK', 'DOS GOLDENEYE', 'DOS SLOWLORIS', 'DOS SLOWHTTPTEST']
    for kw in ddos_keywords:
        if kw in label_upper:
            return 1  # DDoS

    if 'PORTSCAN' in label_upper:
        return 2  # PortScan

    # Brute Force (FTP-Patator, SSH-Patator)
    if 'PATATOR' in label_upper:
        return 3  # Brute Force

    # Web Attacks
    if 'WEB ATTACK' in label_upper:
        return 4  # Web Attack

    if 'INFILTRATION' in label_upper:
        return 5  # Infiltration

    if 'BOT' in label_upper:
        return 6  # Bot

    if 'HEARTBLEED' in label_upper:
        return 7  # Heartbleed

    # Fallback: treat unknown as class 1 (generic attack)
    return 1


def load_cicids2017(data_dir=None, force_reload=False):
    if data_dir is None:
        data_dir = RAW_DIR

    # Use different cache files for binary vs multi-class
    if BINARY_CLASSIFICATION:
        processed_file = PROCESSED_DIR / 'cicids2017_processed.pkl'
    else:
        processed_file = PROCESSED_DIR / 'cicids2017_multiclass.pkl'

    if processed_file.exists() and not force_reload:
        print('Loading preprocessed data from {}...'.format(processed_file))
        with open(processed_file, 'rb') as f:
            data = pickle.load(f)
        print('  Loaded: {} train, {} test samples'.format(len(data['X_train']), len(data['X_test'])))
        print('  Features: {}'.format(data['X_train'].shape[1]))
        print('  Classes: {} -- {}'.format(len(data['label_names']), data['label_names']))
        return (data['X_train'], data['X_test'], data['y_train'], data['y_test'],
                data['feature_names'], data['label_names'])

    print('=' * 60)
    print('  Loading CICIDS 2017 Dataset')
    print('=' * 60)

    # Find CSV files - use archive/ if it exists and has CSVs, else use raw/
    # IMPORTANT: Do NOT combine both -- they may have different column schemas
    archive_dir = Path(data_dir) / 'archive'
    if archive_dir.exists():
        csv_files = sorted(archive_dir.glob('*.csv'))
    else:
        csv_files = []

    if not csv_files:
        csv_files = sorted([f for f in Path(data_dir).glob('*.csv') if '_plus' not in f.stem])

    if not csv_files:
        raise FileNotFoundError('No CSV files found in {} or {}'.format(data_dir, archive_dir))

    print('Found {} CSV files:'.format(len(csv_files)))
    dfs = []
    for f in csv_files:
        print('  Reading {}...'.format(f.name))
        df = pd.read_csv(f, low_memory=False, encoding='utf-8')
        # CRITICAL: strip whitespace from column names (UNB files have leading spaces)
        df.columns = df.columns.str.strip()
        dfs.append(df)

    df = pd.concat(dfs, ignore_index=True)
    print('Total records: {:,}'.format(len(df)))

    # Find label column
    label_col = None
    for col in df.columns:
        if col.strip().lower() == 'label':
            label_col = col
            break
    if label_col is None:
        raise ValueError('No label column found. Columns: {}'.format(list(df.columns)[:10]))

    # Drop identifier columns (case insensitive matching)
    drop_patterns = ['source ip', 'destination ip', 'src ip', 'dst ip',
                     'src port', 'dst port', 'source port', 'destination port',
                     'timestamp', 'flow id', 'attempted category']
    drop_cols = []
    for col in df.columns:
        col_lower = col.strip().lower()
        for pattern in drop_patterns:
            if pattern in col_lower and col not in drop_cols and col != label_col:
                drop_cols.append(col)
                break

    if drop_cols:
        df = df.drop(columns=drop_cols)
        print('Dropped identifier columns: {}'.format(drop_cols))

    labels = df[label_col]
    features = df.drop(columns=[label_col])
    features = features.apply(pd.to_numeric, errors='coerce')
    features = features.replace([np.inf, -np.inf], np.nan)
    valid_mask = features.notna().all(axis=1)
    features = features[valid_mask]
    labels = labels[valid_mask]
    print('After cleaning NaN/Inf: {:,} records'.format(len(features)))

    n_before = len(features)
    combined = features.copy()
    combined['_label'] = labels.values
    combined = combined.drop_duplicates()
    labels = combined['_label']
    features = combined.drop(columns=['_label'])
    print('Dropped {:,} duplicate rows'.format(n_before - len(features)))
    print('Final features: {}'.format(features.shape[1]))

    # Encode labels
    if BINARY_CLASSIFICATION:
        print('Encoding labels (Binary: BENIGN vs ATTACK)...')
        encoded_labels = labels.apply(lambda x: 0 if str(x).strip().upper() == 'BENIGN' else 1)
        label_names = ['BENIGN', 'ATTACK']
    else:
        print('Encoding labels (Multi-Class: {} categories)...'.format(len(ATTACK_CLASSES)))
        encoded_labels = labels.apply(_map_label_to_class)
        label_names = list(ATTACK_CLASSES)

    # Print class distribution
    print('\n  Class distribution:')
    for i, name in enumerate(label_names):
        count = (encoded_labels == i).sum()
        pct = count / len(encoded_labels) * 100 if len(encoded_labels) > 0 else 0
        print('    [{}] {}: {:,} ({:.2f}%)'.format(i, name, count, pct))

    feature_names = list(features.columns)
    X = features.values.astype(np.float32)
    y = encoded_labels.values.astype(np.int64)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_SEED, stratify=y
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    print('Train: {:,} samples'.format(len(X_train)))
    print('Test:  {:,} samples'.format(len(X_test)))

    data = {
        'X_train': X_train, 'X_test': X_test,
        'y_train': y_train, 'y_test': y_test,
        'feature_names': feature_names, 'label_names': label_names
    }
    with open(processed_file, 'wb') as f:
        pickle.dump(data, f)
    print('Saved processed data to {}'.format(processed_file))
    return X_train, X_test, y_train, y_test, feature_names, label_names


def partition_data_iid(X, y, num_clients=3):
    indices = np.random.permutation(len(X))
    splits = np.array_split(indices, num_clients)
    partitions = []
    for i, split in enumerate(splits):
        partitions.append({'X': X[split], 'y': y[split]})
        classes = len(np.unique(y[split]))
        print('  Client {}: {:,} samples, {} classes'.format(i, len(split), classes))
    return partitions


def partition_data_non_iid(X, y, num_clients=3, alpha=0.5):
    print('  Non-IID Partitioning (Dirichlet alpha={}):'.format(alpha))
    classes = np.unique(y)
    client_indices = [[] for _ in range(num_clients)]
    for c in classes:
        class_indices = np.where(y == c)[0]
        np.random.shuffle(class_indices)
        proportions = np.random.dirichlet([alpha] * num_clients)
        splits = (np.cumsum(proportions) * len(class_indices)).astype(int)[:-1]
        class_splits = np.split(class_indices, splits)
        for i in range(num_clients):
            client_indices[i].extend(class_splits[i].tolist())
    partitions = []
    for i in range(num_clients):
        idx = np.array(client_indices[i])
        np.random.shuffle(idx)
        partitions.append({'X': X[idx], 'y': y[idx]})
        cls_counts = ', '.join(['cls{}:{}'.format(c, (y[idx]==c).sum()) for c in classes])
        print('  Client {}: {:,} samples | {}'.format(i, len(idx), cls_counts))
    return partitions


def create_dataloaders(partitions, X_test, y_test, batch_size=256):
    test_dataset = IDSDataset(X_test, y_test)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    client_loaders = []
    for p in partitions:
        train_dataset = IDSDataset(p['X'], p['y'])
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        client_loaders.append((train_loader, test_loader))
    return client_loaders
