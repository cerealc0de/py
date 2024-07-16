#------------------ DISCLAIMER ------------------#
"""""""""""""""""""""""""""""""""""""""""""""""""""
The user is entirely responsible for any issue that
may arise - directly or indirectly - from the use
of this script. Use at your own risk.
This script only works when trading in USD.
"""""""""""""""""""""""""""""""""""""""""""""""""""
#----------------- DEPENDENCIES -----------------#
"""""""""""""""""""""""""""""""""""""""""""""""""""
modules required: metatrader5
"""""""""""""""""""""""""""""""""""""""""""""""""""
#-------------------- CONFIG --------------------#

#Trading account ID
ID = 69
#Trading account password
PASSWORD = 'password'

#Broker server
SERVER = 'VantageInternational-Demo'
#Broker symbol extension
EXT = '+'
#Broker commission fee (USD/LOT)
COMMISSION = 6

# "name": (extension,pip_value,spread_in_pips,fee,capital_multiplier,min_lot)
SYMBOLS = {
    "NAS100": (False,0.1,15,False,100000,0.1),
    "SP500": (False,0.1,0,True,1,0.01),
    "AUDCAD": (True,0.00001,0,True,1,0.01),
    "AUDCHF": (True,0.00001,0,True,1,0.01),
    "AUDJPY": (True,0.001,0,True,1,0.01),
    "AUDNZD": (True,0.00001,0,True,1,0.01),
    "AUDUSD": (True,0.00001,0,True,1,0.01),
    "CADCHF": (True,0.00001,0,True,1,0.01),
    "CADJPY": (True,0.001,0,True,1,0.01),
    "CHFJPY": (True,0.001,0,True,1,0.01),
    "EURAUD": (True,0.00001,0,True,1,0.01),
    "EURCAD": (True,0.00001,0,True,1,0.01),
    "EURCHF": (True,0.00001,0,True,1,0.01),
    "EURGBP": (True,0.00001,0,True,1,0.01),
    "EURJPY": (True,0.001,0,True,1,0.01),
    "EURNZD": (True,0.00001,0,True,1,0.01),
    "EURUSD": (True,0.00001,1,True,1,0.01),
    "GBPAUD": (True,0.00001,0,True,1,0.01),
    "GBPCAD": (True,0.00001,0,True,1,0.01),
    "GBPCHF": (True,0.00001,0,True,1,0.01),
    "GBPJPY": (True,0.001,0,True,1,0.01),
    "GBPNZD": (True,0.00001,0,True,1,0.01),
    "GBPUSD": (True,0.00001,0,True,1,0.01),
    "NZDCAD": (True,0.00001,0,True,1,0.01),
    "NZDCHF": (True,0.00001,0,True,1,0.01),
    "NZDJPY": (True,0.001,0,True,1,0.01),
    "NZDUSD": (True,0.00001,0,True,1,0.01),
    "USDCAD": (True,0.00001,0,True,1,0.01),
    "USDCHF": (True,0.00001,0,True,1,0.01),
    "USDJPY": (True,0.001,0,True,1,0.01),
    "USOUSD": (False,0.001,0.3,True,100,0.01),
    "XAUUSD": (True,0.01,0,True,1000,0.01)
}
#------------------------------------------------#
import os
import math
import MetaTrader5 as mt5

logged_in = False
os.system("mode con cols=46 lines=27")

class Symbol_Class:
    def __init__(self,symbol_name):
        global SYMBOLS
        global EXT
        global COMMISSION
        deets = SYMBOLS[symbol_name]
        self.symbol = symbol_name
        if (deets[0]==True):
            self.symbol += EXT
        self.pip = deets[1]
        self.spread = self.pip*deets[2]
        if (deets[3]==True):
            self.commission = COMMISSION
        else:
            self.commission = 0
        self.capital_multiplier = deets[4]
        self.min_lot = deets[5]
    def GetCurrentBid(self):
        mt5.symbol_select(self.symbol,True)
        bid = (mt5.symbol_info_tick(self.symbol)).bid
        return bid
    def GetCurrentAsk(self):
        mt5.symbol_select(self.symbol,True)
        ask = (mt5.symbol_info_tick(self.symbol)).ask
        return ask
    def __str__(self):
        return f'{self.symbol:>38}'
