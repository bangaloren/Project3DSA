rm lexical-model-data/run/vocab.*
onmt_build_vocab -config lexical-model.yaml -val.txt -n_sample 82429
