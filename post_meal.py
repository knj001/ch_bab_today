import requests
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# 환경변수 로드
NEIS_USERNAME = os.getenv('NEIS_USERNAME')
NEIS_API_KEY = os.getenv('NEIS_API_KEY')
IG_GRAPH_TOKEN = os.getenv('IG_GRAPH_TOKEN')
IG_BUSINESS_ACCOUNT_ID = os.getenv('IG_BUSINESS_ACCOUNT_ID')

def fetch_meal():
    """NEIS 급식 정보 가져오기"""
    today = datetime.now().strftime('%Y%m%d')
    
    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        'ATPT_OFCDC_SC_CODE': 'C10',
        'SD_SCHUL_CODE': NEIS_USERNAME,
        'MLSV_YMD': today,
        'KEY': NEIS_API_KEY,
        'Type': 'json',
        'pIndex': 1,
        'pSize': 100
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'mealServiceDietInfo' in data and len(data['mealServiceDietInfo']) > 1:
        if data['mealServiceDietInfo'][1]['row']:
            return data['mealServiceDietInfo'][1]['row'][0]['DDISH']
    return "급식 정보 없음"

def create_meal_image(meal_text):
    """급식 이미지 생성"""
    img = Image.new('RGB', (1080, 1920), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 60)
        title_font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 80)
    except:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # 제목
    draw.text((100, 200), "오늘의 급식", fill='black', font=title_font)
    
    # 날짜
    date_str = datetime.now().strftime('%Y년 %m월 %d일')
    draw.text((100, 400), date_str, fill='gray', font=font)
    
    # 급식 내용
    lines = meal_text.split('<br/>')
    y_pos = 600
    for line in lines[:8]:
        draw.text((100, y_pos), line.strip(), fill='black', font=font)
        y_pos += 100
    
    img.save('meal.png')
    return 'meal.png'

def post_to_instagram_graph(image_path):
    """Instagram Graph API로 피드 게시"""
    url = f"https://graph.instagram.com/v18.0/{IG_BUSINESS_ACCOUNT_ID}/media"
    
    with open(image_path, 'rb') as img:
        files = {'file': img}
        data = {
            'caption': f"오늘의 급식\n{datetime.now().strftime('%Y년 %m월 %d일')}",
            'access_token': IG_GRAPH_TOKEN,
            'media_type': 'IMAGE'
        }
        
        response = requests.post(url, files=files, data=data)
        
    if response.status_code == 200:
        media_id = response.json()['id']
        
        # 피드에 게시 (2단계)
        publish_url = f"https://graph.instagram.com/v18.0/{IG_BUSINESS_ACCOUNT_ID}/media_publish"
        publish_data = {
            'creation_id': media_id,
            'access_token': IG_GRAPH_TOKEN
        }
        
        pub_response = requests.post(publish_url, data=publish_data)
        print("Instagram 피드 게시 완료!")
        return True
    else:
        print(f"API 오류: {response.text}")
        return False

# 실행
if __name__ == "__main__":
    try:
        meal = fetch_meal()
        print(f"급식: {meal}")
        
        image_path = create_meal_image(meal)
        post_to_instagram_graph(image_path)
        
    except Exception as e:
        print(f"오류: {e}")
        exit(1)
