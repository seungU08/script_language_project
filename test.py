import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote

# URL 및 서비스 키 설정
url = "http://api.data.go.kr/openapi/tn_pubr_prkplce_info_api"
service_key = "OhqZIlJ2117DZPpq83eQross3rg03ldy13MwmQ%2Bdut9ItVp4wCaFPedERueZLsh3kq38pKP3n6rn0DUp7ylrFA%3D%3D"
service_key = unquote(service_key)
queryParams = {
    'serviceKey': service_key,
    'type': 'xml',
    'numOfRows': '100',
    'pageNo': '1'
}

# 첫 번째 요청을 보내고 응답 내용 확인
response = requests.get(url, params=queryParams)
xml_content = response.text
print(xml_content)  # 응답 XML 내용을 출력하여 구조를 확인
print(url)

# XML 데이터 파싱
root = ET.fromstring(response.content)

# 전체 항목 수(totalCount)와 페이지당 항목 수(numOfRows) 가져오기
total_count = root.findtext('./body/totalCount')
num_of_rows = root.findtext('./body/numOfRows')

# 디버깅을 위해 추출한 값을 출력
print(f"Extracted total_count: {total_count}")
print(f"Extracted num_of_rows: {num_of_rows}")

# 값이 존재하는지 확인 후, 존재할 경우 int로 변환
if total_count is not None and num_of_rows is not None:
    try:
        total_count = int(total_count)
        num_of_rows = int(num_of_rows)
    except ValueError as e:
        print(f"Error converting to int: {e}")
        print(f"total_count: {total_count}, num_of_rows: {num_of_rows}")
        exit()
else:
    print("Error: Could not find 'totalCount' or 'numOfRows' in the response.")
    print(f"total_count: {total_count}, num_of_rows: {num_of_rows}")
    exit()

# 전체 페이지 수 계산
total_pages = (total_count + num_of_rows - 1) // num_of_rows

print(f"Total Count: {total_count}")
print(f"Number of Rows per Page: {num_of_rows}")
print(f"Total Pages: {total_pages}")


all_data = []
for page in range(1, total_pages + 1):
    queryParams['pageNo'] = str(page)
    response = requests.get(url, params=queryParams)
    root = ET.fromstring(response.text)
    for item in root.iter('item'):
        prkplceNo = item.findtext('prkplceNo')
        prkplceNm = item.findtext('prkplceNm')
        prkplceSe = item.findtext('prkplceSe')
        prkplceType = item.findtext('prkplceType')
        rdnmadr = item.findtext('rdnmadr')
        lnmadr = item.findtext('lnmadr')
        prkcmprt = item.findtext('prkcmprt')
        operDay = item.findtext('operDay')
        parkingchrgeInfo = item.findtext('parkingchrgeInfo')

        all_data.append((prkplceNo, prkplceNm, prkplceSe, prkplceType, rdnmadr, lnmadr, prkcmprt, operDay, parkingchrgeInfo))

for data in all_data:
    print(data)
