import os
import re
import csv
import subprocess as sp
import time
from datetime import datetime as dt
from profile import Profile

import pywifi
from pywifi import const

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

global USER_NAME, USER_PASSWORD, LOGIN_URL, ADV_URL, BASIC_URL, ADVPri_URL

USER_NAME = "admin"
USER_PASSWORD = "cohesive1french1"
LOGIN_URL = "https://192.168.1.1/#/login/"
LOGIN_URL_E3200 = "https://192.168.1.100/#/login/"

ADV_URL = "https://192.168.1.1/#/adv/home/"
BASIC_URL = "https://192.168.1.1/#/basic/home"
ADVPri_URL = "https://192.168.1.1/#/adv/wifi/primary/"

FW_URL_E3100 = "https://192.168.1.1/firmware_upgrade.htm"
FW_URL_E3200 = "https://192.168.1.100/firmware_upgrade.htm"
model_E3100 = "E3100"
model_E3200 = "E3200"
PREV_FW_PATH_E3100 = "D:\\02-Project\WG9116\\g3100_fw_3.2.0.1e-eng0.bin"
PREV_FW_PATH_E3200 = "D:\\02-Project\WG9116\\e3200_fw_3.2.0.1c-eng0.bin"
LATEST_FW_PATH_E3100 = "D:\\02-Project\WG9116\\3.2.0.3c\\g3100_fw_v3.2.0.3c-eng0.bin"
LATEST_FW_PATH_E3200 = "D:\\02-Project\WG9116\\3.2.0.3c\\e3200_fw_3.2.0.3-eng0.bin"
INVALID_FW_PATH = "D:\\02-Project\WG9116\\error_fw_v1.1.1.1-eng0.bin"
LATEST_FW_VER_E3100 = "3.2.0.3c-eng0"
LATEST_FW_VER_E3200 = "3.2.0.3c-eng0"
PREV_FW_VER_E3100 = "3.2.0.1e-eng0"
PREV_FW_VER_E3200 = "3.2.0.1e-eng0"

#########For WIFI Setting #################
WIFI_24G_SSID = "Fios-Gb7xX_2.4g"
WIFI_5G1_SSID = "Fios-Gb7xX_5g1"
WIFI_5G2_SSID = "Fios-Gb7xX_5g2"
WIFI_pwd = "12345678"

# CSS_SELECTOR
ELM_SELECTORS = {
    # "DIV_LOGIN_DES": "div#login_des", #3100
    "DIV_LOGIN_DES": "div.login-text",  # FBA
    "DIV_ADVERSE": "div.nav-text:nth-child(2)",
    "INPUT_PASSWORD": "input[type='password']",
    "BUTTON_LOGIN": "button.btn-primary",
    "DIV_WiFi": "/html/body/div/div[1]/div[2]/div/div[3]/div[2]/div[2]/div[2]/div[3]/div/label/span[1]",  # son enable
    "DIV_WiFi2": "//div[@id='main_content_basic']/div[2]/div[2]/div/div[4]/div/label/span",
    "FW_table": "//div[@class='data-v-7dc79bbe']",
    "BEGIN_UPGRADE": "button.btn-primary"
}


def get_ver_from_str(str_ver_info: str):
    pattern = "\d{1,2}.\d{1,2}.\d{1,2}.\d{1,2}[a-z]{0,1}-eng0"
    res = re.findall(pattern, str_ver_info)
    if len(res) > 0:
        return res[0]
    return None


def WIFI_contect(wifi_type):
    wifi = pywifi.PyWiFi()  # 創建WiFi對象
    ifaces = wifi.interfaces()[0]  # 獲取網卡
    ifaces.disconnect()
    time.sleep(10)
    wifistatus = ifaces.status()
    if wifistatus == const.IFACE_DISCONNECTED:
        print("wifi disconnect first!")
    else:
        print(wifi_type + "wifi is connect!")
    profile: Profile = pywifi.Profile()
    profile.ssid = wifi_type
    password = WIFI_pwd
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = password
    ifaces.remove_all_network_profiles()
    tep_profile = ifaces.add_network_profile(profile)
    ifaces.connect(tep_profile)  # create wifi contection
    time.sleep(3)

    if ifaces.status() == const.IFACE_CONNECTED:
        print("WIFI is connect with %s" % wifi_type)
        for i in range(3):
            try:
                hostname = "www.google.com"
                response = os.system("ping -n 4 " + hostname)
                if response == 0:
                    print(i, "System " + wifi_type + " is UP! Network active")
                else :
                    print(i, "System " + wifi_type + " is DOWN! Network broken")
            except ValueError:
                break
    else:
        for j in range(3):
            try:
                ifaces.disconnect()
                time.sleep(3)
                ifaces.connect(tep_profile)
                time.sleep(3)
                for k in range(3):
                    hostname = "www.yahoo.com"
                    response = os.system("ping -n 4 " + hostname)
                    if response == 0:
                        print(k, "System " + wifi_type + " is UP! Network active")
                    else:
                        print(k, "System " + wifi_type + " is DOWN! Network broken")
            except ValueError:
                break


