// Small animation helper for smooth page feel.
window.addEventListener("DOMContentLoaded", () => {
    document.body.animate(
        [
            { opacity: 0, transform: "translateY(8px)" },
            { opacity: 1, transform: "translateY(0)" },
        ],
        {
            duration: 350,
            easing: "ease-out",
            fill: "forwards",
        }
    );
});


// Apply progress bar widths without inline styles.
document.querySelectorAll(".progress-fill[data-progress]").forEach((bar) => {
    const value = Number(bar.dataset.progress);
    const safeValue = Number.isFinite(value) ? Math.max(0, Math.min(100, value)) : 0;
    bar.style.width = `${safeValue}%`;
});
