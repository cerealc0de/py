import datetime
import os
import xlsxwriter

###--------------------CONFIG--------------------###

TP_NUMBER = 3
TSL = False

###----------------------------------------------###
positions = TP_NUMBER
if TSL == True:
    positions += 1
    
clusters = {}
clusters['Indices'] = ['NAS100','SP500','Nikkei225']
clusters['CMD'] = ['COFFEE','COPPER','NG','USOUSD','SOYBEAN','WHEAT','XAGUSD','XAUUSD']
clusters['Majors'] = ['NAS100','Nikkei225','USOUSD','XAUUSD','EURUSD','GBPUSD']
clusters['Forex'] = ["USDJPY","EURJPY","GBPJPY","AUDJPY","CADJPY","CHFJPY","NZDJPY","EURUSD","AUDUSD","GBPUSD","NZDUSD","EURGBP","EURAUD","GBPAUD","AUDCAD","EURCAD","GBPCAD","NZDCAD","USDCAD","AUDCHF","CADCHF","EURCHF","GBPCHF","NZDCHF","USDCHF","AUDNZD","EURNZD","GBPNZD"]
clusters['Asia'] = ['Nikkei225','AUDJPY','AUDNZD','AUDUSD','NZDJPY','NZDUSD','USDJPY']
for cluster in clusters.values():
    cluster.sort()
    
zones = (('TKO',300,1200),('LDN_AM',1000,1500),('LDN_NYC',1500,1900),('NYC_PM',1900,2400),('TKO_KZ',0,500),('LDN_KZ',900,1200),('NYC_KZ',1400,1800))

fingerprints = {}

header_number = 12
hops = header_number+2
overview_col = (7,7+hops,7+(2*hops))
zone_col = (0,hops,2*hops,3*hops)

class Trade_Class:
    def __init__(self,symbol,direction,entry_date,raw_profit,commission,commission_percent,rr,poi_stamp,poi_type,number=0,wins=0,t2=0,t3=0,tsl=0):
        self.symbol = symbol
        self.direction = direction
        self.entry_date = entry_date
        entry_date_split = entry_date.split("/")[1].split(":")
        self.stamp = int(entry_date_split[0]+entry_date_split[1])
        self.commission = float(commission)
        self.net_profit = float(raw_profit)+self.commission
        self.commission_percent = float(commission_percent)
        self.commission_number = 1
        self.rr = float(rr)
        if poi_stamp == 'None':
            self.poi_stamp = poi_stamp
        else:
            self.poi_stamp = int(poi_stamp)
        self.poi_type = poi_type
        self.total_trades = number
        self.wins = wins
        self.t2 = t2
        self.t3 = t3
        self.tsl = tsl
    def __str__(self):
        return f'              {self.symbol}:{self.direction}:{self.entry_date} > {self.net_profit}({self.commission_percent}%) > {self.rr}'
class Zone_Class:
    def __init__(self,zone,start,end):
        self.zone = zone
        self.start = start
        self.end = end
        self.net_profit = 0
        self.commission_percent = 0
        self.commission_number = 0
        self.total_trades = 0
        self.wins = 0
        self.t2 = 0
        self.t3 = 0
        self.tsl = 0
        self.rr = 0
    def FeedTrade(self,trade):
        self.net_profit += trade.net_profit
        self.commission_percent += trade.commission_percent
        self.commission_number += 1
        self.total_trades += trade.total_trades
        self.wins += trade.wins
        self.t2 += trade.t2
        self.t3 += trade.t3
        self.tsl += trade.tsl
        self.rr += trade.rr
class Symbol_Class:
    def __init__(self,symbol):
        global zones
        self.symbol = symbol
        self.net_profit = 0
        self.commission_percent = 0
        self.commission_number = 0
        self.total_trades = 0
        self.wins = 0
        self.t2 = 0
        self.t3 = 0
        self.tsl = 0
        self.rr = 0
        self.zones = {}
        for zone in zones:
            self.zones[zone[0]] = (Zone_Class(zone[0],zone[1],zone[2]))
        self.poi_zones = {}
        for zone in zones:
            self.poi_zones[zone[0]] = (Zone_Class(zone[0],zone[1],zone[2]))
    def FeedTrade(self,trade):
        global zones
        self.net_profit += trade.net_profit
        self.commission_percent += trade.commission_percent
        self.commission_number += 1
        self.total_trades += trade.total_trades
        self.wins += trade.wins
        self.t2 += trade.t2
        self.t3 += trade.t3
        self.tsl += trade.tsl
        self.rr += trade.rr
        for zone in self.zones.values():
            if zone.start <= trade.stamp < zone.end:
                zone.FeedTrade(trade)
        for zone in self.poi_zones.values():
            if trade.poi_stamp != 'None':
                if zone.start <= trade.poi_stamp < zone.end:
                    zone.FeedTrade(trade)
