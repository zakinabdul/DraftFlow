// ==========================================
// GLOBAL VARIABLES
// ==========================================
window.isProfileDropdownOpen = false;
window.currentTool = null;
window.isRecording = false;
window.isToolsPopupOpen = false;
window.subjectTimeout = null; // Used to manage the auto-hiding of the subject box
window.userSelectedText = '';// Stores the currently selected text for the subject box
//Get block-id using closest() method
window.blockId = null;
window.blockContent = null;
window.enterKey = false;

// ==========================================
// DOM ELEMENT REFERENCES
// ==========================================
const elements = {};

function initializeDOMElements() {
  elements.profileBtn= document.getElementById("profileBtn");
  elements.profileInitial= document.getElementById('initial');
  elements.profileDropdown= document.getElementById("profileDropdown");
  elements.messageInput= document.getElementById('messageInput');
  elements.sendButton= document.getElementById('sendButton');
  elements.sendBtn= document.getElementById('sendButton'); 
  elements.messagesWrapper= document.getElementById('messagesWrapper');
  elements.exportModal= document.getElementById('exportModal');
  elements.contentFrame= document.getElementById('contentFrame');
  elements.voiceButton= document.getElementById('voiceBtn');
  elements.voiceBtn= document.getElementById('voiceBtn'); // Alias for compatibility
  elements.toolsButton= document.getElementById('toolsBtn');
  elements.toolsBtn= document.getElementById('toolsBtn'); // Alias for compatibility
  elements.selectedTool= document.getElementById('selectedTool');
  elements.selectedToolIcon= document.getElementById('selectedToolIcon');
  elements.selectedToolName= document.getElementById('selectedToolName');
  elements.selectedToolClose= document.getElementById('selectedToolClose');
  elements.toolsPopup= document.getElementById('toolsPopup');
  elements.toolItems= document.querySelectorAll('.tool-item');
  elements.subjectBox= document.getElementById('subjectBox');
  elements.subjectText= document.getElementById('subjectText');
  elements.subjectCloseBtn= document.getElementById('subjectCloseBtn');
  elements.resizeHandle= document.getElementById('resizeHandle');
  elements.previewBtn= document.getElementById('previewBtn');
};


// ==========================================
// CONSTANTS
// ==========================================
const CHAT_RESPONSES = [
  "Thank you for your message! How can I assist you further? 😊",
  "That's a great question! Let me help you with that.",
  "I understand your concern. Here's what I can tell you...",
  "Absolutely! I'd be happy to provide more information.",
  "That sounds interesting! Tell me more about what you're looking for.",
  "Perfect! I can definitely help you with that request."
];

// Tool icon paths
const toolIcons = {
  image: "M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z",
  search: "M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z",
  code: "M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0L19.2 12l-4.6-4.6L16 6l6 6-6 6-1.4-1.4z",
  research: "M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z",
  think: "M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
};

// Voice recording constants
const VOICE_RECORDING_TIMEOUT = 3000; // 3 seconds simulation timeout
const SUBJECT_BOX_TIMEOUT = 5000;

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

function showStatus(message, type = "success") {
  // Remove existing status messages
  const existingStatus = document.querySelector(".status-message");
  if (existingStatus) {
    existingStatus.remove();
  }

  const statusDiv = document.createElement("div");
  statusDiv.className = `status-message ${type}`;
  statusDiv.textContent = message;

  document.body.appendChild(statusDiv);

  // Show with animation
  setTimeout(() => statusDiv.classList.add("visible"), 10);

  // Auto-hide after 3 seconds
  setTimeout(() => {
    if (statusDiv.parentNode) {
      statusDiv.classList.remove("visible");
      setTimeout(() => statusDiv.remove(), 300);
    }
  }, 3000);
}

function loadHtmlContent() {
  const response = localStorage.getItem('Response');

  if (!elements.contentFrame) return;

  if (response) {
    elements.contentFrame.srcdoc = response;
  } else {
    elements.contentFrame.srcdoc = `
      <div style="padding: 20px; text-align: center; color: #666; font-family: Arial, sans-serif;">
        <p>No HTML content found in localStorage.</p>
        <p>Please store your HTML content in localStorage with key 'Response'.</p>
      </div>
    `;
  }

  // Initialize auto-save after loading content
  setTimeout(() => {
    if (window.autoSaver) {
      window.autoSaver.setupAutoSave();
    }
  }, 500);
}


// ==========================================
// AUTO-SAVE MODULE
// ==========================================
const AutoSaveModule = {
  autoSaver: null,

  // Auto-save system for iframe content
  createAutoSaver(iframeElement, options = {}) {
    return new IframeAutoSave(iframeElement, options);
  },

  initializeAutoSave() {
    if (!elements.contentFrame) {
      console.error('Iframe element not found');
      return;
    }

    // Create auto-save instance
    window.autoSaver = this.createAutoSaver(elements.contentFrame, {
      saveKey: 'Response',
      saveDelay: 1000 // Save after 1 second of inactivity
    });

    this.autoSaver = window.autoSaver;
    console.log('Auto-save system ready');
  },

  initSaveStatus() {
    const saveStatus = document.getElementById('save-status');
    if (saveStatus) {
      saveStatus.textContent = 'Saved';
      saveStatus.className = 'save-status saved';
    }
  },

  // Public methods for external access
  forceSave() {
    if (this.autoSaver) {
      this.autoSaver.forceSave();
    }
  },

  setAutoSave(enabled) {
    if (this.autoSaver) {
      this.autoSaver.setAutoSave(enabled);
    }
  }
};

// ==========================================
// IFRAME AUTO-SAVE CLASS
// ==========================================
class IframeAutoSave {
  constructor(iframeElement, options = {}) {
    this.iframe = iframeElement;
    this.saveKey = options.saveKey || 'Response';
    this.saveDelay = options.saveDelay || 1000; // Auto-save delay in ms
    this.saveTimeout = null;
    this.isEditable = false;

    this.init();
  }

  init() {
    // Wait for iframe to load before setting up auto-save
    this.iframe.addEventListener('load', () => {
      this.setupAutoSave();
    });
  }

  setupAutoSave() {
    try {
      const iframeDoc = this.iframe.contentDocument || this.iframe.contentWindow.document;

      if (!iframeDoc) {
        console.warn('Cannot access iframe document. Make sure iframe is from same origin.');
        return;
      }

      // Set up content observation for auto-save
      this.observeContentChanges(iframeDoc);

      console.log('Auto-save system initialized');
    } catch (error) {
      console.error('Error setting up auto-save:', error);
    }
  }

  observeContentChanges(iframeDoc) {
    // Method 1: Using MutationObserver (most reliable)
    const observer = new MutationObserver(() => {
      this.scheduleAutoSave();
    });

    observer.observe(iframeDoc.body, {
      childList: true,
      subtree: true,
      characterData: true,
      attributes: true
    });
    /*
        // Method 2: Input events for form elements
        iframeDoc.addEventListener('input', () => {
          this.scheduleAutoSave();
        });
    
        // Method 3: Key events for contentEditable areas
        iframeDoc.addEventListener('keyup', () => {
          this.scheduleAutoSave();
        });
    
        // Method 4: Paste events
        iframeDoc.addEventListener('paste', () => {
          // Delay to allow paste content to be processed
          setTimeout(() => this.scheduleAutoSave(), 100);
        });
    
        // Method 5: Focus out events (save when user clicks away)
        iframeDoc.addEventListener('blur', () => {
          this.saveNow();
        }, true);
        */
  }

  scheduleAutoSave() {
    // Show saving status immediately
    this.showSaveIndicator('saving');

    // Clear existing timeout
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
    }

    // Schedule new save
    this.saveTimeout = setTimeout(() => {
      this.saveNow();
    }, this.saveDelay);
  }

  saveNow() {
    try {
      const iframeDoc = this.iframe.contentDocument || this.iframe.contentWindow.document;

      if (!iframeDoc) return;

      const htmlContent = iframeDoc.documentElement.outerHTML;
      localStorage.setItem(this.saveKey, htmlContent);

      // Show saved status
      this.showSaveIndicator('saved');

      console.log('Content auto-saved');
    } catch (error) {
      console.error('Error saving content:', error);
      // Show error status
      const indicator = document.getElementById('save-status');
      if (indicator) {
        indicator.textContent = 'Error';
        indicator.className = 'save-status';
        indicator.style.color = '#dc3545';
      }
    }
  }

  showSaveIndicator(status = 'saving') {
    const indicator = document.getElementById('save-status');

    if (!indicator) return;

    if (status === 'saving') {
      indicator.textContent = 'Saving...';
      indicator.className = 'save-status saving';
    } else if (status === 'saved') {
      indicator.textContent = 'Saved';
      indicator.className = 'save-status saved';
    }
  }

  // Manual save method
  forceSave() {
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
    }
    this.saveNow();
  }

  // Enable/disable auto-save
  setAutoSave(enabled) {
    if (!enabled && this.saveTimeout) {
      clearTimeout(this.saveTimeout);
      this.saveTimeout = null;
    }
  }
}


