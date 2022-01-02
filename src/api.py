from string import Template
import database as db
import datetime as dt
import unicodedata
import requests
import json
import os

specificCountries = ["Belgium", "Germany", "Canada", "China", "Ukraine", "New Zealand", "United Kingdom", "Netherlands",
                     "Sweden", "Russian Federation", "Brazil", "Colombia", "Italy", "United States of America",
                     "Japan", "Spain", "Australia", "Peru", "India", "Pakistan", "Mexico"]

# World API
WORLD_API = 'https://api.covid19api.com/total/country/$code'
WORLD_LATEST_API = 'https://api.covid19api.com/live/country/$code'
WORLD_FILE = '../db/worlds/$name.json'
WORLD_LATEST_FILE = '../db/latest/$name.json'
WORLD_CODE = '../db/codes.json'
# Vietnam API
VIETNAM = 'https://api.apify.com/v2/key-value-stores/EaCBL1JNntjR3EakU/records/LATEST?disableRedirect=true&utf8=1'
VIETNAM_FILE = '../db/vietnam_specific.json'


def fetchCountry(name,code):
    '''
    Cập nhật thông tin covid của một quốc gia
     - name: tên quốc gia
     - code: mã quốc gia
    '''

    # Loại bỏ quốc gia bị lỗi
    if(name == 'Saint Vincent and Grenadines'):
        return

    # Lấy dữ liệu total và latest bằng code
    response_total = requests.get(Template(WORLD_API).substitute(code=code))
    response_latest = requests.get(
        Template(WORLD_LATEST_API).substitute(code=code))

    if(response_total.status_code != 200 or response_latest.status_code != 200):
        return

    string_total = json.loads(response_total.content)
    string_latest = json.loads(response_latest.content)

    # Tạo đường dẫn bằng name
    filePathTotal = Template(WORLD_FILE).substitute(name=name)
    filePathLatest = Template(WORLD_LATEST_FILE).substitute(name=name)
    if(string_total != [] and string_latest != []):
        print('Fetching', name)
        db.updateJSON(filePathTotal, string_total)
        db.updateJSON(filePathLatest, string_latest)
    else:
        return


def fetchWorld():
    '''
    Cập nhật thông tin covid của toàn thế giới và lưu về data base
    - return: True nếu cập nhật thành công, False nếu ngược lại
    '''

    with open(WORLD_CODE, mode="r") as f:
        worlds = json.load(f)
    print("Fetching World's database")

    # Cập nhật cho từng quốc gia
    for country in worlds:
        fetchCountry(country['country'],country['code'])
    print("World database is updated")
    return True


def fetchVietnam():
    '''
    Cập nhật thông tin covid các tỉnh thành của Việt Nam trong ngày
    - return: True nếu cập nhật thành công, False nếu ngược lại
    '''

    print("Fetching Vietnam's province")

    # Gọi API
    rq = requests.get(VIETNAM)
    if(rq.status_code != 200):
        return False

    # Lấy dữ liệu và update database
    fetchedData = rq.content
    responseVietnam = json.loads(fetchedData)['locations']
    db.updateJSON(VIETNAM_FILE, responseVietnam)
    print("Vietnam database is updated")

    return True


def fetchData():
    '''
    Cập nhật cơ sở dữ liệu
    '''
    
    db.writeLatestTime(db.getCurrentTime())
    flag = fetchVietnam()
    flag = fetchWorld()
    print("Fetching is done")


def isSpecialCountry(countryName):
    '''
    Kiểm tra có phải quốc gia có nhiều tỉnh thành
    - return: True nếu phải
    '''
    if(countryName not in specificCountries):
        return False
    print("Is a special country")
    return True


def needToBeLatest(date):
    '''
    Kiểm tra xem có phải ngày mong muốn là gần đây (trong vòng 1 tuần)
    - date: ngày mong muốn
    - return: True nếu phải
    '''
    
    currentTime = db.getCurrentTime()
    time = dt.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    delta = currentTime - time

    if(delta.days <= 7):
        return True
    return False


def validTime(date):
    '''
    Kiểm tra xem ngày mong muốn có hợp lệ
    - date: ngày mong muốn
    - return: True nếu hợp lệ
    '''
    currentTime = db.getCurrentTime()
    time = dt.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")

    begin = dt.datetime.strptime("2020-01-22 00:00:00", "%Y-%m-%d %H:%M:%S")
    if(time < begin):
        return False

    delta = currentTime - time
    if(delta.days < 0):
        return False
    return True

def prevDate(today):
    '''
    Tìm ngày hôm trước
    - today: chuỗi ngày hôm nay
    - return: chuỗi ngày hôm trước
    '''
    time = dt.datetime.strptime(today, "%Y-%m-%d")
    yesterday = time - dt.timedelta(days=1)
    return dt.datetime.strftime(yesterday, "%Y-%m-%d")

def summaryCountry(countryName, data, date):
    '''
    Tổng hợp thông tin của các quốc gia nhiều tỉnh thành
    - countryName: tên quốc gia
    - data: json dữ liệu
    - date: ngày cần tìm thông tin
    - return: một dictionary đã được tính tổng
    '''

    dict = {}
    info = {"Confirmed": 0, "Deaths": 0, "Recovered": 0}
    check = False

    for item in data:
        if(item['Date'] == date):
            info['Confirmed'] += int(item['Confirmed'])
            info['Deaths'] += int(item['Deaths'])
            info['Recovered'] += int(item['Recovered'])

            # Lấy đại một tỉnh thành làm mẫu
            dict = item
            check = True
        else:
            if(check == True):
                break
    return dict | info

