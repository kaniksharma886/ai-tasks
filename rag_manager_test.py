import time
import numpy as np
import rag_manager
import utils


# Answer key for req 3.2 (d)

QUERIES = [

    {"query": "Who said 'I should not shout, if I were you'?", "src": "file1.txt"},
    {"query": "Who does a lot of 'sitting and thinking' these days?", "src": "file1.txt"},
    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"},
    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"},
    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"},

    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"},
    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"},
    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"},
    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"},
    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"},

    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"},
    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"},
    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"},
    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"},
    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"},

    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"},
    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"},
    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"},
    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"},
    {"query": "Who is saying 'And you’re all dirty, too, Telescope'?", "src": "faile2.txt"}
   
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

    utils.log(f"""
METRICS TEST REPORT

Total Queries    : {tot_cnt}")
Top-5 RAG Passed : {pass_cnt}
Top-5 RAG Failed : {(tot_cnt - pass_cnt)}

P50 Latency      : {p50_time} ms
P95 Latency      : {p95_time} ms
P99 Latency      : {p99_time} ms
"""


if __name__ == "__main__":
    create_test_report()