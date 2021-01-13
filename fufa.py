#####FOFA爬虫######
###FOFA对于非会员，只允许查看第一页的搜索结果，可以通过添加限制条件并去重，找到同一搜索的不同结果###
##利用FOFA的搜索机制，将一个搜索的结果尽可能多的搜集##
#对于没有使用时间条件的，使用时间条件before和after；国家/地区、server为次选条件；端口、类型、ASN、组织、IPV4/6次之；网站标题不可用；
#FOFA中可搜索字段：title\header\body\domain\icon_hash\host\port\ip\status_code\protocol\city\region\country\cert\banner\type\os\server\app\after\before\asn\org\base_protocol\is_ipv6\is_domain\ip_ports\port_size\port_size_gt\port_size_lt\ip_country\ip_region\ip_city\ip_after
import requests,time,random,os,re,sys,base64,urllib.parse,datetime
from pyquery import PyQuery as pq

banner = '''
  ______ _    _  _____ _  __     ______ ____  ______      
 |  ____| |  | |/ ____| |/ /    |  ____/ __ \|  ____/\    
 | |__  | |  | | |    | ' /_____| |__ | |  | | |__ /  \   
 |  __| | |  | | |    |  <______|  __|| |  | |  __/ /\ \  
 | |    | |__| | |____| . \     | |   | |__| | | / ____ \ 
 |_|     \____/ \_____|_|\_\    |_|    \____/|_|/_/    \_\
                                      by Hoping           
'''
def usera():#随机选择一个UA头赋给header
    #user_agent 集合
    user_agent_list = [#UA头列表，可补充
     'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
     'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
     'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
     'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
     'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
     'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
     'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
     'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
     'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
     'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
     'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    ]
    #随机选择一个
    user_agent = random.choice(user_agent_list)
    #传递给header
    headers = { 'User-Agent': user_agent }
    return headers

def getPage(search):#获得总结过的页数

    url='https://classic.fofa.so/result?page=1&qbase64={}'.format(search)
    #cookies = {'_fofapro_ars_session':cookie}#有会员的话要自己抓个cookie
    req = requests.get(url=url,headers=usera())#,cookies=cookies)
    #print(req.text)
    pageHtml = pq(req.text)#创建一个pq爬虫类，对象是req.text
    page = (pageHtml('div.list_jg')).text()#div下的list_jg，层级用空格分开，同级用逗号，属性用.，内容为后加text
    # page = page.find('')
    
    pattern = re.compile(u'获得 (.*?) 条匹配结果')
    result  = re.findall(pattern,page)
    result  = result[0].replace(',','')

    if (int(result) % 10) >0:
        allPage = int(result) // 10 + 1
    else:
        allPage = int(result) // 10

    return allPage


def start(search,file):
    search_list = []
    country_list = ["CH","CN","US","DE","IE","FR","GB","JP"]#国家简称列表，可补充
    #region_list = ["Fribourg",]#地区列表，太多了，不弄了
    type_list = ["service","subdomain"]#type="service"
    server_list = ["Microsoft","Jetty","Apache","nginx"]#网络服务列表，可补充
    os_list = ["ubuntu","unix","debian","amazon","centos"]#os列表，可补充
    start_date =datetime.date(2020,1,1)#搜索的时间起始日期，可修改
    end_date =datetime.date(2020,1,2)#搜索的时间截止日期，可修改
    date_count=end_date-start_date+1
    #print(date_count)
    step_date = datetime.timedelta(days=1)#日期步进值，单位天
    sleep_time = 3#每次查询的休眠时间
    alltime = (len(country_list)+len(type_list)+len(server_list)+len(os_list))*date_count*sleep_time/step_date
    print("[+] 当前日期步进值为%s，每次查询休眠%s秒，预计最快需要%s秒"%(step_date,sleep_time,alltime))
    #is_ipv6=false或者is_ipv6=true
    #ASN_list=[6830,]#asn
    d = start_date
    #第一个循环，写出所有查询语句
    while d <=end_date:#利用FOFA会把日期最近的ip显示的这一机制
        for i in country_list:
            query = search+"&&country=%s&&before=%s"%(i,d.strftime("%Y-%m-%d"))
            query = query.encode(encoding="utf-8")
            query=base64.b64encode(query).decode()
            query=urllib.parse.quote(query)
            search_list.append(query)
        for i in type_list:
            query = search+"&&type=%s&&before=%s"%(i,d.strftime("%Y-%m-%d"))
            query = query.encode(encoding="utf-8")
            query=base64.b64encode(query).decode()
            query=urllib.parse.quote(query)
            search_list.append(query)
        for i in server_list:
            query = search+"&&server=%s&&before=%s"%(i,d.strftime("%Y-%m-%d"))
            query = query.encode(encoding="utf-8")
            query=base64.b64encode(query).decode()
            query=urllib.parse.quote(query)
            search_list.append(query)
        for i in os_list:
            query = search+"&&os=%s&&before=%s"%(i,d.strftime("%Y-%m-%d"))
            query = query.encode(encoding="utf-8")
            query=base64.b64encode(query).decode()
            query=urllib.parse.quote(query)
            search_list.append(query)
        d +=step_date
    # if os.path.exists("result.txt"): #删除存在的文件
        # os.remove("result.txt")
    # cookie = input("请输入Fofa的Cookie的_fofapro_ars_session值:")
    #print(search)
    search = search.encode(encoding="utf-8")
    search=base64.b64encode(search).decode()
    search=urllib.parse.quote(search)
    allPage = getPage(search)
    print(banner)
    print("[+ 搜索结果共有{}页".format(allPage))
    print(search_list)
    #startPage = input("[+ 搜索结果共有{}页，请输入".format(allPage))
    #page      = input("[+ 搜索结果共有{}页，请输入准备收集页数(例:20):".format(allPage))
    #endPage   = int(startPage) + int(page)

    #cookies={'_fofapro_ars_session':cookie}#这里是你的fofa账号登录后的cookie值
    # doc=pq(url)
    print("[+ 正在向{}.txt文件写入结果".format(file))
    with open('%s.txt'%file,'a+',encoding='utf-8') as f:
        for i in search_list:
            url='https://classic.fofa.so/result?page=1&qbase64={}'.format(i)
            #print(url)
            req = requests.get(url=url,headers=usera())#,cookies=cookies)
            '''
            if '游客使用高级语法' in req.text:
                print('[- Cookie已失效，请重新填写https://classic.fofa.so的Cookie,不是https://fofa.so的Cookie')
                break
            '''
            doc=pq(req.text)

            url=doc('div.results_content .list_mod_t').items()
            title=doc('div.list_mod_c ul').items()

            for u,t in zip(url,title):
                t.find('i').remove()
                relUrl   = u.find('a').eq(0).attr.href#网站ip/URL地址
                relTitle = t.find('li').eq(0).text()#网站title

                if 'result?qbase64=' in relUrl:#特殊情况，还没见过
                    relDoc  = pq(u)
                    relIp   = relDoc('.ip-no-url').text()
                    relPort = (relDoc('.span')).find('a').eq(0).text()
                    relUrl  = 'http://{}:{}'.format(str(relIp),relPort)
                if relTitle == '':
                    relTitle = '空'
                #print("Url: %s  Title: %s"%(relUrl, relTitle))
                f.write("%s\n"%(relUrl))
                f.flush()

            time.sleep(sleep_time)

def unrepeated(file):
    list01 = []
    for i in open('%s.txt'%file):
        if i in list01:
            continue
        list01.append(i)
    with open('unrepeated.txt', 'w') as handle:
        handle.writelines(list01)


if __name__ == '__main__':
    start_t = datetime.datetime.now()
    if len(sys.argv)==1:
        print(banner)
        print('''Usage:请输入参数\n例如:python FofaCrawler.py 'app="Solr"'(Fofa搜索语法) Solr(搜索结果文件名)  ''')
        sys.exit(0)
        
    search=sys.argv[1]
    file=sys.argv[2]
    start(search,file)
    unrepeated(file)
    end_t = datetime.datetime.now()
    print("实际耗时：",(end_t-start_t).seconds)