def Login(url_login, driver):
    driver.get(url_login)
    driver.set_window_size(1050, 664)
    driver.find_element(By.ID, 'details-button').send_keys(Keys.ENTER)
    driver.find_element(By.ID, 'proceed-link').send_keys(Keys.ENTER)

    try:
        elm_login_des = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ELM_SELECTORS["DIV_LOGIN_DES"])))
        elm_input_pass = driver.find_element(By.CSS_SELECTOR, ELM_SELECTORS["INPUT_PASSWORD"])
        elm_input_pass.send_keys(USER_PASSWORD)
        loginpage = dt.now().strftime("login_%Y_%m_%d_%H%M%S.png")
        driver.save_screenshot(loginpage)
        elm_button = driver.find_element(By.CSS_SELECTOR, ELM_SELECTORS["BUTTON_LOGIN"])
        elm_button.click()
        txt_main_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "head title"))).get_attribute("text")
        print("[Info] login %s" % txt_main_title)

    except Exception as e:
        driver.quit()
        print("[Error] %s" % str(e))


def WiFiStatusCheck(driver):
    strScript = 'window.open("' + ADVPri_URL + '");'
    driver.execute_script(strScript)
    driver.get(ADVPri_URL)
    driver.set_window_size(1050, 664)
    time.sleep(5)

    driver.find_element(By.XPATH, ELM_SELECTORS["DIV_WiFi"]).click()
    time.sleep(10)
    filename = dt.now().strftime("wifi_status_%Y_%m_%d_%H%M%S.png")
    driver.save_screenshot(filename)
    print("Wifi check!")


def check_invalid_fw(model, url_login, url_upload, fw_path):
    if model == model_E3100:
        upload_fw(url_login, url_upload, fw_path)
    elif model == model_E3200:
        upload_fw(url_login, url_upload, fw_path)


def check_latest_fw(model, url_login, url_upload, fw_path):
    if model == model_E3100:
        upload_fw(url_login, url_upload, fw_path)
    elif model == model_E3200:
        upload_fw(url_login, url_upload, fw_path)


def check_previous_fw(model, url_login, url_upload, fw_path):
    if model == model_E3100:
        upload_fw(url_login, url_upload, fw_path)
    elif model == model_E3200:
        upload_fw(url_login, url_upload, fw_path)


def upload_fw(url_login, url_upload, fw_path):
    driver = webdriver.Chrome()
    Login(url_login, driver)
    time.sleep(5)
    strScript = 'window.open("' + url_upload + '");'
    driver.execute_script(strScript)
    driver.get(url_upload)
    driver.set_window_size(1050, 664)
    time.sleep(5)
    sss = driver.find_element(By.CSS_SELECTOR, 'input[type="file" i]')
    print("upload fw %s" % fw_path)
    sss.send_keys(fw_path)
    driver.find_element(By.CSS_SELECTOR, ELM_SELECTORS["BEGIN_UPGRADE"]).click()
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, ".popup-modal-middle .btn-primary").click()
    time.sleep(60)
    fw_ver = get_ver_from_str(fw_path)
    print("fw_ver " + fw_ver)

    if '1.1.1.1-eng0' in fw_ver:
        str_expect_invalid = "Invalid firmware, please select another firmware"
        popup_error_msg = driver.find_element(By.CSS_SELECTOR, ".popup-modal-middle .popup-modal-content-box span").text
        print("str_expect_invalid " + str_expect_invalid)
        div_fw_version = driver.find_element(By.CLASS_NAME, "version-text")
        fw_version_latest = div_fw_version.find_element(By.TAG_NAME, "span")
        # print("FW check again:", fw_version_latest[1].text)
        if popup_error_msg == str_expect_invalid:
            print("[PASS] Case1:upload fail due to \"%s\"" % str_expect_invalid)
        filename = dt.now().strftime("invalid_FW_ver_%Y_%m_%d_%H%M%S.png")
        driver.save_screenshot(filename)
        time.sleep(10)
        driver.quit()
    else:
        filename = dt.now().strftime("FW_ver_%Y_%m_%d_%H%M%S.png")
        driver.save_screenshot(filename)
        time.sleep(600)
        driver.quit()


def check_fw(url_login, url_upload, target_val):
    driver = webdriver.Chrome()
    Login(url_login, driver)
    time.sleep(5)
    strScript = 'window.open("' + url_upload + '");'
    driver.execute_script(strScript)
    driver.get(url_upload)
    driver.set_window_size(1050, 664)
    time.sleep(5)
    fw_info = driver.find_element(By.CLASS_NAME, "version-text").text
    fw_ver = get_ver_from_str(fw_info)
    print("target ver:", target_val)
    print("FW check again:", fw_ver)
    if fw_ver == target_val:
        return "PASS"
    else:
        return "FAIL"


