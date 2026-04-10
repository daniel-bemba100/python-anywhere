// Chat JS with Emoji Support
document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    const messagesContainer = document.getElementById('messages');
    const form = document.getElementById('message-form');
    const input = document.getElementById('message-input');
    const emojiBtn = document.getElementById('emoji-btn');
    const emojiPicker = document.getElementById('emoji-picker');
    const userListEl = document.getElementById('user-list');
    const refreshBtnEl = document.getElementById('refresh-users');
    const mobileRefreshBtn = document.getElementById('mobile-refresh');
    const mobileUserListEl = document.getElementById('mobile-user-list');
    const clearBtn = document.getElementById('clear-messages');
    
    if (refreshBtnEl) refreshBtnEl.onclick = refreshUsers;
    if (mobileRefreshBtn) mobileRefreshBtn.onclick = refreshUsers;
    function refreshUsers() { socket.emit('get_online'); }

    // Emoji picker toggle
    if (emojiBtn && emojiPicker) {
        emojiBtn.onclick = function() {
            emojiPicker.classList.toggle('hidden');
        };
        // Close picker on outside click
        document.addEventListener('click', function(e) {
            if (!emojiBtn.contains(e.target) && !emojiPicker.contains(e.target)) {
                emojiPicker.classList.add('hidden');
            }
        });
        // Insert emoji on select
        emojiPicker.addEventListener('emoji-click', function(e) {
            input.value += e.detail.unicode;
            input.focus();
            emojiPicker.classList.add('hidden');
        });
    }

    // Send raw unicode message (fix img tags)
    form.onsubmit = function(e) {
        e.preventDefault();
        let msg = input.value.trim();
        if (msg) {
            socket.emit('send_message', { message: msg });
            input.value = '';
            emojiPicker.classList.add('hidden');
        }
    };
    input.onkeypress = function(e) {
        if (e.key === 'Enter') form.dispatchEvent(new Event('submit'));
    };

    // Events
    socket.on('new_message', addMessage);
    socket.on('online_list', updateUserList);
    socket.on('user_status_change', refreshUsers);
    socket.on('status', (data) => console.log('Status:', data.msg));
    socket.on('error', (data) => console.error('Socket error:', data.msg));
    socket.on('connect', function() {
        console.log('✅ Socket connected!');
        socket.emit('get_online');
    });
    socket.on('disconnect', () => console.log('Disconnected'));
    
    // Reduced polling
    setInterval(() => socket.emit('get_online'), 30000);

    input.focus();

    // Clear messages button
    if (clearBtn) {
        clearBtn.onclick = function() {
            messagesContainer.innerHTML = '<div class="text-center text-gray-500 py-12 animate-pulse">Cleared messages! Start chatting...</div>';
        };
    }

    // Message render with twemoji (client-side only)
    function addMessage(data) {
        const div = document.createElement('div');
        div.className = 'message p-4 rounded-2xl bg-white/80 dark:bg-slate-800/80 shadow-md animate-fade-in max-w-[75%]';
        const escapedMsg = escapeHtml(data.message);
        div.innerHTML = `
            <div class="font-bold text-indigo-600 dark:text-indigo-400 flex items-center gap-1">● ${escapeHtml(data.user)}</div>
            <div class="text-lg twemoji" id="msg-${Date.now()}">${escapedMsg}</div>
            <div class="text-xs text-gray-500 mt-1">${data.timestamp}</div>
        `;
        messagesContainer.appendChild(div);
        // Parse twemoji after DOM insert
        setTimeout(() => twemoji.parse(div.querySelector('.twemoji')), 10);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        const welcome = messagesContainer.querySelector('.animate-pulse');
        if (welcome) welcome.remove();
    }

    function updateUserList(data) {
        console.log('Online list:', data.users);
        if (userListEl) {
            userListEl.innerHTML = data.users.map(u => 
                `<div class="p-2 bg-green-100/50 dark:bg-green-900/30 rounded-lg hover:bg-green-200 dark:hover:bg-green-800 text-green-800 dark:text-green-200 font-medium truncate flex items-center gap-2">
                    ● ${escapeHtml(u.name)}
                </div>`
            ).join('') || '<div class="text-gray-400 italic">No one online</div>';
        }
        if (mobileUserListEl) {
            mobileUserListEl.innerHTML = data.users.map(u => 
                `<div class="p-2 bg-green-100/50 dark:bg-green-900/30 rounded-lg hover:bg-green-200 dark:hover:bg-green-800 text-green-800 dark:text-green-200 font-medium truncate flex items-center gap-2">
                    ● ${escapeHtml(u.name)}
                </div>`
            ).join('') || '<div class="text-gray-400 italic">No one online</div>';
        }
    }

    // XSS escape helper
    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '<',
            '>': '>',
            '"': '"',
            "'": '&#039;'
        };
        return text.replace(/[&<>\"']/g, m => map[m]);
    }

    // Twemoji ready
    twemoji.parse(document.body);
});

