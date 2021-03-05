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

questions = []

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
            message_id = update['object']['message']['conversation_message_id']
            api.messages.markAsRead(peer_id=from_id)

            if peer_id != CHAT_ID_REPORT and peer_id != CHAT_ID_QUESTIONS:
                for word in message.lower().split():
                    for bad_word in bad_words:
                        if is_appropriate_word(word, bad_word):
                            api.messages.send(
                                random_id=int(time() * 1000),
                                peer_id=peer_id,
                                message=f'@id{from_id}, пожалуйста, давай не будем употреблять эти слова.'
                            )

                            response = api.messages.getConversationsById(peer_ids=peer_id)
                            title = response['items'][0]['chat_settings']['title']

                            api.messages.send(
                                random_id=int(time() * 1000),
                                peer_id=CHAT_ID_REPORT,
                                message=f'Название беседы: {title}\n' +
                                        f'Пользователь: @id{from_id}\n' +
                                        f'Текст: {message}\n'
                            )

                            break

                ref = re.match(f'\[{BOT_NAME}\|\w+\]', message)
                if ref:
                    message = message.replace(ref.group(0), "").strip()
                    api.messages.send(
                        random_id=int(time() * 1000),
                        peer_id=CHAT_ID_QUESTIONS,
                        message=f'{message}',
                    )
                    questions.append((peer_id, from_id, message))

            elif peer_id == CHAT_ID_QUESTIONS:
                fwd_message = update['object']['message']['fwd_messages']
                reply_message = update['object']['message'].get('reply_message', None)
                if reply_message is not None:
                    fwd = reply_message['text']
                elif len(fwd_message) == 1:
                    fwd = fwd_message[0]['text']
                else:
                    continue

                for question in questions:
                    if question[2] == fwd:
                        peer_id = question[0]
                        to_id = question[1]
                        api.messages.send(
                            random_id=int(time() * 1000),
                            peer_id=peer_id,
                            message=f'Ответ на вопрос для @id{to_id}:\n' +
                                    f'\n' +
                                    f'{message}',
                        )

    ts = longPoll['ts']
