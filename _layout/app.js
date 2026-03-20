// выбор валюты
const dropdown = document.getElementById('currencyDropdown');
const selected = dropdown.querySelector('.dropdown-selected');
const arrow = selected.querySelector('.arrow');
const items = dropdown.querySelectorAll('.dropdown-item');

selected.addEventListener('click', () => {
    dropdown.classList.toggle('open');
});

items.forEach(item => {
    item.addEventListener('click', () => {
        const code = item.getAttribute('data-code');
        const flag = item.getAttribute('data-flag');
        selected.querySelector('.flag').src = flag;
        selected.querySelector('.code').textContent = code;
        dropdown.classList.remove('open');
    });
});

// Закрытие при клике вне меню
document.addEventListener('click', (e) => {
    if (!dropdown.contains(e.target)) {
        dropdown.classList.remove('open');
    }
});

// многоуровневое меню
document.querySelectorAll('.menu-item[data-toggle]').forEach(item => {
    item.addEventListener('click', () => {
        const targetId = item.getAttribute('data-toggle');
        const submenu = document.getElementById(targetId);
        const arrow = item.querySelector('.arrow');
        submenu.classList.toggle('open');
        arrow.classList.toggle('open');
    });
});


// таблица
const table = document.getElementById("teamTable");

table.addEventListener("click", (e) => {
    const btn = e.target.closest(".toggle-btn");
    if (!btn) return;

    const row = btn.closest("tr");
    const id = row.dataset.id;
    const level = parseInt(row.dataset.level);

    const isOpen = btn.textContent === "−";
    btn.textContent = isOpen ? "+" : "−";

    toggleChildren(id, !isOpen);
});

function toggleChildren(parentId, show) {
    const rows = document.querySelectorAll(`[data-parent='${parentId}']`);
    rows.forEach((row) => {
        if (show) {
            row.classList.remove("hidden-row");
        } else {
            row.classList.add("hidden-row");
            // рекурсивно скрываем дочерние элементы
            const childId = row.dataset.id;
            toggleChildren(childId, false);
            const childBtn = row.querySelector(".toggle-btn");
            if (childBtn) childBtn.textContent = "+";
        }
    });
}

// tabs


const dropdown2 = document.getElementById('currencyDropdown2');
const selected2 = dropdown.querySelector('.dropdown-selected');
const arrow2 = selected.querySelector('.arrow');
const items2 = dropdown.querySelectorAll('.dropdown-item');

selected2.addEventListener('click', () => {
    dropdown2.classList.toggle('open');
});


