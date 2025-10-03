// HotelPilot Voice Interface
// ==========================

class VoiceInterface {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.voices = [];
        this.selectedVoice = null;
        this.initializeRecognition();
        this.loadVoices();
    }

    // Initialize Speech Recognition
    initializeRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();

            // Configuration
            this.recognition.continuous = false;
            this.recognition.interimResults = true;
            this.recognition.lang = 'en-US';
            this.recognition.maxAlternatives = 1;

            // Event handlers
            this.recognition.onstart = () => {
                console.log('Voice recognition started');
                this.updateUI('listening');
            };

            this.recognition.onresult = (event) => {
                const last = event.results.length - 1;
                const transcript = event.results[last][0].transcript;
                const isFinal = event.results[last].isFinal;

                if (isFinal) {
                    this.handleVoiceInput(transcript);
                } else {
                    this.updateTranscript(transcript);
                }
            };

            this.recognition.onerror = (event) => {
                console.error('Recognition error:', event.error);
                this.updateUI('error', event.error);
            };

            this.recognition.onend = () => {
                this.isListening = false;
                this.updateUI('idle');
            };
        } else {
            console.warn('Speech recognition not supported');
            this.updateUI('unsupported');
        }
    }

    // Load available voices
    loadVoices() {
        this.voices = this.synthesis.getVoices();

        if (this.voices.length === 0) {
            // Voices might load async
            this.synthesis.onvoiceschanged = () => {
                this.voices = this.synthesis.getVoices();
                this.selectBestVoice();
            };
        } else {
            this.selectBestVoice();
        }
    }

    // Select the best available voice
    selectBestVoice() {
        // Prefer US English female voices for hotel assistant
        const preferredVoices = [
            'Google US English Female',
            'Microsoft Zira',
            'Samantha',
            'Victoria',
            'Alex'
        ];

        for (let preferred of preferredVoices) {
            const voice = this.voices.find(v => v.name.includes(preferred));
            if (voice) {
                this.selectedVoice = voice;
                break;
            }
        }

        // Fallback to first English voice
        if (!this.selectedVoice) {
            this.selectedVoice = this.voices.find(v => v.lang.startsWith('en')) || this.voices[0];
        }
    }

    // Start listening
    startListening() {
        if (this.recognition && !this.isListening) {
            this.isListening = true;
            this.recognition.start();
        }
    }

    // Stop listening
    stopListening() {
        if (this.recognition && this.isListening) {
            this.isListening = false;
            this.recognition.stop();
        }
    }

    // Toggle listening
    toggleListening() {
        if (this.isListening) {
            this.stopListening();
        } else {
            this.startListening();
        }
    }

    // Handle voice input
    handleVoiceInput(transcript) {
        console.log('Final transcript:', transcript);

        // Update the input field
        const inputField = document.getElementById('user-input');
        if (inputField) {
            inputField.value = transcript;
        }

        // Optional: Auto-send the message
        const autoSend = document.getElementById('auto-send-voice')?.checked;
        if (autoSend) {
            document.getElementById('send-btn')?.click();
        }

        this.updateUI('completed', transcript);
    }

    // Update transcript display
    updateTranscript(transcript) {
        const display = document.getElementById('voice-transcript');
        if (display) {
            display.textContent = transcript;
        }
    }

    // Speak text
    speak(text, options = {}) {
        // Cancel any ongoing speech
        this.synthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);

        // Configure voice settings
        utterance.voice = this.selectedVoice;
        utterance.rate = options.rate || 1.0;
        utterance.pitch = options.pitch || 1.0;
        utterance.volume = options.volume || 1.0;

        // Event handlers
        utterance.onstart = () => {
            this.updateUI('speaking');
        };

        utterance.onend = () => {
            this.updateUI('idle');
        };

        utterance.onerror = (event) => {
            console.error('Speech error:', event);
            this.updateUI('error');
        };

        // Speak
        this.synthesis.speak(utterance);
    }

    // Stop speaking
    stopSpeaking() {
        this.synthesis.cancel();
        this.updateUI('idle');
    }

    // Update UI based on state
    updateUI(state, data = null) {
        const voiceBtn = document.getElementById('voice-btn');
        const voiceIndicator = document.getElementById('voice-indicator');
        const voiceStatus = document.getElementById('voice-status');

        switch (state) {
            case 'listening':
                voiceBtn?.classList.add('listening');
                voiceIndicator?.classList.add('pulse');
                if (voiceStatus) voiceStatus.textContent = 'Listening...';
                break;

            case 'speaking':
                voiceBtn?.classList.add('speaking');
                if (voiceStatus) voiceStatus.textContent = 'Speaking...';
                break;

            case 'idle':
                voiceBtn?.classList.remove('listening', 'speaking');
                voiceIndicator?.classList.remove('pulse');
                if (voiceStatus) voiceStatus.textContent = 'Ready';
                break;

            case 'error':
                voiceBtn?.classList.add('error');
                if (voiceStatus) voiceStatus.textContent = `Error: ${data || 'Unknown'}`;
                setTimeout(() => {
                    voiceBtn?.classList.remove('error');
                    this.updateUI('idle');
                }, 3000);
                break;

            case 'completed':
                if (voiceStatus) voiceStatus.textContent = `Heard: "${data}"`;
                setTimeout(() => this.updateUI('idle'), 2000);
                break;

            case 'unsupported':
                voiceBtn?.disabled = true;
                if (voiceStatus) voiceStatus.textContent = 'Voice not supported';
                break;
        }
    }

    // Read response aloud
    readResponse(text) {
        // Clean text for speech
        const cleanText = this.cleanTextForSpeech(text);

        // Check if voice is enabled
        const voiceEnabled = document.getElementById('voice-enabled')?.checked;
        if (voiceEnabled) {
            this.speak(cleanText);
        }
    }

    // Clean text for speech
    cleanTextForSpeech(text) {
        // Remove HTML tags
        text = text.replace(/<[^>]*>/g, '');

        // Replace special characters
        text = text.replace(/[•·▪]/g, 'bullet point');
        text = text.replace(/[→←↑↓]/g, '');

        // Expand abbreviations
        text = text.replace(/\bADR\b/g, 'average daily rate');
        text = text.replace(/\bRevPAR\b/g, 'revenue per available room');
        text = text.replace(/\bVIP\b/g, 'V I P');

        // Add pauses for better speech
        text = text.replace(/\. /g, '. ... ');
        text = text.replace(/: /g, ': ... ');

        return text;
    }

    // Voice commands
    processVoiceCommand(transcript) {
        const command = transcript.toLowerCase();

        // Check for wake words
        if (command.includes('hey hotel') || command.includes('okay hotel')) {
            this.startListening();
            return true;
        }

        // Check for agent switches
        if (command.includes('switch to')) {
            if (command.includes('pricing') || command.includes('demand')) {
                selectAgent('demand_manager');
                this.speak('Switched to Demand Manager');
                return true;
            }
            if (command.includes('guest') || command.includes('communication')) {
                selectAgent('guest_lifecycle');
                this.speak('Switched to Guest Lifecycle');
                return true;
            }
            if (command.includes('housekeeping') || command.includes('cleaning')) {
                selectAgent('housekeeping');
                this.speak('Switched to Housekeeping');
                return true;
            }
            if (command.includes('billing') || command.includes('payment')) {
                selectAgent('billing');
                this.speak('Switched to Billing Recovery');
                return true;
            }
        }

        // Quick actions
        if (command.includes('clear chat')) {
            clearChat();
            this.speak('Chat cleared');
            return true;
        }

        if (command.includes('stop') || command.includes('cancel')) {
            this.stopSpeaking();
            this.stopListening();
            return true;
        }

        return false;
    }
}

