from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
import threading
import decimal
import re
import clipboard

def clear(driver, item):
    try:
        item.send_keys(Keys.BACK_SPACE)
        item.send_keys(Keys.BACK_SPACE)
        item.send_keys(Keys.BACK_SPACE)
        item.send_keys(Keys.BACK_SPACE)
    except:
        pass

def result(driver, i, is_print):
    try:
        div      = driver.find_element(By.CLASS_NAME, BACKTEST_CLASS).find_element(By.TAG_NAME, "div")
        report   = re.findall(">\\d+\\.\\d+%|>\\d+%|>\\d+\\.\\d+<|>\\d+<", div.get_attribute('innerHTML'))
        net      = decimal.Decimal(report[0][1:-1])
        trades   = decimal.Decimal(report[1][1:-1])
        winrate  = decimal.Decimal(report[2][1:-1])
        pf       = decimal.Decimal(report[3][1:-1])
        maxdown  = decimal.Decimal(report[4][1:-1])
        printdata = [str(i), str(net), str(trades), str(winrate), str(pf), str(maxdown)]
        if is_print:
            print ('	'.join(printdata))
        return decimal.Decimal(net)
    except:
        return decimal.Decimal(0)

def listTrade(driver):
    backData = []
    while True:
        try:
            trs = driver.find_element(By.TAG_NAME , 'tbody').find_elements(By.TAG_NAME, "tr")
            ifBreak = False
            for tr in trs:
                b = '<tr>' + tr.get_attribute('innerHTML') + '</tr>'
                if (b not in backData):
                    backData.append(b.replace('"></td></tr>', '" hidden></td></tr>'))
                if ('>1<' in b):
                    ifBreak = True
                    break
            if (ifBreak):
                break
        except:
            continue
    backData.reverse()
    clipboard.copy('<table>' + ''.join(backData) + '</table>')

def isApply(driver, old_net, j):
    k = 0
    while True:
        new_net = result(driver, j, False)
        if ((new_net != old_net and new_net != 0 ) or (new_net == old_net and k >= 10)):
            break
        time.sleep(1)
        k+=1

def inputcheck(driver, inp, range1, range2, step):
    try:
        print ("================="+str(inp)+"=================")
        i = driver.find_element(By.XPATH, data[inp])
        old_best = i.get_attribute("value")
        time.sleep(1)
        try:
            maxnet = result(driver, 0, False)
        except:
            maxnet = decimal.Decimal(0)
        ip = 0
        j = range1
        while j <= range2:
            old_net = result(driver, j, False)
            clear(driver, i)
            i.send_keys(str(j))
            driver.find_element(By.XPATH, data[0]).click()
            isApply(driver, old_net, j)
            net = result(driver, j, True)
            if (net >= maxnet):
                maxnet = net
                ip = j
            j+=step
            j=round(j, abs(int(f'{step:e}'.split('e')[-1])))
            time.sleep(0.5)
        clear(driver, i)
        i.send_keys(ip)
        print ("Old Best: "+str(old_best))
        print ("New Best: "+str(ip))
        driver.find_element(By.XPATH, data[0]).click()
    except:
        print ("Error")

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--window-size=900,900")
chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

data = ['//*[@id="overlap-manager-root"]/div/div/div[1]/div/div[3]/div/div[1]/div']
for i in range(2, 100, 2):
    data.append('//*[@id="overlap-manager-root"]/div/div/div[1]/div/div[3]/div/div['+str(i)+']/div/span/span[1]/input')

driver=webdriver.Chrome("./chromedriver", chrome_options=chrome_options)
#driver=webdriver.Chrome(".\\chromedriver.exe", chrome_options=chrome_options)

BACKTEST_CLASS = 'backtesting'
driver.get("https://www.tradingview.com/chart/")
driver.add_cookie({"name": "sessionid", "value": "xkgfjgk5fcdsxjmhaguwmfr830pj3wph"})
driver.refresh()

#{
#  "QTY_TYPE": "PERCENT",
#  "TRADE_SIZE": 1,
#  "ORDER": "{{strategy.order.comment}}"
#}
#{
#  "QTY_TYPE": "CASH",
#  "TRADE_SIZE": 635,
#  "ORDER": "{{strategy.order.comment}}"
#}

#inputcheck(driver, 9, 1, 100, 1)



