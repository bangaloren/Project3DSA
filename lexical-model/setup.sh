rm lexical-model-data/run/vocab.*
#change this to the path files for you nvidia/cuda installation
export LD_LIBRARY_PATH=/usr/local/lib/python3.10/dist-packages/nvidia/cusparse/lib/:/usr/local/lib/python3.10/dist-packages/nvidia/cuda_cupti/lib/:/usr/local/lib/python3.10/dist-packages/nvidia/cuda_runtime/lib/:/usr/local/lib/python3.10/dist-packages/nvidia/cublas/lib/:/usr/local/lib/python3.10/dist-packages/nvidia/cufft/lib:/home/michaelbennie/.local/include/cudnn-linux-x86_64-8.9.2.26_cuda11-archive/lib


onmt_build_vocab -config lexical-model.yaml -val.txt -n_sample 82429

#training the model WARNING: THIS MAY TAKE SEVERAL HOURS TO DAYS
onmt_train -config lexical-model.yaml

#if you already have a model you want to continue training, then you can uncomment the below
#line and change the parameter of --train_from to that model
#onmt_train -config lexical-model.yaml --train_from lexical-model-data/run_default/model_step_20000.pt

onmt_release_model --model lexical-model-data/run_default/model_step_40000.pt --output "model_released.pt"

#to do a quick test of the model you can do the below
onmt_translate -model model_released.pt -src ./lexical-model-data/2Sent.txt -output testing.txt