USED_SYMBOLS = []
keys = SYMBOLS.keys()
for key in keys:
    USED_SYMBOLS.append(Symbol_Class(key))
    
class Message_Class:
    suffix = " ('h' for help)"
    def __init__(self):
        self.message = '[*] Awaiting input'
        self.error = ''
    def DefaultMessage(self):
        self.message = '[*] Awaiting input'
        self.error = ''
    def CustomMessage(self,message,error=''):
        self.message = '/!\\ '+message
        self.error = error
    def TradeSuccess(self):
        self.message = '[+] Trade successfully placed'
    def InvalidValue(self):
        self.CustomMessage('Invalid value')
    def __str__(self):
        return f'{self.message}{self.suffix}{self.error}'
input_message = Message_Class()

class TradeSettings_Class:
    def __init__(self):
        self.used_balance = 0
        self.risk = 1.0
        self.engaged_capital = 0
        self.symbol = ''
        self.order_type = 'market'
        self.limit = 0
        self.trade_type = 'buy'
        self.sl = 0
        self.tp_type = 'none'
        self.tp = 0
    def UpdateEngagedBalance(self):
        self.engaged_capital = self.used_balance*self.risk/100
    def GetBalance(self,user_input):
        global input_message
        balance = float(mt5.account_info().balance)
        if balance is not None:
            if Is_Number(user_input):
                user_input = float(user_input)
                if user_input < balance:
                    self.used_balance = user_input
                else:
                    self.used_balance = balance
                self.UpdateEngagedBalance()
            elif user_input=='all':
                self.used_balance = balance
                self.UpdateEngagedBalance()
            else:
                input_message.InvalidValue()
        else:
            input_message.CustomMessage('Balance retrieval failed')
    def GetRisk(self,user_input):
        global input_message
        if Is_Number(user_input):
            user_input = round(float(user_input),2)
            if (0.01 <= user_input <= 100):
                self.risk = user_input
                self.UpdateEngagedBalance()
            else:
                input_message.InvalidValue()
        else:
            input_message.InvalidValue()
    def GetSymbol(self,symbol_name):
        global USED_SYMBOLS
        global input_message
        symbol_name = symbol_name.upper()
        symbol_found = False
        for symbol in USED_SYMBOLS:
            if symbol_name == symbol.symbol[:6]:
                self.symbol = symbol
                symbol_found = True
                break
        if symbol_found==False:
            input_message.CustomMessage('Symbol not found')
    def GetOrderType(self,user_input):
        global input_message
        if user_input=='market' or user_input=='limit':
            self.order_type = user_input
        else:
            input_message.InvalidValue()
    def GetLimit(self,user_input):
        global input_message
        if Is_Number(user_input):
            self.limit = float(user_input)
        else:
            input_message.InvalidValue()
    def GetTradeType(self,user_input):
        global input_message
        if user_input=='buy' or user_input=='sell':
            self.trade_type = user_input
        else:
            input_message.InvalidValue()
    def GetExit(self,sl=None,tp=None):
        global input_message
        if Is_Number(sl):
            self.sl = float(sl)
        elif Is_Number(tp):
            self.tp = float(tp)
        else:
            input_message.InvalidValue()
    def GetTPType(self,user_input):
        global input_message
        if user_input=='none' or user_input=='price' or user_input=='rr':
            self.tp_type = user_input
        else:
            input_message.InvalidValue()
    def SendTrade(self):
        global input_message
        global EXT
        if self.used_balance > 0:
            if self.symbol != '':
                request = {
                    "symbol": self.symbol.symbol,
                    "sl": float(self.sl),
                    "deviation": 0,
                    "type_time": mt5.ORDER_TIME_GTC,
                    "type_filling": mt5.ORDER_FILLING_IOC
                }
                if self.order_type == 'market' or self.limit > 0:
                    if self.sl > 0:
                        try:
                            if self.order_type == 'market':
                                request["action"] = mt5.TRADE_ACTION_DEAL
                                if self.trade_type == 'buy':
                                    request["type"] = mt5.ORDER_TYPE_BUY
                                    entry_price = self.symbol.GetCurrentAsk()
                                else:
                                    request["type"] = mt5.ORDER_TYPE_SELL
                                    entry_price = self.symbol.GetCurrentBid()
                            else:
                                request["action"] = mt5.TRADE_ACTION_PENDING
                                request["price"] = self.limit
                                entry_price = self.limit
                                if self.trade_type == 'buy':
                                    request["type"] = mt5.ORDER_TYPE_BUY_LIMIT
                                else:
                                    request["type"] = mt5.ORDER_TYPE_SELL_LIMIT
                            sl_gap = abs(entry_price - self.sl)
                            divider = sl_gap*100000
                            lot = self.engaged_capital*self.symbol.capital_multiplier/divider
                            symbol_prefix = self.symbol.symbol[0:3]
                            symbol_suffix = self.symbol.symbol[3:6]
                            if symbol_suffix != "USD":
                                if symbol_prefix == "USD":
                                    lot = lot*GetCurrentAsk(self.symbol.symbol)
                                elif symbol_suffix == "CAD":
                                    lot = lot*GetCurrentAsk(("USDCAD"+EXT))
                                elif symbol_suffix == "CHF":
                                    lot = lot*GetCurrentAsk(("USDCHF"+EXT))
                                elif symbol_suffix == "JPY":
                                    lot = lot*GetCurrentAsk(("USDJPY"+EXT))
                                elif symbol_suffix == "AUD":
                                    lot = lot/GetCurrentBid(("AUDUSD"+EXT))
                                elif symbol_suffix == "GBP":
                                    lot = lot/GetCurrentBid(("GBPUSD"+EXT))
                                elif symbol_suffix == "NZD":
                                    lot = lot/GetCurrentBid(("NZDUSD"+EXT))
                        except Exception as e:
                            input_message.CustomMessage('Request crafting failed','\n'+str(e))
                        else:
                            lot = lot-((lot*self.symbol.commission)/divider)
                            lot = lot // self.symbol.min_lot * self.symbol.min_lot
                            if lot > 100:
                                lot = 100
                            if lot > 0:
                                request["volume"] = lot
                                if self.tp_type=='price':
                                    request["tp"] = float(self.tp)
                                elif self.tp_type=='rr':
                                    rr_gap = sl_gap*self.tp
                                    if self.trade_type == 'buy':
                                        request["tp"] = float(entry_price+rr_gap)
                                    else:
                                        request["tp"] = float(entry_price-rr_gap)
                                else:
                                    request["tp"] = float(0)
                                response = mt5.order_send(request)
                                if response==None:
                                    input_message.CustomMessage('No response from API')
                                elif response.retcode == mt5.TRADE_RETCODE_DONE or (self.order_type == 'limit' and response.retcode == mt5.TRADE_RETCODE_PLACED):
                                    input_message.TradeSuccess()
                                else:
                                    input_message.CustomMessage('Request failed','\n'+str(response.retcode)+' - '+str(response.comment))
                            else:
                                input_message.CustomMessage("Can't afford min lot",'\n*SL too far or risk too low')
                    else:
                        input_message.CustomMessage('SL required')
                else:
                    input_message.CustomMessage('Limit required')
            else:
                input_message.CustomMessage('Symbol required')
        else:
            input_message.CustomMessage('Balance required')
    def __str__(self):
        return_string = '••••••••••••••••••••••••••••••••••••••••••••••'
        return_string += f'\nBalance used:{self.used_balance:>32}'
        return_string += f'\nRisk:{self.risk:>39}%'
        return_string += f'\nBalance risked:{self.engaged_capital:>30}'
        return_string += '\n••••••••••••••••••••••••••••••••••••••••••••••'
        return_string += f'\nSymbol:{self.symbol}'
        return_string += f'\nOrder type:{self.order_type:>34}'
        if (self.order_type=='limit'):
            return_string += f'\nLimit:{self.limit:>39}'
        return_string += f'\nTrade type:{self.trade_type:>34}'
        return_string += f'\nSL:{self.sl:>42}'
        return_string += f'\nTP type:{self.tp_type:>37}'
        if (self.tp_type!='none'):
            return_string += f'\nTP:{self.tp:>42}'
        return return_string