class POI_Class:
    def __init__(self,poi_type):
        self.poi_type = poi_type
        self.net_profit = 0
        self.commission_percent = 0
        self.commission_number = 0
        self.total_trades = 0
        self.wins = 0
        self.t2 = 0
        self.t3 = 0
        self.tsl = 0
        self.rr = 0
    def FeedTrade(self,trade):
        self.net_profit += trade.net_profit
        self.commission_percent += trade.commission_percent
        self.commission_number += 1
        self.total_trades += trade.total_trades
        self.wins += trade.wins
        self.t2 += trade.t2
        self.t3 += trade.t3
        self.tsl += trade.tsl
        self.rr += trade.rr
    def __str__(self):
        return f'{self.poi_type} {self.net_profit} {self.total_trades}'
start_time = datetime.datetime.now().strftime("%Y.%m.%d_%H.%M.%S")

class Total_Class:
    def __init__(self):
        self.net_profit = 0
        self.fee_percent = 0
        self.fee_number = 0
        self.trades = 0
        self.wins = 0
        self.t2 = 0
        self.t3 = 0
        self.tsl = 0
        self.rr = 0
    def Increment(self,item):
        self.net_profit += item.net_profit
        self.fee_percent += item.commission_percent
        self.fee_number += item.commission_number
        self.trades += item.total_trades
        self.wins += item.wins
        self.t2 += item.t2
        self.t3 += item.t3
        self.tsl += item.tsl
        self.rr += item.rr
    def WriteCells(self,sheet,column=0,line=3):
        global positions
        sheet.write(line,0+column,'Total')
        sheet.write(line,1+column,self.net_profit)
        if self.fee_number > 0:
            commission_average = (self.fee_percent/self.fee_number)/100
        else:
            commission_average = 0
        sheet.write(line,2+column,commission_average)
        sheet.write(line,3+column,self.wins)
        sheet.write(line,4+column,GetPercent(self.wins,self.trades))
        sheet.write(line,5+column,self.t2)
        sheet.write(line,6+column,GetPercent(self.t2,self.wins))
        sheet.write(line,7+column,self.t3)
        sheet.write(line,8+column,GetPercent(self.t3,self.wins))
        sheet.write(line,9+column,self.tsl)
        sheet.write(line,10+column,GetPercent(self.tsl,self.wins))
        sheet.write(line,11+column,self.rr)
        sheet.write(line,12+column,self.rr+abs((self.fee_percent/positions)/100))

###---------Creating excel file---------###
print('>> Generating file')
log_directory = "./logs/"
all_trades = ()
all_logs = os.listdir(log_directory)
strat_name = all_logs[0].split("~")[0]
graph_file = strat_name+"~"+str(start_time) + '.xlsx'
book = xlsxwriter.Workbook('./graphs/' + graph_file)
zone_names = []
for zone in zones:
    zone_names.append(zone[0])
sheet_names = ['Overview'] + zone_names
sheets = {}
for sheet_name in sheet_names:
    sheets[sheet_name] = book.add_worksheet(sheet_name)
print('       '+str(graph_file))

###---------Getting all trades----------###
print('>> Processing trades')
overview = sheets['Overview']
pink = book.add_format({'bold': True, 'bg_color': '#fed6ff'})
overview_total = Total_Class()
symbols = {}
poi_types = {}
def Round2(val):
    return round(val,2)
def GetPercent(val,total):
    if total==0:
        return 0
    else:
        return Round2(val/total)