function showProfileArea() {
  const profileContainer = document.querySelector(".profile-loading");
  if (profileContainer) {
    profileContainer.style.transition = "all 0.60s cubic-bezier(0.4, 0, 0.2, 1)";
    profileContainer.style.opacity = "1";
    profileContainer.style.transform = "translateY(0)";
  }
}

// ==========================================
// CHAT FUNCTIONALITY
// ==========================================
const ChatModule = {
  createTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = `
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                `;
    return typingDiv;
  },

  // Scroll to bottom
  scrollToBottom() {
    if (!elements.messagesWrapper) return;

    requestAnimationFrame(() => {
      elements.messagesWrapper.scrollTop = elements.messagesWrapper.scrollHeight;
    });

    // Smooth scroll to bottom
    elements.messagesWrapper.scrollTo({
      top: elements.messagesWrapper.scrollHeight,
      behavior: 'smooth'
    });
  },

  //  Initialize scroll position on page load
  initializeScroll() {
    if (!elements.messagesWrapper) return;

    // Wait for DOM to be fully rendered, then scroll to bottom
    setTimeout(() => {
      this.scrollToBottom();
    }, 100); // Small delay to ensure all content is rendered
  },

  addMessage(text, isSent, isTyping = false) {
    if (!elements.messagesWrapper) return null;

    const messageContainer = document.createElement('div');
    messageContainer.className = isSent ? 'message-container sent' : 'message-container received';

    if (isTyping) {
      messageContainer.appendChild(this.createTypingIndicator());
    } else {
      const message = document.createElement('div');
      message.className = isSent ? 'message message-sent' : 'message message-received';
      message.textContent = text;
      messageContainer.appendChild(message);
    }

    const innerWrapper = elements.messagesWrapper.querySelector('.inner-message-wrapper');
    if (innerWrapper) {
      innerWrapper.appendChild(messageContainer);
    } else {
      elements.messagesWrapper.appendChild(messageContainer);
    }

    // Using the centralized scroll method
    this.scrollToBottom();

    return messageContainer;
  },

  removeTypingIndicator(container) {
    if (container && container.parentNode) {
      container.parentNode.removeChild(container);
      // Scroll after removing typing indicator
      this.scrollToBottom();
    }
  },


  async sendMessage() {
    if (!elements.messageInput) return;

    const text = elements.messageInput.value.trim();
    if (!text) return;


    // hide subject box
    // Close subject box when sending a message
    SubjectModule.hideSubjectBox();

    // Add user message
    this.addMessage(text, true);
    elements.messageInput.value = '';
    elements.messageInput.style.height = 'auto';

    // Show typing indicator
    const typingContainer = this.addMessage('', false, true);

    try {
      // Add artificial delay if needed
      await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000));

      const idToken = localStorage.getItem("IDtemp");

      // Get iframe content - make sure to define contentFrame properly
      const contentFrame = document.getElementById('contentFrame'); // Replace with actual iframe ID
      let originalText = '';

      if (contentFrame) {
        const iframeDoc = contentFrame.contentDocument || contentFrame.contentWindow.document;
        if (iframeDoc && iframeDoc.body) {
          originalText = iframeDoc.body.textContent || '';
        }
      }

      const queryData = {
        original_text: originalText,
        user_query: text,
        userSelectedText : userSelectedText,
        dataBlockId: blockId,
        blockContent: blockContent
      };
      console.log(queryData);

      const agent_response = await fetch('/adk/delegate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          "Authorization": `Bearer ${idToken}`
        },
        body: JSON.stringify(queryData),
      });

      if (!agent_response.ok) {
        throw new Error(`HTTP error! status: ${agent_response.status}`);
      }

      const data = await agent_response.json();
      console.log(data);
      const agentMsg = data.response_message || 'No response received';

      // Remove typing indicator and add response
      this.removeTypingIndicator(typingContainer);
      this.addMessage(agentMsg, false);

    } catch (error) {
      console.error('Error in sendMessage:', error);
      this.removeTypingIndicator(typingContainer);
      this.addMessage('Sorry, there was an error processing your message.', false);
    }
  },

  // Auto-resize textarea and enable/disable send button
  handleInputChange() {
    if (!elements.messageInput || !elements.sendButton) return;

    elements.messageInput.style.height = 'auto';
    elements.messageInput.style.height = Math.min(elements.messageInput.scrollHeight, 120) + 'px';

    // Enable/disable send button
    elements.sendButton.disabled = elements.messageInput.value.trim() === '';
  },

  initChat() {
    if (!elements.messageInput || !elements.sendButton) return;

    // Initialize scroll position on page load
    this.initializeScroll();

    // Event listeners
    elements.sendButton.addEventListener('click', () => this.sendMessage());

    elements.messageInput.addEventListener('keydown', (e) => {
      // Enter key sends message (unless Shift is held)
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault(); // Prevent new line
        this.sendMessage();
      }
      // Shift+Enter creates new line (default behavior)
    });

    // Auto-resize input and handle send button state
    elements.messageInput.addEventListener('input', () => {
      this.handleInputChange();
    });

    // Button visual feedback
    elements.sendButton.addEventListener('mousedown', () => {
      elements.sendButton.style.transform = 'scale(0.95)';
    });

    elements.sendButton.addEventListener('mouseup', () => {
      elements.sendButton.style.transform = 'scale(1)';
    });

    elements.sendButton.addEventListener('mouseleave', () => {
      elements.sendButton.style.transform = 'scale(1)';
    });

    // Focus input on load
    elements.messageInput.focus();
  }
};

// ==========================================
// TOOLS FUNCTIONALITY
// ==========================================
const ToolsModule = {
  // Show selected tool badge
  showSelectedTool(tool, toolName) {
    if (!elements.selectedTool || !elements.selectedToolName || !elements.selectedToolIcon) return;

    currentTool = tool;
    elements.selectedToolName.textContent = toolName;
    elements.selectedToolIcon.innerHTML = `<path d="${toolIcons[tool]}"/>`;
    elements.selectedTool.classList.add('show');
  },

  // Hide selected tool badge
  hideSelectedTool() {
    if (!elements.selectedTool) return;

    currentTool = null;
    elements.selectedTool.classList.remove('show');
  },

  // Toggle tools popup
  toggleToolsPopup(e) {
    if (e) e.stopPropagation();

    isToolsPopupOpen = !isToolsPopupOpen;

    if (elements.toolsPopup) {
      if (isToolsPopupOpen) {
        elements.toolsPopup.classList.add('show');
      } else {
        elements.toolsPopup.classList.remove('show');
      }
    }
  },

  // Close tools popup
  closeToolsPopup() {
    if (elements.toolsPopup) {
      elements.toolsPopup.classList.remove('show');
    }
    isToolsPopupOpen = false;
  },

  // Handle tool item selection
  handleToolSelection(e) {
    e.stopPropagation();

    const toolItem = e.target.closest('.tool-item');
    if (!toolItem) return;

    const tool = toolItem.dataset.tool;
    const toolName = toolItem.dataset.toolName;

    console.log('Selected tool:', tool);

    // Close tools popup
    this.closeToolsPopup();

    // Show selected tool badge
    this.showSelectedTool(tool, toolName);

    // Focus input without modifying text
    if (elements.messageInput) {
      elements.messageInput.focus();
    }
  },

  initTools() {
    // Tools button click handler
    if (elements.toolsBtn) {
      elements.toolsBtn.addEventListener('click', (e) => this.toggleToolsPopup(e));
    }

    // Tool items click handlers
    if (elements.toolItems) {
      elements.toolItems.forEach(item => {
        item.addEventListener('click', (e) => this.handleToolSelection(e));
      });
    }

    // Selected tool close button
    if (elements.selectedToolClose) {
      elements.selectedToolClose.addEventListener('click', (e) => {
        e.stopPropagation();
        this.hideSelectedTool();
        if (elements.messageInput) {
          elements.messageInput.focus();
        }
      });
    }

    // Close tools popup when clicking outside
    document.addEventListener('click', (e) => {
      if (elements.toolsBtn && !elements.toolsBtn.contains(e.target)) {
        if (isToolsPopupOpen) {
          this.closeToolsPopup();
        }
      }
    });
  }
};

