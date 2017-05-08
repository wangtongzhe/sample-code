import random
import string
import requests
import json
import sys
import time

# 开始抽奖页面
start_lottery_uri = "http://api.servera.com.cn/cards/generate-card?user_name={0}"
# 查询奖品页面
exist_lottery_uri = "http://api.servera.com.cn/cards/my-cards?user_name={0}"
# 获取奖品页面
get_lottery_uri = "http://api.servera.com.cn/cards/reward-card?user_name={0}"
# 代码解析
code_dict = {30008: "卡券已领完", 30006: "不在活动时间", 30005: "卡券包已满", 30009: "谢谢惠顾"}
# 奖品列表
lottery_dict = {}


def read_lottery_dict():
    file_path = "lottery_config.ini"
    with open(file_path, 'r', encoding="utf-8") as f:
        for item_str in f.readlines():
            split_obj = item_str.strip('\n').split("=")
            if len(split_obj) == 2:
                lottery_dict[int(split_obj[0])] = split_obj[1]


def write_lottery_dict():
    file_path = "lottery_config.ini"
    with open(file_path, 'w', encoding="utf-8") as f:
        for item_key, item_value in lottery_dict.items():
            f.write(str(item_key) + "=" + item_value)
            f.write("\n")


def append_lottery_dict(number_id, lotterys):
    file_path = "lottery_result.txt"
    with open(file_path, 'a', encoding="utf-8") as f:
        f.write("{0}:{1}".format(str(number_id), ",".join(lotterys)))
        f.write("\n")


def random_open_id():
    return ''.join(random.sample(string.ascii_letters + string.digits, 28))


def get_web_result(id_number):
    web_entity = requests.get(start_lottery_uri.format(id_number))
    return json.loads(web_entity.text)


def get_lottery_result(id_number):
    web_entity = requests.get(get_lottery_uri.format(id_number))
    return json.loads(web_entity.text)


def get_lottery_info(id_number):
    lottery_list = []
    web_entity = requests.get(exist_lottery_uri.format(id_number))
    lottery_entities = json.loads(web_entity.text)
    if "cards" not in lottery_entities:
        return lottery_list
    for item in lottery_entities["cards"]:
        lottery_dict[item["card_id"]] = item["store_name"] + "-" + item["title"]
        lottery_list.append(item["store_name"] + "-" + item["title"])
    return lottery_list


if __name__ == '__main__':
    print()
    users_number = 2
    if len(sys.argv) >= 2:
        users_number = int(sys.argv[1])
    read_lottery_dict()
    for int_number in range(users_number):
        opent_id = random_open_id()
        print("准备使用 {0} 进行奖品抽取".format(opent_id))
        number = 0
        try:
            while 1:
                number = number + 1
                print("开始使用 {0} 用户进行第 {1} 次抽取".format(opent_id, str(number)))
                result_obj = get_web_result(opent_id)
                if result_obj["code"] == 30006:
                    raise Exception("当前不在抽奖时间")
                elif result_obj["code"] == 30005:
                    break
                elif result_obj["code"] == 30009:
                    continue
                else:
                    get_result = get_lottery_result(opent_id)
                    print("成功使用 {0} 用户获取奖品：{1}".format(opent_id, str(result_obj["card"]["card_id"])))
                time.sleep(1)
            lottery_gets = get_lottery_info(opent_id)
            print("完成使用 {0} 进行奖品抽取，获得奖品：{1}".format(opent_id, ",".join(lottery_gets)))
            print("写入使用 {0} 进行奖品抽取的列表".format(opent_id))
            append_lottery_dict(opent_id, lottery_gets)
            time.sleep(1)
        except Exception as ex:
            print(ex)
            break
    write_lottery_dict()
