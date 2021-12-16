# PQLite

`PQLite` is an  **Approximate Nearest Neighbor Search** (ANNS) library integrated with the Jina ecosystem.
The `PQLite` class partitions the data into cells at index time, and instantiates a "sub-indexer" in each cell.  Search is performed aggregating results retrieved from cells.

This indexer is recommended to be used when an application requires **search with filters** applied on `Document` tags.
The `filtering query language` is based on [MongoDB's query and projection operators](https://docs.mongodb.com/manual/reference/operator/query/). We currently support a subset of those selectors.
The tags filters can be combined with `$and` and `$or`:

- `$eq` - Equal to (number, string)
- `$ne` - Not equal to (number, string)
- `$gt` - Greater than (number)
- `$gte` - Greater than or equal to (number)
- `$lt` - Less than (number)
- `$lte` - Less than or equal to (number)

For example, we want to search for a product with a price no more than `50$`.
```python
index.search(query, filter={"price": {"$lte": 50}})
```

More example filter expresses

- A Nike shoes with white color

```JSON
{
  "brand": {"$eq": "Nike"},
  "category": {"$eq": "Shoes"},
  "color": {"$eq": "White"}
}
```

Or

```JSON
{
  "$and":
    {
      "brand": {"$eq": "Nike"},
      "category": {"$eq": "Shoes"},
      "color": {"$eq": "White"}
    }
}
```


- A Nike shoes or price less than `100$`

```JSON
{
  "$or":
    {
      "brand": {"$eq": "Nike"},
      "price": {"$lt": 100}
    }
}
```

## Installation

```bash
$ git clone https://github.com/jina-ai/pqlite.git \
  && cd pqlite \
  && pip install -e .
```

**WARNING**: `PQLite` contains code that must be compiled to be used. The build is prepared in `setup.py`. Users only need to `pip install -e .` from the root directory.

## Getting Started

For an in-depth overview of the features of PQLite
you can follow along with one of the examples below:


| Name  | Link  |
|---|---|
| E-commerce product image search with PQLite  | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/jina-ai/pqlite/blob/main/notebooks/fashion_product_search.ipynb)|


## Quick Start

1. Create a new `pqlite`

```python
import random
import numpy as np
from jina import Document, DocumentArray
from pqlite import PQLite

N = 10000 # number of data points
Nq = 10 # number of query data
D = 128 # dimentionality / number of features

# the column schema: (name:str, dtype:type, create_index: bool)
pqlite = PQLite(dim=D, columns=[('price', float)], data_path='./workspace_data')
```

Note that this will create a folder `./workspace_data` where indexed data will be stored.
If there is already a folder with this name and the code presented here is not working remove that folder.


2. Add new data

```python
X = np.random.random((N, D)).astype(np.float32)  # 10,000 128-dim vectors to be indexed
docs = DocumentArray(
    [
        Document(id=f'{i}', embedding=X[i], tags={'price': random.random()})
        for i in range(N)
    ]
)
pqlite.index(docs)
```

3. Search with filtering

```python
Xq = np.random.random((Nq, D)).astype(np.float32)  # a 128-dim query vector
query = DocumentArray([Document(embedding=Xq[i]) for i in range(Nq)])

# without filtering
pqlite.search(query, limit=10)

print(f'the result without filtering:')
for i, q in enumerate(query):
    print(f'query [{i}]:')
    for m in q.matches:
        print(f'\t{m.id} ({m.scores["euclidean"].value})')

# with filtering
pqlite.search(query, filter={"price": {"$lte": 50}}, limit=10)
print(f'the result with filtering:')
for i, q in enumerate(query):
    print(f'query [{i}]:')
    for m in q.matches:
        print(f'\t{m.id} {m.scores["euclidean"].value} (price={m.tags["x"]})')
```

4. Update data

```python
Xn = np.random.random((10, D)).astype(np.float32)  # 10,000 128-dim vectors to be indexed
docs = DocumentArray(
    [
        Document(id=f'{i}', embedding=Xn[i], tags={'price': random.random()})
        for i in range(10)
    ]
)
pqlite.update(docs)
```

5. Delete data

```python
pqlite.delete(['1', '2'])
```

## Benchmark

One can run `executor/benchmark.py` to get a quick performance overview.

|Stored data| Indexing time | Query size=1 | Query size=8 | Query size=64|
|---|---|---|---|---|
|10000 | 2.970 | 0.002 | 0.013 | 0.100|
|100000 | 76.474 | 0.011 | 0.078 | 0.649|
|500000 | 467.936 | 0.046 | 0.356 | 2.823|
|1000000 | 1025.506 | 0.091 | 0.695 | 5.778|


## Research foundations of PQLite

- [Xor Filters](https://lemire.me/blog/2019/12/19/xor-filters-faster-and-smaller-than-bloom-filters/) Faster and Smaller Than Bloom Filters
- [CVPR20 Tutorial](https://www.youtube.com/watch?v=SKrHs03i08Q&list=PLKQB14e0EJUWaTnwgQogJ3nSLzEFNn9d8&t=849s) Billion-scale Approximate Nearest Neighbor Search
- [XOR-Quantization](https://arxiv.org/pdf/2008.02002.pdf) Fast top-K Cosine Similarity Search through XOR-Friendly Binary Quantization on GPUs
- [NeurIPS21 Challenge](http://big-ann-benchmarks.com/index.html) Billion-Scale Approximate Nearest Neighbor Search Challenge [NeurIPS'21 competition track](https://neurips.cc/Conferences/2021/CompetitionTrack)
- [PAMI 2011](https://hal.inria.fr/inria-00514462v1/document) Product quantization for nearest neighbor search
- [CVPR 2016](https://research.yandex.com/publications/138) Efficient Indexing of Billion-Scale Datasets of Deep Descriptors
- [NIPs 2017](https://papers.nips.cc/paper/2017/file/b6617980ce90f637e68c3ebe8b9be745-Paper.pdf) Multiscale Quantization for Fast Similarity Search
- [NIPs 2018](https://research.yandex.com/publications/187) Non-metric Similarity Graphs for Maximum Inner Product Search
- [ACMMM 2018](https://arxiv.org/abs/1808.03969) Reconfigurable Inverted Index [code](https://github.com/matsui528/rii)
- [ECCV 2018](https://arxiv.org/abs/1802.02422) Revisiting the Inverted Indices for Billion-Scale Approximate Nearest Neighbors
- [CVPR 2019](https://research.yandex.com/publications/196) Unsupervised Neural Quantization for Compressed-Domain Similarity Search
- [ICML 2019](https://research.yandex.com/publications/188) Learning to Route in Similarity Graphs
- [ICML 2020](https://research.yandex.com/publications/280) Graph-based Nearest Neighbor Search: From Practice to Theory
