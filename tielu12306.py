import requests
import urllib
import json
from conf import *
from chaojiying import Chaojiying_Client
import re
import time

chaojiying = Chaojiying_Client(chaojiying_user, chaojiying_pwd, chaojiying_id)
sess = requests.session()
secretStr = None
leftTicket = None
seating_type = None
train_location = None
stationTrainCode = None
train_no = None
fromStationTelecode	 = None
headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
}
def login():
    kw={
        'login_site':'E',
        'module':'login',
        'rand':'sjrand',
        '0.4441725873981395':'',
    }
    captcha_image_url = 'https://kyfw.12306.cn/passport/captcha/captcha-image'
    response = sess.get(url=captcha_image_url,params=kw,headers = headers)
    with open("captcha.png", "wb") as f:
        f.write(response.content)
    im = open('captcha.png', 'rb').read()
    print("正在登陆账号...")
    print("正在输入验证码...")
    code_result = chaojiying.PostPic(im, 9004)
    pic_str = handler_code_str(code_result['pic_str'])
    # print(code_result['pic_str'])
    data = {
        'answer':pic_str,
        'login_site':'E',
        'rand':'sjrand',
    }
    response = sess.post("https://kyfw.12306.cn/passport/captcha/captcha-check", data=data, headers=headers)
    message = json.loads(response.text)
    if message['result_code'] == "4":
        print('验证码校验成功')
        login_data = {
            'appid':'otn',
            'password':password,
            'username':user,
        }
        user_login_data = {
            '_json_att':'',
        }
        uamtk_data = {
            'appid':'otn',
        }
        sess.post("https://kyfw.12306.cn/passport/web/login",data = login_data, headers=headers)
        sess.post('https://kyfw.12306.cn/otn/login/userLogin',data=user_login_data,headers=headers)
        sess.get("https://kyfw.12306.cn/otn/passport?redirect=/otn/login/userLogin",headers=headers)
        sess.get('https://kyfw.12306.cn/otn/HttpZF/GetJS',headers=headers)
        uamtk_response = sess.post('https://kyfw.12306.cn/passport/web/auth/uamtk',data=uamtk_data,headers=headers)
        uamauthclient_data = {
            'tk':json.loads(uamtk_response.text)['newapptk'],
        }
        uamauthclient_response = sess.post('https://kyfw.12306.cn/otn/uamauthclient',data=uamauthclient_data,headers=headers)
        sess.get('https://kyfw.12306.cn/otn/login/userLogin',headers=headers)
        My12306 = sess.get('https://kyfw.12306.cn/otn/index/initMy12306',headers=headers)
    else:
        print("验证码失败,重新登录...")
        img_id = code_result['pic_id']
        # print(img_id)
        chaojiying.ReportError(img_id)
        login()

def handler_code_str(code_str):
    try:
        origin_code = list(map(lambda x:int(x),code_str.replace(",","|").split("|")))
        after_code = []
        for i,code in enumerate(origin_code):
            if i%2 == 0:
                code += 10
            after_code.append(code)
        after_code =list(map(lambda x: str(x), after_code))
        # print(after_code)
        return after_code
    except Exception as e:
        print("验证码格式出错，重新登录......")
        login()


def convert_station(station_name):
    stations = station_names.split("|")
    for i,station in enumerate(stations):
        if station_name == station:
            return stations[i + 1]