def generateCovidDict(prev, curr):
    '''
    Tạo một dictionary mới chứa thêm thông tin về sự thay đổi
    - prev: thông tin ngày trước đó
    - curr: thông tin ngày hiện tại
    - return: dictionary mới
    '''
    temp = {"Change in cases": "",
            "Change in deaths": "", "Change in recovered": ""}
    temp['Change in cases'] = str(
        int(curr["Confirmed"]) - int(prev['Confirmed']))
    temp['Change in deaths'] = str(int(curr["Deaths"]) - int(prev['Deaths']))
    temp['Change in recovered'] = str(
        int(curr["Recovered"]) - int(prev['Recovered']))

    return temp


def getCountryData(countryName, date):
    '''
    Lấy dữ liệu của một quốc gia bất kỳ
    - countryName: tên quốc gia
    - date: ngày mong muốn
    - return: dict thông tin nếu tìm thấy, {} nếu không tìm thấy
    '''

    dict1 = {}
    dict2 = {}
    found = False

    # Kiểm tra xem ngày mong muốn có nằm trong khoảng thời gian mà dữ liệu có
    if not validTime(date+" 00:00:00"):
        print("Cannot find that day")
        return {}

    # Mở file mã thế giới để lấy các tên quốc gia
    with open(WORLD_CODE, mode="r") as f1:
        worlds = json.load(f1)

    print("Searching World's database")
    for country in worlds:
        if(country['country'] == countryName or country['code'] == countryName):
            countryName = country['country']
            found = True

            # Lựa chọn database dựa vào thời gian (gần đây hoặc hơn một tuần)
            if(needToBeLatest(date+" 00:00:00")):
                path = Template(WORLD_LATEST_FILE).substitute(name=countryName)
            else:
                path = Template(WORLD_FILE).substitute(name=countryName)

            # Có trong danh sách nhưng không có file
            if not os.path.isfile(path):
                print("Cannot find")
                return {}

            # Mở file quốc gia để lấy dữ liệu
            with open(path, mode="r") as f2:
                data = json.load(f2)

    prev = prevDate(date) + "T00:00:00Z"
    date += "T00:00:00Z"

    if(found):

        if(isSpecialCountry(countryName)):
            dict1 = summaryCountry(countryName, data, prev)
            dict2 = summaryCountry(countryName, data, date)
            temp = generateCovidDict(dict1, dict2)

        else:
            for item in data:
                if(item["Date"] == prev):
                    dict1 = item
                if(item["Date"] == date):
                    dict2 = item
                    temp = generateCovidDict(dict1, dict2)

        return dict2 | temp

    else:
        print("Cannot find")
        return {}


def unicodeToString(str):
    '''
    Chuyển một chuỗi có unicode thành không dấu
    '''

    return unicodedata.normalize('NFKD', str).encode('ascii', 'ignore').decode('utf-8')


def getProvinceData(provinceName):
    '''
    Lấy dữ liệu của một tỉnh thành bất kỳ
    - provinceName: chuỗi nhập vào có thể là không dấu hoặc có dấu
    - return: dict thông tin nếu tìm thấy, {} nếu không tìm thấy
    '''

    # Chuyển chuỗi đầu vào thành không dấu
    provinceName = unicodeToString(provinceName)

    # Nếu nhập vào Ho Chi Minh thì chuyển thành TP. Ho Chi Minh
    if(provinceName == "Ho Chi Minh"):
        provinceName = "TP. Ho Chi Minh"

    with open(VIETNAM_FILE, mode="r") as f:
        provinces = json.load(f)

    print("Searching Viet Nam's database")
    for province in provinces:
        # Chuyển các chuỗi trong file thành không dấu
        name = unicodeToString(province['name'])
        if(name == provinceName):
            return province

    print("Cannot find")
    return {}


def covidDictToString(dict, option):
    '''
    Hàm chuyển một dictionary thông tin covid thành một chuỗi.
    Muốn thay đổi cách hiển thị thì chỉnh biến str
    - dict: dictionary đầu vào
    - option: tùy chọn xử lý loại thông tin
    - return: "deny" nếu như không tìm thấy thông tin và dict nhận vào là rỗng
    - return: str nếu có thông tin và đã được chuyển thành chuỗi
    '''

    # Không tìm thấy dict sẽ rỗng
    if(dict == {}):
        return "deny"

    # Thông tin của
    if(option == 1):  # thế giới
        str = "Country name: $country\nDates: $date\nConfirmed: $confirmed\nDeaths: $deaths\nRecovered: $recovered\nActive: $active\n"
        str += "Change in cases: $change_cases\nChange in deaths: $change_deaths\nChange in recovered: $change_recovered\n"
        str = Template(str).substitute(
            country=dict['Country'], date=dict['Date'], confirmed=dict['Confirmed'], deaths=dict[
                'Deaths'], recovered=dict['Recovered'], active=dict['Active'],
            change_cases=dict['Change in cases'], change_deaths=dict['Change in deaths'], change_recovered=dict['Change in recovered'])
        return str
    elif(option == 2):  # Việt Nam
        str = "Province name: $name\nDeath: $death\nCases: $cases\nToday cases: $casesToday\n"
        str = Template(str).substitute(
            name=dict['name'], death=dict['death'], cases=dict['cases'], casesToday=dict['casesToday'])
        return str
    else:
        return "deny"
