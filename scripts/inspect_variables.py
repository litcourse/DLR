import pyreadstat

def inspect_file(file_path, output_path):
    print(f"Reading metadata from {file_path}...")
    _, metadata = pyreadstat.read_sav(file_path, metadataonly=True)
    
    variables = metadata.column_names
    labels = metadata.column_labels
    var_to_label = dict(zip(variables, labels))
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Total variables: {len(variables)}\n\n")
        f.write("Variables and Labels:\n")
        for var, label in var_to_label.items():
            f.write(f"{var} | {label}\n")
            
    print(f"Saved metadata to {output_path}")

def main():
    inspect_file("data/CY08MSP_STU_QQQ.SAV", "student_variables.txt")
    inspect_file("data/CY08MSP_SCH_QQQ.SAV", "school_variables.txt")

if __name__ == "__main__":
    main()
