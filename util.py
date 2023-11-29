#Clase MD5Hash
import hashlib
#Clase CustomJsonEncoder
import json
from decimal import Decimal
import datetime
import os
from werkzeug.utils import secure_filename

class CustomJsonEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)

        if isinstance(obj, datetime.date):
            return obj.isoformat()

        return super(CustomJsonEncoder, self).default(obj)     