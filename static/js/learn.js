/* ============================================================
   LearnHub – Main JS
   ============================================================ */

// ── Nav scroll effect ──────────────────────────────────────
const nav = document.getElementById('lhNav');
if (nav) {
    window.addEventListener('scroll', () => {
        nav.classList.toggle('scrolled', window.scrollY > 20);
    });
}

// ── Mobile hamburger ───────────────────────────────────────
const hamburger   = document.getElementById('lhHamburger');
const mobileMenu  = document.getElementById('lhMobileMenu');
if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', () => {
        mobileMenu.classList.toggle('open');
        const spans = hamburger.querySelectorAll('span');
        hamburger.classList.toggle('is-open');
        if (hamburger.classList.contains('is-open')) {
            spans[0].style.transform = 'rotate(45deg) translateY(7px)';
            spans[1].style.opacity = '0';
            spans[2].style.transform = 'rotate(-45deg) translateY(-7px)';
        } else {
            spans.forEach(s => { s.style.transform = ''; s.style.opacity = ''; });
        }
    });
}

// ── Auto-dismiss flash messages ────────────────────────────
document.querySelectorAll('.lh-flash').forEach(flash => {
    setTimeout(() => {
        flash.style.transition = 'opacity .4s, transform .4s';
        flash.style.opacity = '0';
        flash.style.transform = 'translateY(-8px)';
        setTimeout(() => flash.remove(), 400);
    }, 5000);
});

// ── Password toggle ────────────────────────────────────────
function togglePw(id) {
    const input = document.getElementById(id);
    if (!input) return;
    input.type = input.type === 'password' ? 'text' : 'password';
}

// ── Scroll-reveal ──────────────────────────────────────────
function initReveal() {
    const targets = document.querySelectorAll(
        '.lh-course-card, .lh-cat-card, .lh-step, .lh-testimonial, ' +
        '.lh-diff-card, .lh-team-card, .lh-astat, .lh-dash-stat, .lh-enrolled-card'
    );
    const io = new IntersectionObserver((entries) => {
        entries.forEach((e, i) => {
            if (e.isIntersecting) {
                setTimeout(() => {
                    e.target.style.opacity = '1';
                    e.target.style.transform = 'translateY(0)';
                }, i * 60);
                io.unobserve(e.target);
            }
        });
    }, { threshold: 0.08 });

    targets.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(18px)';
        el.style.transition = 'opacity .45s ease, transform .45s ease';
        io.observe(el);
    });
}

// ── Progress bar animation ─────────────────────────────────
function animateProgressBars() {
    document.querySelectorAll('.lh-progress-bar').forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0';
        setTimeout(() => { bar.style.width = width; }, 300);
    });
}

// ── Hero counter animation ─────────────────────────────────
function animateCounters() {
    document.querySelectorAll('.lh-dash-stat-num').forEach(el => {
        const rawText = el.textContent.trim();
        const numMatch = rawText.match(/[\d.]+/);
        if (!numMatch) return;
        const target = parseFloat(numMatch[0]);
        const suffix = rawText.replace(numMatch[0], '').trim();
        const isFloat = rawText.includes('.');
        let start = 0;
        const step = target / 40;
        const interval = setInterval(() => {
            start = Math.min(start + step, target);
            el.textContent = (isFloat ? start.toFixed(1) : Math.floor(start)) + suffix;
            if (start >= target) clearInterval(interval);
        }, 30);
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initReveal();
    animateProgressBars();
    animateCounters();
});
