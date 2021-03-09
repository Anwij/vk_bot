from requests import post
from time import time
import re
import vk
from ldistance import is_appropriate_word
from config import *


bad_words = []
f = open('badwords.txt', 'r', encoding='utf-8')
for bad_word in f:
    bad_words.append(bad_word.strip().lower())

session = vk.Session(access_token=VK_TOKEN)
api = vk.API(session, v=VK_VERSION)

longPoll = api.groups.getLongPollServer(group_id=GROUP_ID)
server, key, ts = longPoll['server'], longPoll['key'], longPoll['ts']
while True:
    longPoll = post(server, data={
        'act': 'a_check',
        'key': key,
        'ts': ts,
        'wait': 25,
    }).json()

    for update in longPoll.get('updates', []):
        if update['type'] == 'message_new':
            message = update['object']['message']['text']
            from_id = update['object']['message']['from_id']
            peer_id = update['object']['message']['peer_id']
            api.messages.markAsRead(peer_id=peer_id, mark_conversation_as_read=1)

            if peer_id != CHAT_ID_REPORT and peer_id != CHAT_ID_QUESTIONS:
                for word in message.lower().split():
                    for bad_word in bad_words:
                        if is_appropriate_word(word, bad_word):
                            response = api.messages.getConversationsById(peer_ids=CHAT_ID)
                            title = response['items'][0]['chat_settings']['title']

                            message_id = api.messages.getHistory(peer_id=CHAT_ID, count=1)['items'][0]['id']
                            api.messages.send(
                                random_id=int(time() * 1000),
                                peer_id=CHAT_ID_REPORT,
                                message=f'Название беседы: {title}\n' +
                                        f'Пользователь: @id{from_id}\n' +
                                        f'Текст: {message}\n',
                                forward_messages=message_id
                            )

                            api.messages.send(
                                random_id=int(time() * 1000),
                                peer_id=CHAT_ID,
                                message=f'@id{from_id}, пожалуйста, давай не будем употреблять эти слова.'
                            )

                            break

                ref = re.match(f'\[{BOT_NAME}\|\w+\]', message)
                if ref:
                    message = message.replace(ref.group(0), "").strip()
                    message_id = api.messages.getHistory(peer_id=CHAT_ID, count=1)['items'][0]['id']
                    api.messages.send(
                        random_id=int(time() * 1000),
                        peer_id=CHAT_ID_QUESTIONS,
                        message='',
                        forward_messages=message_id
                    )

            elif peer_id == CHAT_ID_QUESTIONS:
                fwd_message = update['object']['message']['fwd_messages']
                reply_message = update['object']['message'].get('reply_message', None)

                if reply_message is not None and len(reply_message['fwd_messages']) == 1:
                    to_id = reply_message['fwd_messages'][0]['from_id']
                elif len(fwd_message) == 1 and len(fwd_message[0]['fwd_messages']) == 1:
                    to_id = fwd_message[0]['fwd_messages'][0]['from_id']
                else:
                    continue

                message_id = api.messages.getHistory(peer_id=CHAT_ID_QUESTIONS, count=1)['items'][0]['id']
                api.messages.send(
                    random_id=int(time() * 1000),
                    peer_id=CHAT_ID,
                    message=f'Поступил ответ на ваш вопрос @id{to_id}',
                    forward_messages=message_id
                )
    if longPoll.get('updates', None):
        ts = longPoll['ts']
