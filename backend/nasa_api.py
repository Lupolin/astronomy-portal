import requests
from flask import jsonify

NASA_API_KEY = 'NeBwtfWqeNneNUgh4TYQmCbcWbcyD2iy1bkBalYN'  # 替換成您自己的 API 金鑰
NASA_APOD_URL = f'https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}'

def get_apod_data():
    response = requests.get(NASA_APOD_URL)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({'error': 'Unable to fetch data from NASA API'}), 500
