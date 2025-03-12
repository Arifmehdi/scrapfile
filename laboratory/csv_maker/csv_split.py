import pandas as pd


# Load the CSV file
file_path = 'detail_20000_backup_raw.csv'  # Replace with your file path
df = pd.read_csv(file_path)

# Define the chunk size
chunk_size = 2000

# Calculate the number of chunks needed
num_chunks = len(df) // chunk_size + (1 if len(df) % chunk_size else 0)

# Split the DataFrame and save each chunk as a separate CSV file
for i in range(num_chunks):
    start_idx = i * chunk_size
    end_idx = start_idx + chunk_size
    chunk = df[start_idx:end_idx]
    
    # Save the chunk to a new CSV file
    chunk.to_csv(f'chunk_{i+1}.csv', index=False)

print(f'Split into {num_chunks} files.')