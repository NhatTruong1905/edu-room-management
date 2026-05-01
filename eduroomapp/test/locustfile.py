import random
from locust import HttpUser, task, between


class EduRoomStudent(HttpUser):
    wait_time = between(2, 5)

    def on_start(self):
        self.client.post("/login", data={
            "username": "gv03",
            "password": "123"
        })

    @task(4)
    def search_rooms(self):
        random_day = random.randint(15, 20)
        query_params = {
            "date": f"2026-05-{random_day:02d}",
            "start_time": "08:00",
            "end_time": "10:00",
            "capacity": "50",
        }

        with self.client.get("/api/rooms", params=query_params, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Lỗi tìm phòng! Status Code: {response.status_code}")

    @task(2)
    def view_booking_dashboard(self):
        with self.client.get("/booking", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Lỗi tải Dashboard: {response.status_code}")

    @task(2)
    def view_my_history(self):
        with self.client.get("/api/bookings", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Lỗi lịch sử: {response.status_code}")

    @task(1)
    def view_home_page(self):
        self.client.get("/")