def check_ticket():
    print("正在检查余票...")
    ticket = sess.get('https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={date}&leftTicketDTO.from_station={from_station}&leftTicketDTO.to_station={to_station}&purpose_codes=ADULT'.format(date=trian_date,from_station=convert_station(from_station),to_station=convert_station(to_station)),headers=headers)
    # print(ticket.text)
    results = json.loads(ticket.text)['data']['result']
    for result in results:
        ticket_detail = result.split("|")
        # for i, station in enumerate(ticket_detail):
        #     print(i,station)
        print("车次:{0},发车时间:{1},结束时间:{2},历时:{3},日期:{4},无座:{5},二等座:{6},一等座:{7}"
              .format(ticket_detail[3], ticket_detail[8], ticket_detail[9], ticket_detail[10], ticket_detail[13],
                      ticket_detail[26], ticket_detail[30], ticket_detail[31]))
        # print(ticket_detail[0])
        # print(ticket_detail[12])
    global leftTicket
    global secretStr
    global seating_type
    global train_location
    global stationTrainCode
    global train_no
    global fromStationTelecode
    # print("发现有余票...")
    # break
    while True:
        user_selection = input("请输入你要乘坐的车次，还有座位类型:比如（G6305,二等座）")
        # user_selection = "D7509,无座"
        try:
            train_number, seating_type = re.split("[，,]",user_selection )
            if len(re.split("[，,]",user_selection )) == 2:
                for result in results:
                    ticket_detail = result.split("|")
                    if ticket_detail[3]==train_number:
                        if seating_type == "无座":
                            if ticket_detail[26] == "有":
                                print("您输入的车次有票，进入买票...")
                                leftTicket = ticket_detail[12]
                                secretStr = ticket_detail[0]
                                train_location = ticket_detail[15]
                                stationTrainCode = ticket_detail[3]
                                train_no = ticket_detail[2]
                                fromStationTelecode = ticket_detail[4]
                                return
                            else:
                                print("没票")
                                break
                        if seating_type == "二等座":
                            if ticket_detail[30] == "有":
                                print("您输入的车次有票，进入买票...")
                                leftTicket = ticket_detail[12]
                                secretStr = ticket_detail[0]
                                train_location = ticket_detail[15]
                                stationTrainCode = ticket_detail[3]
                                train_no = ticket_detail[2]
                                fromStationTelecode = ticket_detail[4]
                                return
                            else:
                                print("没票")
                                break
                        if seating_type == "一等座":
                            if ticket_detail[31] != "无":
                                print("您输入的车次有票，进入买票...")
                                leftTicket = ticket_detail[12]
                                secretStr = ticket_detail[0]
                                train_location = ticket_detail[15]
                                stationTrainCode = ticket_detail[3]
                                train_no = ticket_detail[2]
                                fromStationTelecode = ticket_detail[4]
                                return
                            else:
                                print("没票")
                                break
            else:
                print("你输入的车次有误，请重新输入!")
        except Exception as e:
            print("输入有误，请重新输入!")
            pass


