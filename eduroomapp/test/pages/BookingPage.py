import time

from selenium.webdriver.common.by import By
from eduroomapp.test.pages.BasePage import BasePage


class BookingPage(BasePage):
    URL = 'http://localhost:5000/booking'

    DATE_INPUT = (By.ID, 'date')
    START_TIME = (By.ID, 'start_time')
    END_TIME = (By.ID, 'end_time')
    MIN_CAPACITY = (By.ID, 'capacity')
    SEARCH_BTN = (By.CSS_SELECTOR, '#search-form button[type="submit"]')
    RESET_BTN = (By.ID, 'btn-reset-form')
    ROOM_LIST = (By.ID, 'room-list-container')
    PAGINATION = (By.ID, 'pagination-container')
    CLEAR_ROOMS = (By.ID, 'btn-clear-rooms')
    BOOKING_TABLE = (By.ID, 'user-bookings-list')
    CANCEL_ROOMS = (By.CSS_SELECTOR, '#user-bookings-list > button')
    CANCEL_BTNS = (By.CLASS_NAME,'btn-outline-danger')

    def cancel_first_booking(self):
        btn = self.finds(*self.CANCEL_BTNS)[0]
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});",btn)
        time.sleep(1)
        btn.click()

    def get_booking_table_text(self):
        return self.find(*self.BOOKING_TABLE).text

    def open_page(self):
        self.open(self.URL)

    def search_room(self, start, end, min_capacity, date=None):
        e = self.find(*self.DATE_INPUT)

        self.driver.execute_script("arguments[0].value = arguments[1]",e,date)
        self.find(*self.START_TIME).send_keys(start)
        self.find(*self.END_TIME).send_keys(end)

        self.typing(*self.MIN_CAPACITY, str(min_capacity))

        self.click(*self.SEARCH_BTN)

    def reset_form(self):
        self.click(*self.RESET_BTN)