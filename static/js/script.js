document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Enable Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });
    
    // Automatically close alerts after 5 seconds
    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(function(alert) {
            if (alert) {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        });
    }, 5000);
    
    // Form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Attendance check-in/check-out time auto-update
    var currentTimeElement = document.getElementById('current-time');
    if (currentTimeElement) {
        function updateTime() {
            var now = new Date();
            var hours = now.getHours().toString().padStart(2, '0');
            var minutes = now.getMinutes().toString().padStart(2, '0');
            var seconds = now.getSeconds().toString().padStart(2, '0');
            currentTimeElement.textContent = hours + ':' + minutes + ':' + seconds;
        }
        updateTime();
        setInterval(updateTime, 1000);
    }
    
    // Membership expiry warning
    var expiryElements = document.querySelectorAll('.membership-expiry');
    if (expiryElements.length > 0) {
        expiryElements.forEach(function(element) {
            var expiryDate = new Date(element.dataset.expiry);
            var today = new Date();
            var diffTime = expiryDate - today;
            var diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays <= 0) {
                element.classList.add('text-danger');
                element.textContent = 'Expired';
            } else if (diffDays <= 7) {
                element.classList.add('text-warning');
                element.textContent = 'Expires in ' + diffDays + ' days';
            }
        });
    }
    
    // Class capacity progress bars
    var capacityBars = document.querySelectorAll('.capacity-bar');
    if (capacityBars.length > 0) {
        capacityBars.forEach(function(bar) {
            var enrolled = parseInt(bar.dataset.enrolled);
            var capacity = parseInt(bar.dataset.capacity);
            var percentage = (enrolled / capacity) * 100;
            
            bar.style.width = percentage + '%';
            
            if (percentage >= 90) {
                bar.classList.add('bg-danger');
            } else if (percentage >= 70) {
                bar.classList.add('bg-warning');
            } else {
                bar.classList.add('bg-success');
            }
        });
    }
    
    // Search functionality for tables
    var searchInput = document.getElementById('table-search');
    if (searchInput) {
        searchInput.addEventListener('keyup', function() {
            var filter = searchInput.value.toUpperCase();
            var table = document.querySelector('.searchable-table');
            var tr = table.getElementsByTagName('tr');
            
            for (var i = 1; i < tr.length; i++) {
                var found = false;
                var td = tr[i].getElementsByTagName('td');
                
                for (var j = 0; j < td.length; j++) {
                    var txtValue = td[j].textContent || td[j].innerText;
                    if (txtValue.toUpperCase().indexOf(filter) > -1) {
                        found = true;
                        break;
                    }
                }
                
                if (found) {
                    tr[i].style.display = '';
                } else {
                    tr[i].style.display = 'none';
                }
            }
        });
    }
});