def ImportTrades(log,line_number):
    global log_directory
    global overview
    global overview_total
    global symbols
    global poi_types
    global fingerprints
    global positions
    global TSL
    log_file = log_directory + log
    trades = ()
    with open(log_file,'r') as f:
        for line in f:
            line = line.split()
            if len(line) > 3:
                number = 0
                wins = 0
                t2 = 0
                t3 = 0
                tsl = 0
                l1 = line[0].split(':')
                l2 = line[2].split('}')[0].split('{')[1]
                l3 = line[7][:-3]
                l4 = line[8].split('U')
                l5 = l4[1].split('(')[1].split('%')[0]
                rr = float(line[9].split('=')[1])
                l7 = line[14].split(";")
                l8 = l7[0]
                l9 = l7[1]
                fingerprint = l1[0]+'.'+l1[1]+'.'+l2.split('/')[0]+'.'+line[3].split(':')[0]
                if fingerprint not in fingerprints:
                    fingerprints[fingerprint] = [True,1]
                    number = 1
                    if rr >= -0.02:
                        wins = 1
                        if TSL==True and positions==1:
                            tsl = 1
                else:
                    fp = fingerprints[fingerprint]
                    if fp[0]==True:
                        if rr >= 0.02:
                            if fp[1]+1==positions and TSL==True:
                                tsl = 1
                            elif fp[1]==1:
                                t2 = 1
                                fp[1]=2
                            elif fp[1]==2:
                                t3 = 1
                                fp[1]=3
                        else:
                            fp[0] = False
                trades += (Trade_Class(l1[0],l1[1],l2,l3,l4[0],l5,rr,l8,l9,number,wins,t2,t3,tsl),)
    for trade in trades:
        print(str(trade))
        overview.write('A'+str(line_number),trade.symbol)
        overview.write('B'+str(line_number),trade.direction)
        overview.write('C'+str(line_number),trade.entry_date)
        overview.write('D'+str(line_number),trade.net_profit)
        overview.write('E'+str(line_number),trade.commission_percent/100)
        overview.write('F'+str(line_number),trade.rr)
        line_number += 1
        overview_total.Increment(trade)
        if trade.symbol not in symbols:
            symbols[trade.symbol] = Symbol_Class(trade.symbol)
            keys = list(symbols.keys())
            keys.sort()
            symbols = {i: symbols[i] for i in keys}
        symbols[trade.symbol].FeedTrade(trade)
        if trade.poi_type not in poi_types:
            poi_types[trade.poi_type] = POI_Class(trade.poi_type)
            keys = list(poi_types.keys())
            keys.sort()
            poi_types = {i: poi_types[i] for i in keys}
        poi_types[trade.poi_type].FeedTrade(trade)
    return trades
for x in range(len(all_logs)):
    log = all_logs[x]
    print('       '+str(log))
    cell_number = str(x+3+len(all_trades))
    overview.write('A'+cell_number,log,pink)
    overview.merge_range('A'+cell_number+":F"+cell_number,None)
    all_trades += ImportTrades(log,int(cell_number)+1)
    
###---------Swagging up sheets----------###
print('>> Swagging sheets')
purple = book.add_format({'bold': True, 'bg_color': '#c5c2ff', 'align': 'center'})
orange = book.add_format({'bold': True, 'bg_color': '#ffd7a8', 'align': 'center'})
black = book.add_format({'bold': True, 'bg_color': '#000000'})
blue = book.add_format({'bold': True, 'bg_color': '#d4fffb', 'align': 'center'})
white_font = book.add_format({'bold': True, 'bg_color': '#000000', 'font_color': '#ffffff', 'align': 'center'})
percent_format = book.add_format({'num_format': '0.00%'})
def StratNameHeader(sheet,column,merge=True):
    global strat_name
    global white_font
    global header_number
    sheet.write(0,column,strat_name,white_font)
    if merge==True:
        Merge(sheet,0,column,column+header_number)
def TitleColumn(sheet,line,column,title,color):
    sheet.write(line,column,title,color)
    sheet.set_column(column,column,12)
def PercentColumn(sheet,column):
    global percent_format
    sheet.set_column(column,column,8,percent_format)
def SeparatorColumn(sheet,column):
    global black
    sheet.set_column(column,column,3,black)
def Merge(sheet,line,column_one,column_two):
    sheet.merge_range(line,column_one,line,column_two,None)
