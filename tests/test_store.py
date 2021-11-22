from pqlite.storage.kv import DocStorage


def test_get(tmpdir, docs):
    storage = DocStorage(tmpdir + 'test_doc_store')

    storage.insert(docs)

    doc = storage.get('doc1')[0]
    assert doc.id == 'doc1'
    assert (doc.embedding == [1, 0, 0, 0]).all()

    docs = storage.get('doc7')
    assert len(docs) == 0


def test_update(tmpdir, docs, update_docs):
    storage = DocStorage(tmpdir + 'test_doc_store')
    storage.insert(docs)

    storage.update(update_docs)

    doc = storage.get('doc1')[0]
    assert (doc.embedding == [0, 0, 0, 1]).all()


def test_delete(tmpdir, docs):
    storage = DocStorage(tmpdir + 'test_doc_store')
    storage.insert(docs)
    storage.delete(['doc1'])
    docs = storage.get('doc1')
    assert len(docs) == 0


def test_clear(tmpdir, docs):
    storage = DocStorage(tmpdir + 'test_doc_store')
    storage.insert(docs)

    assert storage.size == 6
    storage.clear()
    assert storage.size == 0


def test_batched_iterator(tmpdir, docs):
    storage = DocStorage(tmpdir + 'test_doc_store')
    storage.insert(docs)
    for docs in storage.batched_iterator(batch_size=3):
        assert len(docs) == 3