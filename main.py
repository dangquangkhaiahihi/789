from DrissionPage import ChromiumPage
from DrissionPage import ChromiumOptions
import pytesseract
from PIL import Image
import threading
import time
import requests
import base64
import json
import random
import logging

ports = ["FAFA", "SUNPAY", "V8Pay", "ASIA"]
logging.basicConfig(level=logging.INFO, filename="789_log.log",filemode="a")

# Open the file and load JSON data
with open('./config.json') as file:
    config_data = json.load(file)

# Print the loaded data
logging.info(f"config_data {config_data}")

def fill_user_name(tab, username):
    try:
        tab.wait.ele_displayed('xpath://*[@id="rootBody"]/div[1]/div/div/gupw-login-box/div[2]/form/div[1]/input', 60)
        usernameInput = tab.ele('xpath://*[@id="rootBody"]/div[1]/div/div/gupw-login-box/div[2]/form/div[1]/input')
        usernameInput.focus()
        usernameInput.input(username)
    except Exception as e:
        logging.info(f"An ERROR: {e}")
        # fill_user_name(tab, username)
        raise e
def fill_password(tab, password):
    try:
        tab.wait.ele_displayed('xpath://*[@id="rootBody"]/div[1]/div/div/gupw-login-box/div[2]/form/div[2]/input', 60)
        passwordInput = tab.ele('xpath://*[@id="rootBody"]/div[1]/div/div/gupw-login-box/div[2]/form/div[2]/input')
        passwordInput.focus()
        passwordInput.input(password)
    except Exception as e:
        logging.info(f"An ERROR: {e}")
        # fill_password(tab, password)
        raise e
def fill_captcha(tab, captcha):
    logging.info(f"captcha {captcha}")
    try:
        tab.wait.ele_displayed('xpath://*[@id="rootBody"]/div[1]/div/div/gupw-login-box/div[2]/form/div[3]/gupw-captcha-login-box/input', 60)
        captchaInput = tab.ele('xpath://*[@id="rootBody"]/div[1]/div/div/gupw-login-box/div[2]/form/div[3]/gupw-captcha-login-box/input')
        captchaInput.input(captcha)
    except Exception as e:
        logging.info(f"An ERROR: {e}")
        # fill_password(tab, captcha)
        raise e

def focus_captcha(tab):
    try:
        tab.wait.ele_displayed('xpath://*[@id="rootBody"]/div[1]/div/div/gupw-login-box/div[2]/form/div[3]/gupw-captcha-login-box/input', 60)
        captchaInput = tab.ele('xpath://*[@id="rootBody"]/div[1]/div/div/gupw-login-box/div[2]/form/div[3]/gupw-captcha-login-box/input')
        captchaInput.focus()
    except Exception as e:
        logging.info(f"An ERROR: {e}")
        # fill_password(tab)
        raise e

def close_ad_top(tab):
    try:
        tab.wait.ele_displayed('xpath://*[@id="rootBody"]/div[1]/div/div/gupw-dialog-marquee/aside/div[2]/span', 60)
        closeBtn = tab.ele('xpath://*[@id="rootBody"]/div[1]/div/div/gupw-dialog-marquee/aside/div[2]/span')
        closeBtn.click()
    except Exception as e:
        logging.info(f"An ERROR: {e}")
        # close_ad_top(tab)
        raise e

pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR/tesseract.exe'

def read_captcha(path):
    captcha_image = Image.open(path)
    captcha_text = pytesseract.image_to_string(captcha_image)
    logging.info(f"CAPTCHA Text: {captcha_text}")
    return captcha_text

# Decoded the data using the base64 codec, and then write it to the filesystem
def saveBase64ToFile(base64_data_img, file_path):
    # Split the base64 string to get the actual data part
    base64_data = base64_data_img.split(',')[1]
    with open(file_path, "wb") as fh:
        # Decode base64 string to bytes and write to file
        fh.write(base64.b64decode(base64_data))

# luồng login
def handle_login (tab3, file_captcha_name):
    logging.info("run login")
    try:
        close_ad_top(tab3)
        fill_user_name(tab3, config_data["username"])
        fill_password(tab3, config_data["password"])
        focus_captcha(tab3)
        time.sleep(1)
        tab3.wait.ele_displayed('xpath://*[@id="rootBody"]/div[1]/div/div/gupw-login-box/div[2]/form/div[3]/gupw-captcha-login-box/img', 60)
        captchaImage = tab3.ele('xpath://*[@id="rootBody"]/div[1]/div/div/gupw-login-box/div[2]/form/div[3]/gupw-captcha-login-box/img')
        saveBase64ToFile(captchaImage.attr('ng-src'), file_captcha_name)

        time.sleep(1)
        captchaValue = read_captcha(file_captcha_name)
        time.sleep(1)
        logging.info("Start fill captcha")
        fill_captcha(tab3, captchaValue)
        logging.info("End fill captcha")
        loginButton = tab3.ele('xpath://*[@id="rootBody"]/div[1]/div/div/gupw-login-box/div[2]/form/div[4]/button') # ấn login
        try:
            loginButton.click()
        except Exception as e:
            logging.info(f"An ERROR: {e}")

        time.sleep(2)
        result = check_login_success(tab3)
        if not result:
            tab3.refresh()
            tab3.wait.doc_loaded()
            handle_login(tab3, file_captcha_name)

    except Exception as e:
        logging.info(f"An ERROR handle_login: {e}")
        tab3.refresh()
        tab3.wait.doc_loaded()
        # if not check_login_success():
        #     return
        handle_login(tab3, file_captcha_name)

