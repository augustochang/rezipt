document.addEventListener('DOMContentLoaded', function () {
    const taxInput = document.getElementById('taxInput');
    const tipInput = document.getElementById('tipInput');
    const automaticSubtotal = document.getElementById('automaticSubtotal');
    const automaticTotal = document.getElementById('automaticTotal');
    const subtotal = parseFloat('{{ misc_data.Subtotal }}');

    function updateAutomaticValues() {
        const tax = parseFloat(taxInput.value) || 0;
        const tip = parseFloat(tipInput.value) || 0;

        const total = subtotal + tax + tip;

        automaticSubtotal.textContent = subtotal.toFixed(2);
        automaticTotal.textContent = total.toFixed(2);
    }

    // Listen for changes in the tax and tip input fields
    taxInput.addEventListener('input', updateAutomaticValues);
    tipInput.addEventListener('input', updateAutomaticValues);

    // Initial update when the page loads
    updateAutomaticValues();
});