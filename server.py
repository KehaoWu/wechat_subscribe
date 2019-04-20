import re
import json
import requests
from flask import Flask, jsonify, request, abort
from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import (
    InvalidSignatureException,
    InvalidAppIdException,
)

WECHAT2_TOKEN = 'Y8ZHXhNlHYP'
WECHAT2_AES = '2u8i9T0hGWQrhHuw1gu60M83zCiZtr5bY8ZHXhNlHYP'

app = Flask(__name__)

city_2_id = {}
city_json = json.load(open('city.json'))
for city in city_json:
    city_name = city['city_name']
    city_2_id[city_name] = city['city_code']
    city_name = re.sub('市$', '', city_name)
    city_name = re.sub('县$', '', city_name)
    city_2_id[city_name] = city['city_code']


@app.route('/zhuzhou_weixin',  methods=['GET'])
def get():
    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    encrypt_type = request.args.get('encrypt_type', 'raw')
    msg_signature = request.args.get('signature', '')
    try:
        status = check_signature(WECHAT2_TOKEN, signature, timestamp, nonce)
    except InvalidSignatureException:
        abort(403)
    echo_str = request.args.get('echostr', '')
    return echo_str, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/zhuzhou_weixin', methods=['POST'])
def post():
    msg = parse_message(request.data)
    city = msg.content
    city_id = city_2_id.get(city)
    if city_id:
        req = requests.get("http://t.weather.sojson.com/api/weather/city/" + city_id)
        data = json.loads(req.text)
        today = data['data']
        tpl = "{} 今天{} {} {} {}"
        high = today['forecast'][0]['high']
        low = today['forecast'][0]['low']
        notice = today['forecast'][0]['notice']
        ganmao = today['ganmao']
        content = tpl.format(city, high, low, notice, ganmao)
    else:
        content = "没有找到您想要查找的城市"
    reply = create_reply(content, msg)
    return reply.render()


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=55001)
