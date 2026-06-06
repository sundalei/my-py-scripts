DATASET_FILE_PATH = "top-movies-kibana.txt"


def read_file_in_chunks(file_path: str, line_per_chunk: int):
    """
    Read a pre-formatted ND JSON file and yields text chunks.
    lines_per_chunk must be an even number to keep action/document pairs intact.
    """
    # Force line_per_chunk to be an even number
    if line_per_chunk % 2 != 0:
        line_per_chunk += 1
    
    chunk = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        batch_num = 0
        for line in f:
            chunk.append(line)

            # When we hit our limit, join the lines and yield
            if len(chunk) >= line_per_chunk:
                batch_num += 1
                print(f"Batch size: {line_per_chunk}, Processing batch {batch_num}")
                yield "".join(chunk)
                chunk = [] # Reset for the next batch
        
        # Yield any leftover lines at the end of the file
        if chunk:
            # Ensure it ends with a newline, as required by the bulk API
            print("Process leftover batch")
            payload = "".join(chunk)
            if not payload.endswith('\n'):
                payload += '\n'
            yield payload


def run_rest_bulk_index(file_path: str):
    """
    Execute the bulk request.
    """
    print(f"Starting bulk index from file '{file_path}'...")

    success_total = 0
    error_total = 0

    # 1000 lines = 500 documents per request
    gen = read_file_in_chunks(file_path, line_per_chunk=4)
    
    for i, chunk in enumerate(gen):
        print(f"{i}\n{chunk}")


if __name__ == "__main__":
    run_rest_bulk_index(DATASET_FILE_PATH)
