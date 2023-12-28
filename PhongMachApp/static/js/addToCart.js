function addToCart(id, name, medicine_unit){
    event.preventDefault()

    fetch('/api/add_medicine', {
        method: 'post',
        body: JSON.stringify({
            'id': id,
            'name': name,
            'medicine_unit': medicine_unit,
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
}