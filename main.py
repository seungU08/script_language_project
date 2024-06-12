from tkinter import *
from tkinter import font, messagebox
from googlemaps import Client
from PIL import Image, ImageTk
import requests
import io
import xml.etree.ElementTree as ET
from urllib.parse import unquote
import teller
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from tkinter.simpledialog import askstring

sender_email = "iseungu08@gmail.com"
sender_password = "cxnh frtn kpuk djzp"
receiver_email = ""



service_key = "OhqZIlJ2117DZPpq83eQross3rg03ldy13MwmQ%2Bdut9ItVp4wCaFPedERueZLsh3kq38pKP3n6rn0DUp7ylrFA%3D%3D"
url = 'http://api.data.go.kr/openapi/tn_pubr_prkplce_info_api'
service_key = unquote(service_key)
queryParams = {
    'serviceKey': service_key,
    'type': 'xml',
    'numOfRows': '100',
    'pageNo': '1'
}

# 첫 번째 요청을 보내고 전체 페이지 수를 구하기
response = requests.get(url, params=queryParams)
root = ET.fromstring(response.content)

# 페이지 사이즈 가져오기
# 전체 항목 수(totalCount)와 페이지당 항목 수(numOfRows) 가져오기
total_count = int(root.findtext('./body/totalCount'))
num_of_rows = int(root.findtext('./body/numOfRows'))


# 전체 페이지 수 계산
page_size = (total_count + num_of_rows - 1) // num_of_rows

# 모든 페이지의 데이터를 저장할 리스트
all_data = []

# 각 페이지의 데이터를 반복적으로 요청
for page in range(1, page_size + 1):
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
        basicCharge = item.findtext('basicCharge')
        addUnitTime = item.findtext('addUnitTime')
        addUnitCharge = item.findtext('addUnitCharge')

        all_data.append((prkplceNo, prkplceNm, prkplceSe, prkplceType, rdnmadr, lnmadr, prkcmprt, operDay, parkingchrgeInfo,basicCharge, addUnitTime ,addUnitCharge ))


