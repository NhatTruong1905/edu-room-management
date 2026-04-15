document.addEventListener('DOMContentLoaded', function () {
    let currentPage = 1;

    const dateInput = document.getElementById('date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.setAttribute('min', today);
        if (!dateInput.value) dateInput.value = today;
    }

    const startTimeSelect = document.getElementById('start_time');
    const endTimeSelect = document.getElementById('end_time');
    if (startTimeSelect && endTimeSelect) {
        startTimeSelect.addEventListener('change', function () {
            const startHour = parseInt(this.value.split(':')[0]);
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

    function loadRooms(page = 1) {
        currentPage = page;

        const date = document.getElementById('date').value;
        const start = document.getElementById('start_time').value;
        const end = document.getElementById('end_time').value;
        const cap = document.getElementById('capacity').value;

        if (!date || !start || !end) {
            alert("Vui lòng chọn đầy đủ Ngày và Khung giờ!");
            return;
        }

        const container = document.getElementById('room-list-container');
        const pagination = document.getElementById('pagination-container');

        container.innerHTML = '<div class="col-12 text-center py-5"><div class="spinner-border text-primary"></div></div>';

        const url = `/api/rooms?date=${date}&start_time=${start}&end_time=${end}&capacity=${cap}&page=${page}`;
        fetch(url).then(res => res.json()).then(data => {
            console.info(data)
            if (data.error) {
                alert(data.error);
                return;
            }

            document.getElementById('hidden_date').value = date;
            document.getElementById('hidden_start_time').value = start;
            document.getElementById('hidden_end_time').value = end;

            container.innerHTML = '';

            if (data.rooms.length === 0) {
                container.innerHTML = `
                        <div class="col-12 text-center py-5">
                            <h6 class="fw-bold text-dark"><i class="fa-regular fa-face-frown text-warning fs-1 mb-3 block"></i><br>Rất tiếc! Không có phòng khả dụng.</h6>
                        </div>`;
                if (pagination) pagination.innerHTML = '';
                return;
            }

            data.rooms.forEach(r => {
                const isAvail = (r.status === 'AVAILABLE');
                container.innerHTML += `
                        <div class="col-md-6">
                            <div class="card h-100 rounded-3 ${isAvail ? 'border-primary bg-primary bg-opacity-10' : 'room-card-disabled'}">
                                <div class="card-body p-3">
                                    <div class="d-flex justify-content-between align-items-center mb-3">
                                        <h5 class="card-title ${isAvail ? 'text-primary' : 'text-secondary'} fw-bold mb-0">${r.name}</h5>
                                        <span class="badge ${isAvail ? 'bg-success' : 'bg-danger'} rounded-pill px-2 py-1">
                                            ${isAvail ? 'Sẵn sàng' : 'Bảo trì'}
                                        </span>
                                    </div>
                                    <div class="d-flex justify-content-between align-items-end">
                                        <small class="text-muted mb-1"><i class="fa-solid fa-users me-1"></i> ${r.capacity} chỗ</small>
                                        ${isAvail ? `<button type="submit" name="room_id" value="${r.id}" class="btn btn-primary btn-sm fw-semibold shadow-sm px-3">Đặt ngay</button>`
                    : `<button type="button" disabled class="btn btn-secondary btn-sm px-2">Đã khóa</button>`}
                                    </div>
                                </div>
                            </div>
                        </div>`;
            });

            renderPagination(data.total_pages, data.current_page);
        }).catch(err => {
            console.error('Lỗi:', err);
            container.innerHTML = '<p class="text-center text-danger">Có lỗi xảy ra khi kết nối máy chủ!</p>'
        });
    }

    function renderPagination(totalPages, activePage) {
        const paginationContainer = document.getElementById('pagination-container');
        if (!paginationContainer) return;
        paginationContainer.innerHTML = '';
        if (totalPages <= 1) return;
        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement('li');
            li.className = `page-item ${i === activePage ? 'active' : ''}`;

            const a = document.createElement('a');
            a.className = 'page-link shadow-none';
            a.href = '#';
            a.innerText = i;

            a.addEventListener('click', function (e) {
                e.preventDefault();
                if (i !== currentPage) {
                    loadRooms(i);
                }
            });

            li.appendChild(a);
            paginationContainer.appendChild(li);
        }
    }

    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function (e) {
            e.preventDefault();
            loadRooms(1);
        });
    }

    const btnResetForm = document.getElementById('btn-reset-form');
    if (btnResetForm) {
        btnResetForm.addEventListener('click', function () {
            document.getElementById('search-form').reset();
            const today = new Date().toISOString().split('T')[0];
            dateInput.value = today;
        });
    }

    const btnClearRooms = document.getElementById('btn-clear-rooms');
    if (btnClearRooms) {
        btnClearRooms.addEventListener('click', function () {
            document.getElementById('room-list-container').innerHTML = `
                <div class="col-12 text-center py-5 text-muted">
                    <i class="fa-solid fa-calendar-day fs-1 mb-3 bg-light p-4 rounded-circle"></i>
                    <p>Vui lòng chọn thời gian bên trái để tìm phòng.</p>
                </div>`;

            const paginationContainer = document.getElementById('pagination-container');
            if (paginationContainer) paginationContainer.innerHTML = '';
            ['hidden_date', 'hidden_start_time', 'hidden_end_time'].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.value = '';
            });
        });
    }
});