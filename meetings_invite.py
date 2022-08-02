import json
from urllib.request import urlopen
import pandas as pd
import re
from persiantools.jdatetime import JalaliDate
from persiantools import digits
from datetime import timedelta


class meetings:
    def __init__(self) -> None:
        self.target = digits.en_to_fa(str(JalaliDate.today() - timedelta(days = 30)).replace('-','/'))
        pass
    def invite(self):
        list_of_df = [];
        num = 1;
        
        while True:
            url = "https://search.codal.ir/api/search/v2/q?&Audited=true&AuditorRef=-1&Category=6&Childs=true&CompanyState=-1&CompanyType=-1&Consolidatable=true&IsNotAudited=false&Length=-1&LetterType=-1&Mains=true&NotAudited=true&NotConsolidatable=true&PageNumber={}&Publisher=false&TracingNo=-1&search=true".format(num);
            
            with urlopen(url) as response:
                body = response.read().decode('utf-8');
                
            data_json = json.loads(body);
            df = pd.DataFrame(data_json['Letters'])
            df = df[['Symbol', 'CompanyName','Title', 'LetterCode','PublishDateTime','Url']]
            list_of_codes=["ن-۵۰","ن-۵۳","ن-۵۴","ن-۵۶"];
            df_to_use = df[df['LetterCode'].isin(list_of_codes)]
            list_of_df.append(df_to_use)
            num += 1;
            
            if df_to_use.empty:
                pass
            else:
                if (str(df_to_use['PublishDateTime'].iloc[-1]).split())[0] < self.target:
                    break;
            
            

        invite_df = pd.concat(list_of_df,ignore_index=True)
        invite_df['date'] = '';
        invite_df['hour'] = '';
        broken_links =[];
        count = 0;
        for w in invite_df['Url']:
            site = 'https://www.codal.ir' + w
            try:
                with urlopen(site) as response_u:
                    body_u = response_u.read().decode('utf-8');
                Hour = re.search('(<span id="txbHour">(.*)</span>)',body_u).group(1).replace('<span id="txbHour">',"").replace('</span>','');
                Date = re.search('(<span id="txbDate">(.*)</span>)',body_u).group(1).replace('<span id="txbDate">',"").replace('</span>','');
                invite_df['date'].iloc[count] = Date
                invite_df['hour'].iloc[count] = Hour
            except:
                broken_links.append(site)
                invite_df['date'].iloc[count] = "Date not found"
                invite_df['hour'].iloc[count] = "Hour not found"
            
            count += 1 ;
        
        
        return  invite_df , broken_links


meet = meetings()
df = (meet.invite())[0]
print(df)