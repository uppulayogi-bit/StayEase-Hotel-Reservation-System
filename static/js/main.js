
/* =====================================================
   STAYEASE - MAIN JAVASCRIPT
   Shared website interactions
===================================================== */

document.addEventListener("DOMContentLoaded", function () {

    /* ---------------------------------
       1. FLASH MESSAGE AUTO DISMISS
    --------------------------------- */

    const flashMessages = document.querySelectorAll(".flash-message");

    flashMessages.forEach(function (message) {

        // Dismiss button
        const closeButton = document.createElement("button");

        closeButton.type = "button";
        closeButton.textContent = "×";
        closeButton.setAttribute("aria-label", "Close message");

        closeButton.style.cssText = `
            float: right;
            border: none;
            background: transparent;
            font-size: 20px;
            font-weight: bold;
            cursor: pointer;
            margin-left: 15px;
        `;

        closeButton.addEventListener("click", function () {
            message.remove();
        });

        message.appendChild(closeButton);

    });


    /* ---------------------------------
       2. MOBILE NAVIGATION
    --------------------------------- */

    const navbar = document.querySelector(".navbar");
    const navLinks = document.querySelector(".nav-links");

    if (navbar && navLinks) {

        const menuButton = document.createElement("button");

        menuButton.type = "button";
        menuButton.className = "mobile-menu-button";
        menuButton.textContent = "☰";
        menuButton.setAttribute("aria-label", "Toggle navigation");

        menuButton.style.cssText = `
            display: none;
            background: transparent;
            border: none;
            color: #173D35;
            font-size: 25px;
            cursor: pointer;
        `;

        navbar.insertBefore(menuButton, navLinks);

        const mobileStyle = document.createElement("style");

        mobileStyle.textContent = `
            @media (max-width: 768px) {
                .mobile-menu-button {
                    display: block !important;
                }

                .navbar .nav-links.mobile-hidden {
                    display: none !important;
                }

                .navbar .nav-links.mobile-visible {
                    display: flex !important;
                    flex-direction: column;
                    align-items: center;
                    width: 100%;
                    padding: 15px 0;
                }
            }
        `;

        document.head.appendChild(mobileStyle);

        navLinks.classList.add("mobile-hidden");

        menuButton.addEventListener("click", function () {

            const isOpen = navLinks.classList.contains("mobile-visible");

            navLinks.classList.toggle("mobile-visible", !isOpen);
            navLinks.classList.toggle("mobile-hidden", isOpen);

            menuButton.textContent = isOpen ? "☰" : "✕";

        });

    }


    /* ---------------------------------
       3. BOOKING DATE VALIDATION
    --------------------------------- */

    const checkIn = document.querySelector("#check_in");
    const checkOut = document.querySelector("#check_out");

    if (checkIn && checkOut) {

        const today = new Date();

        const localToday = new Date(
            today.getTime() - today.getTimezoneOffset() * 60000
        ).toISOString().split("T")[0];

        checkIn.min = localToday;
        checkOut.min = localToday;

        checkIn.addEventListener("change", function () {

            checkOut.min = checkIn.value || localToday;

            if (checkOut.value && checkOut.value <= checkIn.value) {
                checkOut.value = "";
            }

        });

    }


    /* ---------------------------------
       4. CONFIRM BOOKING CANCELLATION
    --------------------------------- */

    const cancelForms = document.querySelectorAll(
        'form[action*="/booking/cancel/"]'
    );

    cancelForms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const confirmed = window.confirm(
                "Are you sure you want to cancel this booking?"
            );

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });


    /* ---------------------------------
       5. CONFIRM ADMIN STATUS UPDATES
    --------------------------------- */

    const statusForms = document.querySelectorAll(
        ".booking-status-form"
    );

    statusForms.forEach(function (form) {

        form.addEventListener("submit", function (event) {

            const selectedStatus = form.querySelector(
                'select[name="status"]'
            );

            if (!selectedStatus) {
                return;
            }

            const confirmed = window.confirm(
                "Update this booking status to " +
                selectedStatus.value + "?"
            );

            if (!confirmed) {
                event.preventDefault();
            }

        });

    });


    /* ---------------------------------
       6. IMAGE FALLBACK
    --------------------------------- */

    const images = document.querySelectorAll("img");

    images.forEach(function (img) {

        img.addEventListener("error", function () {

            if (img.dataset.fallbackUsed) {
                return;
            }

            img.dataset.fallbackUsed = "true";

            img.src =
                "https://placehold.co/900x600/F0EFE9/173D35?text=StayEase";

        });

    });


    /* ---------------------------------
       7. FORM SUBMISSION PROTECTION
    --------------------------------- */

    const forms = document.querySelectorAll(
        "form:not(.booking-status-form)"
    );

    forms.forEach(function (form) {

        form.addEventListener("submit", function () {

            const submitButton = form.querySelector(
                'button[type="submit"]'
            );

            if (!submitButton) {
                return;
            }

            if (!form.checkValidity()) {
                return;
            }

            // Prevent accidental repeated submissions.
            submitButton.dataset.originalText =
                submitButton.textContent;

            submitButton.disabled = true;
            submitButton.textContent = "Please wait...";

        });

    });


    /* ---------------------------------
       8. SMOOTH SCROLL
    --------------------------------- */

    document.querySelectorAll('a[href^="#"]').forEach(function (link) {

        link.addEventListener("click", function (event) {

            const targetId = link.getAttribute("href");

            if (!targetId || targetId === "#") {
                return;
            }

            const target = document.querySelector(targetId);

            if (target) {

                event.preventDefault();

                target.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            }

        });

    });

});
