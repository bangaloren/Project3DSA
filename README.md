# TalKannada: ASR Webserver For Kannada

This repository contains all the code needed to run the server. However, due to the data required to train the model being several gigabytes large, developers will need to download significant portions of the data to replicate our results.

You can access the website directly at [https://talk.kanda.ru/](https://talk.kanda.ru/). There is also an API available at [https://talk.kanda.ru/translate](https://talk.kanda.ru/translate) where you can translate audio files using curl. 

For example:
```
curl -X POST -F "file=@c.wav" -F "splitterType=best first" -F "width=5"  https://talk.kanda.ru/transcribe .
```


## Local Setup

### 1. Data Download

The raw audio files, totaling over 20GB, can be downloaded from the links below.

1. [https://www.openslr.org/126/](https://www.openslr.org/126/) (Attribution 2.0 Generic (CC BY 2.0))
2. [https://www.openslr.org/79/](https://www.openslr.org/79/) (Attribution-ShareAlike 4.0 International)

The File structure of our data folder looks like this:
'''
❯ ls -a
. kn_in_female_trans line_index_male.tsv probabilities
.. kn_in_male makeTSV.py testTrain
combined_sentences.tsv kn_in_male_trans mile_kannada_test text
kn_in_female line_index_female.tsv mile_kannada_train
'''

### 2. Installing Local Dependencies

This project requires the installation of Nvidia CUDA 12.1 drivers. These can be downloaded from the official developer website: [https://developer.nvidia.com/cuda-12-1-1-download-archive](https://developer.nvidia.com/cuda-12-1-1-download-archive?target_os=Linux&target_arch=x86_64&Distribution=Ubuntu&target_version=22.04&target_type=deb_network)

After installing the drivers, you can install the necessary Python 3.10 dependencies with the following command:

'''
pip install pandas allosaurus sklearn flask flask-cors pydub ctranslate2 OpenNMT-py==2.* sentencepiece 
'''


### 3. Training the Lexical Model

To train the lexical model, navigate to the `lexical-model/` directory. Inside, execute the `setup.sh` script to set up the RNN and initiate training over 4000 iterations. The duration of this process can range from a few hours to several days, depending on your hardware configuration. Should you encounter GPU memory issues, consider adjusting the `batch_size` parameter within the `lexical-model.yaml` file to a smaller value.

### 4. Running The Language Server

After being trained, the language server can be run with the below command.

```
nohup python3 WebServer.py
```


## Frontend Server Setup

![圖片](https://github.com/bangaloren/Project3DSA/assets/115109992/e6835e1f-e55c-474d-ab73-13fa3208fcd8)


We are using an ubuntu 20.04 VPS to run the front-end server.

### 1. Move the Files over to the Server.

You want to copy the folder labeled 'Website' into the server and start the webserver by running the following commands.

```
cd Website/
nohup python3 FrontendSite.py
```

This will startup a webserver at port 5000.

### 2. Setup Nginx

```
sudo apt update
sudo apt install nginx
```

After installing Nginx you want to create a configuration file to route traffic from either port 80 or 443 to port 5000.
You can replace 'talk.kanda.ru' with your own domain name.

```
sudo nano /etc/nginx/sites-available/talk.kanda.ru
sudo ln -s /etc/nginx/sites-available/talk.kanda.ru /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3. Setup Let's Encrypt on the VPS


You can follow the below tutorial to setup HTTPS for the server.
https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-22-04


### 4. Setup the Reverse Proxy to the Language Server

You want to open up a terminal from your language server and write the following command.

```
ssh -R 5000:localhost:5000 -p [ssh port] -o ServerAliveInterval=60 [username]@[frontend-server-ip]
```




