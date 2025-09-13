import re
from collections import OrderedDict
import argparse

def process_file(input_file):
    with open(input_file, 'r') as f:
        lines = [(i+1, line.strip()) for i, line in enumerate(f) if line.strip()]
    
    # Create word arrays with line numbers
    word_arrays = [(num, re.split(r'\s+', line)) for num, line in lines]
    operations = []
    removed_indices = set()
    
    # Compare all pairs of lines
    for i in range(len(word_arrays)):
        if i in removed_indices:
            continue
            
        line1_num, arr1 = word_arrays[i]
        set1 = set(arr1)
        
        for j in range(i+1, len(word_arrays)):
            if j in removed_indices:
                continue
                
            line2_num, arr2 = word_arrays[j]
            set2 = set(arr2)
            
            # Rule 1: Remove if lines are identical (as sets)
            if set1 == set2:
                operations.append(f"Deleted duplicate line {line2_num}: {' '.join(arr2)}")
                removed_indices.add(j)
                continue
                
            # Rule 2: Remove if one line is subset of another
            if set1.issubset(set2):
                operations.append(f"Deleted subset line {line1_num}: {' '.join(arr1)}")
                removed_indices.add(i)
                break
            elif set2.issubset(set1):
                operations.append(f"Deleted subset line {line2_num}: {' '.join(arr2)}")
                removed_indices.add(j)
                continue
    
    # Prepare final result
    result = []
    for idx, (num, arr) in enumerate(word_arrays):
        if idx not in removed_indices:
            result.append(' '.join(arr))
    
    # Write operations to log file
    with open('filter_operations.log', 'w') as log:
        log.write("\n".join(operations))
    
    print("=== Operations Log ===")
    print("\n".join(operations))
    print("\n=== Final Result ===")
    return '\n'.join(result)

def main():
    parser = argparse.ArgumentParser(description='Filter text file content (remove duplicates and subsets)')
    parser.add_argument('-i', '--input', default='待过滤句子', help='Input file path')
    parser.add_argument('-o', '--output', default='过滤后句子', help='Output file path')
    args = parser.parse_args()

    output = process_file(args.input)
    
    # Write to output file
    with open(args.output, 'w') as f:
        f.write(output)
    print(f"Filtered content saved to {args.output}")

if __name__ == '__main__':
    main()
