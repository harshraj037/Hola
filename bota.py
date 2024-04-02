import os
import requests
import json
from datetime import datetime, timedelta
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import random
import string
import time

TOKEN = '6990798388:AAFLHhtafk9-0s5h5zuu-VmgVlCZ8MTrBNQ'
current_token = None
token_expiration = None
user_data = {}


def users_command(update, context):
    users_info = "\n".join([f"{user_id}: t.me/{username}" for user_id, username in user_data.items()])
    update.message.reply_text(f"Bot Users:\n{users_info}")



def generate_random_string():
    pattern = [''.join(random.choices(string.digits, k=4)), '-', ''.join(random.choices(string.ascii_lowercase, k=4)),
               ''.join(random.choices(string.digits, k=1)), ''.join(random.choices(string.ascii_lowercase, k=1)), '-',
               ''.join(random.choices(string.digits, k=4)), ''.join(random.choices(string.ascii_lowercase, k=1)),
               ''.join(random.choices(string.digits, k=3))]
    return ''.join(pattern)


def upload_image(image_data):
    global current_token, token_expiration
    if not current_token or datetime.now() > token_expiration:
        current_token = refresh_token()
        token_expiration = datetime.now() + timedelta(hours=1)
    random_string = generate_random_string()
    url_first_request = f'https://firebasestorage.googleapis.com/v0/b/mimic-prod.appspot.com/o?uploadType=resumable&name=client-inputs%2FsFPEWFYSrMZ7uSCCofhf5uSdh1c2%2Fb9dc5a2d-{random_string}.JPEG'
    headers_first_request = {'Authorization': f'Bearer {current_token}',
                             'X-Firebase-Storage-Version': 'Android/[No Gmscore]',
                             'X-Goog-Upload-Header-Content-Type': 'image/jpeg', 'X-Goog-Upload-Protocol': 'resumable',
                             'x-firebase-gmpid': '1:585921882981:android:719cc14f7d5c1925778f8c',
                             'X-Goog-Upload-Command': 'start',
                             'Content-Type': 'application/json',
                             'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; Redmi Note 7 Pro Build/N6F26Q)',
                             'Host': 'firebasestorage.googleapis.com', 'Connection': 'Keep-Alive',
                             'Accept-Encoding': 'gzip'}
    payload_first_request = {"contentType": "image/jpeg"}
    response_first_request = requests.post(url_first_request, headers=headers_first_request, json=payload_first_request)
    if response_first_request.status_code == 200:
        upload_url = response_first_request.headers['X-Goog-Upload-URL']
        url_second_request = upload_url
        headers_second_request = {"Authorization": f'Bearer {current_token}',
                                  "X-Firebase-Storage-Version": "Android/[No Gmscore]",
                                  "X-Goog-Upload-Offset": "0", "X-Goog-Upload-Protocol": "resumable",
                                  "x-firebase-gmpid": "1:585921882981:android:719cc14f7d5c1925778f8c",
                                  "X-Goog-Upload-Command": "upload, finalize",
                                  "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 7.1.2; Redmi Note 7 Pro Build/N6F26Q)",
                                  "Host": "firebasestorage.googleapis.com", "Connection": "Keep-Alive",
                                  "Accept-Encoding": "gzip"}
        response_second_request = requests.post(url_second_request, headers=headers_second_request, data=image_data)
        if response_second_request.status_code == 200:
            response_data = json.loads(response_second_request.text)
            name = response_data['name']
            return name
        elif response_second_request.status_code == 401:
            current_token = refresh_token()
            token_expiration = datetime.now() + timedelta(hours=1)
            return upload_image(image_data)
        else:
            return f"Error: {response_second_request.status_code}"
    else:
        return f"Error: {response_first_request.status_code}"


def refresh_token():
    url = 'https://securetoken.googleapis.com/v1/token?key=AIzaSyCmxu9bG292Np8kDIKJi146DFXF0wR6igU'
    headers = {'Content-Type': 'application/json', 'X-Android-Package': 'com.magiclabs.mimic',
               'X-Android-Cert': '61ED377E85D386A8DFEE6B864BD85B0BFAA5AF81',
               'Accept-Language': 'en-US', 'X-Client-Version': 'Android/Fallback/X22000000/FirebaseCore-Android',
               'X-Firebase-GMPID': '1:585921882981:android:719cc14f7d5c1925778f8c', 'X-Firebase-Client': 'H4sIAAAAAAAAAKtWykhNLCpJSk0sKVayio7VUSpLLSrOzM9TslIyUqoFAFyivEQfAAAA',
               'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; Redmi Note 7 Pro Build/N6F26Q)'}
    data = {"grantType": "refresh_token",
            "refreshToken": "AMf-vBzIA0N_Jxka09K13CN5XVLKeR8WPCgWd4wQAudfIr0YejoO0k28S6WsfwoLp2CNzZ3zwOR0Vxjo05ut-o32UEplXKAFPmZQRlIZjgriY10FzH04RWSY2rWtKlF40te_8n4Tu1orvF0DfjY6H6Q4kG6wJ_LzDdsA2UTiABC4lfIGyiLLBxo"}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None


