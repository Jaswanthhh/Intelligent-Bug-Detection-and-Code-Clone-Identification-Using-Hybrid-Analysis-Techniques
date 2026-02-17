function calculateCartTotal(cart) {
    // Clone of processOrder
    let sum = 0;
    cart.items.forEach(product => {
        sum += product.price * product.quantity;
    });

    // Apply discount for large orders
    if (sum > 100) {
        sum *= 0.9;
    }

    return sum;
}

const toMoneyString = (val) => {
    return "$" + val.toFixed(2);
}
