import requests
import os
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import instagrapi

# 환경변수 로드
NEIS_USERNAME = os.getenv('NEIS_USERNAME')  # 학교코드 B100000501
NEIS_API_KEY = os.getenv('NEIS_API_KEY')    # 5616183c27ac48bba6dbd64ead54be1a
IG_USERNAME = os.getenv('IG_USERNAME')
IG_PASSWORD = os.getenv('IG_PASSWORD')

def fetch_meal():
    """NEIS 급식 정보 가져오기"""
    today = datetime.now().strftime('%Y%m%d')
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    
    url = "https://open.neis.go.kr/hub/mealServiceDietInfo"
    params = {
        'ATPT_OFCDC_SC_CODE': 'B10',
        'SD_SCHUL_CODE': NEIS_USERNAME,
        'MLSV_YMD': today,
        'KEY': NEIS_API_KEY,
        'Type': 'json',
        'pIndex': 1,
        'pSize': 100
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if 'mealServiceDietInfo' in data and data['mealServiceDietInfo'][1]['row']:
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
    
    # 급식 내용 (줄바꿈 처리)
    lines = meal_text.split('<br/>')
    y_pos = 600
    for line in lines[:8]:  # 최대 8줄
        draw.text((100, y_pos), line.strip(), fill='black', font=font)
        y_pos += 100
    
    img.save('meal.png')
    return 'meal.png'

def post_to_instagram(image_path):
    """Instagram 스토리 업로드"""
    cl = instagrapi.Client()
    cl.login(IG_USERNAME, IG_PASSWORD)
    cl.photo_upload_to_story(image_path)
    print("Instagram 스토리 업로드 완료!")

# 실행
if __name__ == "__main__":
    try:
        meal = fetch_meal()
        print(f"급식: {meal}")
        
        image_path = create_meal_image(meal)
        post_to_instagram(image_path)
        
    except Exception as e:
        print(f"오류: {e}")
        exit(1)
