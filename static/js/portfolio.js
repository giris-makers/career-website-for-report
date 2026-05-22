/* =========================================
   Portfolio – Vector Transformer JS
   ========================================= */

/* --- Animated dot canvas background --- */
(function () {
    const canvas = document.getElementById('dotCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');

    let W, H, dots = [], lines = [];
    const NUM_DOTS = 60;
    const CONNECT_DIST = 160;
    const COLORS = ['#818cf8', '#38bdf8', '#6ee7b7', '#fb923c'];

    function resize() {
        W = canvas.width  = canvas.offsetWidth;
        H = canvas.height = canvas.offsetHeight;
    }

    function randomDot() {
        return {
            x: Math.random() * W,
            y: Math.random() * H,
            vx: (Math.random() - 0.5) * 0.4,
            vy: (Math.random() - 0.5) * 0.4,
            r: Math.random() * 2 + 1,
            color: COLORS[Math.floor(Math.random() * COLORS.length)],
        };
    }

    function init() {
        resize();
        dots = Array.from({ length: NUM_DOTS }, randomDot);
    }

    function draw() {
        ctx.clearRect(0, 0, W, H);

        for (let i = 0; i < dots.length; i++) {
            const a = dots[i];
            for (let j = i + 1; j < dots.length; j++) {
                const b = dots[j];
                const dx = a.x - b.x, dy = a.y - b.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < CONNECT_DIST) {
                    ctx.strokeStyle = `rgba(129,140,248,${(1 - dist / CONNECT_DIST) * 0.2})`;
                    ctx.lineWidth = 0.8;
                    ctx.beginPath();
                    ctx.moveTo(a.x, a.y);
                    ctx.lineTo(b.x, b.y);
                    ctx.stroke();
                }
            }
        }

        dots.forEach(d => {
            ctx.beginPath();
            ctx.arc(d.x, d.y, d.r, 0, Math.PI * 2);
            ctx.fillStyle = d.color + '99';
            ctx.fill();

            d.x += d.vx;
            d.y += d.vy;
            if (d.x < 0 || d.x > W) d.vx *= -1;
            if (d.y < 0 || d.y > H) d.vy *= -1;
        });

        requestAnimationFrame(draw);
    }

    window.addEventListener('resize', resize);
    init();
    draw();
})();


/* --- Self-Attention demo --- */
(function () {
    const attnWeights = {
        0:  [0.9, 0.3, 0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1, 0.1],
        1:  [0.3, 0.9, 0.2, 0.3, 0.2, 0.4, 0.2, 0.7, 0.2, 0.2, 0.3],
        2:  [0.1, 0.3, 0.9, 0.5, 0.2, 0.3, 0.2, 0.2, 0.2, 0.2, 0.2],
        3:  [0.2, 0.4, 0.4, 0.9, 0.4, 0.7, 0.4, 0.3, 0.3, 0.2, 0.3],
        4:  [0.1, 0.1, 0.1, 0.2, 0.9, 0.4, 0.2, 0.2, 0.2, 0.1, 0.1],
        5:  [0.2, 0.3, 0.2, 0.6, 0.3, 0.9, 0.3, 0.3, 0.3, 0.2, 0.3],
        6:  [0.1, 0.3, 0.3, 0.4, 0.3, 0.4, 0.9, 0.5, 0.4, 0.3, 0.4],
        7:  [0.2, 0.8, 0.2, 0.3, 0.2, 0.3, 0.4, 0.9, 0.5, 0.4, 0.6],
        8:  [0.1, 0.2, 0.2, 0.3, 0.2, 0.3, 0.3, 0.5, 0.9, 0.4, 0.5],
        9:  [0.1, 0.2, 0.1, 0.2, 0.1, 0.2, 0.3, 0.4, 0.4, 0.9, 0.7],
        10: [0.1, 0.3, 0.2, 0.3, 0.1, 0.3, 0.4, 0.6, 0.5, 0.6, 0.9],
    };

    const words = document.querySelectorAll('.attn-word');

    function clearAttn() {
        words.forEach(w => {
            w.classList.remove('attn-active', 'attn-high', 'attn-medium', 'attn-low');
        });
    }

    words.forEach(word => {
        word.addEventListener('mouseenter', () => {
            clearAttn();
            const idx = parseInt(word.dataset.index);
            word.classList.add('attn-active');
            const weights = attnWeights[idx];
            if (!weights) return;
            words.forEach(w => {
                const j = parseInt(w.dataset.index);
                if (j === idx) return;
                const wt = weights[j];
                if (wt >= 0.6) w.classList.add('attn-high');
                else if (wt >= 0.3) w.classList.add('attn-medium');
                else w.classList.add('attn-low');
            });
        });

        word.addEventListener('mouseleave', clearAttn);
    });
})();


/* --- Copy code button --- */
function copyCode(btn) {
    const code = btn.closest('.code-block').querySelector('code');
    const text = code.innerText;
    navigator.clipboard.writeText(text).then(() => {
        btn.textContent = 'Copied!';
        setTimeout(() => { btn.textContent = 'Copy'; }, 2000);
    });
}


/* --- Scroll-reveal animation --- */
(function () {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(e => {
            if (e.isIntersecting) {
                e.target.style.opacity = '1';
                e.target.style.transform = 'translateY(0)';
                observer.unobserve(e.target);
            }
        });
    }, { threshold: 0.08 });

    document.querySelectorAll('.concept-card, .app-card, .timeline-item, .pf-stat').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(el);
    });
})();
