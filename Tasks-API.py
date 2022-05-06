import os.path
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

#使用するスコープ（tasks api)
SCOPES = ['https://www.googleapis.com/auth/tasks']

#credentials.jsonから認証情報を取得
def credentials():
    creds = None
    #tokenが存在する場合
    if os.path.exists('./gitignore/token.json'):
        creds = Credentials.from_authorized_user_file('./gitignore/token.json', SCOPES)
    # credentialsファイルにvalidがない場合、ログイン認証する。
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('./gitignore/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('./gitignore/token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def main():
    creds =credentials()

    try:
        #tasksAPIのエンドポイントを呼び出している
        service = build('tasks', 'v1', credentials=creds)

        results = service.tasklists().list(maxResults=100).execute()
        items_list = list(results.get('items', []))#list形式に変換しながら、取得結果をitemsに代入

        if not items_list:
            print('No task lists found.')
            return

        print('Task lists:')
        for i,item in zip(range(len(items_list)),items_list):
            print(u'{0}:{1} ({2})'.format(i,item['title'], item['id']))

        select = int(input("select-tasklists(integer):"))
        select_id = str(items_list[select]['id'])
        res_tasks = service.tasks().list(tasklist=select_id).execute()
        tasks_list = list(res_tasks.get('items',[]))
        
        if not tasks_list:
            print('No task lists found.')

        for i,task in zip(range(len(tasks_list)),tasks_list):
            due = None
            try:
                due = task['due']
                print(u'{0}:{1}({2})'.format(i,task['title'],due))
            except KeyError:
                due = 'Not Set'
                print(u'{0}:{1}({2})'.format(i,task['title'],due))

    except HttpError as err:
        print(err)


if '__main__' == __name__:
    while True:
        confirm = input('#')
        if confirm == '':
            main()
        else:
            exit()
