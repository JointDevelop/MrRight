# MrRight web server config
# will change to IP. This IP can be visite in websit, so you must by a cloud hosting and a domain name.
WEB_SERVER_HOST = '192.168.1.3'
# redis config
REDIS = {
    'host':'localhost',
    'port':6379,
    'db':2
}

# qncloud config
QN_AK = 'bUM86uco-yu7w9cTSLQMalBcIuAtW3KQbCalpP4m'
QN_SK = 'g3HTJGy9qPKaT7X24OVt9kAsIXLtCuTMvTAS_0Zm'
QN_BUCKET = 'mr-right-app'
QN_CALLBACK = f'http://{WEB_SERVER_HOST}/qiniu/callback'
QN_FILESIZE = 5*1024*1024    # max size of file is 5M
# The host of bucket in qiniu cloud, that will be expired after 30 days until you bind it to your own domain name.
# If file is 'Avatar-1.jpg', the qiniu cloud will save it and set URL to 'http://qpreaw93y.hn-bkt.clouddn.com/Avatar-1.jpg'
QN_BASE_URL = 'http://qpreaw93y.hn-bkt.clouddn.com'
