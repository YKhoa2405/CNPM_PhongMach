var selectedDate = ''; // Đây là biến lưu trữ ngày khám được chọn

document.addEventListener("DOMContentLoaded", function() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('ngayKham').setAttribute('min', today);

});


function deletePatient(patientId) {
    const confirmation = confirm('Bạn có chắc chắn muốn xóa bệnh nhân này không?');

    if (confirmation) {
        fetch(`/patients/${patientId}/delete`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ patientId: patientId })
        })
        .then(response => {
            location.reload(); // Load lại trang sau khi xóa thành công
        })
        .catch(error => console.error('There was an error!', error));
    }
}

function filterByDate() {
    var selectedDate = document.getElementById('ngayKham').value;

    fetch(`/get_patients_by_date?ngayKham=${selectedDate}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Phản hồi từ mạng không hợp lệ');
            }
            return response.json();
        })
        .then(data => {
            // Xử lý dữ liệu trả về ở đây (nếu cần)
            console.log(data);
            // Ví dụ: Hiển thị dữ liệu lên bảng hoặc thực hiện các thao tác khác
        })
        .catch(error => console.error('There was an error!', error));

    window.location.href = `/get_patients_by_date?ngayKham=${selectedDate}`;
}

//document.addEventListener('DOMContentLoaded', function() {
//    var ngayKhamInput = document.getElementById('ngayKham');
//    if (selectedDate !== '') {
//        ngayKhamInput.value = selectedDate;
//    }
//
//    ngayKhamInput.addEventListener('change', function() {
//        selectedDate = this.value;
//    });
//});
//function createAppointmentList() {
//    var selectedDate = document.getElementById('ngayKham').value;
//
//    if (!selectedDate) {
//        alert('Vui lòng chọn ngày khám.');
//        return; // Không làm gì cả nếu ngày khám trống
//    }
//
//    // Tiếp tục với việc gửi dữ liệu lên server nếu ngày khám đã được chọn
//    // Gọi hàm hoặc yêu cầu fetch tại đây
//}
//function getAppointmentDate() {
//    var ngayKhamInput = document.getElementById('ngayKham');
//    var selectedDate = ngayKhamInput.value;
//    // Sử dụng biến selectedDate cho việc xử lý tiếp theo
//    console.log("Ngày khám được chọn:", selectedDate);
//    return selectedDate;
//}

//
////XÓA Appointment khỏi session chỗ trang danh sách khám theo ngày
//function deletePatientFromSession(rowId) {
//    console.log("Appointment ID to delete:", rowId);
//    var confirmed = confirm("Bạn có chắc chắn muốn xóa bệnh nhân này không?");
//    if (confirmed) {
//        $.ajax({
//            url: '/delete_from_session/' + rowId,
//            type: 'GET',
//            success: function(response) {
//                if (response.success) {
//                    var rowToDelete = document.getElementById('row_' + rowId);
//                    if (rowToDelete) {
//                        rowToDelete.remove(); // Xóa hàng khỏi DOM
//                    }
//                } else {
//                    alert('Không thể xóa bệnh nhân khỏi session.');
//                }
//            },
//            error: function() {
//                alert('Đã xảy ra lỗi khi thực hiện yêu cầu xóa.');
//            }
//        });
//    }
//}
