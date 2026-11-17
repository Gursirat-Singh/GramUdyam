/**
 * Progressive Enhancement Vanilla JavaScript (main.js)
 * All business logic, calculations, and security validation operate 100% server-side in Django.
 * This script provides touch interaction, scroll effects, alert dismissal, and accessibility.
 */
document.addEventListener("DOMContentLoaded", function () {
  // 1. Page load progress bar
  var loadBar = document.getElementById("pageLoadBar");
  if (loadBar) {
    loadBar.style.width = "100%";
    setTimeout(function () {
      loadBar.style.opacity = "0";
      setTimeout(function () {
        loadBar.style.display = "none";
      }, 400);
    }, 250);
  }

  // 2. Mobile navigation toggle
  var menuToggle = document.getElementById("mobile-menu-toggle");
  var navLinks = document.getElementById("primary-nav-links");
  if (menuToggle && navLinks) {
    menuToggle.addEventListener("click", function () {
      var expanded = menuToggle.getAttribute("aria-expanded") === "true";
      menuToggle.setAttribute("aria-expanded", String(!expanded));
      navLinks.classList.toggle("open");
    });

    // Close mobile nav when clicking outside
    document.addEventListener("click", function (e) {
      if (!menuToggle.contains(e.target) && !navLinks.contains(e.target) && navLinks.classList.contains("open")) {
        menuToggle.setAttribute("aria-expanded", "false");
        navLinks.classList.remove("open");
      }
    });
  }

  // 3. Navbar scroll effect (glassmorphism on scroll)
  var siteHeader = document.querySelector(".site-header");
  if (siteHeader) {
    var checkScroll = function () {
      if (window.scrollY > 20) {
        siteHeader.setAttribute("data-scrolled", "true");
      } else {
        siteHeader.removeAttribute("data-scrolled");
      }
    };
    window.addEventListener("scroll", checkScroll, { passive: true });
    checkScroll();
  }

  // 4. Alert close buttons and auto-dismiss
  var alerts = document.querySelectorAll(".alert");
  alerts.forEach(function (alert) {
    // Add close button if not already present
    if (!alert.querySelector(".alert-close-btn")) {
      var closeBtn = document.createElement("button");
      closeBtn.className = "alert-close-btn";
      closeBtn.type = "button";
      closeBtn.setAttribute("aria-label", "Close notification");
      closeBtn.innerHTML = "&times;";
      closeBtn.style.cssText = "float:right; background:transparent; border:none; font-size:1.25rem; line-height:1; cursor:pointer; color:inherit; opacity:0.7; margin-left:0.5rem;";
      closeBtn.addEventListener("click", function () {
        alert.style.transition = "opacity 0.25s ease, transform 0.25s ease";
        alert.style.opacity = "0";
        alert.style.transform = "translateY(-6px)";
        setTimeout(function () {
          alert.remove();
        }, 260);
      });
      alert.prepend(closeBtn);
    }

    // Auto-dismiss success messages after 5 seconds
    if (alert.classList.contains("alert-success")) {
      setTimeout(function () {
        if (document.body.contains(alert)) {
          alert.style.transition = "opacity 0.4s ease, transform 0.4s ease";
          alert.style.opacity = "0";
          alert.style.transform = "translateY(-6px)";
          setTimeout(function () {
            if (document.body.contains(alert)) {
              alert.remove();
            }
          }, 420);
        }
      }, 5000);
    }
  });

  // 5. Progressive loading state on form submission to prevent double-clicks
  var forms = document.querySelectorAll("form[data-loading-text]");
  forms.forEach(function (form) {
    form.addEventListener("submit", function (e) {
      // Don't disable if form is already prevented
      if (e.defaultPrevented) return;
      var submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn && !submitBtn.disabled) {
        var loadingText = form.getAttribute("data-loading-text") || "Processing...";
        submitBtn.setAttribute("data-original-text", submitBtn.innerHTML);
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span style="display:inline-block; animation:spin 1s linear infinite;">⏳</span> ' + loadingText;
        // Safety timeout: re-enable after 15 seconds if page doesn't unload
        setTimeout(function () {
          submitBtn.disabled = false;
          if (submitBtn.getAttribute("data-original-text")) {
            submitBtn.innerHTML = submitBtn.getAttribute("data-original-text");
          }
        }, 15000);
      }
    });
  });

  // 6. Print button trigger
  var printButtons = document.querySelectorAll("[data-action='print-page']");
  printButtons.forEach(function (btn) {
    btn.addEventListener("click", function (e) {
      e.preventDefault();
      window.print();
    });
  });

  // 7. Password visibility toggle
  var passwordFields = document.querySelectorAll('input[type="password"]');
  passwordFields.forEach(function (field) {
    var wrapper = field.parentElement;
    if (wrapper && !wrapper.querySelector(".toggle-pwd-btn")) {
      var toggleBtn = document.createElement("button");
      toggleBtn.type = "button";
      toggleBtn.className = "toggle-pwd-btn";
      toggleBtn.setAttribute("aria-label", "Toggle password visibility");
      toggleBtn.innerHTML = "👁️";
      toggleBtn.style.cssText = "position:absolute; right:12px; top:50%; transform:translateY(-50%); background:transparent; border:none; cursor:pointer; font-size:1rem; padding:4px;";
      wrapper.style.position = "relative";
      wrapper.appendChild(toggleBtn);

      toggleBtn.addEventListener("click", function () {
        if (field.type === "password") {
          field.type = "text";
          toggleBtn.innerHTML = "🔒";
          toggleBtn.setAttribute("aria-label", "Hide password");
        } else {
          field.type = "password";
          toggleBtn.innerHTML = "👁️";
          toggleBtn.setAttribute("aria-label", "Show password");
        }
      });
    }
  });

  // 8. IntersectionObserver for smooth scroll animations
  if ("IntersectionObserver" in window) {
    var animObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("visible");
          animObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll(".animate-on-scroll").forEach(function (el) {
      animObserver.observe(el);
    });
  } else {
    // Fallback for browsers without IntersectionObserver
    document.querySelectorAll(".animate-on-scroll").forEach(function (el) {
      el.classList.add("visible");
    });
  }
});
