import sys

def check_parity(aux_file):
    with open(aux_file, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        if "\\@writefile{toc}{\\contentsline {chapter}" in line:
            parts = line.split("}{")
            if len(parts) >= 3:
                try:
                    page_num = int(parts[2].split("}")[0])
                    chapter_name = parts[1].split("}")[-1]
                    print(f"Chapter '{chapter_name}' starts on page {page_num}. {'OK (odd)' if page_num % 2 != 0 else 'ERROR (even)'}")
                except Exception as e:
                    pass

if __name__ == "__main__":
    check_parity(".build/my-thesis.aux")