// ==========================================
// VOICE FUNCTIONALITY
// ==========================================
const VoiceModule = {
  // Start voice recording
  startRecording() {
    if (!elements.voiceBtn) return;

    isRecording = true;
    elements.voiceBtn.classList.add('voice-recording');
    elements.voiceBtn.title = 'Stop recording';
    console.log('Started voice recording');

    // Simulation of voice recording - replace with actual voice recording logic
    setTimeout(() => {
      if (isRecording) {
        this.stopRecording();
        if (elements.messageInput) {
          elements.messageInput.value = 'This is a voice message transcription.';
          elements.messageInput.dispatchEvent(new Event('input'));
        }
      }
    }, VOICE_RECORDING_TIMEOUT);
  },

  // Stop voice recording
  stopRecording() {
    if (!elements.voiceBtn) return;

    isRecording = false;
    elements.voiceBtn.classList.remove('voice-recording');
    elements.voiceBtn.title = 'Voice input';
    console.log('Stopped voice recording');
  },

  // Toggle voice recording
  toggleRecording() {
    if (!isRecording) {
      this.startRecording();
    } else {
      this.stopRecording();
    }
  },

  initVoice() {
    // Voice button click handler
    if (elements.voiceBtn) {
      elements.voiceBtn.addEventListener('click', () => this.toggleRecording());
    }
  }
};

// ==========================================
// SUBJECT MODULE 
// ==========================================
const SubjectModule = {
  isEditMode: true, // Track current mode

  // Set edit mode status
  setEditMode(editMode) {
    this.isEditMode = editMode;

    // If switching to edit mode, hide subject box immediately
    if (editMode) {
      this.hideSubjectBox();
    }
  },

  // Truncates text to a specified maximum length and appends '...' if truncated.
  truncateText(text, maxLength = 50) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength).trim() + '...';
  },

  // Displays the subject box with the provided text.
  // Now works in both edit and preview modes.
  showSubjectBox(selectedText) {
    console.log('showSubjectBox called with:', selectedText, 'isEditMode:', this.isEditMode);

    if (!elements.subjectBox || !elements.subjectText) {
      console.log('Missing elements:', { 
        subjectBox: !!elements.subjectBox, 
        subjectText: !!elements.subjectText 
      });
      return;
    }

    const truncatedText = this.truncateText(selectedText);
    elements.subjectText.textContent = truncatedText;
    elements.subjectText.title = selectedText; // Show full text on hover
    
    // Clear any existing timeout
    if (window.subjectTimeout) {
      clearTimeout(window.subjectTimeout);
    }
    
    elements.subjectBox.classList.add('show');
    console.log('Subject box should now be visible');
  },

  // Hides the subject box.
  hideSubjectBox() {
    if (!elements.subjectBox) return;

    elements.subjectBox.classList.remove('show');
    elements.subjectBox.classList.add('hiding');

    if (typeof userSelectedText !== 'undefined') {
      userSelectedText = '';
    }

    // Remove classes after animation completes to reset state
    setTimeout(() => {
      elements.subjectBox.classList.remove('show', 'hiding');
    }, 250);

    // Clear selection based on current mode
    if (!this.isEditMode) {
      setTimeout(() => {
        try {
          const iframe = document.getElementById('contentFrame');
          if (iframe) {
            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
            if (iframeDoc && iframeDoc.getSelection) {
              iframeDoc.getSelection().removeAllRanges();
            }
          }
        } catch (error) {
          console.warn("Could not clear iframe selection due to cross-origin policy:", error);
        }
      }, 300);
    }
  },

  /**
   * Handles text selection events within the iframe.
   * Now active in both edit and preview modes.
   */
  handleIframeSelection() {
    console.log('handleIframeSelection called, isEditMode:', SubjectModule.isEditMode);

    const iframe = elements.contentFrame;
    if (!iframe) {
      console.log('No iframe found');
      return;
    }

    try {
      const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
      const selection = iframeDoc.getSelection();
      const selectedText = selection.toString().trim();

      console.log('Selected text:', selectedText);

     
      
      if (selection && selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        let selectedElement = range.commonAncestorContainer;
      
        // If it's a text node, move up to the parent element
        if (selectedElement.nodeType === Node.TEXT_NODE) {
          selectedElement = selectedElement.parentElement;
        }
      
        // Use closest() to find the nearest element with data-block-id
        const blockElement = selectedElement.closest('[data-block-id]');
        
        if (blockElement) {
          blockId = blockElement.getAttribute('data-block-id');
          blockContent = blockElement.outerHTML;
        } else {
          blockId = null;
          blockContent = null;
        }
      }

      if (selectedText.length > 0) {
        // Clear any existing timeout before setting a new one
        if (window.subjectTimeout) {
          clearTimeout(window.subjectTimeout);
        }
        
        // Store selected text globally if variable exists
        if (typeof userSelectedText !== 'undefined') {
          userSelectedText = selectedText;
        }
        
        // Debounce showing the subject box
        window.subjectTimeout = setTimeout(() => {
          SubjectModule.showSubjectBox(selectedText);
        }, 150);

        console.log('Block ID:', blockId);
        console.log('Selected text:', selectedText);
      } else {
        // Clear any existing timeout before setting a new one
        if (window.subjectTimeout) {
          clearTimeout(window.subjectTimeout);
        }
        
        // Debounce hiding the subject box
        window.subjectTimeout = setTimeout(() => {
          const currentIframeSelection = iframeDoc.getSelection().toString().trim();
          if (!currentIframeSelection) {
            if (typeof userSelectedText !== 'undefined') {
              userSelectedText = '';
            }
            SubjectModule.hideSubjectBox();
          }
        }, 100);
      }
    } catch (error) {
      console.warn('Cannot access iframe selection (likely cross-origin):', error);
    }
  },

  /**
   * Handles messages from iframe (for cross-origin scenarios).
   * Now works in both edit and preview modes.
   */
  handleIframeMessage(event) {
    const iframe = elements.contentFrame;
    if (!iframe) return;

    if (event.data && event.data.type === 'textSelection') {
      const selectedText = event.data.text;

      if (selectedText && selectedText.trim().length > 0) {
        if (typeof userSelectedText !== 'undefined') {
          userSelectedText = selectedText.trim();
        }
        SubjectModule.showSubjectBox(selectedText.trim());
      } else {
        if (typeof userSelectedText !== 'undefined') {
          userSelectedText = '';
        }
        SubjectModule.hideSubjectBox();
      }
    }
  },

  /**
   * Initializes iframe content and selection handling.
   */
  setupIframeSelectionListeners() {
    const iframe = elements.contentFrame;
    if (!iframe) {
      console.warn('contentFrame element not found.');
      return;
    }

    
    
    // Use a single load handler to avoid conflicts
    iframe.addEventListener('load', () => {
      console.log('Iframe loaded, setting up listeners');
      
      try {
        const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

        // Remove any existing listeners to prevent duplicates
        iframeDoc.removeEventListener('mouseup', SubjectModule.handleIframeSelection);
        iframeDoc.removeEventListener('selectionchange', SubjectModule.handleIframeSelection);

        // Add listeners to iframe document
        iframeDoc.addEventListener('mouseup', SubjectModule.handleIframeSelection);
        iframeDoc.addEventListener('selectionchange', SubjectModule.handleIframeSelection);

        console.log('Iframe selection listeners attached.');
      } catch (error) {
        console.warn('Cannot attach direct iframe listeners (cross-origin policy likely). Setting up message listener.', error);
        // Fallback: Setup message listener for cross-origin iframes
        window.removeEventListener('message', SubjectModule.handleIframeMessage);
        window.addEventListener('message', SubjectModule.handleIframeMessage);
      }
    });
  },

  /**
   * Main initialization for the Subject Box module.
   */
  initSubjectBox() {
    console.log('Initializing SubjectBox, isEditMode:', this.isEditMode);
    
    if (!elements.subjectCloseBtn) {
      console.warn('subjectCloseBtn element not found.');
      return;
    }

    // Event listener for the close button
    elements.subjectCloseBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      this.hideSubjectBox();
    });

    // Setup iframe listeners
    this.setupIframeSelectionListeners();
    
    console.log('SubjectBox initialization complete');
  }
};

