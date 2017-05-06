cfg = {
    "path": {
        "embeddings": "./data/wordembeddings-dim100.word2vec",
        "train": "./data/sentences.train",
        "test": "./data/sentences.eval",
        "continuation": "./data/sentences.continuation",
    },
    "vocab_size": 20000,
    "sentence_length": 30,

    "embeddings_size" : 100,
    "lstm_size" : 512,
    "intermediate_projection_size": 512,

    "max_sentences" : -1,
    "max_test_sentences" : -1,
    "max_iterations" : 100,
    "batch_size": 64,
    "out_batch": 100,

    "use_fred": False,
    "use_pretrained": False,
    "extra_project": False,

    "dictionary_name": "dict.p"
}