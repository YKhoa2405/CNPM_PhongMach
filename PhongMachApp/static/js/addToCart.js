function addToCart(id, name, medicineUnit_id){
    event.preventDefault()

    fetch('/api/add_medicine', {
        method: 'put',
        body: JSON.stringify({
            'id': id,
            'name': name,
            'medicineUnit_id': medicineUnit_id
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(function(res){
        console.info(res)
        return res.json()
    }).then(function(data){
        console.info(data)
        location.reload();
    }).catch(function(err){
        console.error(err)
    })
}

function deleteCart(id) {
    if (confirm("Bạn chắn chắn xóa thuốc này khỏi đơn?") == true) {
        fetch('/api/delete_cart/' + id, {
            method: 'delete',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(function (res) {
            console.info(res);
            return res.json();
        }).then(function (data) {
            console.info(data);
            // Sau khi xóa thành công, làm mới trang
            location.reload();
        }).catch(function (err) {
            console.error(err);
        });
    }
}