def buy_ticket():
    print("正在买票...")
    check_user_data = {
        '_json_att':'',
    }
    time.sleep(1)
    check_user_response = sess.post("https://kyfw.12306.cn/otn/login/checkUser",data=check_user_data, headers=headers)
    submitOrderRequest_data = {
        'back_train_date':trian_date,
        'purpose_codes':'ADULT',
        'query_from_station_name':from_station,
        'query_to_station_name':to_station,
        'secretStr':urllib.parse.unquote(secretStr),
        'tour_flag':'dc',
        'train_date':trian_date,
        'undefined':'',
    }
    initDc_data = {
        '_json_att':'',
    }
    time.sleep(1)
    OrderRequest = sess.post("https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest",data=submitOrderRequest_data, headers=headers)
    time.sleep(2)
    initDc_response = sess.post('https://kyfw.12306.cn/otn/confirmPassenger/initDc',data=initDc_data,headers=headers)
    pattern = re.compile(r"var globalRepeatSubmitToken = '(.*)';")
    m = pattern.search(initDc_response.text)
    token = m.group(1)
    # print(token)

    try:
        pattern1 = re.compile(r"'key_check_isChange'.*?:.*?'(.*?)'.*?,")
        m1 = pattern1.search(initDc_response.text)
        key = m1.group(1)
    except Exception as e:
        print("您有未处理的订单，请先处理...程序退出！")
        return

    # print(key)
    PassengerDTOs_data = {
        '_json_att	':'',
        'REPEAT_SUBMIT_TOKEN':token,
    }
    time.sleep(3)
    PassengerDTOs_response = sess.post("https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs",data=PassengerDTOs_data,headers=headers)
    PassengerDTOs_json = json.loads(PassengerDTOs_response.text)
    passenger_list = []
    for passengers in PassengerDTOs_json['data']['normal_passengers']:
        passenger_list.append(passengers['passenger_name'])
        print("您可以给下列的乘客买票:%s"%(passengers['passenger_name']))
    name = input("请输入你要给那个乘客买票：")
    while True:
        if name in passenger_list:
            break
        else:
            print("您输入的乘客不存在，请重新输入!")
            name = input("请输入你要给那个乘客买票：")

    for passengers in PassengerDTOs_json['data']['normal_passengers']:
        if passengers['passenger_name'] == name:
            passenger_id_no = passengers['passenger_id_no']
            mobile_no = passengers['mobile_no']

    OrderInfo_data = {
        '_json_att':'',
        'bed_level_order_num':'000000000000000000000000000000',
        'cancel_flag':'2',
        'oldPassengerStr':'{name},1,{id},1_'.format(name=name,id=passenger_id_no),
        'passengerTicketStr':'O,0,1,{name},1,{id},{mobile},N'.format(name=name, id=passenger_id_no,mobile = mobile_no),
        'randCode':'',
        'REPEAT_SUBMIT_TOKEN':token,
        'tour_flag':'dc',
        'whatsSelect':'1',
    }
    time.sleep(2)
    print("进入排队处理...")
    OrderInfo_response = sess.post("https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo", data=OrderInfo_data,headers=headers)
    OrderInfo_json = json.loads(OrderInfo_response.text)
    # print(OrderInfo_json)
    if seating_type == "无座" or seating_type == "二等座":
        seat = "O"
    else:
        seat = "M"
    timeArray = time.strptime(trian_date, "%Y-%m-%d")
    # 转换成时间戳
    timestamp = time.mktime(timeArray)
    l_time = time.localtime(timestamp)
    new_train_date = time.strftime("%a %b %d %Y", l_time)

    QueueCount_data = {
        '_json_att':'',
        'fromStationTelecode':fromStationTelecode,
        'leftTicket':urllib.parse.unquote(leftTicket),
        'purpose_codes':'00',
        'REPEAT_SUBMIT_TOKEN':token,
        'seatType':seat,
        'stationTrainCode':stationTrainCode,
        'toStationTelecode':convert_station(to_station),
        'train_date':str(new_train_date) + " 00:00:00 GMT+0800",
        'train_location':train_location,
        'train_no':train_no,
    }
    # print(QueueCount_data)
    time.sleep(4)
    QueueCount_response = sess.post("https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount",data=QueueCount_data,headers=headers)
    QueueCount_json = json.loads(QueueCount_response.text)
    # print(QueueCount_json)

    SingleForQueue_data = {
        '_json_att':'',
        'choose_seats':'1F',
        'dwAll':'N',
        'key_check_isChange':key,
        'leftTicketStr':urllib.parse.unquote(leftTicket),
        'oldPassengerStr':'{name},1,{id},1_'.format(name=name,id=passenger_id_no),
        'passengerTicketStr':'O,0,1,{name},1,{id},{mobile},N'.format(name=name, id=passenger_id_no,mobile = mobile_no),
        'purpose_codes':'00',
        'randCode':'',
        'REPEAT_SUBMIT_TOKEN':token,
        'roomType':'00',
        'seatDetailType':'000',
        'train_location':train_location,
        'whatsSelect':'1'
    }
    # print("SingleForQueue_data")
    # print(SingleForQueue_data)
    time.sleep(3)
    SingleForQueue_response = sess.post("https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue",data=SingleForQueue_data,headers=headers)
    # print("11111111")
    # print(json.loads(SingleForQueue_response.text))
    OrderWaitTime_data = {
        '_json_att':'',
        'random':'1525860914102',
        'REPEAT_SUBMIT_TOKEN':token,
        'tourFlag':'dc',
    }
    print("正在处理你的购票...")
    time.sleep(5)
    OrderWaitTime_response = sess.get("https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime", params=OrderWaitTime_data, headers=headers)
    OrderWaitTime_json = json.loads(OrderWaitTime_response.text)
    # print("22222")
    # print(OrderWaitTime_json)
    orderId = OrderWaitTime_json['data']['orderId']
    OrderForDcQueue_data = {
        '_json_att':'',
        'orderSequence_no':orderId,
        'REPEAT_SUBMIT_TOKEN':token,
    }
    time.sleep(2)
    OrderForDcQueue_response = sess.post("https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue",data=OrderForDcQueue_data, headers=headers)
    # print(json.loads(OrderForDcQueue_response.text))
    print("购票成功，请在30分钟内完成支付...")

if __name__ == "__main__":
    login()
    check_ticket()
    buy_ticket()
