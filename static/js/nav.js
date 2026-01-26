// Mobile navigation (hamburger) for portfolio + dashboard navs
// - Enhances existing markup; no HTML changes required besides including this script.
// - Adds accessible toggle buttons and handles close on outside click / Esc / link click.

(function () {
  function uniqueId(prefix, index) {
    return `${prefix}-${index}-${Math.random().toString(16).slice(2)}`;
  }

  function createHamburgerButton(className, openLabel, closeLabel) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = className;
    btn.setAttribute('aria-label', openLabel);
    btn.setAttribute('aria-expanded', 'false');
    btn.dataset.openLabel = openLabel;
    btn.dataset.closeLabel = closeLabel;

    // 3 bars
    for (let i = 0; i < 3; i++) {
      const bar = document.createElement('span');
      bar.className = 'nav-toggle-bar';
      btn.appendChild(bar);
    }

    return btn;
  }

  function wireMenu({
    rootEl,
    menuEl,
    toggleEl,
    openClass,
  }) {
    const menuId = menuEl.id || uniqueId('nav-menu', 0);
    menuEl.id = menuId;
    toggleEl.setAttribute('aria-controls', menuId);

    const close = () => {
      rootEl.classList.remove(openClass);
      toggleEl.setAttribute('aria-expanded', 'false');
      if (toggleEl.dataset.openLabel) toggleEl.setAttribute('aria-label', toggleEl.dataset.openLabel);
    };

    const open = () => {
      rootEl.classList.add(openClass);
      toggleEl.setAttribute('aria-expanded', 'true');
      if (toggleEl.dataset.closeLabel) toggleEl.setAttribute('aria-label', toggleEl.dataset.closeLabel);
    };

    const toggle = () => {
      const isOpen = rootEl.classList.contains(openClass);
      if (isOpen) close();
      else open();
    };

    toggleEl.addEventListener('click', toggle);

    // Close when a nav link is clicked
    menuEl.addEventListener('click', (e) => {
      const target = e.target;
      if (target && target.closest && target.closest('a')) close();
    });

    // Close on Escape
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') close();
    });

    // Close on outside click
    document.addEventListener('click', (e) => {
      if (!rootEl.classList.contains(openClass)) return;
      if (!rootEl.contains(e.target)) close();
    });

    // Close when resizing up to desktop
    window.addEventListener('resize', () => {
      // If the toggle is not visible, ensure the menu isn't "stuck" open.
      const style = window.getComputedStyle(toggleEl);
      if (style.display === 'none') close();
    });
  }

  function initPortfolioNavs() {
    const navs = Array.from(document.querySelectorAll('nav.portfolio-nav'));
    navs.forEach((nav, i) => {
      if (nav.querySelector('.portfolio-nav-toggle')) return; // already enhanced

      const container = nav.querySelector('.container') || nav;
      const menu = nav.querySelector('ul');
      if (!menu) return;

      const btn = createHamburgerButton('portfolio-nav-toggle', 'Open menu', 'Close menu');
      const menuId = menu.id || uniqueId('portfolio-menu', i);
      menu.id = menuId;
      btn.setAttribute('aria-controls', menuId);

      // Put the toggle just before the menu
      container.insertBefore(btn, menu);

      wireMenu({
        rootEl: nav,
        menuEl: menu,
        toggleEl: btn,
        openClass: 'nav-open',
      });
    });
  }

  function initDashboardNavs() {
    const headers = Array.from(document.querySelectorAll('header.dashboard-header'));
    headers.forEach((header, i) => {
      const nav = header.querySelector('nav.dashboard-nav');
      if (!nav) return;
      if (header.querySelector('.dashboard-nav-toggle')) return; // already enhanced

      const container = header.querySelector('.container') || header;

      const btn = createHamburgerButton('dashboard-nav-toggle', 'Open menu', 'Close menu');
      const navId = nav.id || uniqueId('dashboard-menu', i);
      nav.id = navId;
      btn.setAttribute('aria-controls', navId);

      // Insert toggle before nav
      container.insertBefore(btn, nav);

      wireMenu({
        rootEl: header,
        menuEl: nav,
        toggleEl: btn,
        openClass: 'nav-open',
      });
    });
  }

  function init() {
    initPortfolioNavs();
    initDashboardNavs();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();