// ==========================================
// EXPORT MODAL FUNCTIONALITY
// ==========================================
const ExportModule = {
  openModal() {
    if (elements.exportModal) {
      elements.exportModal.classList.add('active');
    }
  },

  closeModal() {
    if (elements.exportModal) {
      elements.exportModal.classList.remove('active');
    }
  },

  async confirmExport() {
    const selectedOptions = {};
    const fileName = document.getElementById('fileName').value;
    const iframe = document.getElementById("contentFrame");
    const doc = iframe.contentDocument || iframe.contentWindow.document;
    const html = doc.documentElement.outerHTML;
    const idToken = localStorage.getItem("IDtemp")
    // Create the payload with both HTML and filename
    const payload = {
      html: html,
      filename: fileName // assuming titleName is accessible in this scope
    };

    try {
      const resp = await fetch("/api/generate-pdf", {

        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${idToken}`
        },
        body: JSON.stringify(payload)
      });

      if (!resp.ok) {
        const errorText = await resp.text();
        console.error("Export failed:", errorText);
        return;
      }

      const blob = await resp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${fileName}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Export error:", error);
    }
    /*
        document.querySelectorAll('.option-group').forEach(group => {
          const buttons = group.querySelectorAll('.option-button.selected');
          const optionType = buttons[0]?.dataset.option;
    
          if (optionType === 'include') {
            selectedOptions[optionType] = Array.from(buttons).map(btn => btn.dataset.value);
          } else {
            selectedOptions[optionType] = buttons[0]?.dataset.value;
          }
        });
    
        console.log('Export options:', selectedOptions);
    
        // Simulate export process
        alert(`Exporting conversation as ${selectedOptions.format?.toUpperCase()} with ${selectedOptions.content} content...`);
    */
    this.closeModal();
  },

  initExportModal() {
    // Option selection functionality
    document.querySelectorAll('.option-button').forEach(button => {
      button.addEventListener('click', function () {
        const optionType = this.dataset.option;
        const isMultiSelect = optionType === 'include';

        if (isMultiSelect) {
          this.classList.toggle('selected');
        } else {
          const siblings = this.parentElement.querySelectorAll('.option-button');
          siblings.forEach(sibling => sibling.classList.remove('selected'));
          this.classList.add('selected');
        }
      });
    });

    // Modal event listeners
    if (elements.exportModal) {
      elements.exportModal.addEventListener('click', function (e) {
        console.log("Modal clicked");
        // Uncomment if you want to close on outside click
        // if (e.target === this) {
        //   ExportModule.closeModal();
        // }
      });
    }

    // Close modal with Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.closeModal();
      }
    });
  }
};

// ==========================================
// PROFILE FUNCTIONALITY
// ==========================================
const ProfileModule = (function () {
  let isProfileDropdownOpen = false;

  // Declare elements 
  let profileBtn;
  let profileDropdown;
  let iframeElement;

  function toggleDropdown() {
    if (!profileDropdown) {
      console.error('[ProfileModule] Profile dropdown element not found.');
      return;
    }

    isProfileDropdownOpen = !isProfileDropdownOpen;
    console.log(`[ProfileModule] Profile dropdown toggled. Open: ${isProfileDropdownOpen}`);

    if (isProfileDropdownOpen) {
      profileDropdown.classList.add("visible");
      if (profileBtn) {
        profileBtn.classList.add("active");
      }
    } else {
      profileDropdown.classList.remove("visible");
      if (profileBtn) {
        profileBtn.classList.remove("active");
      }
    }
  }

  function closeDropdown() {
    if (profileDropdown) {
      profileDropdown.classList.remove("visible");
    }
    if (profileBtn) {
      profileBtn.classList.remove("active");
    }
    isProfileDropdownOpen = false;
    console.log('[ProfileModule] Profile dropdown closed.');
  }

  function handleAction(action) {
    switch (action) {
      case "settings":
        showStatus("Settings page coming soon! ⚙️", "success");
        break;
      case "help":
        showStatus("Help & Support coming soon! 🛟", "success");
        break;
      case "about":
        showStatus("About page coming soon! ℹ️", "success");
        break;
      case "privacy":
        showStatus("Privacy settings coming soon! 🔒", "success");
        break;
      case "logout":
        if (confirm("Are you sure you want to logout?")) {
          showStatus("Logging out... 👋", "success");
          // FirebaseLogout();
        }
        break;
      default:
        showStatus("Feature coming soon!", "success");
    }
    closeDropdown();
  }

  function initProfile() {
    profileBtn = document.getElementById('profileBtn');
    profileDropdown = document.getElementById('profileDropdown');
    // IMPORTANT: You need to get a reference to your iframe here.
    // Replace 'yourIframeId' with the actual ID of your iframe.
    iframeElement = document.getElementById('contentFrame'); // <--- ADD THIS LINE AND UPDATE 'yourIframeId'

    if (!profileBtn || !profileDropdown) {
      console.error('[ProfileModule] Required profile elements (button or dropdown) not found. Initialization aborted.');
      return;
    }

    profileBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleDropdown();
    });

    // Click outside logic for the main document
    document.addEventListener("click", (e) => {
      if (
        isProfileDropdownOpen &&
        !profileBtn.contains(e.target) &&
        !profileDropdown.contains(e.target)
      ) {
        closeDropdown();
      }
    });

    // =========================================================================
    // ADD THIS SECTION TO HANDLE CLICKS INSIDE THE IFRAME
    // =========================================================================
    if (iframeElement && iframeElement.contentWindow) {
      // Wait for the iframe content to load
      iframeElement.onload = function () {
        try {
          const iframeDocument = iframeElement.contentWindow.document;
          iframeDocument.addEventListener("click", (e) => {
            // When a click happens inside the iframe, close the dropdown
            if (isProfileDropdownOpen) {
              closeDropdown();
            }
          });
          console.log('[ProfileModule] Iframe click listener added.');
        } catch (error) {
          console.warn('[ProfileModule] Could not attach click listener to iframe document, likely due to cross-origin policy:', error);
        }
      };

      // If the iframe is already loaded (e.g., from a page reload), try to attach listener immediately
      if (iframeElement.contentDocument && iframeElement.contentDocument.readyState === 'complete') {
        try {
          const iframeDocument = iframeElement.contentWindow.document;
          iframeDocument.addEventListener("click", (e) => {
            if (isProfileDropdownOpen) {
              closeDropdown();
            }
          });
          console.log('[ProfileModule] Iframe click listener added (initial load).');
        } catch (error) {
          console.warn('[ProfileModule] Could not attach click listener to iframe document on initial load, likely due to cross-origin policy:', error);
        }
      }
    } else {
      console.warn('[ProfileModule] Iframe element not found or not ready. Cannot attach iframe click listener.');
    }
    // =========================================================================


    document.addEventListener("click", (e) => {
      const menuItem = e.target.closest(".profile-menu-item");
      if (menuItem) {
        e.preventDefault();
        const action = menuItem.getAttribute("data-action");
        handleAction(action);
      }
    });

    console.log('[ProfileModule] Initialized.');
  }

  return {
    init: initProfile
  };
})();

// ==========================================
// UI ENHANCEMENTS
// ==========================================
const UIModule = {
  initProfileAvatar() {
    const profileAvatar = document.querySelector('.profile-avatar');
    if (profileAvatar) {
      profileAvatar.addEventListener('mouseenter', () => {
        profileAvatar.style.boxShadow = '0 12px 40px rgba(99, 102, 241, 0.8), 0 0 60px rgba(99, 102, 241, 0.4)';
      });

      profileAvatar.addEventListener('mouseleave', () => {
        profileAvatar.style.boxShadow = '0 8px 32px rgba(99, 102, 241, 0.4)';
      });
    }
  },

  initNavigation() {
    document.querySelectorAll('.nav-button').forEach(button => {
      button.addEventListener('click', function () {
        document.querySelectorAll('.nav-button').forEach(btn => btn.classList.remove('active'));
        this.classList.add('active');
      });
    });
  }
};


// ==========================================
// RESIZE FUNCTIONALITY
// ==========================================
const ResizeModule = {
  isResizing: false,
  startX: 0,
  startWidth: 0,
  chatColumn: null, // Will store the chat column element
  chatLayout: null, // Will store the overall chat layout element

  /**
   * Initializes the resize functionality for the chat column.
   * Attaches mouse event listeners to the resize handle.
   */
  initResize() {
    // Ensure the resizeHandle element exists before proceeding
    if (!elements.resizeHandle) {
      console.warn('Resize handle element not found (ID: resizeHandle). Resize functionality will not be active.');
      return;
    }

    // Get references to the chat column and chat layout container
    // Assuming these classes exist in your HTML structure
    this.chatColumn = document.querySelector('.chat-column');
    this.chatLayout = document.querySelector('.chat-layout');

    // Ensure essential elements are found
    if (!this.chatColumn || !this.chatLayout) {
      console.warn('Chat column (.chat-column) or chat layout (.chat-layout) not found. Resize functionality will not be active.');
      return;
    }

    // Mousedown event on the resize handle starts the resizing process
    elements.resizeHandle.addEventListener('mousedown', (e) => {
      this.isResizing = true;
      this.startX = e.clientX; // Record initial mouse X position
      this.startWidth = this.chatColumn.offsetWidth; // Record initial width of the chat column

      // Change cursor and prevent text selection during resize for better UX
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';

      e.preventDefault(); // Prevent default browser drag behavior
    });

    // Mousemove event globally to track mouse movement during resize
    document.addEventListener('mousemove', (e) => {
      if (!this.isResizing) return; // Only execute if resizing is active

      const containerWidth = this.chatLayout.offsetWidth; // Get the total width of the container
      const deltaX = e.clientX - this.startX; // Calculate mouse movement
      let newWidth = this.startWidth + deltaX; // Calculate new width based on mouse movement

      // Convert new width to percentage relative to the container for flexible layout
      const newWidthPercent = (newWidth / containerWidth) * 100;

      // Enforce minimum and maximum width constraints (30% to 70% of container width)
      // This prevents the columns from becoming too small or too large
      if (newWidthPercent >= 30 && newWidthPercent <= 70) {
        this.chatColumn.style.width = newWidthPercent + '%'; // Apply the new width
      }
    });

    // Mouseup event globally to stop the resizing process
    document.addEventListener('mouseup', () => {
      if (this.isResizing) {
        this.isResizing = false; // Stop resizing
        // Reset cursor and user-select properties
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
      }
    });
  }
};

// ==========================================
// CONTENT EDIT FUNCTIONALITY IN IFRAME
// ==========================================
const ContentEditModule = {
  isEditMode: true, // Default to edit mode

  // Enable editing in iframe
  enableEditing() {
    const iframe = elements.contentFrame;
    if (!iframe) return false;

    try {
      const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
      if (iframeDoc && iframeDoc.body) {
        iframeDoc.body.contentEditable = true;
        iframeDoc.body.style.outline = 'none'; // Remove focus outline
        this.isEditMode = true;

        // Notify SubjectModule about edit mode
        SubjectModule.setEditMode(true);
        return true;
      }
    } catch (error) {
      console.warn('Cannot enable editing (cross-origin):', error);
      return false;
    }
    return false;
  },

  // Disable editing in iframe
  disableEditing() {
    const iframe = elements.contentFrame;
    if (!iframe) return false;

    try {
      const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
      if (iframeDoc && iframeDoc.body) {
        iframeDoc.body.contentEditable = false;
        this.isEditMode = false;

        // Notify SubjectModule about preview mode
        SubjectModule.setEditMode(false);
        return true;
      }
    } catch (error) {
      console.warn('Cannot disable editing (cross-origin):', error);
      return false;
    }
    return false;
  },

  // Initialize iframe when it loads
  setupIframe() {
    const iframe = elements.contentFrame;
    if (!iframe) return;

    iframe.addEventListener('load', () => {
      // Small delay to ensure iframe is fully loaded
      setTimeout(() => {
        this.enableEditing();
        console.log('Iframe initialized as editable');
      }, 100);
    });

    // If iframe is already loaded
    if (iframe.contentDocument) {
      setTimeout(() => {
        this.enableEditing();
      }, 100);
    }
  },

  initContentEdit() {
    this.setupIframe();
  }
};

// ==========================================
// PREVIEW TOGGLE FUNCTIONALITY
// ==========================================
const PreviewToggleModule = {
  isPreviewMode: false,

  // SVG icons
  icons: {
    edit: "M12,9A3,3 0 0,0 9,12A3,3 0 0,0 12,15A3,3 0 0,0 15,12A3,3 0 0,0 12,9M12,17A5,5 0 0,1 7,12A5,5 0 0,1 12,7A5,5 0 0,1 17,12A5,5 0 0,1 12,17M12,4.5C7,4.5 2.73,7.61 1,12C2.73,16.39 7,19.5 12,19.5C17,19.5 21.27,16.39 23,12C21.27,7.61 17,4.5 12,4.5Z",
    preview: "M11.83,9L15,12.16C15,12.11 15,12.05 15,12A3,3 0 0,0 12,9C11.94,9 11.89,9 11.83,9M7.53,9.8L9.08,11.35C9.03,11.56 9,11.77 9,12A3,3 0 0,0 12,15C12.22,15 12.44,14.97 12.65,14.92L14.2,16.47C13.53,16.8 12.79,17 12,17A5,5 0 0,1 7,12C7,11.21 7.2,10.47 7.53,9.8M2,4.27L4.28,6.55L4.73,7C3.08,8.3 1.78,10 1,12C2.73,16.39 7,19.5 12,19.5C13.55,19.5 15.03,19.2 16.38,18.66L16.81,19.08L19.73,22L21,20.73L3.27,3M12,7A5,5 0 0,1 17,12C17,12.64 16.87,13.26 16.64,13.82L19.57,16.75C21.07,15.5 22.27,13.86 23,12C21.27,7.61 17,4.5 12,4.5C10.6,4.5 9.26,4.75 8,5.2L10.17,7.35C10.76,7.13 11.37,7 12,7Z"
  },

  // Update button appearance
  updateButton(isPreview) {
    const previewBtn = document.getElementById('previewBtn');
    if (!previewBtn) return;

    const iconPath = previewBtn.querySelector('path');
    const tooltip = previewBtn.parentElement?.querySelector('.tooltip-text');

    if (iconPath) {
      iconPath.setAttribute('d', isPreview ? this.icons.preview : this.icons.edit);
    }

    if (tooltip) {
      tooltip.textContent = isPreview ? 'Edit Mode' : 'Preview Mode';
    }

    // Toggle active class
    previewBtn.classList.toggle('preview-active', isPreview);
  },

  // Handle toggle
  handleToggle() {
    this.isPreviewMode = !this.isPreviewMode;

    if (this.isPreviewMode) {
      // Switch to preview mode
      if (ContentEditModule.disableEditing()) {
        this.updateButton(true);
        showStatus("Preview mode - Content is read-only", "success");
      }
    } else {
      // Switch to edit mode
      if (ContentEditModule.enableEditing()) {
        this.updateButton(false);
        showStatus("Edit mode - Content is editable", "success");
      }
    }
  },

  initPreviewToggle() {
    const previewBtn = document.getElementById('previewBtn');
    if (previewBtn) {
      previewBtn.addEventListener('click', () => this.handleToggle());
    }
  }
};

// ==========================================
//  UNDO/REDO Module
// ==========================================
const UndoRedoModule = (function () {
  let undoButton;
  let redoButton;
  let contentFrame;

  // Function to execute undo/redo command on the iframe's document
  function executeCommand(command) {
    const iframeDoc = contentFrame.contentDocument || contentFrame.contentWindow.document;
    if (iframeDoc) {
      try {
        // Ensure the iframe body has focus before executing command for consistency
        // Although execCommand usually works without explicit focus on the document,
        // focusing the body can sometimes help, especially for undo/redo state.
        if (iframeDoc.body.contentEditable === 'true') { // Only focus if editable
          iframeDoc.body.focus();
        }
        iframeDoc.execCommand(command);
        console.log(`[UndoRedoModule] Executed command: ${command}`);
      } catch (e) {
        console.error(`[UndoRedoModule] Error executing ${command}:`, e);
      }
    } else {
      console.warn(`[UndoRedoModule] Iframe document not ready for ${command} command.`);
    }
  }

  // Initialize the module
  function init() {
    undoButton = document.getElementById('undoBtn');
    redoButton = document.getElementById('redoBtn');
    contentFrame = document.getElementById('contentFrame'); // Get reference to the iframe

    if (!undoButton || !redoButton || !contentFrame) {
      console.error('Undo/Redo buttons or content iframe not found. Cannot initialize UndoRedoModule.');
      return;
    }

    // Add click listeners to the buttons
    undoButton.addEventListener('click', () => {
      executeCommand('undo');
    });

    redoButton.addEventListener('click', () => {
      executeCommand('redo');
    });

    // Add keydown listener to the main document for keyboard shortcuts
    document.addEventListener('keydown', (e) => {
      // Check for Ctrl+Z (Undo)
      if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault(); // Prevent default browser undo
        undoButton.click(); // Trigger our custom undo button click
      }

      // Check for Ctrl+Y or Ctrl+Shift+Z (Redo)
      if ((e.ctrlKey || e.metaKey) && (e.key === 'y' || (e.key === 'z' && e.shiftKey))) {
        e.preventDefault(); // Prevent default browser redo
        redoButton.click(); // Trigger our custom redo button click
      }
    });

    console.log('[UndoRedoModule] Initialized.');
  }

  return {
    init: init
  };
})();

// ==========================================
// CONTENT PANEL FUNCTIONALITY
// ==========================================
const ContentModule = (function () {
  let copyButton;
  let shareButton;
  let fullscreenButton;
  let contentFrame;
  let copyTooltip;

  // This object should contain references to your DOM elements
  const elements = {
    copyBtn: document.getElementById('copyBtn'),
    shareBtn: document.getElementById('shareBtn'),
    fullscreenBtn: document.getElementById('fullscreenBtn'),
    contentFrame: document.getElementById('contentFrame')
  };

  // Helper function to update and temporarily display the tooltip
  function showTooltipFeedback(tooltipElement, originalText, feedbackText, duration = 2000) {
    if (!tooltipElement) return;

    // Store the original text (e.g., "Copy")
    const originalTooltipText = tooltipElement.dataset.originalText || originalText; // Store if not already there
    tooltipElement.dataset.originalText = originalTooltipText; // Save it for future use

    // Update to feedback text (e.g., "Copied!")
    tooltipElement.textContent = feedbackText;

    // Add the 'show' class to trigger visibility and opacity transition
    tooltipElement.classList.add('show');

    // Clear any previous timeout to prevent conflicts if clicked rapidly
    if (tooltipElement.timeoutId) {
      clearTimeout(tooltipElement.timeoutId);
    }

    // Set a timeout to revert to original text and hide
    tooltipElement.timeoutId = setTimeout(() => {
      // Remove the 'show' class to trigger hiding transition
      tooltipElement.classList.remove('show');

      // After the transition, revert the text
      // You might need a small delay here if the transition is long
      // Or, use a 'transitionend' event listener for perfect timing
      setTimeout(() => {
        tooltipElement.textContent = originalTooltipText;
      }, 200); // Match this to your CSS transition duration if needed, or slightly more
      // 0.2s transition + a small buffer for safety
    }, duration);
  }

  function copyContent() {
    console.log('[ContentModule] Copy clicked');
    const iframeDoc = contentFrame.contentDocument || contentFrame.contentWindow.document;

    if (iframeDoc && iframeDoc.body) {
      const textToCopy = iframeDoc.body.textContent;

      if (textToCopy.trim() === '') {
        console.warn('[ContentModule] Iframe content is empty. Nothing to copy.');
        // Provide feedback via tooltip for no content
        showTooltipFeedback(copyTooltip, 'Copy', 'No content!', 1500); // Shorter duration for this
        return;
      }

      navigator.clipboard.writeText(textToCopy)
        .then(() => {
          console.log('[ContentModule] Content successfully copied to clipboard!');
          // Call the new helper function to update the tooltip
          showTooltipFeedback(copyTooltip, 'Copy', 'Copied!');
        })
        .catch(err => {
          console.error('[ContentModule] Failed to copy content: ', err);
          // Provide feedback via tooltip for failure
          showTooltipFeedback(copyTooltip, 'Copy', 'Failed to copy!', 2500); // Longer duration for error
        });
    } else {
      console.error('[ContentModule] Iframe document or body not accessible for copying.');
      showTooltipFeedback(copyTooltip, 'Copy', 'Cannot access content!', 2500);
    }
  }

  function shareContent() {
    console.log('[ContentModule] Share clicked');
    if (navigator.share) {
      const iframeDoc = contentFrame.contentDocument || contentFrame.contentWindow.document;
      const textForShare = (iframeDoc && iframeDoc.body) ? iframeDoc.body.textContent : 'No content available.';

      navigator.share({
        title: 'Shared Content from Page',
        text: textForShare,
        url: window.location.href
      })
        .then(() => console.log('[ContentModule] Share successful!'))
        .catch((error) => console.error('[ContentModule] Error sharing:', error));
    } else {
      console.warn('[ContentModule] Web Share API not supported in this browser.');
      // Optional: If share button also has a tooltip, you could use showTooltipFeedback here
      // e.g., showTooltipFeedback(shareTooltip, 'Share', 'Not supported!', 2000);
    }
  }

  function toggleFullscreen() {
    console.log('[ContentModule] Fullscreen clicked');
    const contentPanel = document.querySelector('.content-panel');
    if (contentPanel) {
      if (!document.fullscreenElement) {
        contentPanel.requestFullscreen()
          .then(() => console.log('[ContentModule] Entered fullscreen mode.'))
          .catch(err => console.error(`[ContentModule] Error attempting to enable fullscreen: ${err.message} (${err.name})`));
      } else {
        document.exitFullscreen()
          .then(() => console.log('[ContentModule] Exited fullscreen mode.'))
          .catch(err => console.error(`[ContentModule] Error attempting to exit fullscreen: ${err.message} (${err.name})`));
      }
    } else {
      console.error('[ContentModule] Content panel not found for fullscreen toggle.');
    }
  }

  function initContentControls() {
    copyButton = elements.copyBtn;
    shareButton = elements.shareBtn;
    fullscreenButton = elements.fullscreenBtn;
    contentFrame = elements.contentFrame;

    // Get the tooltip element associated with the copy button
    // Assuming it's the next sibling of the button or inside its parent
    if (copyButton && copyButton.parentElement && copyButton.parentElement.querySelector('.tooltip-text')) {
      copyTooltip = copyButton.parentElement.querySelector('.tooltip-text');
      // Store the initial 'Copy' text so we can revert to it
      copyTooltip.dataset.originalText = copyTooltip.textContent;
    } else {
      console.error('[ContentModule] Copy button tooltip not found.');
    }

    if (!copyButton || !shareButton || !fullscreenButton || !contentFrame) {
      console.error('One or more content control elements or iframe not found. Cannot initialize ContentModule.');
      return;
    }

    copyButton.addEventListener('click', copyContent);
    shareButton.addEventListener('click', shareContent);
    fullscreenButton.addEventListener('click', toggleFullscreen);

    console.log('[ContentModule] Content controls initialized.');
  }

  return {
    init: initContentControls
  };
})();

// ==========================================
// TITLE SYNCHRONIZATION FUNCTIONALITY
// ==========================================
const TitleSyncModule = {
  currentTitle: 'Untitled',
  navTitleInput: null,
  exportTitleInput: null,

  // Get references to input elements
  getElements() {
    this.navTitleInput = document.querySelector('.nav-bar .document-title-input');
    this.exportTitleInput = document.querySelector('.export-modal .document-title-input');

    return this.navTitleInput && this.exportTitleInput;
  },

  // Update title value and sync both inputs
  updateTitle(newTitle) {
    // Update the stored title value
    this.currentTitle = newTitle || 'Untitled';

    // Synchronize both input fields
    if (this.navTitleInput) {
      this.navTitleInput.value = this.currentTitle;
    }
    if (this.exportTitleInput) {
      this.exportTitleInput.value = this.currentTitle;
    }

    // Optional: Update document title
    document.title = this.currentTitle;

    // Dispatch custom event for other modules
    this.dispatchTitleChangeEvent();
  },

  // Dispatch title change event
  dispatchTitleChangeEvent() {
    const event = new CustomEvent('titleChanged', {
      detail: { title: this.currentTitle }
    });
    document.dispatchEvent(event);
  },

  // Handle input events
  handleInputChange(event) {
    this.updateTitle(event.target.value);
  },

  // Public method to get current title
  getTitle() {
    return this.currentTitle;
  },

  // Public method to set title programmatically
  setTitle(title) {
    this.updateTitle(title);
  },

  // Initialize title synchronization
  initTitleSync() {
    if (!this.getElements()) {
      console.warn('Title input elements not found');
      return;
    }

    // Set initial values
    this.navTitleInput.value = this.currentTitle;
    this.exportTitleInput.value = this.currentTitle;

    // Add event listeners for synchronization
    this.navTitleInput.addEventListener('input', (e) => this.handleInputChange(e));
    this.navTitleInput.addEventListener('blur', (e) => this.handleInputChange(e));

    this.exportTitleInput.addEventListener('input', (e) => this.handleInputChange(e));
    this.exportTitleInput.addEventListener('blur', (e) => this.handleInputChange(e));

    console.log('Title synchronization initialized');
  }
};

// Optional: Listen for title changes from other modules
document.addEventListener('titleChanged', (e) => {
  console.log('Title changed to:', e.detail.title);
  // Add additional logic here when title changes if needed
});


// ==========================================
// BLOCK PATCHER FUNCTIONALITY
// ==========================================
const BlockPatcherModule = (function () {
  let contentFrame;
  let isAnimating = false;

  // Configuration options
  const config = {
    transitionDuration: 300, // milliseconds
    fadeOutOpacity: 0.3,
    animationClass: 'block-updating',
    errorClass: 'block-error',
    successClass: 'block-success'
  };

  // This object should contain references to your DOM elements
  const elements = {
    contentFrame: document.getElementById('contentFrame') // Your iframe element
  };

  // CSS styles for transitions (inject into iframe)
  const transitionStyles = `
    <style id="block-patcher-styles">
      .block-updating {
        transition: all ${config.transitionDuration}ms ease-in-out;
        opacity: ${config.fadeOutOpacity};
        transform: translateY(-2px);
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      }
      
      .block-success {
        transition: all ${config.transitionDuration}ms ease-in-out;
        opacity: 1;
        transform: translateY(0);
        box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2);
        background-color: rgba(34, 197, 94, 0.05);
      }
      
      .block-error {
        transition: all ${config.transitionDuration}ms ease-in-out;
        opacity: 1;
        transform: translateY(0);
        box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.2);
        background-color: rgba(239, 68, 68, 0.05);
      }
      
      .block-fade-in {
        animation: blockFadeIn ${config.transitionDuration}ms ease-out;
      }
      
      @keyframes blockFadeIn {
        from {
          opacity: 0;
          transform: translateY(5px);
        }
        to {
          opacity: 1;
          transform: translateY(0);
        }
      }
    </style>
  `;

  /**
   * Helper function to inject transition styles into iframe
   */
  function injectTransitionStyles() {
    if (!contentFrame) return false;

    try {
      const iframeDoc = contentFrame.contentDocument || contentFrame.contentWindow.document;
      if (!iframeDoc) {
        console.error('[BlockPatcherModule] Cannot access iframe document');
        return false;
      }

      // Check if styles already exist
      if (!iframeDoc.getElementById('block-patcher-styles')) {
        const head = iframeDoc.head || iframeDoc.getElementsByTagName('head')[0];
        if (head) {
          head.insertAdjacentHTML('beforeend', transitionStyles);
          console.log('[BlockPatcherModule] Transition styles injected');
        }
      }
      return true;
    } catch (error) {
      console.error('[BlockPatcherModule] Error injecting styles:', error);
      return false;
    }
  }

  /**
   * Helper function to add CSS class with animation
   */
  function addTransitionClass(element, className, duration = config.transitionDuration) {
    return new Promise((resolve) => {
      element.classList.add(className);
      setTimeout(() => {
        resolve();
      }, duration);
    });
  }

  /**
   * Helper function to remove CSS classes
   */
  function removeTransitionClasses(element) {
    element.classList.remove(config.animationClass, config.errorClass, config.successClass, 'block-fade-in');
  }

  /**
   * Main function to update a specific HTML block with smooth transitions
   * @param {string} currentBlockId - The block ID to target (e.g., "block-1")
   * @param {string} currentRevisedText - The new HTML content to replace the target block
   * @param {Object} options - Additional options for the update
   * @returns {Promise<boolean>} - Returns promise that resolves to true if update was successful
   */
  async function updateBlockWithTransition(currentBlockId, currentRevisedText, options = {}) {
    // Prevent multiple simultaneous updates
    if (isAnimating) {
      console.warn('[BlockPatcherModule] Update already in progress, skipping...');
      return false;
    }

    try {
      isAnimating = true;

      // Ensure iframe is accessible
      if (!contentFrame) {
        console.error('[BlockPatcherModule] Content frame not initialized');
        return false;
      }

      const iframeDoc = contentFrame.contentDocument || contentFrame.contentWindow.document;
      if (!iframeDoc) {
        console.error('[BlockPatcherModule] Cannot access iframe document');
        return false;
      }

      // Inject styles if not already present
      injectTransitionStyles();

      // Find the target element
      const targetElement = iframeDoc.querySelector(`[data-block-id="${currentBlockId}"]`);
      if (!targetElement) {
        console.error(`[BlockPatcherModule] Element with block ID "${currentBlockId}" not found`);
        return false;
      }

      // Execute onBeforeUpdate callback if provided
      if (options.onBeforeUpdate && typeof options.onBeforeUpdate === 'function') {
        options.onBeforeUpdate(targetElement, currentRevisedText);
      }

      console.log(`[BlockPatcherModule] Starting update for block "${currentBlockId}"`);

      // Phase 1: Add updating animation
      removeTransitionClasses(targetElement);
      await addTransitionClass(targetElement, config.animationClass);

      // Phase 2: Create and validate new element
      const tempContainer = iframeDoc.createElement('div');
      // ################ S-E-C-U-R-I-T-Y -- F-I-X ################
      // Sanitize the 'currentRevisedText' using DOMPurify before assigning to innerHTML
      const sanitizedRevisedText = DOMPurify.sanitize(currentRevisedText.trim(), {
          USE_PROFILES: { html: true } // This is a good default, allows safe HTML.
                                      // Adjust if you need more restrictive or permissive settings.
      });
      tempContainer.innerHTML = sanitizedRevisedText; // Use the SANITIZED text
      // #########################################################
      
      const newElement = tempContainer.firstElementChild;

      if (!newElement) {
        // Show error state
        await addTransitionClass(targetElement, config.errorClass);
        console.error('[BlockPatcherModule] Invalid revised text - no valid HTML element found');
        
        // Remove error class after delay
        setTimeout(() => {
          removeTransitionClasses(targetElement);
        }, 1500);
        
        return false;
      }

      // Verify block ID consistency (optional)
      const newBlockId = newElement.getAttribute('data-block-id');
      if (newBlockId && newBlockId !== currentBlockId) {
        console.warn(`[BlockPatcherModule] Block ID mismatch: expected "${currentBlockId}", got "${newBlockId}"`);
      }

      // Phase 3: Replace the element
      targetElement.parentNode.replaceChild(newElement, targetElement);

      // Phase 4: Add success animation to new element
      removeTransitionClasses(newElement);
      newElement.classList.add('block-fade-in');
      await addTransitionClass(newElement, config.successClass, 200);

      // Phase 5: Clean up success styling
      setTimeout(() => {
        removeTransitionClasses(newElement);
      }, 1500);

      // Execute onAfterUpdate callback if provided
      if (options.onAfterUpdate && typeof options.onAfterUpdate === 'function') {
        options.onAfterUpdate(newElement);
      }

      console.log(`[BlockPatcherModule] Successfully updated block "${currentBlockId}"`);
      return true;

    } catch (error) {
      console.error('[BlockPatcherModule] Error during block update:', error);
      
      // Try to show error state if target element still exists
      try {
        const targetElement = contentFrame.contentDocument.querySelector(`[data-block-id="${currentBlockId}"]`);
        if (targetElement) {
          removeTransitionClasses(targetElement);
          await addTransitionClass(targetElement, config.errorClass);
          setTimeout(() => {
            removeTransitionClasses(targetElement);
          }, 1500);
        }
      } catch (cleanupError) {
        console.error('[BlockPatcherModule] Error during cleanup:', cleanupError);
      }
      
      return false;
    } finally {
      isAnimating = false;
    }
  }

  /**
   * Batch update multiple blocks with staggered animations
   * @param {Array} updates - Array of {blockId, revisedText, options} objects
   * @param {number} staggerDelay - Delay between each update in milliseconds
   * @returns {Promise<Array>} - Array of results for each update
   */
  async function updateMultipleBlocks(updates, staggerDelay = 100) {
    const results = [];
    
    for (let i = 0; i < updates.length; i++) {
      const { blockId, revisedText, options } = updates[i];
      
      if (i > 0) {
        await new Promise(resolve => setTimeout(resolve, staggerDelay));
      }
      
      const result = await updateBlockWithTransition(blockId, revisedText, options);
      results.push(result);
    }
    
    return results;
  }

  /**
   * Simple update without transitions (for performance-critical scenarios)
   * @param {string} currentBlockId - The block ID to target
   * @param {string} currentRevisedText - The new HTML content
   * @returns {boolean} - Returns true if update was successful
   */
  function updateBlockSimple(currentBlockId, currentRevisedText) {
    try {
      if (!contentFrame) {
        console.error('[BlockPatcherModule] Content frame not initialized');
        return false;
      }

      const iframeDoc = contentFrame.contentDocument || contentFrame.contentWindow.document;
      if (!iframeDoc) {
        console.error('[BlockPatcherModule] Cannot access iframe document');
        return false;
      }

      const targetElement = iframeDoc.querySelector(`[data-block-id="${currentBlockId}"]`);
      if (!targetElement) {
        console.error(`[BlockPatcherModule] Element with block ID "${currentBlockId}" not found`);
        return false;
      }

      // Direct replacement using outerHTML
      targetElement.outerHTML = currentRevisedText;
      console.log(`[BlockPatcherModule] Successfully updated block "${currentBlockId}" (simple mode)`);
      return true;

    } catch (error) {
      console.error('[BlockPatcherModule] Error updating block (simple mode):', error);
      return false;
    }
  }

  /**
   * Initialize the Block Patcher Module
   */
  function initBlockPatcher() {
    contentFrame = elements.contentFrame;

    if (!contentFrame) {
      console.error('[BlockPatcherModule] Content frame element not found. Cannot initialize BlockPatcherModule.');
      return false;
    }

    // Wait for iframe to load before injecting styles
    if (contentFrame.contentDocument && contentFrame.contentDocument.readyState === 'complete') {
      injectTransitionStyles();
    } else {
      contentFrame.addEventListener('load', () => {
        injectTransitionStyles();
      });
    }

    console.log('[BlockPatcherModule] Block patcher initialized.');
    return true;
  }

  // Public API
  return {
    init: initBlockPatcher,
    updateBlock: updateBlockWithTransition,
    updateBlockSimple: updateBlockSimple,
    updateMultipleBlocks: updateMultipleBlocks,
    injectStyles: injectTransitionStyles,
    config: config
  };
})();

// ==========================================
// USAGE EXAMPLES (for reference)
// ==========================================

// Initialize the module (call this in your DOMContentLoaded event)
// BlockPatcherModule.init();

// Simple usage with transitions
// BlockPatcherModule.updateBlock('block-1', '<h1 data-block-id="block-1">New Title with Smooth Animation</h1>');

// Advanced usage with callbacks
// BlockPatcherModule.updateBlock('block-2', '<p data-block-id="block-2">Updated content</p>', {
//   onBeforeUpdate: (oldElement, newHtml) => console.log('About to update:', oldElement.textContent),
//   onAfterUpdate: (newElement) => console.log('Updated to:', newElement.textContent)
// });

// Batch updates with staggered animations
// BlockPatcherModule.updateMultipleBlocks([
//   { blockId: 'block-1', revisedText: '<h1 data-block-id="block-1">First Update</h1>' },
//   { blockId: 'block-2', revisedText: '<p data-block-id="block-2">Second Update</p>' },
//   { blockId: 'block-3', revisedText: '<div data-block-id="block-3">Third Update</div>' }
// ], 150);

// Performance mode (no animations)
// BlockPatcherModule.updateBlockSimple('block-1', '<h1 data-block-id="block-1">Fast Update</h1>');


// Global variables to store block_id and revised_text
let currentBlockId = null;
let currentRevisedText = null;
class WebSocketClient {
    constructor(userId, baseUrl = 'wss://draftflow-fjod.onrender.com') {
        this.userId = userId;
        this.baseUrl = baseUrl;
        this.websocket = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 3000;
        
        this.connect();
    }

    connect() {
        try {
            this.websocket = new WebSocket(`${this.baseUrl}/api/ws/${this.userId}`);
            
            this.websocket.onopen = (event) => {
                console.log('🔌 WebSocket connection established');
                this.reconnectAttempts = 0;
            };

            this.websocket.onmessage = (event) => {
                try {
                    const message = JSON.parse(event.data);
                    console.log('📨 Received WebSocket message:', message);

                    // Handle agent_suggestion messages
                    if (message.type === 'agent_suggestion') {
                        currentBlockId = message.block_id;
                        let receivedRevisedText = message.revised_text; // Use a distinct variable name for the received raw text

                        console.log('📝 Updated global variables:');
                        console.log('Block ID:', currentBlockId);
                        console.log('Received Raw Text (Will be sanitized):', receivedRevisedText); // Indicate it will be sanitized

                        if (currentBlockId && receivedRevisedText) {
                            // Pass the received raw text to updateBlock
                            // updateBlock will handle the sanitization internally.
                            BlockPatcherModule.updateBlock(currentBlockId, receivedRevisedText)
                                .then(success => {
                                    if (success) {
                                        console.log('✅ Block updated successfully');
                                    } else {
                                        console.error('❌ Block update failed');
                                    }
                                })
                                .catch(error => {
                                    console.error('❌ Block update error:', error);
                                });
                        }
                    }

                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.websocket.onclose = (event) => {
                console.log('🔌 WebSocket connection closed', event.code, event.reason);
                this.attemptReconnect();
            };

            this.websocket.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
            };

        } catch (error) {
            console.error('Failed to establish WebSocket connection:', error);
            this.attemptReconnect();
        }
    }

    // Add the missing attemptReconnect method
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
            setTimeout(() => {
                this.connect();
            }, this.reconnectInterval);
        } else {
            console.error('❌ Max reconnection attempts reached');
        }
    }

    disconnect() {
        if (this.websocket) {
            this.websocket.close();
        }
    }
}

// Usage example:
// const wsClient = new WebSocketClient('user123');
// 
// // Access global variables anytime:
// console.log('Block ID:', getCurrentBlockId());
// console.log('Revised Text:', getCurrentRevisedText());
// console.log('Both values:', getBothValues());

// Usage example:
// const wsClient = new WebSocketClient('user123');
// 
// // Access stored data:
// console.log(wsClient.getAllMessages());
// console.log(wsClient.getBlockUpdate('block1'));
// console.log(wsClient.getAllBlockUpdates());

// Usage example:
// const wsClient = new WebSocketClient('user123');
// 
// // Access stored data:
// console.log(wsClient.getAllMessages());
// console.log(wsClient.getBlockUpdate('block1'));
// console.log(wsClient.getAllBlockUpdates());


// Usage example:
// Initialize the WebSocket client when the page loads

// Clean up on page unload
window.addEventListener('beforeunload', function() {
    if (window.wsClient) {
        window.wsClient.disconnect();
    }
});



// ==========================================
// GLOBAL FUNCTIONS (for external access)
// ==========================================

// Utility functions to access global variables

window.getCurrentBlockId = function() {
    return currentBlockId; // Assuming currentBlockId is a top-level module-scoped variable
};

window.getCurrentRevisedText = function() {
    return currentRevisedText; // Assuming currentRevisedText is a top-level module-scoped variable
};

window.getBothValues = function() {
    return {
        blockId: currentBlockId,
        revisedText: currentRevisedText
    };
};




window.initializeAutoSave = function() {
  AutoSaveModule.initializeAutoSave();
};

window.forceSave = function() {
  AutoSaveModule.forceSave();
};

window.setAutoSave = function(enabled) {
  AutoSaveModule.setAutoSave(enabled);
};

window.openExportModal = function() {
  ExportModule.openModal();
};

window.closeExportModal = function() {
  ExportModule.closeModal();
};

window.confirmExport = function() {
  ExportModule.confirmExport();
};

window.showSelectedTool = function(tool, toolName) {
  ToolsModule.showSelectedTool(tool, toolName);
};

window.hideSelectedTool = function() {
    ToolsModule.hideSelectedTool();
};

window.startRecording = function() {
    VoiceModule.startRecording();
};

window.stopRecording = function() {
    VoiceModule.stopRecording();
};

window.showSubjectBox = function(selectedText) {
    SubjectModule.showSubjectBox(selectedText);
};

window.hideSubjectBox = function() {
    SubjectModule.hideSubjectBox();
};

window.togglePreviewMode = function() {
    PreviewToggleModule.handleToggle();
};

// ==========================================
// INITIALIZATION
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  // Load  content and show profile
  initializeDOMElements();
  loadHtmlContent();
  showProfileArea();
  initializeAutoSave();
  // Initialize all modules
  ChatModule.initChat();
  ExportModule.initExportModal();
  ProfileModule.init();
  UIModule.initProfileAvatar();
  UIModule.initNavigation();
  ResizeModule.initResize();
  ContentEditModule.initContentEdit();
  PreviewToggleModule.initPreviewToggle();
  ToolsModule.initTools();
  VoiceModule.initVoice();
  SubjectModule.initSubjectBox();
  UndoRedoModule.init();
  ContentModule.init();
  TitleSyncModule.initTitleSync();
  AutoSaveModule.initSaveStatus();
  

  // websocket
      const userId = localStorage.getItem("userId");
    
    // Initialize BlockPatcher first
    const initSuccess = BlockPatcherModule.init();
    if (!initSuccess) {
        console.error('❌ Failed to initialize BlockPatcherModule');
        return;
    }
    
    // Create WebSocket client instance
    window.wsClient = new WebSocketClient(userId);
    
    console.log('✅ Application initialized successfully');
});