// Initialize voice interface when page loads
let voiceInterface = null;

document.addEventListener('DOMContentLoaded', () => {
    voiceInterface = new VoiceInterface();

    // Add voice UI elements if not present
    addVoiceControls();

    // Set up event listeners
    setupVoiceEventListeners();
});

// Add voice controls to the UI
function addVoiceControls() {
    // Check if controls already exist
    if (document.getElementById('voice-controls')) return;

    // Create voice control panel
    const voiceHTML = `
        <div id="voice-controls" class="voice-controls">
            <div class="voice-header">
                <h3>🎤 Voice Controls</h3>
                <label class="toggle">
                    <input type="checkbox" id="voice-enabled" checked>
                    <span>Enable Voice</span>
                </label>
            </div>

            <div class="voice-buttons">
                <button id="voice-btn" class="voice-btn" title="Click to speak">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                        <line x1="12" y1="19" x2="12" y2="23"></line>
                        <line x1="8" y1="23" x2="16" y2="23"></line>
                    </svg>
                    <span id="voice-indicator" class="voice-indicator"></span>
                </button>

                <button id="speaker-btn" class="speaker-btn" title="Toggle speech output">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                        <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                        <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
                    </svg>
                </button>
            </div>

            <div class="voice-status">
                <span id="voice-status">Ready</span>
                <div id="voice-transcript" class="voice-transcript"></div>
            </div>

            <div class="voice-settings">
                <label>
                    <input type="checkbox" id="auto-send-voice">
                    <span>Auto-send after speaking</span>
                </label>
                <label>
                    <input type="checkbox" id="read-responses" checked>
                    <span>Read responses aloud</span>
                </label>
            </div>

            <div class="voice-tips">
                <p><strong>Voice Commands:</strong></p>
                <ul>
                    <li>"Hey Hotel" - Wake word</li>
                    <li>"Switch to [agent name]"</li>
                    <li>"Clear chat"</li>
                    <li>"Stop" - Stop speaking</li>
                </ul>
            </div>
        </div>
    `;

    // Add to info panel or create new panel
    const infoPanel = document.querySelector('.info-panel');
    if (infoPanel) {
        const voiceDiv = document.createElement('div');
        voiceDiv.innerHTML = voiceHTML;
        infoPanel.appendChild(voiceDiv.firstElementChild);
    }
}

