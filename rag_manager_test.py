import time
import numpy as np
import rag_manager
import utils


# Answer key for req 3.2 (d)

QUERIES = [

    {"query": "Who said 'I should not shout, if I were you'?", "src": "file1.txt"},
    {"query": "Who does a lot of 'sitting and thinking' these days?", "src": "file1.txt"},
    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "file2.txt"},
    {"query": "What comes after 'At last Mother said to Father'?", "src": "pg1874.txt"},
    {"query": "Who said 'I expect it's the subscription to the Vicar's testimonial'", "src": "pg1874.txt"},
    
    {"query": "Where did Peter cringed and shuffled his boots?", "src": "pg1874.txt"},
    {"query": "Who said 'You'll promise this, too, won't you' ?", "src": "pg1874.txt"},    
    {"query": "Who said 'I do not often laugh, sir'?", "src": "pg1257.txt"},
    {"query": "Who said 'Your Excellency is safe and sound'?", "src": "pg1257.txt"},
    {"query": "Who said 'Exactly as I have the honor to tell your Excellency'?", "src": "pg1257.txt"},

    {"query": "What's the number of capter 'CHRISTMAS AT THE FARM'?", "src": "pg22163.txt"},
    {"query": "Where had coming from the mountains, the three youths expected to go back to?", "src": "pg22163.txt"},
    {"query": "Who asked : Didn't they say some parts were haunted?", "src": "pg22163.txt"},
    {"query": "When was ebook #24375 released ?", "src": "pg24375.txt"},
    {"query": "Who put on his most pleasant expression?", "src": "pg24375.txt"},

    {"query": "Who said 'I would be most grateful'?", "src": "pg24375.txt"},
    {"query": "When was eBook #27609 updates?", "src": "pg27609.txt"},
    {"query": "Who said 'Good luck, my boy, on your journey'?", "src": "pg27609.txt"},
    {"query": "Who was like a symbol from the sunken City?", "src": "pg27609.txt"},
    {"query": "What is the release date of ebook #43936?", "src": "pg43936.txt"}
   
]


def create_test_report():
    try:
        retriever = rag_manager.get_retriever()
    except Exception as e:
        utils.log(f"Error: Failed to get retriever: {e}")
        return

    pass_cnt = 0
    tot_cnt = len(QUERIES)
    rag_latencies = []
    cnt = 0
    
    # This is to mimic actual telemetry format, as that is not in the scope of the task.
    res_template = {
    "id": 0,
    "status": "",
    "latency":0,
    }
    
    for test_case in QUERIES:
        cnt += 1
        query = test_case["query"]
        target_file = test_case["src"]

        # Run high-resolution time profiling on the retrieval layer
        start_mark = time.perf_counter()
        docs = retriever.invoke(query)
        end_mark = time.perf_counter()

        latency_ms = int((end_mark - start_mark) * 1000)
        rag_latencies.append(latency_ms)
        
        top_k_sources = [doc.metadata.get("source") for doc in docs]
        
        status = "FAIL"
        if target_file in top_k_sources:
            pass_cnt += 1
            status = "PASS"
            

        utils.log(f"{cnt}# | Status: {status} | RAG Time: {latency_ms}ms | Exp Source: {target_file} | Found: {top_k_sources}")

    # Calculate metrics
    p50_time = np.median(rag_latencies)
    p95_time = np.percentile(rag_latencies, 95)
    p99_time = np.percentile(rag_latencies, 99)

    res = f"""
METRICS TEST REPORT

Total Queries        : {tot_cnt}

Top-5 RAG Passed     : {pass_cnt}

Top-5 RAG Failed     : {(tot_cnt - pass_cnt)}

P50 Latency (Median) : {p50_time} ms (This should be < 300 ms)

P95 Latency          : {p95_time} ms
"""
    return res, rag_latencies


if __name__ == "__main__":
    res, _ = create_test_report()
    utils.log(res)