import pandas as pd
import numpy as np
import timeit

# Generate sample data
np.random.seed(0)
n_rows = 100000

data = {
    'B19013_001E': np.random.randint(1, 100000, n_rows).astype(str),
    'B19301_001E': np.random.randint(1, 100000, n_rows).astype(str),
    'B23025_002E': np.random.randint(1, 100000, n_rows).astype(str),
    'B23025_003E': np.random.randint(1, 100000, n_rows).astype(str),
    'B23025_004E': np.random.randint(1, 100000, n_rows).astype(str),
    'B23025_005E': np.random.randint(1, 100000, n_rows).astype(str),
    'state': np.random.randint(1, 50, n_rows).astype(str),
}

df_original = pd.DataFrame(data)

def original_method(df):
    numeric_columns = ['B19013_001E', 'B19301_001E', 'B23025_002E',
                      'B23025_003E', 'B23025_004E', 'B23025_005E']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df['state'] = pd.to_numeric(df['state'], errors='coerce')
    return df

def optimized_method(df):
    numeric_columns = ['B19013_001E', 'B19301_001E', 'B23025_002E',
                      'B23025_003E', 'B23025_004E', 'B23025_005E']
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
    df['state'] = pd.to_numeric(df['state'], errors='coerce')
    return df

# Test for equivalence
df1 = original_method(df_original.copy())
df2 = optimized_method(df_original.copy())
pd.testing.assert_frame_equal(df1, df2)

time_original = timeit.timeit("original_method(df_original.copy())", globals=globals(), number=10)
time_optimized = timeit.timeit("optimized_method(df_original.copy())", globals=globals(), number=10)

print(f"Original: {time_original:.4f}s")
print(f"Optimized: {time_optimized:.4f}s")
print(f"Improvement: {(time_original - time_optimized) / time_original * 100:.2f}%")
