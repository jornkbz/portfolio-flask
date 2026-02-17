document.addEventListener('DOMContentLoaded', () => {

    /* =========================================
       1. MATRIX RAIN EFFECT
       ========================================= */
    const initMatrixRain = () => {
        const canvas = document.getElementById('matrix-rain');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        const katakana = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン';
        const latin = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        const nums = '0123456789';
        const alphabet = katakana + latin + nums;

        const fontSize = 16;
        let columns = Math.floor(canvas.width / fontSize);

        const rainDrops = [];
        for (let x = 0; x < columns; x++) {
            rainDrops[x] = 1;
        }

        const draw = () => {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = '#0F0';
            ctx.font = fontSize + 'px monospace';

            for (let i = 0; i < rainDrops.length; i++) {
                const text = alphabet.charAt(Math.floor(Math.random() * alphabet.length));
                ctx.fillText(text, i * fontSize, rainDrops[i] * fontSize);

                if (rainDrops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                    rainDrops[i] = 0;
                }
                rainDrops[i]++;
            }
        };

        setInterval(draw, 30);

        window.addEventListener('resize', () => {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            columns = Math.floor(canvas.width / fontSize);
            // Reiniciar gotas
            for (let x = 0; x < columns; x++) {
                rainDrops[x] = 1;
            }
        });
    };

    initMatrixRain();

    /* =========================================
       2. AI WIDGET (ORACLE_SYSTEM)
       ========================================= */
    const aiWindow = document.getElementById('ai-window-v3');
    const aiInput = document.getElementById('ai-input-v3');
    const aiChatBox = document.getElementById('ai-chat-box-v3');
    const aiTriggerBtn = document.getElementById('ai-trigger-v3');
    
    // Close button might not have an ID, we'll delegate or select by class if possible
    // For robustness with existing HTML, we can add event listeners to elements if we find them
    const aiCloseBtns = document.querySelectorAll('.btn-close-custom'); // Assuming class exists
    const aiSendBtns = document.querySelectorAll('.btn-send-custom');

    const toggleWidgetV3 = () => {
        if (!aiWindow) return;
        if (aiWindow.classList.contains('d-none')) {
            aiWindow.classList.remove('d-none');
            setTimeout(() => aiInput.focus(), 100);
        } else {
            aiWindow.classList.add('d-none');
        }
    };

    if (aiTriggerBtn) {
        aiTriggerBtn.addEventListener('click', toggleWidgetV3);
    }
    
    aiCloseBtns.forEach(btn => {
        btn.addEventListener('click', toggleWidgetV3);
    });

    const appendAiMessage = (sender, text, cssClass) => {
        const msgId = 'msg-' + Date.now();
        const div = document.createElement('div');
        div.className = 'mb-2 small';
        div.id = msgId;
        div.innerHTML = `<span class="${cssClass} fw-bold">[${sender}]:</span> <span class="text-white">${text}</span>`;
        aiChatBox.appendChild(div);
        aiChatBox.scrollTop = aiChatBox.scrollHeight;
        return msgId;
    };

    const typeWriterAi = (text) => {
        const div = document.createElement('div');
        div.className = 'mb-2 small';
        div.innerHTML = `<span class="text-info fw-bold">[ORACLE]:</span> <span class="text-white ai-response-text"></span>`;
        aiChatBox.appendChild(div);

        const span = div.querySelector('.ai-response-text');
        let i = 0;
        const interval = setInterval(() => {
            span.textContent += text.charAt(i);
            aiChatBox.scrollTop = aiChatBox.scrollHeight;
            i++;
            if (i >= text.length) clearInterval(interval);
        }, 10);
    };

    const sendAiMessageV3 = () => {
        if (!aiInput) return;
        const text = aiInput.value.trim();
        if (!text) return;

        appendAiMessage('VISITOR', text, 'text-warning');
        aiInput.value = '';

        const loadingId = appendAiMessage('SYSTEM', 'Procesando...', 'text-success blinking-cursor');

        fetch('/ask_oracle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ question: text })
        })
        .then(response => response.json())
        .then(data => {
            const loadingMsg = document.getElementById(loadingId);
            if (loadingMsg) loadingMsg.remove();
            typeWriterAi(data.answer);
        })
        .catch(err => {
            console.error(err);
            const loadingMsg = document.getElementById(loadingId);
            if (loadingMsg) loadingMsg.remove();
            appendAiMessage('ERROR', 'Sin conexión.', 'text-danger');
        });
    };

    aiSendBtns.forEach(btn => {
        btn.addEventListener('click', sendAiMessageV3);
    });

    if (aiInput) {
        aiInput.addEventListener("keypress", function(event) {
            if (event.key === "Enter") sendAiMessageV3();
        });
    }


    /* =========================================
       3. CONTACT FORM ANIMATION
       ========================================= */
    // Previously window.initiateContactProtocol
    const contactTrigger = document.getElementById('contact-trigger');
    if (contactTrigger) {
        contactTrigger.addEventListener('click', () => {
            contactTrigger.classList.add('d-none');

            const loader = document.getElementById('terminal-loader');
            if (loader) loader.classList.remove('d-none');

            const lines = [
                { id: 'log-line-1', text: '> Resolving host: jose-cabezas.server...', delay: 500 },
                { id: 'log-line-2', text: '> Handshaking with SSL certificate...', delay: 1500 },
                { id: 'log-line-3', text: '> Encrypting transmission channel [2048-bit]...', delay: 2500 },
                { id: 'log-line-4', text: '> ACCESS GRANTED. LOAD FORM.', delay: 3500 }
            ];

            lines.forEach(line => {
                setTimeout(() => {
                    const el = document.getElementById(line.id);
                    if (el) el.innerText = line.text;
                }, line.delay);
            });

            setTimeout(() => {
                if (loader) loader.classList.add('d-none');
                const formWrapper = document.getElementById('contact-form-wrapper');
                if (formWrapper) formWrapper.classList.remove('d-none');
            }, 4500);
        });
    }

    /* =========================================
       4. HOME: PILL FILTERS
       ========================================= */
    const pillWrappers = document.querySelectorAll('.pill-wrapper');
    const stackStatusText = document.getElementById('stack-status');
    const techGrid = document.getElementById('tech-grid');

    if (pillWrappers.length > 0 && techGrid) {
        pillWrappers.forEach(wrapper => {
            wrapper.addEventListener('click', function() {
                // Determine color based on child class or custom attribute if we added one.
                // Or deduce from onclick attribute in original HTML (which we are removing).
                // We will add data-color attributes to the HTML to make this clean.
                const color = this.getAttribute('data-color'); 
                if (color) filterStack(color);
            });
        });
    }

    function filterStack(color) {
        const items = document.querySelectorAll('.tech-item');
        
        // Fade out
        techGrid.style.opacity = '0';

        setTimeout(() => {
            items.forEach(item => {
                const itemCat = item.getAttribute('data-cat');
                if (color === 'all' || itemCat === color) {
                    item.style.display = '';
                } else {
                    item.style.display = 'none';
                }
            });

            if (stackStatusText) {
                if (color === 'blue') {
                    stackStatusText.innerHTML = '> Reality accepted. Loading Development & Data Environment...';
                    stackStatusText.style.color = '#00BFFF';
                } else if (color === 'red') {
                    stackStatusText.innerHTML = '> Breaking the simulation. Accessing SysAdmin & Security Infrastructure...';
                    stackStatusText.style.color = '#FF4500';
                } else {
                    stackStatusText.innerHTML = '> Merging realities. Full Stack capabilities loaded.';
                    stackStatusText.style.color = '#DA70D6';
                }
            }

            // Fade in
            techGrid.style.opacity = '1';
        }, 200);
    }

    /* =========================================
       5. HOME: TERMINAL INTERACTION
       ========================================= */
    const terminalOutput = document.getElementById('terminal-output');
    const typedCommandSpan = document.getElementById('typed-command');
    const terminalWindow = document.querySelector('.terminal-window'); // Note: ai-window also has this class, might be ambiguous?
    // In home.html logic: const terminalWindow = document.querySelector('.terminal-window');
    // But base.html has <div id="ai-window-v3" class="terminal-window">.
    // If we are on home page, document.querySelector('.terminal-window') might pick the AI one if it appears first in DOM?
    // Actually the AI widget is in base.html which is loaded. The home content is in block content.
    // The AI widget is usually at the bottom. The terminal section is in the middle.
    // However, to be safe, we should use a more specific selector for the main terminal if possible, or ID.
    // Looking at home.html: <div class="col-lg-9 ..."><div class="terminal-window h-100" ...>
    // It doesn't have a unique ID. I should add one. Let's assume I'll add ID="main-terminal-window".

    const commandMap = {
        'education': { cmd: 'cat education.txt', tplId: 'tpl-education' },
        'capabilities': { cmd: 'cat capabilities.json', tplId: 'tpl-capabilities' },
        'career': { cmd: 'tail -f career.log', tplId: 'tpl-career' },
        'projects': { cmd: 'git remote show origin', tplId: 'tpl-projects' }
    };

    let isExecuting = false;

    // Command buttons
    const cmdButtons = document.querySelectorAll('.btn-matrix-command');
    cmdButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            // We need to know which command. 
            // We'll rely on onclick removal and adding data-cmd attribute in HTML.
            const cmdKey = this.getAttribute('data-cmd');
            if (cmdKey) executeCommand(cmdKey);
        });
    });

    const clearBtn = document.getElementById('terminal-clear-btn'); // Will add this ID
    // fallback if we can't find by ID (if I forget to add it), try to find by text content? 
    // better to ensure ID is added.

    if (document.querySelector('.text-danger.btn-matrix-command')) {
         // This is a hacky selector for the clear button if ID is missing
    }
    
    // Actually, I can selector by onclick content... no.
    // I will definitely add IDs/Attributes in HTML.

    function executeCommand(commandKey) {
        if (isExecuting) return;
        isExecuting = true;

        const commandData = commandMap[commandKey];
        if (!commandData) { isExecuting = false; return; }
        
        const commandText = commandData.cmd;
        const templateId = commandData.tplId;

        let i = 0;
        if (typedCommandSpan) typedCommandSpan.textContent = '';
        
        const typeInterval = setInterval(() => {
            if (typedCommandSpan && i < commandText.length) {
                typedCommandSpan.textContent += commandText.charAt(i);
                i++;
            } else {
                clearInterval(typeInterval);
                setTimeout(() => processCommandOutput(commandText, templateId), 500);
            }
        }, 50);
    }

    function processCommandOutput(commandText, templateId) {
        if (!terminalOutput) return;

        const previousPrompt = document.createElement('div');
        previousPrompt.innerHTML = `<span class="text-success me-2">user@jose-portfolio:~$</span><span class="text-white">${commandText}</span>`;
        terminalOutput.appendChild(previousPrompt);

        if (typedCommandSpan) typedCommandSpan.textContent = '';

        const template = document.getElementById(templateId);
        if (template) {
            const clone = template.content.cloneNode(true);
            terminalOutput.appendChild(clone);
        }

        // We need the specific terminal window for scrolling
        // I will add ID "main-terminal-window" to the HTML
        const mainTermWindow = document.getElementById('main-terminal-window');
        if (mainTermWindow) {
            mainTermWindow.scrollTop = mainTermWindow.scrollHeight;
        } else if (terminalWindow) {
             // Fallback
             terminalWindow.scrollTop = terminalWindow.scrollHeight;
        }
        
        isExecuting = false;
    }

    // Clear terminal logic
    const clearTerminalBtn = document.getElementById('terminal-clear-btn');
    if (clearTerminalBtn) {
        clearTerminalBtn.addEventListener('click', () => {
            if (terminalOutput) {
                terminalOutput.innerHTML = '<div class="terminal-line text-muted">Terminal cleared. Session reset.</div><div class="terminal-line mb-3">------------------------------------------------------------</div>';
            }
        });
    }
    
    /* Copy Email Logic */
    const copyEmailBtn = document.getElementById('copy-email-btn');
    if (copyEmailBtn) {
        copyEmailBtn.addEventListener('click', () => {
            const email = "josecabezaspulgarin@gmail.com";
            const icon = document.getElementById('copy-icon');

            navigator.clipboard.writeText(email).then(() => {
                if (icon) {
                    icon.classList.remove('fa-copy');
                    icon.classList.add('fa-check');
                    setTimeout(() => {
                        icon.classList.remove('fa-check');
                        icon.classList.add('fa-copy');
                    }, 2000);
                }
            }).catch(err => {
                console.error('Error al copiar: ', err);
            });
        });
    }

});
