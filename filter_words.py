import re
from collections import OrderedDict

def process_file(input_file):
    with open(input_file, 'r') as f:
        lines = [(i+1, line.strip()) for i, line in enumerate(f) if line.strip()]
    
    # Create word arrays with line numbers
    word_arrays = [(num, re.split(r'\s+', line)) for num, line in lines]
    operations = []
    merged_indices = set()
    
    # Compare all pairs of lines
    for i in range(len(word_arrays)):
        if i in merged_indices:
            continue
            
        line1_num, arr1 = word_arrays[i]
        set1 = set(arr1)
        
        for j in range(i+1, len(word_arrays)):
            if j in merged_indices:
                continue
                
            line2_num, arr2 = word_arrays[j]
            set2 = set(arr2)
            
            # Rule 1: Remove if lines are reverse (as sets)
            if set1 == set2:
                operations.append(f"Deleted reverse line {line2_num}: {' '.join(arr2)}")
                merged_indices.add(j)
                continue
                
            # Rule 2: Remove if one line is subset of another
            if set1.issubset(set2):
                operations.append(f"Deleted subset line {line1_num}: {' '.join(arr1)}")
                merged_indices.add(i)
                break
            elif set2.issubset(set1):
                operations.append(f"Deleted subset line {line2_num}: {' '.join(arr2)}")
                merged_indices.add(j)
                continue
                
            # Rule 3: Merge if lines share some words
            common = set1 & set2
            if common:
                merged = list(OrderedDict.fromkeys(arr1 + arr2))
                operations.append(f"Merged lines:\n  Line {line1_num}: {' '.join(arr1)}\n  Line {line2_num}: {' '.join(arr2)}\n  Into: {' '.join(merged)}")
                word_arrays[i] = (line1_num, merged)
                merged_indices.add(j)
                break
    
    # Prepare final result
    result = []
    for idx, (num, arr) in enumerate(word_arrays):
        if idx not in merged_indices:
            result.append(' '.join(arr))
    
    # Write operations to log file
    with open('filter_operations.log', 'w') as log:
        log.write("\n".join(operations))
    
    print("=== Operations Log ===")
    print("\n".join(operations))
    print("\n=== Final Result ===")
    return '\n'.join(result)

if __name__ == '__main__':
    output = process_file('待过滤句子')
    print(output)
