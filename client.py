from elasticsearch import Elasticsearch
from datetime import datetime

es = Elasticsearch("localhost:9200")
today = str(datetime.now().strftime('%Y.%m.%d'))
index_name = "sensor_data-{}".format(today)
results = es.search(index=index_name, size=1000, q="experimentid=0")["hits"]["hits"]
count = len(results)
sequence = [int(r["_source"]["sequenceNumber"]) for r in results]
max_sequence = max(sequence)
print count
print max_sequence
print float(count)/max_sequence*100