class GUI:
    NAME = "Parking Finder"
    WIDTH = 1024
    HEIGHT = 768
    zoom = 13

    def __init__(self):
        self.window = Tk()
        self.window.title(self.NAME)
        self.window.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.window.configure(bg='gray')

        self.Home_Image = PhotoImage(file='home.png')
        self.GMail_Image = PhotoImage(file='gmail.png')
        self.TelegramImage = PhotoImage(file='telegram.png')
        self.CalculatorImgae = PhotoImage(file='calculator.png')

        MYFONT = font.Font(family='Helvetica', size=20)
        ListboxFont = font.Font(family='Helvetica', size=10)
        self.SearchEntry = Entry(self.window, font=MYFONT, width=40)
        self.SearchEntry.insert(0, "지역 검색")  # 초기 힌트 텍스트 설정
        self.SearchEntry.place(x=200, y=40)

        search_button = Button(self.window, text='검색', command=self.on_search_click)
        search_button.place(x=880, y=50)

        self.Result_Listbox = Listbox(self.window, font=ListboxFont, height=23, width=30, relief="raised", selectmode="extended")
        self.Result_Listbox.place(x=50, y=140)
        self.Result_Listbox.bind('<<ListboxSelect>>', self.on_listbox_select)  # 리스트박스 항목 클릭 이벤트 바인딩

        self.Google_API_Key = 'AIzaSyDnAQ21eoBblD7WGHlcV90hnmIWh5Hg21c'
        self.gmaps = Client(key=self.Google_API_Key)

        self.current_location = self.gmaps.geocode("한국공학대학교")[0]['geometry']['location']
        self.update_map(self.current_location)

        # 확대/축소 버튼 추가
        zoom_in_button = Button(self.window, text="+", command=self.zoom_in)
        zoom_in_button.place(x=970, y=140, width=30, height=30)

        zoom_out_button = Button(self.window, text="-", command=self.zoom_out)
        zoom_out_button.place(x=970, y=170, width=30, height=30)

        self.info_text = Text(self.window, height=30, width=33, wrap=WORD)
        self.info_text.place(x=300, y=140)

        self.select_TF = False
        self.canvas = Canvas(self.window, width=500, height=180)
        self.canvas.place(x=50, y=570)

        self.create_buttons()

        self.window.mainloop()

    def create_buttons(self):
        home_button = Button(self.window, image=self.Home_Image, command=self.home)
        home_button.place(x=630, y=670)

        Gamil_button = Button(self.window, image=self.GMail_Image, command=self.gmail)
        Gamil_button.place(x=730, y=670)

        Telegram_button = Button(self.window, image=self.TelegramImage, command=self.telegram)
        Telegram_button.place(x=830, y=670)

        Calculator_button = Button(self.window, image=self.CalculatorImgae, command=self.calculator)
        Calculator_button.place(x=930, y=670)

    def home(self):
        # 검색 엔트리 초기화
        self.SearchEntry.delete(0, END)
        self.SearchEntry.insert(0, "검색")

        # 결과 리스트박스 초기화
        self.Result_Listbox.delete(0, END)

        # 지도 초기화
        self.current_location = self.gmaps.geocode("한국공학대학교")[0]['geometry']['location']
        self.update_map(self.current_location)

        # 정보 텍스트 초기화
        self.info_text.delete('1.0', END)
        self.select_TF = False

        self.canvas.delete("all")

    def gmail(self):
        if self.select_TF:
            receiver_email = askstring('gamil', "메일 주소를 입력하세요")

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = self.info

            msg.attach(MIMEText(self.info, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
            server.quit()

            messagebox.showinfo("알림", "이메일로 메시지가 전송되었습니다.")
        else:
            messagebox.showinfo("알림", "전송할 정보를 선택해주세요.")

    def telegram(self):
        messagebox.showinfo('Telegram', '이승우/수목2반/봇')
        teller.telegram_main()


    def calculator(self):
        if self.select_TF:
            parking_time = eval(askstring('Calculator', "주차시간을 입력해주세요."))
            for data in all_data:
                if data[1] == self.selected_service_area:
                    if data[8] == "무료":
                        messagebox.showinfo('calculator', '무료')
                    else:
                        try:
                            parking_time = int(data[10])  # 문자열을 정수로 변환
                            charge = data[9] + (parking_time - data[10]) * data[11]
                            print(f"Charge: {charge}")
                        except ValueError as e:
                            print(f"Error converting to integer: {e}")
                        except TypeError as e:
                            print(f"Type error: {e}")

    def clear_search_hint(self, event):
        if self.SearchEntry.get() == "지역명(예: 강릉)":
            self.SearchEntry.delete(0, END)

    def restore_search_hint(self, event):
        if not self.SearchEntry.get():
            self.SearchEntry.insert(0, "지역명(예: 강릉)")

    def update_map(self, location):
        map_url = f"https://maps.googleapis.com/maps/api/staticmap?center={location['lat']},{location['lng']}&zoom={self.zoom}&size=400x425&maptype=roadmap"
        marker_url = f"&markers=color:red%7C{location['lat']},{location['lng']}"
        map_url += marker_url

        response = requests.get(map_url + '&key=' + self.Google_API_Key)
        image = Image.open(io.BytesIO(response.content))
        photo = ImageTk.PhotoImage(image)

        # 지도 이미지 표시
        if hasattr(self, 'map_label'):
            self.map_label.configure(image=photo)
            self.map_label.image = photo  # 참조를 유지하기 위해 속성에 이미지 저장
        else:
            self.map_label = Label(self.window, image=photo)
            self.map_label.image = photo  # 참조를 유지하기 위해 속성에 이미지 저장
            self.map_label.place(x=550, y=140)  # 적절한 위치에 지도 이미지 라벨 배치

    def on_search_click(self):
        self.Result_Listbox.delete(0, END)  # 기존 리스트박스 항목 제거
        search_text = self.SearchEntry.get().lower()  # 검색어를 소문자로 변환
        self.prkcmprt_data = []
        self.prk_list_name = []

        for data in all_data:
            if search_text in data[1].lower():  # serviceAreaName을 기준으로 검색
                self.Result_Listbox.insert(END, data[1])  # serviceAreaName을 리스트박스에 추가
                self.prkcmprt_data.append(data[6])
                self.prk_list_name.append(data[1])
        self.create_graph(self.prkcmprt_data, self.prk_list_name)

    def on_listbox_select(self, event):
        selected_index = self.Result_Listbox.curselection()
        if selected_index:
            self.select_TF = True
            index = selected_index[0]
            self.selected_service_area = self.Result_Listbox.get(index)
            for data in all_data:
                if data[1] == self.selected_service_area:
                    address = data[5]  # 선택된 데이터의 주소 가져오기
                    print("Selected data:", data)
                    self.current_location = self.gmaps.geocode(address)[0]['geometry']['location']
                    self.update_map(self.current_location)  # 지도 업데이트
                    self.update_info(data)  # 데이터 표시 업데이트
                    break

    def update_info(self, data):
        self.info_text.delete('1.0', END)  # 기존 텍스트 제거
        self.info = (
            f"주자장관리번호: {data[0]}\n"
            f"주차장명: {data[1]}\n"
            f"주차장구분: {data[2]}\n"
            f"주차장유형: {data[3]}\n"
            f"도로명주소: {data[4]}\n"
            f"지번주소: {data[5]}\n"
            f"주차구획수: {data[6]}\n"
            f"운영요일: {data[7]}\n"
            f"요금정보: {data[8]}\n"
        )
        self.info_text.insert(END, self.info)

    def zoom_in(self):
        if self.zoom < 21:  # 구글 지도 API는 최대 21까지 지원합니다.
            self.zoom += 1
            self.update_map(self.current_location)  # 현재 위치를 사용해 지도를 업데이트

    def zoom_out(self):
        if self.zoom > 1:  # 구글 지도 API는 최소 1까지 지원합니다.
            self.zoom -= 1
            self.update_map(self.current_location)  # 현재 위치를 사용해 지도를 업데이트

    def create_graph(self,data, name_list):
        self.canvas.delete('all')
        int_data = [int(value) for value in data]
        max_prkcmprt = max(int_data)
        bar_width = 8
        x_gap = 10
        x0 = 60
        y0 = 100
        for i in range(len(int_data)):
            x1 = x0 + i * (bar_width + x_gap)
            y1 = y0 - 80 * int_data[i] / max_prkcmprt
            self.canvas.create_rectangle(x1, y1, x1 + bar_width, y0, fill='blue')
            self.canvas.create_text(x1 + bar_width / 2, y0 + 50, text=name_list[i], anchor='n', angle=90)
            self.canvas.create_text(x1 + bar_width / 2, y1 - 10, text=data[i], anchor='s')

        # 병원 목록에 추가


GUI()
