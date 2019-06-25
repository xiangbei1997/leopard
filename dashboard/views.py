from django.shortcuts import render
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response

import pandas as pd
import json
import datetime
import pymongo

def index(request):
    return render(request, 'index.html')


class DaysList(APIView):
    def __init__(self, **kwargs):
        super(DaysList, self).__init__(**kwargs)
        self.client = pymongo.MongoClient(settings.MONGO_URI)
        self.db = self.client['every_day_num']
        self.demo = {
            'data_company': '企业信息',
            'data_company_project':'企业项目',
            'data_company_project_tender' :'项目招投标',
            'data_company_project_censor' : '项目施工图审查',
            'data_company_project_censor_engineer' : '施工图审查从业人员',
            'data_company_project_contract': '项目合同备案',
            'data_company_project_builder_licence': '项目施工许可',
            'data_company_project_finish': '项目竣工验收备案',
            'data_cert': '资质',
            'data_engineer': '注册人员',
            'data_company_record': '外省备案',
            'data_company_record_engineer': '外省备案人员',
        }

    def get(self, request):
        now = datetime.datetime.now().date()
        month = now.replace(day=1)

        res = self.db['updata_adddata_num'].find({
            "data_time":{"$gte": str(month), "$lte": str(now)}
        }).sort("data_time", 1)
        self.client.close()

        data = []
        for row in res:
            del row['_id']
            tmp = {}
            date = row.pop('data_time')
            df = pd.DataFrame(list(row.values()))
            tmp['date'] = date
            tmp['value'] = (df.iloc[:,0].sum(), df.iloc[:,1].sum())
        
            data.append(tmp)

        return Response(data)

    def post(self, request):
        yesterday = datetime.datetime.now().date() - datetime.timedelta(days=1)
        date = request.POST.get('date', str(yesterday))
        res = self.db['updata_adddata_num'].find({'data_time':date})
        self.client.close()
        
        tmp = {}
        for row in res:
            del row['_id']

            tmp['date'] = row.pop('data_time')
            item = []
            add = []
            update = []
            
            for k, v in row.items():
                item.append(self.demo[k])
                add.append(v[1])
                update.append(v[0])
            tmp['add'] = add
            tmp['update'] = update
            tmp['item'] = item

        return Response(tmp)