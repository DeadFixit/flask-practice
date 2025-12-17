(function() {
    const body = document.body;
    const toggleButton = document.getElementById('toggle-accessibility');
    const panel = document.getElementById('accessibility-panel');

    const palettes = {
        gost: {
            bg: '#000000',
            card: '#0f1115',
            text: '#f4f5f7',
            muted: '#d3d6dc',
            primary: '#ffd200',
            primaryContrast: '#000000',
            accent: '#3ea6ff',
            border: '#2b2f36',
        },
        blue: {
            bg: '#0b1a2c',
            card: '#102542',
            text: '#e8f0ff',
            muted: '#c1c9d6',
            primary: '#5bd1ff',
            primaryContrast: '#02101f',
            accent: '#b6fffa',
            border: '#1f3352',
        },
        sepia: {
            bg: '#f4eddc',
            card: '#fff7e6',
            text: '#2d2415',
            muted: '#4f4023',
            primary: '#a25b00',
            primaryContrast: '#fff4e1',
            accent: '#7a5c3f',
            border: '#d2c2a4',
        }
    };

    const defaultPrefs = {
        mode: 'standard',
        fontScale: 0,
        color: 'gost',
        line: 'normal'
    };

    const normalizePrefs = (raw) => {
        if (!raw) return { ...defaultPrefs };
        try {
            const parsed = JSON.parse(raw);
            return { ...defaultPrefs, ...parsed };
        } catch (e) {
            // backward compatibility with older string value
            if (raw === 'accessible') {
                return { ...defaultPrefs, mode: 'accessible' };
            }
            return { ...defaultPrefs };
        }
    };

    let prefs = normalizePrefs(localStorage.getItem('cgh-theme'));

    const applyColors = (palette) => {
        body.style.setProperty('--bg', palette.bg);
        body.style.setProperty('--card', palette.card);
        body.style.setProperty('--text', palette.text);
        body.style.setProperty('--muted', palette.muted);
        body.style.setProperty('--primary', palette.primary);
        body.style.setProperty('--primary-contrast', palette.primaryContrast);
        body.style.setProperty('--accent', palette.accent);
        body.style.setProperty('--border', palette.border);
    };

    const resetColors = () => {
        const defaults = getComputedStyle(document.documentElement);
        ['--bg','--card','--text','--muted','--primary','--primary-contrast','--accent','--border'].forEach((key) => {
            body.style.setProperty(key, defaults.getPropertyValue(key));
        });
    };

    const applyFonts = () => {
        const base = 16 + prefs.fontScale * 2;
        body.style.setProperty('--font-size-base', `${base}px`);
        const line = prefs.line === 'normal' ? 1.6 : prefs.line === 'wide' ? 1.8 : 2.0;
        body.style.setProperty('--line-height', line);
    };

    const setTheme = (mode) => {
        prefs.mode = mode;
        body.classList.remove('theme-standard', 'theme-accessible');
        body.classList.add(mode === 'accessible' ? 'theme-accessible' : 'theme-standard');
        toggleButton.textContent = mode === 'accessible' ? 'Стандартная версия' : 'Версия для слабовидящих';
        toggleButton.setAttribute('aria-expanded', mode === 'accessible');

        if (mode === 'accessible') {
            panel?.removeAttribute('hidden');
            const palette = palettes[prefs.color] || palettes.gost;
            applyColors(palette);
        } else {
            panel?.setAttribute('hidden', 'hidden');
            resetColors();
            body.style.removeProperty('--font-size-base');
            body.style.removeProperty('--line-height');
        }
        applyFonts();
        localStorage.setItem('cgh-theme', JSON.stringify(prefs));
    };

    setTheme(prefs.mode);

    toggleButton?.addEventListener('click', () => {
        const next = body.classList.contains('theme-accessible') ? 'standard' : 'accessible';
        setTheme(next);
    });

    panel?.addEventListener('click', (event) => {
        const target = event.target;
        if (!(target instanceof HTMLElement)) return;
        const font = target.getAttribute('data-font');
        const color = target.getAttribute('data-color');
        const line = target.getAttribute('data-line');
        let changed = false;

        if (font !== null) {
            prefs.fontScale = Number(font);
            applyFonts();
            changed = true;
        }
        if (color) {
            prefs.color = color;
            applyColors(palettes[prefs.color] || palettes.gost);
            changed = true;
        }
        if (line) {
            prefs.line = line;
            applyFonts();
            changed = true;
        }
        if (changed) {
            localStorage.setItem('cgh-theme', JSON.stringify(prefs));
        }
    });
})();
