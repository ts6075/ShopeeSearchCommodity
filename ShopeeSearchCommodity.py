import configparser
import requests
import json


# #################
# # 發送LineNotify訊息 #
# #################
def lineNotify(message, token):
    notify_Post_Url = 'https://notify-api.line.me/api/notify'     # Line api
    headers = {'Authorization': 'Bearer ' + token}
    payload = {"message": message}
    res = requests.post(notify_Post_Url, headers=headers, params=payload)
    print(res)


# #################
# # 基礎設定       #
# #################
# load config
config = configparser.ConfigParser()
config.read('Config.ini')
# Line token
notify_token = config.get('Section_Info', 'notify_token')
# 商家ID
shopId = '54133273'
# 商品分類ID
shop_categoryid = '40151690'
# 商品頁面Url
commodityUrl = 'https://shopee.tw/0-i.' + shopId + '.'
# 商品清單api
listUrl = 'https://shopee.tw/api/v2/search_items/?' +\
          'match_id=' + shopId +\
          '&shop_categoryids=' + shop_categoryid +\
          '&limit=100&newest=0'
# 商品詳細資訊api
detailUrl = 'https://shopee.tw/api/v2/item/get?' +\
            'shopid=' + shopId + '&itemid='
# 目標關鍵字
targetStr = '3060,3070'
# 爬取結果
outList = []


# #################
# # 取得新的headers #
# #################
ses = requests.Session()
homeUrl = 'https://shopee.tw/mall'
headers = {'User-Agent': 'Mozilla/5.0'}
headers = ses.get(homeUrl, headers=headers).request.headers


# #################
# # 取得商品清單   #
# #################
res = ses.get(listUrl, headers=headers)
result = json.loads(res.text)
commodityList = result['items']


# #################
# # 逐一爬取各商品 #
# #################
outStr = ''
i = 1
for commodity in commodityList:
    print('爬取中...(', i, ')')
    i = i + 1
    outStr = ''
    first = True
    commodityDetail = {}  # 商品詳細資訊

    # #################
    # # 取得商品詳細資訊 #
    # #################
    res = ses.get(detailUrl + str(commodity['itemid']), headers=headers)
    result = json.loads(res.text)

    if result is None or result['error'] is not None:
        outStr += 'error:' + detailUrl + str(commodity['itemid'])
        outList.append(outStr)
        continue
    else:
        commodityDetail = result['item']

    # #################
    # # 取得商品可選配項目清單 #
    # #################
    models = commodityDetail['models']
    for model in models:
        # 查找指定關鍵字且該選配項目庫存需大於0
        if model['stock'] != 0 and any(s in model['name'] for s in targetStr.split(',')):
            if first is True:
                outStr += '============================================================\n'
                outStr += '網址：' + commodityUrl + str(commodityDetail['itemid']) + '\n'
                outStr += '品名：' + commodityDetail['name'] + '\n'
                outStr += '============================================================\n'
                first = False
            outStr += '\t選配名稱：' + model['name'] + '\n'
            outStr += '\t選配價格：' + str(model['price']) + '\n'
            outStr += '\t銷售庫存：' + str(model['stock']) + '/' +\
                      str(int(model['stock']) + int(model['sold'])) + '\n'
            outStr += '\t------------------------------\n'

    if outStr != '':
        outList.append(outStr)

# 輸出結果
for s in outList:
    print(s)
    # lineNotify(s, notify_token)