trade_settings = None
        
def ClearConsole():
    os.system('cls' if os.name=='nt' else 'clear')
def Login():
    global input_message
    global SERVER
    global ID
    global PASSWORD
    global trade_settings
    try:
        mt5.initialize(login=ID,password=PASSWORD,server=SERVER)
    except:
        input_message.CustomMessage('Login failed')
        return False
    else:
        trade_settings = TradeSettings_Class()
        trade_settings.GetBalance('all')
        return True
def Is_Number(s):
    if s is None:
        return False
    else:
        try:
            float(s)
        except ValueError:
            return False
        else:
            return True
def ShowSettings(logged_in,account_string):
    global trade_settings
    global input_message
    ClearConsole()
    print('▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄')
    print('      ▄▄▄▄▄ ▄▄▄· ▄ •▄ ▄▄▄▄▄▄▄▄   ▄▄▄· ')
    print('      •██  ▐█ ▀█ █▌▄▌▪•██  ▀▄ █·▐█ ▀█ ')
    print('       ▐█.▪▄█▀▀█ ▐▀▀▄· ▐█.▪▐▀▀▄ ▄█▀▀█ ')
    print('       ▐█▌·▐█ ▪▐▌▐█.█▌ ▐█▌·▐█•█▌▐█ ▪▐▌')
    print('       ▀▀▀  ▀  ▀ ·▀  ▀ ▀▀▀ .▀  ▀ ▀  ▀ ')
    print('---------------Taker of Trades----------------')
    print('▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀')
    if (logged_in):
        print(account_string)
        print(trade_settings)
    else:
        print('Offline')
    print('▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄')
    print(input_message)
