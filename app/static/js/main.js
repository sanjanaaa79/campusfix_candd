// CampusFix Frontend JavaScript
document.addEventListener("DOMContentLoaded", function () {
  // 1. Initialize Lucide Icons
  if (typeof lucide !== "undefined") {
    lucide.createIcons();
  }

  // 2. Auto-dismiss alerts after 5 seconds
  const alerts = document.querySelectorAll(".alert:not(.alert-permanent)");
  alerts.forEach(function (alert) {
    setTimeout(function () {
      try {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      } catch (e) {
        alert.remove();
      }
    }, 5000);
  });

  // 3. Form validation helper
  const forms = document.querySelectorAll(".needs-validation");
  Array.from(forms).forEach(function (form) {
    form.addEventListener(
      "submit",
      function (event) {
        if (!form.checkValidity()) {
          event.preventDefault();
          event.stopPropagation();
        }
        form.classList.add("was-validated");
      },
      false
    );
  });

  // 4. Quick filter auto-submit on change
  const filterSelects = document.querySelectorAll(".auto-filter-select");
  filterSelects.forEach(function (select) {
    select.addEventListener("change", function () {
      if (this.form) {
        this.form.submit();
      }
    });
  });
});
