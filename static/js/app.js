// HotelPilot Web Interface JavaScript

let currentAgent = 'ops_copilot';
let scenarios = {};

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    checkStatus();
    loadScenarios();
    setupEventListeners();

    // Check status every 30 seconds
    setInterval(checkStatus, 30000);
});

// Setup event listeners
function setupEventListeners() {
    // Agent selection
    document.querySelectorAll('.agent-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            selectAgent(btn.dataset.agent);
        });
    });

    // Scenario buttons
    document.querySelectorAll('.scenario-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            loadScenario(btn.dataset.scenario);
        });
    });

    // Send button
    document.getElementById('send-btn').addEventListener('click', sendMessage);

    // Enter key to send (Shift+Enter for new line)
    document.getElementById('user-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
}

// Check API status
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();

        const statusEl = document.getElementById('status');
        const statusIndicator = statusEl.querySelector('.status-indicator');
        const statusText = statusEl.querySelector('.status-text');

        if (data.api_configured) {
            statusIndicator.style.background = '#10b981';
            statusText.textContent = 'Connected';
        } else {
            statusIndicator.style.background = '#f59e0b';
            statusText.textContent = 'No API Key';
        }
    } catch (error) {
        const statusEl = document.getElementById('status');
        const statusIndicator = statusEl.querySelector('.status-indicator');
        const statusText = statusEl.querySelector('.status-text');
        statusIndicator.style.background = '#ef4444';
        statusText.textContent = 'Offline';
    }
}

// Load scenarios
async function loadScenarios() {
    try {
        const response = await fetch('/api/scenarios');
        scenarios = await response.json();
    } catch (error) {
        console.error('Failed to load scenarios:', error);
    }
}

// Select agent
function selectAgent(agentId) {
    currentAgent = agentId;

    // Update UI
    document.querySelectorAll('.agent-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.agent === agentId);
    });

    // Update chat header
    const agentBtn = document.querySelector(`[data-agent="${agentId}"]`);
    const icon = agentBtn.querySelector('.agent-icon').textContent;
    const name = agentBtn.querySelector('.agent-name').textContent;

    document.getElementById('current-agent-icon').textContent = icon;
    document.getElementById('current-agent-name').textContent = name;

    // Add system message
    addMessage('system', `Switched to ${name}. How can I help you?`);
}

// Load scenario
function loadScenario(scenarioId) {
    const scenario = scenarios[scenarioId];
    if (!scenario) return;

    // Select the appropriate agent
    if (scenario.agent) {
        selectAgent(scenario.agent);
    }

    // Fill the input
    document.getElementById('user-input').value = scenario.prompt;

    // Focus on input
    document.getElementById('user-input').focus();
}

// Send message
async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();

    if (!message) return;

    // Disable send button
    const sendBtn = document.getElementById('send-btn');
    sendBtn.disabled = true;

    // Add user message
    addMessage('user', message);

    // Clear input
    input.value = '';

    // Show loading
    const loadingId = addMessage('ai', '<div class="loading"></div>', true);

    const startTime = Date.now();

    try {
        const response = await fetch('/api/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                agent: currentAgent,
                input: message
            })
        });

        const data = await response.json();

        // Remove loading message
        removeMessage(loadingId);

        if (data.success) {
            // Add AI response
            addMessage('ai', formatResponse(data.response));

            // Update response time
            const responseTime = Date.now() - startTime;
            document.getElementById('response-time').textContent = `${responseTime}ms`;
        } else {
            addMessage('system', `Error: ${data.error || 'Failed to get response'}`);
        }
    } catch (error) {
        removeMessage(loadingId);
        addMessage('system', `Error: ${error.message}`);
    } finally {
        sendBtn.disabled = false;
        input.focus();
    }
}

// Add message to chat
function addMessage(type, content, isHtml = false) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    const messageId = 'msg-' + Date.now();

    messageDiv.id = messageId;
    messageDiv.className = `message ${type}`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (isHtml) {
        contentDiv.innerHTML = content;
    } else {
        contentDiv.innerHTML = `<p>${escapeHtml(content)}</p>`;
    }

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;

    return messageId;
}

// Remove message
function removeMessage(messageId) {
    const message = document.getElementById(messageId);
    if (message) {
        message.remove();
    }
}