def WinCells(sheet,line,column):
    sheet.set_column(column,column,3)
    PercentColumn(sheet,column+1)
    Merge(sheet,line,column,column+1)
def RRColumn(sheet,line,column,ext=''):
    global purple
    sheet.write(line,column,'RR'+ext,purple)
    sheet.set_column(column,column,6)
def AllColumnHeaders(sheet,line,column):
    global purple
    global orange
    StratNameHeader(sheet,column)
    TitleColumn(sheet,line,0+column,'Symbol',orange)
    TitleColumn(sheet,line,1+column,'Net Profit',purple)
    TitleColumn(sheet,line,2+column,'Fee',orange)
    PercentColumn(sheet,2+column)
    TitleColumn(sheet,line,3+column,'Wins',purple)
    WinCells(sheet,line,3+column)
    TitleColumn(sheet,line,5+column,'T2',orange)
    WinCells(sheet,line,5+column)
    TitleColumn(sheet,line,7+column,'T3',purple)
    WinCells(sheet,line,7+column)
    TitleColumn(sheet,line,9+column,'TSL',orange)
    WinCells(sheet,line,9+column)
    RRColumn(sheet,line,11+column)
    RRColumn(sheet,line,12+column,'a')
    SeparatorColumn(sheet,13+column)
StratNameHeader(overview,0,False)
Merge(overview,0,0,5)
TitleColumn(overview,1,0,'Symbol',orange)
overview.write(1,1,'Direction',purple)
overview.set_column(1,1,9)
overview.write(1,2,'Entry Date',orange)
overview.set_column(2,2,18)
TitleColumn(overview,1,3,'Net Profit',purple)
TitleColumn(overview,1,4,'Fee',orange)
PercentColumn(overview,4)
RRColumn(overview,1,5)
SeparatorColumn(overview,6)
for column in overview_col:
    AllColumnHeaders(overview,1,column)
TitleColumn(overview,1,overview_col[1],'POI Type',orange)
for zone in zone_names:
    sheet = sheets[zone]
    sheet.write(1,zone_col[0],'ENTRY STAMP',blue)
    sheet.write(1,zone_col[2],'POI STAMP',blue)
    Merge(sheet,1,zone_col[0],zone_col[2]-2)
    Merge(sheet,1,zone_col[2],zone_col[3]+header_number)
    for column in zone_col:
        AllColumnHeaders(sheet,2,column)

###----------Filling overview-----------###
print('>> Filling overview')
def PrintItemLine(sheet,item,column,line,first_column):
    global positions
    sheet.write(line,0+column,first_column)
    sheet.write(line,1+column,item.net_profit)
    sheet.write(line,2+column,(item.commission_percent/item.commission_number)/100)
    sheet.write(line,3+column,item.wins)
    sheet.write(line,4+column,GetPercent(item.wins,item.total_trades))
    sheet.write(line,5+column,item.t2)
    sheet.write(line,6+column,GetPercent(item.t2,item.wins))
    sheet.write(line,7+column,item.t3)
    sheet.write(line,8+column,GetPercent(item.t3,item.wins))
    sheet.write(line,9+column,item.tsl)
    sheet.write(line,10+column,GetPercent(item.tsl,item.wins))
    sheet.write(line,11+column,item.rr)
    sheet.write(line,12+column,item.rr+abs((item.commission_percent/positions)/100))
for col_x in range(2):
    overview_total.WriteCells(overview,overview_col[col_x],2)
x = 3
for symbol in symbols.values():
    PrintItemLine(overview,symbol,overview_col[0],x,symbol.symbol)
    x += 1
x = 3
for poi_type in poi_types.values():
    PrintItemLine(overview,poi_type,overview_col[1],x,poi_type.poi_type)
    x += 1
x = 2
for key in clusters.keys():
    cluster = clusters[key]
    overview.write(x,overview_col[2],key+' ('+str(len(cluster))+')',pink)
    Merge(overview,x,overview_col[2],overview_col[2]+header_number)
    total_x = x + 1
    x += 2
    cluster_total = Total_Class()
    for symbol in symbols.values():
        symbol_upper = symbol.symbol.upper()
        for s in cluster:
            if s.upper() in symbol_upper:
                PrintItemLine(overview,symbol,overview_col[2],x,symbol.symbol)
                cluster_total.Increment(symbol)
                x += 1
    cluster_total.WriteCells(overview,overview_col[2],total_x)

