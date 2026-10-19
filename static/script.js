
const earningsInput = document.getElementById("earnings");
const petrolInput = document.getElementById("petrol");
const otherInput = document.getElementById("other_expenses");
const liveProfit = document.getElementById("liveProfit");

function formatRupees(amount) {
    return amount.toLocaleString("en-IN", {
        style: "currency",
        currency: "INR",
        minimumFractionDigits: 2
    });
}

function calculateDailyProfit() {
    const earnings = Number(earningsInput.value) || 0;
    const petrol = Number(petrolInput.value) || 0;
    const other = Number(otherInput.value) || 0;

    const profit = earnings - petrol - other;

    liveProfit.textContent = formatRupees(profit);
    liveProfit.style.color = profit < 0 ? "#d64251" : "#6957e8";
}

[earningsInput, petrolInput, otherInput].forEach(input => {
    input.addEventListener("input", calculateDailyProfit);
});

calculateDailyProfit();

// Search the records currently displayed in the table.
const searchInput = document.getElementById("searchInput");
const noResults = document.getElementById("noResults");

searchInput.addEventListener("input", function () {
    const query = this.value.toLowerCase().trim();
    const rows = document.querySelectorAll("#recordsTable tbody tr");

    let visibleRows = 0;

    rows.forEach(row => {
        // Ignore the placeholder row shown when no records exist.
        if (row.querySelector(".delete-form") === null) {
            return;
        }

        const matches = row.textContent.toLowerCase().includes(query);

        row.hidden = !matches;

        if (matches) {
            visibleRows++;
        }
    });

    noResults.hidden = query === "" || visibleRows > 0;
});

// Confirm before deleting a record.
document.querySelectorAll(".delete-form").forEach(form => {
    form.addEventListener("submit", function (event) {
        if (!confirm("Do you want to delete this daily record?")) {
            event.preventDefault();
        }
    });
});

// Fade out success/error notifications.
document.querySelectorAll(".alert").forEach(message => {
    setTimeout(() => {
        message.style.transition = "opacity .5s";
        message.style.opacity = "0";

        setTimeout(() => message.remove(), 500);
    }, 3500);
});
