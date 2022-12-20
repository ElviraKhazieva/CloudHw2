import telegram
import os
import ydb
import ydb.iam
import json

TOKEN = os.getenv("BOT_TOKEN")
BOT = telegram.Bot(token=TOKEN)
driver: ydb.Driver
PHOTO_LINK_TEMPLATE = os.getenv("PHOTO_LINK_TEMPLATE")
OBJECT_LINK_TEMPLATE = os.getenv("OBJECT_LINK_TEMPLATE")


def init_driver():
    global driver
    driver = get_driver()
    driver.wait(timeout=10)


def get_driver():
    endpoint = os.getenv("DB_ENDPOINT")
    path = os.getenv("DB_PATH")
    creds = ydb.iam.MetadataUrlCredentials()
    driver_config = ydb.DriverConfig(
        endpoint, path, credentials=creds
    )
    return ydb.Driver(driver_config)


def set_name_of_last_photo(name):
    query = f"""
        PRAGMA TablePathPrefix("{os.getenv("DB_PATH")}");
        SELECT * FROM photo WHERE name is NULL LIMIT 1;
        """
    session = driver.table_client.session().create()
    result_sets = session.transaction().execute(query, commit_tx=True)
    face_id = ''
    for row in result_sets[0].rows:
        face_id = row.face_id
    if face_id == '':
        return
    query = f"""
    PRAGMA TablePathPrefix("{os.getenv("DB_PATH")}");
    UPDATE photo SET name = '{name}' WHERE face_id = '{face_id}';
    """
    session.transaction().execute(query, commit_tx=True)
    session.closing()


def find_photos_by_name(chat_id, name):
    query = f"""
    PRAGMA TablePathPrefix("{os.getenv("DB_PATH")}");
    SELECT DISTINCT original_id, name FROM photo WHERE name = '{name}';
    """
    session = driver.table_client.session().create()
    result_sets = session.transaction().execute(query, commit_tx=True)
    session.closing()
    if len(result_sets[0].rows) == 0:
        BOT.sendMessage(chat_id, text=f'Photos with name {name} not found')
    for row in result_sets[0].rows:
        object_id = row.original_id
        photo_url = OBJECT_LINK_TEMPLATE.format(object_id)
        BOT.send_photo(chat_id=chat_id, photo=photo_url)


def get_face(chat_id):
    query = f"""
    PRAGMA TablePathPrefix("{os.getenv("DB_PATH")}");
    SELECT * FROM photo WHERE name is NULL LIMIT 1;
    """
    session = driver.table_client.session().create()
    result_sets = session.transaction().execute(query, commit_tx=True)
    session.closing()
    for row in result_sets[0].rows:
        face_id = row.face_id
        photo_url = PHOTO_LINK_TEMPLATE.format(face_id)
        BOT.send_photo(chat_id=chat_id, photo=photo_url)


def main(event, context):
    init_driver()
    request = event['body']
    update = telegram.Update.de_json(json.loads(request), BOT)
    command = update.message.text.encode('utf-8').decode()
    chat_id = update.message.chat.id

    if command == '/start':
        BOT.sendMessage(chat_id=chat_id, text='Hello!)')
        return
    if command == '/getface':
        get_face(chat_id)
        return
    if command.startswith('/find'):
        args = command.split(' ')
        find_photos_by_name(chat_id, args[1])
        return

    set_name_of_last_photo(command)
    BOT.sendMessage(chat_id=chat_id, text=f'Set new name {command}')