// Format AI response
function formatResponse(text) {
    // First, clean up any HTML entities
    text = text.replace(/&lt;/g, '<')
               .replace(/&gt;/g, '>')
               .replace(/&quot;/g, '"')
               .replace(/&#39;/g, "'")
               .replace(/&amp;/g, '&');

    // Remove unwanted HTML tags but keep the content
    text = text.replace(/<br\s*\/?>/gi, '\n')
               .replace(/<\/?strong>/gi, '**')
               .replace(/<\/?em>/gi, '*')
               .replace(/<\/?p>/gi, '\n')
               .replace(/<[^>]*>/g, '');

    // Now format the cleaned text
    let formatted = '';
    const lines = text.split('\n');

    for (let line of lines) {
        line = line.trim();
        if (!line) continue;

        // Headers (lines ending with :)
        if (line.endsWith(':') && !line.includes('</') && line.length < 50) {
            formatted += `<h4 style="color: #2563eb; margin-top: 16px; margin-bottom: 8px; font-weight: 600;">${escapeHtml(line)}</h4>`;
        }
        // Bullet points
        else if (line.startsWith('•') || line.startsWith('-') || line.startsWith('*')) {
            const bulletContent = line.replace(/^[•\-\*]\s*/, '');
            formatted += `<div style="margin-left: 20px; margin-bottom: 4px;">• ${formatInlineElements(bulletContent)}</div>`;
        }
        // Numbered lists
        else if (/^\d+[\.\)]\s/.test(line)) {
            const listContent = line.replace(/^\d+[\.\)]\s*/, '');
            const number = line.match(/^\d+/)[0];
            formatted += `<div style="margin-left: 20px; margin-bottom: 4px;"><strong>${number}.</strong> ${formatInlineElements(listContent)}</div>`;
        }
        // Regular paragraphs
        else {
            formatted += `<p style="margin-bottom: 12px; line-height: 1.6;">${formatInlineElements(line)}</p>`;
        }
    }

    return formatted || '<p>No response received.</p>';
}

// Format inline elements within text
function formatInlineElements(text) {
    let formatted = escapeHtml(text);

    // Bold text (** ** or __ __)
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong style="color: #1f2937;">$1</strong>');
    formatted = formatted.replace(/__(.*?)__/g, '<strong style="color: #1f2937;">$1</strong>');

    // Italic text (* * or _ _)
    formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
    formatted = formatted.replace(/_(.*?)_/g, '<em>$1</em>');

    // Highlight numbers and percentages
    formatted = formatted.replace(/\b(\d+\.?\d*%?)\b/g, '<span style="color: #2563eb; font-weight: 600;">$1</span>');

    // Highlight dollar amounts
    formatted = formatted.replace(/\$[\d,]+\.?\d*/g, (match) =>
        `<span style="color: #10b981; font-weight: 600;">${match}</span>`
    );

    // Highlight room types
    formatted = formatted.replace(/\b(standard|deluxe|suite|Standard|Deluxe|Suite)\b/gi, (match) =>
        `<span style="color: #7c3aed; font-weight: 500;">${match}</span>`
    );

    // Highlight important keywords
    const keywords = ['RECOMMENDATION', 'IMPORTANT', 'NOTE', 'WARNING', 'TIP', 'ALERT'];
    keywords.forEach(keyword => {
        const regex = new RegExp(`\\b${keyword}\\b`, 'gi');
        formatted = formatted.replace(regex, `<span style="color: #ef4444; font-weight: 600; text-transform: uppercase;">${keyword}</span>`);
    });

    return formatted;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Clear chat
function clearChat() {
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.innerHTML = `
        <div class="message system">
            <div class="message-content">
                <p>Chat cleared. How can I help you today?</p>
            </div>
        </div>
    `;
}

// Export chat
function exportChat() {
    const messages = document.querySelectorAll('.message');
    let chatText = 'HotelPilot Chat Export\n';
    chatText += '=' .repeat(50) + '\n';
    chatText += `Date: ${new Date().toLocaleString()}\n`;
    chatText += `Agent: ${document.getElementById('current-agent-name').textContent}\n`;
    chatText += '=' .repeat(50) + '\n\n';

    messages.forEach(msg => {
        const type = msg.classList.contains('user') ? 'User' :
                     msg.classList.contains('ai') ? 'AI' :
                     'System';
        const content = msg.querySelector('.message-content').textContent;
        chatText += `[${type}]:\n${content}\n\n`;
    });

    // Download as text file
    const blob = new Blob([chatText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `hotelpilot-chat-${Date.now()}.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

// Toggle theme (placeholder)
function toggleTheme() {
    alert('Dark mode coming soon!');
}