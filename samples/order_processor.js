function processOrder(order) {
    let total = 0;
    for (let item of order.items) {
        total += item.price * item.quantity;
    }

    if (total > 100) {
        total = total * 0.9; // 10% discount
    }

    return total;
}

function formatCurrency(amount) {
    return "$" + amount.toFixed(2);
}
