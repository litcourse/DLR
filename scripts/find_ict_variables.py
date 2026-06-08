def search_vars(input_path, output_path, keywords):
    matches = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line_lower = line.lower()
            if any(kw in line_lower for kw in keywords):
                matches.append(line.strip())
                
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"Found {len(matches)} matches for keywords {keywords}:\n\n")
        for m in matches:
            f.write(m + "\n")
            
    print(f"Saved {len(matches)} matches from {input_path} to {output_path}")

def main():
    keywords = ["ict", "digital", "computer", "internet", "software", "device", "tablet", "phone"]
    search_vars("student_variables.txt", "ict_student_variables.txt", keywords)
    search_vars("school_variables.txt", "ict_school_variables.txt", keywords)

if __name__ == "__main__":
    main()
