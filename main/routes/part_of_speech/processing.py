import os
import time
from datetime import datetime
from flask import request, json
import flask_restful as restful




class POSData(restful.Resource):

    def post(self):
        data = request.get_data().decode('utf-8')
        data = json.loads(data)







# POLLING #
############################## POLLING ###########################
class POSDataUpdate(restful.Resource):

    def _is_updated(self, request_time):
        """
        Returns if resource is updated or it's the first
        time it has been requested.
        args:
            request_time: last request timestamp
        """
        return os.stat('main/routes/part_of_speech/data.txt').st_mtime > request_time

    def get(self):
        """
        Returns 'data.txt' content when the resource has
        changed after the request time
        """
        request_time = time.time()
        while not self._is_updated(request_time):
            time.sleep(0.5)
        content = ''
        with open('main/routes/part_of_speech/data.txt') as data:
            content = data.read()
        return {'content': content,
                'date': datetime.now().strftime('%Y/%m/%d %H:%M:%S')}

    def post(self):
        time.sleep(10)
        a = request.get_data().decode('utf-8')
        print(json.loads(a))
        return 123

#
# class POSData(restful.Resource):
#
#     def get(self):
#         """
#         Returns the current data content
#         """
#         content = ''
#         with open('main/routes/part_of_speech/data.txt') as data:
#             content = data.read()
#         return {'content': content}
