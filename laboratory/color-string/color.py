import pandas as pd
import sys

def map_interior_colors(input_file, output_file):
    # Load the CSV file
    df = pd.read_csv(input_file)
    # print(df)
    # sys.exit()
    # Group colors by category
    color_mapping = {}
    for _, row in df.iterrows():
        group = row['Group']
        # color = row['Exteroior Color Name']
        color = row['Interior Color Name']
        if group in color_mapping:
            color_mapping[group].append(color)
        else:
            color_mapping[group] = [color]
    
    # Format as a PHP-style array string
    array_output = "$exteriorColorMapping = [\n"
    for group, colors in color_mapping.items():
        color_list = ', '.join(f'"{color}"' for color in colors)
        array_output += f'    "{group}" => [{color_list}],\n'
    array_output += "]\n"
    
    # Save to text file
    with open(output_file, 'w') as f:
        f.write(array_output)
    
    print(f"Array saved as: {output_file}")

# Example usage
map_interior_colors('interior_color_001.csv', 'interior_color_mapping.txt')
