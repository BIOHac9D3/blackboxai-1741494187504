let orderItemIndex = 0;

// Order Modal Functions
function openOrderModal(orderId = null) {
    const modal = document.getElementById('order-modal');
    const title = document.getElementById('modal-title');
    const form = document.getElementById('order-form');
    
    modal.classList.remove('hidden');
    
    if (orderId) {
        title.textContent = 'Edit Order';
        
        // Show loading state
        form.innerHTML = `
            <div class="flex items-center justify-center h-64">
                <div class="text-center">
                    <i class="fas fa-spinner fa-spin fa-2x text-blue-500 mb-4"></i>
                    <p class="text-gray-600">Loading order data...</p>
                </div>
            </div>
        `;
        
        // Fetch order data
        fetch(`/admin/orders/${orderId}`)
            .then(response => {
                if (!response.ok) throw new Error('Failed to load order');
                return response.json();
            })
            .then(order => {
                // Restore form content and populate data
                form.innerHTML = document.getElementById('order-form-template').innerHTML;
                
                document.getElementById('order-id').value = order.id;
                document.getElementById('status').value = order.status;
                document.getElementById('payment_status').value = order.payment_status;
                document.getElementById('shipping_address').value = order.shipping_address;
                document.getElementById('billing_address').value = order.billing_address;
                document.getElementById('total_amount').value = order.total_amount;
                
                // Add order items
                order.items.forEach(item => addOrderItem(item));
                updateTotalAmount();
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Failed to load order data', 'error');
                closeOrderModal();
            });
    } else {
        title.textContent = 'Add Order';
        form.reset();
        document.getElementById('order-items').innerHTML = '';
        addOrderItem(); // Add one empty item by default
    }
}

function closeOrderModal() {
    document.getElementById('order-modal').classList.add('hidden');
}

function addOrderItem(item = null) {
    const template = document.getElementById('order-item-template');
    const container = document.getElementById('order-items');
    const clone = template.content.cloneNode(true);
    
    // Replace INDEX placeholder with actual index
    clone.querySelectorAll('[name*="INDEX"]').forEach(element => {
        element.name = element.name.replace('INDEX', orderItemIndex);
    });
    
    // Add event listeners
    const productSelect = clone.querySelector('.product-select');
    const quantityInput = clone.querySelector('.quantity-input');
    const priceInput = clone.querySelector('.price-input');
    
    productSelect.addEventListener('change', function() {
        const option = this.options[this.selectedIndex];
        const price = option.dataset.price || 0;
        priceInput.value = price;
        updateItemSubtotal(this.closest('.order-item'));
    });
    
    quantityInput.addEventListener('input', function() {
        updateItemSubtotal(this.closest('.order-item'));
    });
    
    // Populate data if editing
    if (item) {
        productSelect.value = item.product_id;
        quantityInput.value = item.quantity;
        priceInput.value = item.price;
        updateItemSubtotal(clone.querySelector('.order-item'));
    }
    
    container.appendChild(clone);
    orderItemIndex++;
    updateTotalAmount();
}

function removeOrderItem(button) {
    const item = button.closest('.order-item');
    item.remove();
    updateTotalAmount();
}

function updateItemSubtotal(item) {
    const quantity = parseFloat(item.querySelector('.quantity-input').value) || 0;
    const price = parseFloat(item.querySelector('.price-input').value) || 0;
    const subtotal = quantity * price;
    item.querySelector('.subtotal-input').value = subtotal.toFixed(2);
    updateTotalAmount();
}

function updateTotalAmount() {
    const subtotals = Array.from(document.querySelectorAll('.subtotal-input'))
        .map(input => parseFloat(input.value) || 0);
    const total = subtotals.reduce((sum, subtotal) => sum + subtotal, 0);
    document.getElementById('total-amount').textContent = total.toFixed(2);
    document.getElementById('total_amount').value = total;
}

function saveOrder() {
    const form = document.getElementById('order-form');
    const formData = new FormData(form);
    const orderId = formData.get('id');
    const saveButton = document.querySelector('button[onclick="saveOrder()"]');
    
    // Show loading state
    const originalContent = saveButton.innerHTML;
    saveButton.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Saving...';
    saveButton.disabled = true;

    // Clear previous errors
    document.querySelectorAll('[id$="-error"]').forEach(el => {
        el.classList.add('hidden');
        el.textContent = '';
    });

    const url = orderId ? `/admin/orders/${orderId}` : '/admin/orders';
    const method = orderId ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrf_token')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showToast(data.message, 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            if (data.errors) {
                Object.entries(data.errors).forEach(([field, errors]) => {
                    const errorDiv = document.getElementById(`${field}-error`);
                    if (errorDiv) {
                        errorDiv.textContent = errors.join(', ');
                        errorDiv.classList.remove('hidden');
                    }
                });
            }
            showToast(data.message || 'Failed to save order', 'error');
            saveButton.innerHTML = originalContent;
            saveButton.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('An error occurred while saving the order', 'error');
        saveButton.innerHTML = originalContent;
        saveButton.disabled = false;
    });
}

function deleteOrder(orderId) {
    if (confirm('Are you sure you want to delete this order?