###------------Filling zones------------###
print('>> Filling zones')
def WriteCluster(z_line,poi_line,key):
    global clusters
    global pink
    global zone_col
    global header_number
    cluster = clusters[key]
    sheet.write(z_line,zone_col[1],key+' ('+str(len(cluster))+')',pink)
    sheet.write(poi_line,zone_col[3],key+' ('+str(len(cluster))+')',pink)
    Merge(sheet,z_line,zone_col[1],zone_col[1]+header_number)
    Merge(sheet,poi_line,zone_col[3],zone_col[3]+header_number)
for zone in zone_names:
    s_total = Total_Class()
    poi_total = Total_Class()
    sheet = sheets[zone]
    s_x = 4
    poi_x = 4
    for symbol in symbols.values():
        s_zone = symbol.zones[zone]
        if s_zone.total_trades > 0:
            PrintItemLine(sheet,s_zone,zone_col[0],s_x,symbol.symbol)
            s_total.Increment(s_zone)
            s_x += 1
        poi_zone = symbol.poi_zones[zone]
        if poi_zone.total_trades > 0:
            PrintItemLine(sheet,poi_zone,zone_col[2],poi_x,symbol.symbol)
            poi_total.Increment(poi_zone)
            poi_x += 1
    s_total.WriteCells(sheet)
    poi_total.WriteCells(sheet,zone_col[2])
    z_line = 3
    poi_line = 3
    for key in clusters.keys():
        cluster = clusters[key]
        WriteCluster(z_line,poi_line,key)
        z_line_total = z_line + 1
        poi_line_total = poi_line + 1
        z_line += 2
        poi_line += 2
        z_total = Total_Class()
        poi_total = Total_Class()
        for symbol in symbols.values():
            symbol_upper = symbol.symbol.upper()
            for s in cluster:
                if s.upper() in symbol_upper:
                    s_zone = symbol.zones[zone]
                    if s_zone.total_trades > 0:
                        PrintItemLine(sheet,s_zone,zone_col[1],z_line,symbol.symbol)
                        z_total.Increment(s_zone)
                        z_line += 1
                    poi_zone = symbol.poi_zones[zone]
                    if poi_zone.total_trades > 0:
                        PrintItemLine(sheet,poi_zone,zone_col[3],poi_line,symbol.symbol)
                        poi_total.Increment(poi_zone)
                        poi_line += 1
        z_total.WriteCells(sheet,zone_col[1],z_line_total)
        poi_total.WriteCells(sheet,zone_col[3],poi_line_total)

"""
#Crafting results chart (sheet 1)
print('[*] Crafting charts')
chart = book.add_chart({'type': 'bar','subtype': 'percent_stacked'})
chart.set_title({'name': str(TradesTotal) + ' trades, ' + str(PNLTotal) + ' PNL'})
chart.add_series({
    'name': '=' + str(s1name) + '!$H$1',
    'categories': '=' + str(s1name) + '!$G$2:$G$4',
    'values': '=' + str(s1name) + '!$H$2:$H$4',
    'data_labels': {'value':True},
})
chart.add_series({
    'name': '=' + str(s1name) + '!$I$1',
    'categories': '=' + str(s1name) + '!$G$2:$G$4',
    'values': '=' + str(s1name) + '!$I$2:$I$4',
    'data_labels': {'value':True},
})
chart.add_series({
    'name': '=' + str(s1name) + '!$J$1',
    'categories': '=' + str(s1name) + '!$G$2:$G$3',
    'values': '=' + str(s1name) + '!$J$2:$J$3',
    'data_labels': {'value':True},
})
chart.add_series({
    'name': '=' + str(s1name) + '!$K$1',
    'categories': '=' + str(s1name) + '!$G$2:$G$3',
    'values': '=' + str(s1name) + '!$K$2:$K$3',
    'data_labels': {'value':True},
})
currentsheet.insert_chart('G6',chart,{'x_scale': 2.5, 'y_scale': 2})
"""

book.close()
input('Nuke enter')