def start(update, context):
    user_id = update.effective_user.id
    username = update.effective_user.username
    user_data[user_id] = username  # Save user data
    update.message.reply_text('Welcome to Mimic AI Bot! Create your mimics by using the command /mimic.')

def mimic(update, context):
    user_id = update.effective_user.id
    username = update.effective_user.username
    user_data[user_id] = username  # Save user data
    update.message.reply_text('Please upload an image with a clear face. We will process your request shortly.')


def handle_image(update, context):
    file_id = update.message.photo[-1].file_id
    file_info = context.bot.get_file(file_id)
    image_url = file_info.file_path
    image_data = requests.get(image_url).content
    generation_message = f"👨‍🎤 Requested by: {update.effective_user.first_name}\n" \
                         f"📷 Mimic Id: {generate_random_string()}\n" \
                         f"⚡ Song ID: {random.randint(1001, 1099)}\n" \
                         f"🤵 BOT BY: 匚卄卂尺LIE"
    update.message.reply_text(generation_message)
    firebase_response = upload_image(image_data)
    if firebase_response:
        process_image(update, context, firebase_response)
    else:
        update.message.reply_text("Error uploading image to Firebase.")


def process_image(update, context, firebase_response, tries=0, message_id=None, previous_message=None):
    time.sleep(5)


    url_first = "https://api.mimicapp.co/publisher/v2/get-credentials?ip=1"
    headers_first = {"Host": "api.mimicapp.co", "Accept": "application/json", "x-platform": "android",
                     "x-userid": "cfBzhSqYQhm5Yy_OLTo521", "Accept-Encoding": "gzip", "User-Agent": "okhttp/4.9.2",
                     "If-None-Match": 'W/"71-cS/o5ZUxtLRbtcp0ulmrLX4976U"'}
    response_first = requests.get(url_first, headers=headers_first)
    process_id = response_first.json()["response"]["processId"]
    song_id = random.randint(1001, 1099)
    if message_id is not None:
        new_message = f"({tries + 1}/3) Generating your video. Please wait patiently..."
        context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message_id, text=new_message)
    else:
        message = update.message.reply_text(f"(1/3) Generating your video. Please wait patiently...")
        message_id = message.message_id
    url_second = 'https://api.mimicapp.co/publisher/v2/publish-image'
    headers_second = {'Host': 'api.mimicapp.co', 'accept': 'application/json', 'x-platform': 'android',
                      'x-userid': 'cfBzhSqYQhm5Yy_OLTo521',
                      'content-type': 'application/json', 'accept-encoding': 'gzip', 'user-agent': 'okhttp/4.9.2'}
    data_second = {'processId': process_id, 'imageDirectoryPath': firebase_response, 'songId': song_id,
                   'breed': None, 'is_raw': True, 'isOnlyHead': True}
    response_second = requests.post(url_second, headers=headers_second, json=data_second)
    time.sleep(35)
    url_third = 'https://api.mimicapp.co/result/v2/status'
    params_third = {'processId': process_id}
    headers_third = {'Host': 'api.mimicapp.co', 'Accept': 'application/json', 'X-Platform': 'android',
                     'X-Userid': 'cfBzhSqYQhm5Yy_OLTo521', 'Accept-Encoding': 'gzip', 'User-Agent': 'okhttp/4.9.2'}
    response_third = requests.get(url_third, params=params_third, headers=headers_third)
    video_url = None
    try:
        video_url = response_third.json()["response"]["data"]["base_url"]
    except KeyError:
        if tries < 2:
            new_message = f"({tries + 1}/3) Trying again. Please wait patiently..."
            context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=message_id, text=new_message)
            return process_image(update, context, firebase_response, tries + 1, message_id, previous_message)
        else:
            update.message.reply_text(
                "Please send another image with a clear face visible. Unable to generate video with this image.")
            return
    if video_url:
        video_response = requests.get(video_url)
        if video_response.status_code == 200:
            send_video(update, context, video_response.content)
        else:
            update.message.reply_text('Error downloading video. Please try again later.')
    else:
        update.message.reply_text('Error generating video. Please try again later.')


def send_video(update, context, video_data):
    video_file = f'video_{update.message.chat_id}.mp4'
    with open(video_file, 'wb') as f:
        f.write(video_data)
    with open(video_file, 'rb') as f:
        context.bot.send_video(chat_id=update.message.chat_id, video=f)
    os.remove(video_file)
    context.bot.send_message(chat_id=update.message.chat_id,
                             text="🌟 This bot is made by Charlie!(@chillyyyyyyyy) 🚀 Let me know if there's anything else I can do for you!")


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("users", users_command, run_async=True))  # Pass run_async=True here
    dp.add_handler(CommandHandler("start", start, run_async=True))  # Pass run_async=True here
    dp.add_handler(CommandHandler("mimic", mimic, run_async=True))  # Pass run_async=True here
    dp.add_handler(MessageHandler(Filters.photo, handle_image, run_async=True))  # Pass run_async=True here
    
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
