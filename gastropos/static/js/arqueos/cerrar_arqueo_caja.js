document.addEventListener('DOMContentLoaded', (event) => {
    const updateTotal = () => {
        let total = 0;
        total += parseInt(document.getElementById('id_monedas_50').value || 0) * 50;
        total += parseInt(document.getElementById('id_monedas_100').value || 0) * 100;
        total += parseInt(document.getElementById('id_monedas_200').value || 0) * 200;
        total += parseInt(document.getElementById('id_monedas_500').value || 0) * 500;
        total += parseInt(document.getElementById('id_monedas_1000').value || 0) * 1000;
        total += parseInt(document.getElementById('id_billetes_2000').value || 0) * 2000;
        total += parseInt(document.getElementById('id_billetes_5000').value || 0) * 5000;
        total += parseInt(document.getElementById('id_billetes_10000').value || 0) * 10000;
        total += parseInt(document.getElementById('id_billetes_20000').value || 0) * 20000;
        total += parseInt(document.getElementById('id_billetes_50000').value || 0) * 50000;
        total += parseInt(document.getElementById('id_billetes_100000').value || 0) * 100000;

        document.getElementById('total_monedas_billetes').value = total.toFixed(2);
    };

    // Set default values to 0 if fields are empty
    const setDefaultValues = () => {
        const fields = [
            'id_monedas_50', 'id_monedas_100', 'id_monedas_200', 
            'id_monedas_500', 'id_monedas_1000', 
            'id_billetes_2000', 'id_billetes_5000', 
            'id_billetes_10000', 'id_billetes_20000', 
            'id_billetes_50000', 'id_billetes_100000'
        ];
        
        fields.forEach(field => {
            const input = document.getElementById(field);
            if (!input.value) {
                input.value = 0;
            }
        });
    };

    // Initialize the input values
    setDefaultValues();
    updateTotal();

    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', updateTotal);
    });

    document.querySelectorAll('button[data-action]').forEach(button => {
        button.addEventListener('click', function() {
            const action = this.getAttribute('data-action');
            const target = document.querySelector(this.getAttribute('data-target'));
            let currentValue = parseInt(target.value || 0);
            if (action === 'increase') {
                target.value = currentValue + 1;
            } else if (action === 'decrease') {
                target.value = Math.max(currentValue - 1, 0);
            }
            updateTotal();
        });
    });

    // Initialize the total again to ensure it reflects the defaults
    updateTotal();
});
