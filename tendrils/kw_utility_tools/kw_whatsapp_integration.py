
import requests
import json



def send_whatsapp_message(destination_mobno,message):

    url         = "https://api.karix.io/message/"
            
    json_data   = {
                "channel": "whatsapp", 
                "source" : "+917064491000",
                "destination" : [destination_mobno],
                "content" : {"text":message},
                # "media": {
                #         "url": "https://portal.csmpl.com/Console/customizeV2/login_Csm.png",
                #         "caption": message
                #         }
    }
    
    header                  = {'Content-type': 'application/json','Authorization': 'Basic NTkyZjcwODYtYmIxYi00MTQ0LTg1YTktMjc0N2U5Yjk0M2U0OjU4OTE0ODE2LTJiNzEtNDVlZi05N2NmLTMyNzQwMTQwYjMzNQ=='} 
    data                    = json.dumps(json_data)
    
    #########################################################################################
    try:
        # print(data)
        response_result     = requests.post(url, data = data,headers=header,timeout=30)           
        resp                = json.loads(response_result.text)
        # print(resp)
        return {'status':200,'result':resp}

    except Exception as e:
        #print(e)
        return {'status':500,'error_log':str(e)}


