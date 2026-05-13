import time
from datetime import datetime
from telnetlib import EC

from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from eduroomapp.test.pages.BookingPage import BookingPage
from eduroomapp.test.pages.LoginPage import LoginPage
from eduroomapp.test.test_base import driver
from eduroomapp.utils import sleep

BASE_URL = 'http://localhost:5000'


def login(driver):
    login = LoginPage(driver)
    login.open_page()
    login.login('admin1', '123')


def test_login_logout_success(driver):
    login = LoginPage(driver=driver)
    login.open_page()
    login.login('admin1', '123')

    time.sleep(2)

    assert driver.current_url == 'http://localhost:5000/'
    e = driver.find_element(By.CSS_SELECTOR, 'body > nav > div > div > span')
    assert 'Quản Trị' in e.text

    logout = driver.find_element(By.CSS_SELECTOR, 'body > nav > div > div > a')
    logout.click()
    time.sleep(2)
    assert driver.current_url == 'http://localhost:5000/login'

def login(driver):
    login = LoginPage(driver)
    login.open_page()
    login.login('admin1', '123')

    time.sleep(2)



def test_search_room(driver):
    login(driver)
    booking = BookingPage(driver)
    booking.open_page()

    min_capacity = 5
    booking.search_room(date='2026-05-25', start='18:00', end='19:00', min_capacity=min_capacity)

    time.sleep(2)
    smalls = driver.find_elements(
        By.CSS_SELECTOR,
        '#room-list-container .d-flex.justify-content-between.align-items-end small'
    )

    for small in smalls:
        assert min_capacity <= int(small.text[:-3].strip())


def test_reset_search_form(driver):
    login(driver)
    booking = BookingPage(driver)
    booking.open_page()

    booking.search_room(date='2026-06-20', start='18:00', end='19:00', min_capacity=20)
    time.sleep(1)
    booking.reset_form()
    time.sleep(1)

    date = driver.find_element(By.ID, 'date').get_attribute('value')
    capacity = driver.find_element(By.ID, 'capacity').get_attribute('value')

    try:
        driver.find_element(By.CSS_SELECTOR, '#room-list-container > div > p')
    except NoSuchElementException:
        assert False

    assert date == datetime.today().strftime('%Y-%m-%d')

def test_book_room(driver):
    login(driver)
    booking = BookingPage(driver)
    booking.open_page()
    booking.search_room(date='2026-07-20', start='18:00', end='19:00', min_capacity=20)

    time.sleep(2)
    before = booking.get_booking_table_text()
    btn = driver.find_element(By.CSS_SELECTOR, '#room-list-container > div:nth-child(4) > div > div > div.d-flex.justify-content-between.align-items-end > button')
    btn.click()
    time.sleep(2)

    after = booking.get_booking_table_text()
    assert before != after


def test_cancel_booking(driver):
    login(driver)
    booking = BookingPage(driver)
    booking.open_page()
    booking.search_room(date='2026-08-24', start='18:00', end='19:00', min_capacity=20)

    time.sleep(2)
    booking.get_booking_table_text()
    btn = driver.find_element(By.CSS_SELECTOR, '#room-list-container > div:nth-child(4) > div > div > div.d-flex.justify-content-between.align-items-end > button')
    btn.click()
    time.sleep(2)
    before = booking.get_booking_table_text()
    booking.cancel_first_booking()

    time.sleep(1)
    alert = driver.switch_to.alert
    assert 'Bạn có chắc chắn muốn hủy lịch đặt phòng này không?'.strip().lower() in alert.text.strip().lower()
    alert.accept()
    time.sleep(1)
    alert = driver.switch_to.alert
    assert 'Hủy phòng thành công'.strip().lower() in alert.text.strip().lower()
    alert.accept()
    time.sleep(1)

    after = booking.get_booking_table_text()

    assert before != after


def test_cancel_booking_dismiss(driver):
    login(driver)
    booking = BookingPage(driver)
    booking.open_page()
    booking.search_room(date='2026-05-26', start='18:00', end='19:00', min_capacity=20)

    time.sleep(2)
    booking.get_booking_table_text()
    btn = driver.find_element(By.CSS_SELECTOR, '#room-list-container > div:nth-child(4) > div > div > div.d-flex.justify-content-between.align-items-end > button')
    btn.click()
    time.sleep(2)

    before = booking.get_booking_table_text()
    booking.cancel_first_booking()

    time.sleep(1)
    alert = driver.switch_to.alert
    assert 'hủy lịch đặt phòng' in alert.text.lower()
    alert.dismiss()
    time.sleep(2)

    after = booking.get_booking_table_text()
    assert before == after