document.addEventListener('DOMContentLoaded', function () {
        let currentPage = 1;

        const dateInput = document.getElementById('date');
        const startTimeSelect = document.getElementById('start_time');
        const endTimeSelect = document.getElementById('end_time');

        const now = new Date();
        const todayStr = now.getFullYear() + '-' +
            String(now.getMonth() + 1).padStart(2, '0') + '-' +
            String(now.getDate()).padStart(2, '0');
        if (dateInput) {
            dateInput.setAttribute('min', todayStr);
            if (!dateInput.value) dateInput.value = todayStr;
        }

        function updateStartTimeOptions() {
            if (!dateInput || !startTimeSelect) return;
            const selectedDate = dateInput.value;
            const currentHour = new Date().getHours();

            Array.from(startTimeSelect.options).forEach(option => {
                if (option.value === "") return;
                const optionHour = parseInt(option.value.split(':')[0]);
                if (selectedDate === todayStr) {
                    if (optionHour <= currentHour) {
                        option.disabled = true;
                        option.style.display = 'none';
                    } else {
                        option.disabled = false;
                        option.style.display = 'block';
                    }
                } else {
                    option.disabled = false;
                    option.style.display = 'block';
                }
            });

            const selectedOption = startTimeSelect.options[startTimeSelect.selectedIndex];
            if (selectedOption && selectedOption.disabled) {
                startTimeSelect.value = "";
                if (endTimeSelect) endTimeSelect.value = "";
            }
        }

        if (dateInput) {
            dateInput.addEventListener('change', updateStartTimeOptions);
            updateStartTimeOptions();
        }

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
                    let cardClass = '';
                    let titleClass = '';
                    let statusBadge = '';
                    let actionBtn = '';

                    if (r.status === 'AVAILABLE') {
                        cardClass = 'border-primary bg-primary bg-opacity-10';
                        titleClass = 'text-primary';
                        statusBadge = '<span class="badge bg-success rounded-pill px-2 py-1">Sẵn sàng</span>';
                        actionBtn = `<button type="submit" name="room_id" value="${r.id}" class="btn btn-primary btn-sm fw-semibold shadow-sm px-3">Đặt ngay</button>`;
                    } else if (r.status === 'BOOKED') {
                        cardClass = 'room-card-disabled shadow-none';
                        titleClass = 'text-secondary';
                        statusBadge = '<span class="badge bg-warning text-dark rounded-pill px-2 py-1">Kín lịch</span>';
                        actionBtn = `<button type="button" disabled class="btn btn-secondary btn-sm px-2">Đã có người đặt</button>`;
                    } else {
                        cardClass = 'room-card-disabled shadow-none';
                        titleClass = 'text-secondary';
                        statusBadge = '<span class="badge bg-danger rounded-pill px-2 py-1">Bảo trì</span>';
                        actionBtn = `<button type="button" disabled class="btn btn-secondary btn-sm px-2">Đã khóa</button>`;
                    }

                    container.innerHTML += `
                    <div class="col-md-6">
                        <div class="card h-100 rounded-3 ${cardClass}">
                            <div class="card-body p-3">
                                <div class="d-flex justify-content-between align-items-center mb-3">
                                    <h5 class="card-title ${titleClass} fw-bold mb-0">${r.name}</h5>
                                    ${statusBadge}
                                </div>
                                <div class="d-flex justify-content-between align-items-end">
                                    <small class="text-muted"><i class="fa-solid fa-users me-1"></i> ${r.capacity} chỗ</small>
                                    ${actionBtn}
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
                updateStartTimeOptions();

                document.getElementById('room-list-container').innerHTML = `
                <div class="col-12 text-center py-5 text-muted">
                    <i class="fa-solid fa-calendar-day fs-1 mb-3 bg-light p-4 rounded-circle"></i>
                    <p>Vui lòng chọn thời gian bên trái để tìm phòng.</p>
                </div>`;
                const paginationContainer = document.getElementById('pagination-container');
                if (paginationContainer) paginationContainer.innerHTML = '';
            });
        }

        const btnClearRooms = document.getElementById('btn-clear-rooms');
        if (btnClearRooms) {
            btnClearRooms.addEventListener('click', function () {
                const date = document.getElementById('date').value;
                const start = document.getElementById('start_time').value;
                const end = document.getElementById('end_time').value;

                if (date && start && end) {
                    const icon = this.querySelector('i');
                    if (icon) icon.classList.add('fa-spin');
                    loadRooms(currentPage);
                    setTimeout(() => {
                        if (icon) icon.classList.remove('fa-spin');
                    }, 800);
                } else {
                    document.getElementById('room-list-container').innerHTML = `
                    <div class="col-12 text-center py-5 text-muted">
                        <i class="fa-solid fa-calendar-day fs-1 mb-3 bg-light p-4 rounded-circle"></i>
                        <p>Vui lòng chọn thời gian bên trái để tìm phòng.</p>
                    </div>`;
                    const paginationContainer = document.getElementById('pagination-container');
                    if (paginationContainer) paginationContainer.innerHTML = '';
                }
            });
        }

        loadUserBookings();

    }
)
document.addEventListener('DOMContentLoaded', function () {
    const btnReloadBookings = document.getElementById('btn-reload-bookings');

    if (btnReloadBookings) {
        btnReloadBookings.addEventListener('click', function () {
            const icon = this.querySelector('i');
            icon.classList.add('fa-spin');
            loadUserBookings();
            setTimeout(() => {
                icon.classList.remove('fa-spin');
            }, 1000);
        });
    }
});
window.loadUserBookings = function () {
    const tbody = document.getElementById('user-bookings-list');
    if (!tbody) return;
    fetch('/api/bookings').then(res => res.json()).then(data => {
        tbody.innerHTML = '';

        if (!data.bookings || data.bookings.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4">Bạn chưa có lịch đặt phòng nào.</td></tr>';
            return;
        }

        data.bookings.forEach(b => {
            let statusHtml = '';
            let actionHtml = '';

            if (b.status === 'UPCOMING') {
                statusHtml = '<span class="badge bg-light text-success border px-2 py-1">Sắp diễn ra</span>';
                actionHtml = `<button type="button" class="btn btn-outline-danger btn-sm fw-semibold rounded-pill px-3" onclick="cancelBooking(${b.id})">Hủy</button>`;
            } else if (b.status === 'ONGOING') {
                statusHtml = '<span class="badge bg-light text-primary border px-2 py-1">Đang diễn ra</span>';
                actionHtml = `<button type="button" class="btn btn-secondary btn-sm fw-semibold rounded-pill px-3" disabled>Đang dùng</button>`;
            } else if (b.status === 'CANCELED') {
                statusHtml = '<span class="badge bg-light text-secondary border px-2 py-1">Đã hủy</span>';
                actionHtml = `<button type="button" class="btn btn-secondary btn-sm fw-semibold rounded-pill px-3" disabled>Đã hủy</button>`;
            } else if (b.status === 'COMPLETED') {
                statusHtml = '<span class="badge bg-light text-muted border px-2 py-1">Đã kết thúc</span>';
                actionHtml = `<button type="button" class="btn btn-secondary btn-sm fw-semibold rounded-pill px-3" disabled>Hết hạn</button>`;
            }

            tbody.innerHTML += `
                        <tr class="booking-row">
                            <td class="ps-4">
                                <input class="form-check-input row-checkbox" type="checkbox" value="${b.id}">
                            </td>
                            <td class="py-3 fw-semibold text-dark">${b.name_room} <br>
                                <span class="text-muted small fw-normal">${b.capacity} chỗ</span>
                            </td>
                            <td class="py-3">${b.date}<br>
                                <span class="fw-bold text-primary">${b.time_range}</span>
                            </td>
                            <td class="py-3">${statusHtml}</td>
                            <td class="text-end pe-4 py-3">${actionHtml}</td>
                        </tr>
                    `;
        });
        const checkAllBtn = document.getElementById('check-all-bookings');
        const hideBtn = document.getElementById('btn-hide-selected');
        const rowCheckboxes = document.querySelectorAll('.row-checkbox');

        if (checkAllBtn) checkAllBtn.checked = false;
        if (hideBtn) hideBtn.classList.add('d-none');

        function toggleHideButton() {
            const anyChecked = document.querySelector('.row-checkbox:checked');
            if (anyChecked) {
                hideBtn.classList.remove('d-none');
            } else {
                hideBtn.classList.add('d-none');
            }
        }

        if (checkAllBtn) {
            checkAllBtn.addEventListener('change', function () {
                rowCheckboxes.forEach(cb => cb.checked = this.checked);
                toggleHideButton();
            });
        }

        rowCheckboxes.forEach(cb => {
            cb.addEventListener('change', function () {
                toggleHideButton();
                if (!this.checked) checkAllBtn.checked = false;
            });
        });

        if (hideBtn) {
            hideBtn.onclick = function () {
                document.querySelectorAll('.row-checkbox:checked').forEach(cb => {
                    cb.closest('tr').remove();
                });
                this.classList.add('d-none');
                checkAllBtn.checked = false;

                if (document.querySelectorAll('.booking-row').length === 0) {
                    tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-4">Đã ẩn toàn bộ danh sách hiển thị. Tải lại trang để xem lại.</td></tr>';
                }
            };
        }

    }).catch(err => {
        console.error("Lỗi khi tải lịch đặt phòng:", err);
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-danger py-4">Lỗi kết nối máy chủ!</td></tr>';
    });
}
document.addEventListener('DOMContentLoaded', function () {
    const collapseEl = document.getElementById('bookingTableCollapse');
    const toggleIcon = document.getElementById('toggle-icon');

    if (collapseEl && toggleIcon) {
        collapseEl.addEventListener('show.bs.collapse', function () {
            toggleIcon.classList.replace('fa-chevron-down', 'fa-chevron-up');
        });
        collapseEl.addEventListener('hide.bs.collapse', function () {
            toggleIcon.classList.replace('fa-chevron-up', 'fa-chevron-down');
        });
    }
});

window.cancelBooking = function (id) {
    if (!confirm("Bạn có chắc chắn muốn hủy lịch đặt phòng này không?")) {
        return;
    }
    fetch(`/api/bookings/${id}`, {method: 'POST'})
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                alert(data.message);
                loadUserBookings();
                location.reload();
            } else {
                alert("Lỗi: " + data.message);
            }
        })
        .catch(err => {
            console.error('Lỗi khi hủy:', err);
            alert("Lỗi kết nối đến máy chủ!");
        });
};