// Set up voice event listeners
function setupVoiceEventListeners() {
    // Voice button click
    document.getElementById('voice-btn')?.addEventListener('click', () => {
        if (voiceInterface) {
            voiceInterface.toggleListening();
        }
    });

    // Speaker button click
    document.getElementById('speaker-btn')?.addEventListener('click', () => {
        if (voiceInterface) {
            if (voiceInterface.synthesis.speaking) {
                voiceInterface.stopSpeaking();
            } else {
                const lastMessage = document.querySelector('.message.ai:last-child .message-content')?.textContent;
                if (lastMessage) {
                    voiceInterface.speak(lastMessage);
                }
            }
        }
    });

    // Keyboard shortcut for voice (Space bar when not in input)
    document.addEventListener('keydown', (e) => {
        if (e.code === 'Space' && !['INPUT', 'TEXTAREA'].includes(e.target.tagName)) {
            e.preventDefault();
            voiceInterface?.toggleListening();
        }
    });

    // Read responses when they arrive
    const originalAddMessage = window.addMessage;
    window.addMessage = function(type, content, isHtml) {
        const messageId = originalAddMessage(type, content, isHtml);

        // If it's an AI response and voice is enabled, read it
        if (type === 'ai' && document.getElementById('read-responses')?.checked) {
            // Wait a bit for the message to render
            setTimeout(() => {
                const messageContent = document.getElementById(messageId)?.querySelector('.message-content')?.textContent;
                if (messageContent && !messageContent.includes('loading')) {
                    voiceInterface?.readResponse(messageContent);
                }
            }, 100);
        }

        return messageId;
    };
}