from pathlib import Path
import config


def log(*msg, end="\n", flush=False):
    print(*msg, end=end, flush=flush)

def log_error(*msg):
    print("[ERROR]", *msg)


def get_file_paths(dir_path = config.RAG_DIR):
    directory_path = Path(dir_path)
    files = []
    for item in directory_path.iterdir():
        if item.is_file() and item.suffix == '.txt':
            files.append(str(item.resolve()))
    return files

'''
Following code is commented to demo how text was ingested.

Requirement 3.2 (a) and (b)

print(get_file_paths())
import rag_manager
rag_manager.insert_text(get_file_paths())

'''