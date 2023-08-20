from sentence_transformers import SentenceTransformer, util
import os
import csv
import time
import pickle
# https://zhuanlan.zhihu.com/p/638929185
from langchain.text_splitter import SpacyTextSplitter
import faiss
import numpy as np

# Model for computing sentence embeddings. We use one trained for similar questions detection
# model_name = "/Users/chalecao/Downloads/model/paraphrase-multilingual-MiniLM-L12-v2"
model_name = '/Users/chalecao/Downloads/sbert-chinese-general-v2/quora-distilbert-multilingual'
# model_name = '/Users/chalecao/Downloads/sbert-chinese-general-v2/sbert-chinese-general-v2'
model = SentenceTransformer(model_name)

chunk_size = 100
chunk_overlap = 20 # 1/5 of chunk_size

def getEmbeding(filename):
    dataset_path = f'embededFile/{filename}'
    print("handle data path", dataset_path)
    filename = dataset_path.split('/')[-1]
    embedding_cache_path = 'embededCache/{}-{}.pkl'.format(
        filename.split('.')[0], chunk_size)
    # Check if embedding cache path exists
    if not os.path.exists(embedding_cache_path):
        # Get all unique sentences from the file
        corpus_sentences = set()
        with open(dataset_path, encoding='utf8') as fIn:
            text = fIn.read()
            # Split the text into sentences
            text_splitter = SpacyTextSplitter(
                pipeline='zh_core_web_md',
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap)
            # 文档：https://spacy.io/models/zh
            # 下载https://github.com/explosion/spacy-models/releases/tag/zh_core_web_md-3.6.0
            sentences = text_splitter.split_text(text)
            corpus_sentences = sentences

        print("Encode the corpus. This might take a while")
        corpus_embeddings = model.encode(
            corpus_sentences,
            show_progress_bar=True,
            convert_to_numpy=True  #如果为 true，则输出为 numpy 向量的列表。否则，它是一个 pytorch 张量列表
        )

        print("Store file on disc")
        with open(embedding_cache_path, "wb") as fOut:
            pickle.dump({'sentences': corpus_sentences, 'embeddings': corpus_embeddings}, fOut)
    else:
        print("Load pre-computed embeddings from disc")
        with open(embedding_cache_path, "rb") as fIn:
            cache_data = pickle.load(fIn)
            corpus_sentences = cache_data['sentences']
            corpus_embeddings = cache_data['embeddings']
    return corpus_embeddings, corpus_sentences



embedding_size = 768    #Size of embeddings 向量维度, 不同的SentenceTransformer模型不一样
top_k_hits = 3  #Output k hits 定义召回向量个数
n_clusters = 1  # 聚类中心的个数

def saveFaiss(filename, corpus_embeddings):
    index_path = 'faiss/{}.index'.format(
        filename.split('.')[0])
    if not os.path.exists(index_path):
        quantizer=faiss.IndexFlatIP(embedding_size) # 点乘，归一化的向量点乘即cosine相似度（越大越好）
        index = faiss.IndexIVFFlat(quantizer, embedding_size, n_clusters, faiss.METRIC_INNER_PRODUCT)
        ### Create the FAISS index
        print("Start creating FAISS index")
        # First, we need to normalize vectors to unit length
        corpus_embeddings = corpus_embeddings / np.linalg.norm(corpus_embeddings, axis=1)[:, None]
        # Then we train the index to find a suitable clustering
        index.train(corpus_embeddings)
        # Finally we add all embeddings to the index
        index.add(corpus_embeddings)
        # Save the index
        faiss.write_index(index, index_path)


def queryFaiss(filename, inp_question, corpus_embeddings, corpus_sentences):
    index_path = 'faiss/{}.index'.format(
        filename.split('.')[0])
    simliarInfo = []
    start_time = time.time()
    question_embedding = model.encode(inp_question)
    index = faiss.read_index(index_path)
    index.nprobe = n_clusters # 查找聚类中心的个数，默认为1个，若nprobe=n_clusters则等同于精确查找
    #FAISS works with inner product (dot product). When we normalize vectors to unit length, inner product is equal to cosine similarity
    question_embedding = question_embedding / np.linalg.norm(question_embedding)
    question_embedding = np.expand_dims(question_embedding, axis=0)

    # Search in FAISS. It returns a matrix with distances and corpus ids.
    distances, corpus_ids = index.search(question_embedding, top_k_hits)

    # We extract corpus ids and scores for the first query
    hits = [{'corpus_id': id, 'score': score} for id, score in zip(corpus_ids[0], distances[0])]
    hits = sorted(hits, key=lambda x: x['score'], reverse=True)
    end_time = time.time()

    print("Input question:", inp_question)
    print("Results (after {:.3f} seconds):".format(end_time-start_time))
    for hit in hits[0:top_k_hits]:
        simliarInfo.append(corpus_sentences[hit['corpus_id']]);
        print("\t{:.3f}\t{}".format(hit['score'], corpus_sentences[hit['corpus_id']]))

    # Approximate Nearest Neighbor (ANN) is not exact, it might miss entries with high cosine similarity
    # Here, we compute the recall of ANN compared to the exact results
    correct_hits = util.semantic_search(question_embedding, corpus_embeddings, top_k=top_k_hits)[0]
    correct_hits_ids = set([hit['corpus_id'] for hit in correct_hits])

    ann_corpus_ids = set([hit['corpus_id'] for hit in hits])
    if len(ann_corpus_ids) != len(correct_hits_ids):
        print("Approximate Nearest Neighbor returned a different number of results than expected")

    recall = len(ann_corpus_ids.intersection(correct_hits_ids)) / len(correct_hits_ids)
    print("\nApproximate Nearest Neighbor Recall@{}: {:.2f}".format(top_k_hits, recall * 100))

    if recall < 1:
        print("Missing results:")
        for hit in correct_hits[0:top_k_hits]:
            if hit['corpus_id'] not in ann_corpus_ids:
                simliarInfo.append(corpus_sentences[hit['corpus_id']]);
                print("\t{:.3f}\t{}".format(hit['score'], corpus_sentences[hit['corpus_id']]))
    print("\n\n========\n")
    return simliarInfo
