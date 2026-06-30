// Confirms before any "Delete" link runs, using the message in data-confirm.
// Works automatically on any link with class="btn-danger" and a data-confirm attribute —
// no need to touch this file when you rename entities, it just works.
document.addEventListener("click", function (event) {
    const link = event.target.closest("[data-confirm]");
    if (!link) return;

    const message = link.getAttribute("data-confirm") || "Are you sure?";
    if (!window.confirm(message)) {
        event.preventDefault();
    }
});