def Case_5G1_Previous_Fw(model):
    print("Test model=" + model)
    if model == model_E3100:
        check_previous_fw(model_E3100, LOGIN_URL, FW_URL_E3100, PREV_FW_PATH_E3100)
        print("##### Case_5G1_Previos #########")
        print("conntect wifi again")
        WIFI_contect(WIFI_5G1_SSID)
        res1 = check_fw(LOGIN_URL, FW_URL_E3100, PREV_FW_VER_E3100)  # for E3100
        print("Test Result %s" % str(res1))
        with open('FW_update_test_result.csv', 'a', newline='') as testresult_file:
            writer = csv.writer(testresult_file)
            writer.writerow(["model", "Name", "TestResult"])
            writer.writerow([model, "Case_5G1_Previous_Fw", str(res1)])
    elif model == model_E3200:
        check_previous_fw(model_E3200, LOGIN_URL_E3200, FW_URL_E3200, PREV_FW_VER_E3200)
        print("##### Case_5G1_Previos #########")
        print("conntect wifi again")
        WIFI_contect(WIFI_5G1_SSID)
        res2 = check_fw(LOGIN_URL_E3200, FW_URL_E3200, PREV_FW_VER_E3200)  # for E3200
        print("Test Result %s" % str(res2))
        with open('FW_update_test_result.csv', 'a', newline='') as testresult_file:
            writer = csv.writer(testresult_file)
            # writer.writerow(["model", "Name", "TestResult"])
            writer.writerow([model, "Case_5G1_Previous_Fw", str(res2)])


def Case_5G1_Latest_Fw(model):
    if model == model_E3100:
        check_latest_fw(model_E3100, LOGIN_URL, FW_URL_E3100, LATEST_FW_PATH_E3100)
        print("##### Case_5G1_LATEST #########")
        print("conntect wifi again")
        WIFI_contect(WIFI_5G1_SSID)
        res1 = check_fw(LOGIN_URL, FW_URL_E3100, LATEST_FW_VER_E3100)  # for E3100
        print("Test Result %s" % str(res1))
        with open('FW_update_test_result.csv', 'a', newline='') as testresult_file:
            writer = csv.writer(testresult_file)
            # writer.writerow(["model", "Name", "TestResult"])
            writer.writerow([model, "Case_5G1_Latest_Fw", str(res1)])
    elif model == model_E3200:
        check_previous_fw(model_E3200, LOGIN_URL_E3200, FW_URL_E3200, LATEST_FW_VER_E3200)
        print("##### Case_5G1_LATEST #########")
        print("conntect wifi again")
        WIFI_contect(WIFI_5G1_SSID)
        res2 = check_fw(LOGIN_URL_E3200, FW_URL_E3200, LATEST_FW_VER_E3200)  # for E3200
        print("Test Result %s" % str(res2))
        with open('FW_update_test_result.csv', 'a', newline='') as testresult_file:
            writer = csv.writer(testresult_file)
            # writer.writerow(["model", "Name", "TestResult"])
            writer.writerow([model, "Case_5G1_Latest_Fw", str(res2)])


def Case_5G1_Invalid_Fw(model):
    print("Test model=" + model)
    if model == model_E3100:
        check_previous_fw(model_E3100, LOGIN_URL, FW_URL_E3100, INVALID_FW_PATH)
        print("##### Case_5G1_Invalid #########")
        print("conntect wifi again")
        WIFI_contect(WIFI_5G1_SSID)
        res1 = check_fw(LOGIN_URL, FW_URL_E3100, INVALID_FW_PATH)  # for E3100
        print("Test Result %s" % str(res1))
        with open('FW_update_test_result.csv', 'a', newline='') as testresult_file:
            writer = csv.writer(testresult_file)
            #  writer.writerow(["model", "Name", "TestResult"])
            writer.writerow([model, "Case_5G1_Invalid_Fw", str(res1)])
    elif model == model_E3200:
        check_previous_fw(model_E3200, LOGIN_URL_E3200, FW_URL_E3200, INVALID_FW_PATH)
        print("##### Case_5G1_Invalid #########")
        print("conntect wifi again")
        WIFI_contect(WIFI_5G1_SSID)
        res2 = check_fw(LOGIN_URL_E3200, FW_URL_E3200, INVALID_FW_PATH)  # for E3200
        print("Test Result %s" % str(res2))
        with open('FW_update_test_result.csv', 'a', newline='') as testresult_file:
            writer = csv.writer(testresult_file)
            # writer.writerow(["model", "Name", "TestResult"])
            writer.writerow([model, "Case_5G1_Invalid_Fw", str(res2)])

if __name__ == "__main__":
    Case_5G1_Previous_Fw(model_E3100)
    Case_5G1_Previous_Fw(model_E3200)
    Case_5G1_Latest_Fw(model_E3100)
    Case_5G1_Latest_Fw(model_E3200)
    Case_5G1_Invalid_Fw(model_E3100)
    Case_5G1_Invalid_Fw(model_E3200)