def ShowHelp():
    ClearConsole()
    print('Available commands')
    print('  login....................Log onto MT5')
    print('    use {value}/[all]........Set used balance')
    print('    risk [0.01-100]...........Set risk (%)')
    print('    sym {symbol}.............Set symbol')
    print('    order [market/limit].....Set order type')
    print('    limit {value}............Set limit')
    print('    trade [buy/sell].........Set trade type')
    print('    sl {value}...............Set SL')
    print('    tpt [none/price/rr]......Set TP type')
    print('    tp {value}...............Set TP')
    print('      send.....................Send request')
    print()
    uinput = input("Demolish enter to return")
    
while (1==1):
    ShowSettings(logged_in,f'Broker:{SERVER:>38}\nID:{ID:>42}')
    input_message.DefaultMessage()
    user_input = input("taktra> ")
    user_input_split = user_input.split()
    if user_input=='h':
        ShowHelp()
    elif user_input=='login':
        logged_in = Login()
    elif logged_in==True:
        if user_input=='send':
            trade_settings.SendTrade()
        elif len(user_input_split) > 1:
            fed_input = user_input_split[1].lower()
            if user_input_split[0]=='use':
                trade_settings.GetBalance(fed_input)
            elif user_input_split[0]=='risk':
                trade_settings.GetRisk(fed_input)
            elif user_input_split[0]=='sym':
                trade_settings.GetSymbol(fed_input)
            elif user_input_split[0]=='order':
                trade_settings.GetOrderType(fed_input)
            elif user_input_split[0]=='limit':
                trade_settings.GetLimit(fed_input)
            elif user_input_split[0]=='trade':
                trade_settings.GetTradeType(fed_input)
            elif user_input_split[0]=='sl':
                trade_settings.GetExit(sl=fed_input)
            elif user_input_split[0]=='tpt':
                trade_settings.GetTPType(fed_input)
            elif user_input_split[0]=='tp':
                trade_settings.GetExit(tp=fed_input)
