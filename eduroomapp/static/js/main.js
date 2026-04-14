document.addEventListener('DOMContentLoaded', function () {
    const dateInput = document.getElementById('date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
        if (!dateInput.value) {
            dateInput.value = today;
        }
    }

    const startTimeSelect = document.getElementById('start_time');
    const endTimeSelect = document.getElementById('end_time');

    if (startTimeSelect && endTimeSelect) {
        startTimeSelect.addEventListener('change', function () {
            const selectedStart = startTimeSelect.value;
            const startHour = parseInt(selectedStart.split(':')[0]);

            endTimeSelect.value = "";

            Array.from(endTimeSelect.options).forEach(option => {
                if (option.value === "") return;

                const endHour = parseInt(option.value.split(':')[0]);

                if (endHour <= startHour) {
                    option.disabled = true;
                    option.style.display = 'none';
                } else {
                    option.disabled = false;
                    option.style.display = 'block';
                }
            });
        });
    }

    const btnResetForm = document.getElementById('btn-reset-form');
    if (btnResetForm) {
        btnResetForm.addEventListener('click', function () {
            document.getElementById('search-form').reset();
        });
    }

    const btnClearRooms = document.getElementById('btn-clear-rooms');
    if (btnClearRooms) {
        btnClearRooms.addEventListener('click', function () {
            const container = document.getElementById('room-list-container');

            container.innerHTML = `
                    <div class="col-12 text-center py-5 text-muted">
                        <i class="fa-solid fa-calendar-day fs-1 mb-3 bg-light p-4 rounded-circle"></i>
                        <p>Vui lòng chọn thời gian bên trái để tìm phòng.</p>
                    </div>
                `;

            const hiddenDate = document.getElementById('hidden_date');
            if (hiddenDate) hiddenDate.value = '';
            const hiddenStart = document.getElementById('hidden_start_time');
            if (hiddenStart) hiddenStart.value = '';
            const hiddenEnd = document.getElementById('hidden_end_time');
            if (hiddenEnd) hiddenEnd.value = '';
        });
    }

    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const date = document.getElementById('date').value;
            const start_time = document.getElementById('start_time').value;
            const end_time = document.getElementById('end_time').value;
            const capacity = document.getElementById('capacity').value;

            const url = `/api/rooms?date=${date}&start_time=${start_time}&end_time=${end_time}&capacity=${capacity}`;
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    const container = document.getElementById('room-list-container');

                    if (data.error) {
                        alert(data.error);
                        return;
                    }
                    const hiddenDate = document.getElementById('hidden_date');
                    if (hiddenDate) hiddenDate.value = date;
                    const hiddenStart = document.getElementById('hidden_start_time');
                    if (hiddenStart) hiddenStart.value = start_time;
                    const hiddenEnd = document.getElementById('hidden_end_time');
                    if (hiddenEnd) hiddenEnd.value = end_time;

                    container.innerHTML = '';
                    if (data.rooms.length === 0) {
                        container.innerHTML = `
                                    <div class="col-12 text-center py-5">
                                        <h6 class="fw-bold text-dark"><i class="fa-regular fa-face-frown text-warning fs-1 mb-3 block"></i><br>Rất tiếc! Không có phòng khả dụng.</h6>
                                    </div>`;
                        return;
                    }
                    let htmlContent = '';
                    data.rooms.forEach(r => {
                        const isAvail = (r.status === 'AVAILABLE');
                        htmlContent += `
                                    <div class="col-md-6">
                                        <div class="card h-100 rounded-3 ${isAvail ? 'border-primary bg-primary bg-opacity-10' : 'room-card-disabled'}">
                                            <div class="card-body p-3">
                                                <div class="d-flex justify-content-between align-items-center mb-3">
                                                    <h5 class="card-title ${isAvail ? 'text-primary' : 'text-secondary'} fw-bold mb-0">${r.name}</h5>
                                                    ${isAvail ? '<span class="badge bg-success rounded-pill px-2 py-1">Sẵn sàng</span>' : '<span class="badge bg-danger rounded-pill px-2 py-1">Bảo trì</span>'}
                                                </div>
                                                <div class="d-flex justify-content-between align-items-end">
                                                    <small class="text-muted mb-1"><i class="fa-solid fa-users me-1"></i> ${r.capacity} chỗ</small>
                                                    
                                                    ${isAvail ? '<button type="submit" name="room_id" value="' + r.id + '" class="btn btn-primary btn-sm fw-semibold shadow-sm px-3">Đặt ngay</button>' : '<button type="button" disabled class="btn btn-secondary btn-sm px-2">Đã khóa</button>'}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                `;
                    });
                    container.innerHTML = htmlContent;
                })
                .catch(error => {
                    console.error('Lỗi khi gọi API:', error);
                    alert('Có lỗi xảy ra khi kết nối đến máy chủ!');
                });
        });
    }
});