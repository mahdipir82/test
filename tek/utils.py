def create_random_code(count):
    import random
    count-=1
    return random.randint(10**count,10**(count+1)-1)
#====================================================
def send_sms(mobile_number,message):
    pass
    # try:
    #     api=kavenegarAPI('')
    #     params={'sender':'','recepter':mobile_number,'message':message}
    #     respone=api.sms_send(params)
    #     return respone
    # except APIExcption as error:
    #     print(f'error:{error}')
    # except HTTPExcption as error:
    #     print(f'error2:{error}')
    
#====================================================
import os
from uuid import uuid4
from datetime import datetime
# ========================================
# مدیریت آپلود فایل‌ها
# ========================================
class FileUpload:
    def __init__(self, base_dir, prefix):
        self.base_dir = base_dir
        self.prefix = prefix

    def upload_to(self, instance, filename):
        _, ext = os.path.splitext(filename)
        model_name = instance.__class__.__name__.lower()
        today = datetime.now().strftime("%Y/%m/%d")
        unique_name = f"{uuid4().hex}{ext}"

        return os.path.join(
            self.base_dir,
            self.prefix,
            model_name,
            today,
            unique_name
        )


#================================================================
from django import template
register = template.Library()

@register.filter
def persian_intcomma(value):
        str_value = str(value)[::-1]
        new_value = ''
        for i in range(len(str_value)):
            new_value += str_value[i]
            if (i+1) % 3 == 0 and i != len(str_value) - 1:
                new_value += ','
        return new_value[::-1]
    
#     {% load base_tags %}
# {{ myNumber|persian_intcomma }}


#=============================================
def price_by_delivery_tax(price,discount=0):
    delivery=50000
    if price>500000:
        delivery=0
    sum=price+delivery
    sum=sum-(sum*discount/100)
    return int(sum),delivery
