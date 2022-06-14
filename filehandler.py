import os
import shutil
import csv

def read(path):
    if path.endswith('.csv'):
        return read_csv(path)

    return read_file(path)

def write(path, content, header=[]):
    if path.endswith('.csv'):
        write_csv(path, content, header)
        return

    write_file(path, content)
    return

def read_file(path):
    content = []
    with open(path, 'r') as fh:
        content.append(fh.readline())
    return content

def write_file(path, content):
    content_with_newline = [x + '\n' for x in content]
    content_with_newline[-1] = content[-1]
    
    with open(path, 'w') as fh:
        fh.writelines(content_with_newline)

def read_csv(path):
    content = []
    with open(path, 'r', newline='') as fh:
        content = csv.DictReader(fh)
    return content

def write_csv(path, content, header):
    with open(path, 'w', newline='') as fh:
        writer = csv.DictWriter(fh, header)
        writer.writeheader()
        for i in range(len(content)):
            writer.writerow(content[i])
