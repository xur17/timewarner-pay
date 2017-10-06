from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import sys
import time
import traceback
from decimal import Decimal


PAYMENT_COUNT = 13
USERNAME = 'emailaddress@gmail.com'
PASSWORD = 'spectrumpasswordhere'
CARD = {
    'name': 'Name',
    'number': '1234567812345678',
    'month': '02',
    'year': '2019'
}


class Driver():
    def __init__(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(10)
        self.driver.set_page_load_timeout(5)
        try:
            self.driver.get("https://www.spectrum.net/login/?ReferringPartner=TWC")
        except TimeoutException:
            pass
        self.driver.set_page_load_timeout(30)
        self.login()

    def close(self):
        self.driver.close()

    def login(self):
        # Login
        username = self.driver.find_element_by_name("username")
        username.send_keys(USERNAME)

        password = self.driver.find_element_by_name("password")
        password.send_keys(PASSWORD)
        password.send_keys(Keys.ENTER)

    def get_balance(self):
        # Get balance amount
        return self.driver.find_element_by_class_name("amount").text[1:]

    def calculate_payments(self, total_due, chunks):
        total_due = int(total_due * 100)
        starting = (float)(total_due / chunks) - chunks
        payments = []
        for i in range(0, chunks - 1):
            payments.append(starting + i)
        last_payment = total_due - sum(payments)
        payments.append(last_payment)
        return ["%.2f" % (x / 100) for x in payments]

    def pay(self, amount):
        # Pay bill
        self.driver.get("https://myservices.timewarnercable.com/account/index?jli=true")
        self.driver.find_element_by_xpath("//button[@id='start-pay-bill']").click()
        time.sleep(5)
        self.driver.execute_script('''$('#payment-method').css('display', 'inline')''')
        time.sleep(5)
        # self.driver.find_element_by_xpath("//select[@id='payment-method']/option[@value='card']").click()
        self.driver.find_element_by_id("confirm-billpay-type").click()

        # Agree
        self.driver.find_element_by_xpath("//label[@for='agree-terms-checkbox']").click()
        self.driver.find_element_by_id("agree-terms").click()

        # Payment
        self.driver.switch_to_frame(self.driver.find_element_by_class_name("obpIframe"))
        # self.driver.find_element_by_class_name("selectric").click()
        # self.driver.find_element_by_class_name("newcreditcard").click()
        name = self.driver.find_element_by_id("cardName")
        name.send_keys(CARD['name'])
        card_number = self.driver.find_element_by_id("cardNumber")
        card_number.send_keys(CARD['number'])
        self.driver.find_element_by_xpath("//select[@id='expiration_date_month']/option[@value='{}']".format(CARD['month'])).click()
        self.driver.find_element_by_xpath("//select[@id='expiration_date_year']/option[@value='{}']".format(CARD['year'])).click()
        amount_text = self.driver.find_element_by_xpath("//input[@id='payment_amount_value']")
        amount_text.send_keys(amount)
        self.driver.find_element_by_xpath("//a[@href='#verify']").click()
        time.sleep(5)
        self.driver.find_element_by_xpath("//a[@href='#submit']").click()
        time.sleep(10)
        if self.driver.find_element_by_xpath("//a[@data-action='reSubmit']"):
            self.driver.find_element_by_xpath("//a[@data-action='reSubmit']").click()
            time.sleep(10)
        self.driver.find_element_by_id("thank_view").click()

    def pay_in_chunks(self, chunks, balance):
        """Pay bill in 'chunks' payments"""
        for amount in self.calculate_payments(balance, chunks):
            for attempt in range(3):
                try:
                    self.pay(amount)
                    print("Paid", str(amount))
                except:
                    print("Failed payment, retrying once")
                    print(traceback.format_exc())
                else:
                    break
            else:
                print("Failed multiple attempts")
                sys.exit()


if __name__ == "__main__":
    d = Driver()
    balance = Decimal(d.get_balance())
    print('Payment amounts: {}'.format(d.calculate_payments(balance, 13)))
    d.pay_in_chunks(13, balance)
    d.close()
