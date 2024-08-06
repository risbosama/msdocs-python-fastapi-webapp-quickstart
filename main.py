from fastapi import FastAPI, Form, Query, Request, status
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import re
import pandas as pd
import numpy as np

class Client:
    def __init__(self, msisdn, flag_hvc, flag_sme, data_user, momo_app_user, flag_merchant, momo_dormancy, mymtn_usage):
        self.msisdn = msisdn
        self.flag_hvc = flag_hvc
        self.flag_sme = flag_sme
        self.data_user = data_user
        self.momo_app_user = momo_app_user
        self.flag_merchant = flag_merchant
        self.momo_dormancy = momo_dormancy
        self.mymtn_usage = mymtn_usage

    def __str__(self):
        return (f"MSISDN: {self.msisdn}, FLAG_HVC: {self.flag_hvc}, FLAG_SME: {self.flag_sme}, "
                f"DATA_USER: {self.data_user}, MOMO_APP_USER: {self.momo_app_user}, "
                f"FLAG_MERCHANT: {self.flag_merchant}, MOMO_DORMANCY: {self.momo_dormancy}, "
                f"MYMTN_USAGE: {self.mymtn_usage}")


def find_client(msisdn_to_find, file_path='base.xls'):
    # Lire le fichier Excel
    df = pd.read_excel(file_path)

    # Trouver la ligne correspondant au MSISDN
    df['MSISDN'] = df['MSISDN'].astype(str)
    msisdn_to_find = str(msisdn_to_find)  # Ensure msisdn_to_find is also a string
    client_row = df[df['MSISDN'] == msisdn_to_find]

    # Vérifier si le client est trouvé
    client_row = client_row.replace({np.nan: None})
    if client_row.empty:
        print(f"Client with MSISDN {msisdn_to_find} not found.")
        return None
    
    # Extraire les données et créer une instance de Client
    row = client_row.iloc[0]  # Prendre la première (et seule) ligne correspondante
    client = Client(
        msisdn=row['MSISDN'],
        flag_hvc=row['FLAG_HVC'],
        flag_sme=row['FLAG_SME'],
        data_user=row['DATA_USER'],
        momo_app_user=row['MOMO_APP_USER'],
        flag_merchant=row['FLAG_MERCHANT'],
        momo_dormancy=row['MOMO_DORMANCY'],
        mymtn_usage=row['MYMTN_USAGE']
    )

    return format_output(client)

def format_output(client):
    base_response = ''
    base_response = base_response + "The customer " + client.msisdn + " has the following characteristics : \n"
    base_response = base_response + "->"
    return base_response

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    print('Request for index page received')
    return templates.TemplateResponse('index.html', {"request": request})

@app.get("/api/validateinput")
async def read_validateinput(msisdn: str = Query(...)):
    pattern = r'^(65|66|67|68|69)\d{7}$'
    result = bool(re.match(pattern, msisdn))
    return result

@app.get("/api/lookup")
async def read_validateinput(msisdn: str = Query(...)):
    client = find_client(msisdn)
    return client

@app.get('/favicon.ico')
async def favicon():
    file_name = 'favicon.ico'
    file_path = './static/' + file_name
    return FileResponse(path=file_path, headers={'mimetype': 'image/vnd.microsoft.icon'})

@app.post('/hello', response_class=HTMLResponse)
async def hello(request: Request, name: str = Form(...)):
    if name:
        print('Request for hello page received with name=%s' % name)
        return templates.TemplateResponse('hello.html', {"request": request, 'name':name})
    else:
        print('Request for hello page received with no name or blank name -- redirecting')
        return RedirectResponse(request.url_for("index"), status_code=status.HTTP_302_FOUND)

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)