def check_login_success(tab3):
    confirm_login_not_success = tab3.ele('xpath://*[@id="rootBody"]/div[1]/div/div/gupw-dialog-alert/div[3]/div/div[2]/button')
    logging.info(f"check_login_success {confirm_login_not_success}")
    try:
        confirm_login_not_success.click()
        logging.info("login not success")
        return False
    except Exception as e:
        logging.info(f"login success {e}")
        return True

# def check_is_logged_in():
#     logedin_info = tab3.ele('xpath://*[@id="app"]/ui-view/gupw-app/ui-view/gupw-sample-layout/gupw-header/header/section[1]/div/div[2]/div[1]/gupw-account-box-with-nav')
#     if logedin_info

def send_message(message):
    url = f"https://api.telegram.org/bot{config_data['bot_token']}/sendMessage?chat_id={config_data['chat_id']}&text={message}"
    requests.get(url)

def check_bank_exist(input_str):
    result = False
    with open('banks.txt', "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() == input_str.strip():
                result = True
                break
    return result

def ghi_file_txt(textlines):
  try:
    with open('banks.txt', "a", encoding="utf-8") as f:
        f.write(textlines + "\n")
    return True
  except Exception as e:
    logging.info(f"An ERROR ghi_file_txt: {e}")

def random_integer_between(lower, upper):
    return random.randint(lower, upper)

def run_web (index, file_captcha_name):
    # Create a page object
    option = ChromiumOptions().auto_port()
    option.set_user("Profile" + str(index))
    page = ChromiumPage(option)
    # Control the browser to visit Baidu
    page.get(config_data['domain'])
    tab1 = page.get_tab(page.latest_tab)
    # Locate the input box and enter the keyword
    page.ele('xpath:/html/body/div[2]/div[1]/div[1]/a').click()

    # Vào tab mới vừa bật
    page.wait.new_tab()
    tab1.close()
    # tab2 = page.get_tab(page.latest_tab)
    # tab2.ele('#btn-5').click()

    # Tiếp tục đến tab tiếp theo
    # page.wait.new_tab()
    tab3 = page.get_tab(page.latest_tab)
    # tab2.close()

    # Bắt đầu thao tác trên trang chính của 789
    original_url = tab3.url # Origin URL
    base_url = original_url.split('?')[0] # Extract base URL
    login_url = base_url + '/Login'
    tab3.get(login_url)
    tab3.wait.doc_loaded()

    handle_login(tab3, file_captcha_name)

    # Sau khi đã login thành công => Vào trạng nạp tiền
    deposit_url = base_url + '/Deposit'
    logging.info("deposit url goooo")

    tab3.get(deposit_url)
    tab3.wait.doc_loaded()

    close_ad_top(tab3)

    # //*[@id="app"]/ui-view/gupw-app/ui-view/gupw-sample-layout/gupw-header/header/section[1]/div/div[2]/div[1]/gupw-account-box-with-nav

    while True:
        port_bank = ports[random_integer_between(0, 3)]
        logging.info(f"DOING AT PORT {port_bank}")
        try:
            tab3.wait.ele_displayed('xpath://*[@id="app"]/ui-view/gupw-app/ui-view/gupw-sample-layout/div[3]/div/ui-view/gupw-member-center-layout/div/div/div[2]/ui-view/gupw-deposit/article/div/gupw-online-deposit/div/div/div/div/div/div/div[1]/ul', 60)
            list_buttons_select_payment = tab3.ele(
                'xpath://*[@id="app"]/ui-view/gupw-app/ui-view/gupw-sample-layout/div[3]/div/ui-view/gupw-member-center-layout/div/div/div[2]/ui-view/gupw-deposit/article/div/gupw-online-deposit/div/div/div/div/div/div/div[1]/ul')
            selected_payment_name = None
            try:
                for element in list_buttons_select_payment.children():
                    logging.info(f"element.ele('t:h3').text : {element.ele('t:h3').text}")
                    logging.info(f"{port_bank} in {element.ele('t:h3').text}? : {port_bank in element.ele('t:h3').text}")
                    if port_bank in element.ele('t:h3').text:
                        selected_payment_name = element.ele('t:h3').text
                        element.click()
                        break
            except Exception as e:
                tab3.get(login_url)
                tab3.wait.doc_loaded()

                handle_login(tab3, file_captcha_name)

                # Sau khi đã login thành công => Vào trạng nạp tiền
                deposit_url = base_url + '/Deposit'
                logging.info(f"deposit_url {deposit_url}")
                tab3.get(deposit_url)
                tab3.wait.doc_loaded()
                close_ad_top(tab3)
                continue

            if "ASIA" in selected_payment_name or "FAFA" in selected_payment_name or "SUNPAY" in selected_payment_name:
                time.sleep(1)
                tab3.wait.ele_displayed('xpath://*[@id="form"]/form/fieldset[1]/select')
                select_bank = tab3.ele('xpath://*[@id="form"]/form/fieldset[1]/select')
                logging.info(f"select_bank: {select_bank}")

                time.sleep(1)

                options = select_bank.select.options
                option = options[random_integer_between(1, len(options) - 1)]
                logging.info(f'option: {option}')
                select_bank.select.by_option(option)

                input_amount = tab3.ele('xpath://*[@id="form"]/form/fieldset[4]/div/div/input')
                input_amount.input(random_integer_between(100, 300))
            else:
                input_amount = tab3.ele('xpath://*[@id="form"]/form/fieldset[2]/div/div/input')
                input_amount.input(random_integer_between(100, 300))

            tab3.wait.ele_displayed('xpath://*[@id="submitOnlineDeposit"]/span', 60)
            thanh_toan_ngay_btn = tab3.ele('xpath://*[@id="submitOnlineDeposit"]/span')
            logging.info(f"thanh_toan_ngay_btn: {thanh_toan_ngay_btn}")
            thanh_toan_ngay_btn.click()

            tab_thanh_toan = page.get_tab(page.latest_tab)
            tab_thanh_toan.wait.doc_loaded()

            try:
                tab_thanh_toan.wait.doc_loaded()
                tab_thanh_toan.wait.ele_displayed('#body')
                tab_thanh_toan.save(path='./download')
                username = tab_thanh_toan.ele('#username').text
                bankNumber = tab_thanh_toan.ele('#bankNumber').text
                bankName = tab_thanh_toan.ele('#bankName').text

                result = f"- {port_bank} - {bankName} - {username} - {bankNumber}"
                if check_bank_exist(result) or result.find("*") != -1:
                    logging.info(f"BANK EXISTED: {f'- {port_bank} - {bankName} - {username} - {bankNumber}'}")
                else:
                    ghi_file_txt(result)
                    send_message(f"- {port_bank} -\n{bankName} - {username} - {bankNumber}")
                tab_thanh_toan.close()
            except Exception as e:
                try:
                    list_select_bank = tab_thanh_toan.ele('xpath://*[@id="body"]/div/div/div/div[4]').children()
                    selected_item_index = random_integer_between(0, len(list_select_bank) - 1)
                    selected_item = tab_thanh_toan.ele(
                        f'xpath://*[@id="body"]/div/div/div/div[4]/div[{selected_item_index}]/div/div/div/div[2]/button')
                    selected_item.click()

                    tab_thanh_toan.wait.doc_loaded()

                    # Đoạn dưới giống hệt try
                    username = tab_thanh_toan.ele(
                        'xpath://*[@id="body"]/div/div/div/div/div[3]/div/div[2]/div/div[2]/div/div/span').text
                    bankNumber = tab_thanh_toan.ele(
                        'xpath://*[@id="body"]/div/div/div/div/div[3]/div/div[3]/div/div[1]/div/span').text
                    bankName = tab_thanh_toan.ele(
                        'xpath://*[@id="body"]/div/div/div/div/div[3]/div/div[4]/div/div[1]/div/span').text

                    result = f"- {port_bank} - {bankName} - {username} - {bankNumber}"
                    if check_bank_exist(result) or result.find("*") != -1:
                        logging.info(f"BANK EXISTED: {f'- {port_bank} - {bankName} - {username} - {bankNumber}'}")
                    else:
                        ghi_file_txt(result)
                        send_message(f"- {port_bank} - OKVIP -\n{bankName} - {username} - {bankNumber}")
                    tab_thanh_toan.close()
                except Exception as e:
                    tab_thanh_toan.close()
        except Exception as e:
            logging.info(f"An ERROR while true: {e}")
            tab3.refresh()
            tab3.wait.doc_loaded()
            close_ad_top(tab3)
            continue
def main():
    logging.info('running........')

    p1 = threading.Thread(target=run_web, args=(1, 'captcha1.png'))
    p1.start()
    time.sleep(20)
    p2 = threading.Thread(target=run_web, args=(2, 'captcha2.png'))
    p2.start()
    time.sleep(20)
    p3 = threading.Thread(target=run_web, args=(3, 'captcha3.png'))
    p3.start()
    time.sleep(20)
    p4 = threading.Thread(target=run_web, args=(4, 'captcha4.png'))
    p4.start()

if __name__ == "__main__":
     _ = main()