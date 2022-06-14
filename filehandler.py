import os
import shutil
import csv

def read(path):
    if path.endswith('.csv'):
        return read_csv(path)

    return read_file(path)

def write(path, content, header=[]):
    if path.endswith('.csv'):
        return write_csv(path, content, header)

    return write_file(path, content)

def read_file(path):
    content = []
    try:
        with open(path, 'r') as fh:
            content = fh.read().splitlines()
    except Exception:
        content = []
    return content

def write_file(path, content):
    if not content:
        return True
    
    content_with_newline = [x + '\n' for x in content]
    content_with_newline[-1] = content[-1]
    try:
        with open(path, 'w') as fh:
            fh.writelines(content_with_newline)
    except Exception:
        return False
    return True

def read_csv(path):
    content = []
    try:
        with open(path, 'r', newline='') as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                content.append(row)
            
    except Exception:
        content = []
    return content

def write_csv(path, content, header):
    try:
        with open(path, 'w', newline='') as fh:
            writer = csv.DictWriter(fh, header)
            writer.writeheader()
            for i in range(len(content)):
                writer.writerow(content[i])
    except Exception:
        return False
    return True
