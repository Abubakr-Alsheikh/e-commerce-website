// scripts.js (Common Logic)

document.addEventListener("DOMContentLoaded", () => {
  // User ID Management
  const getUserID = () => {
    let userId = localStorage.getItem("userID");
    if (!userId) {
      userId = generateUUID();
      localStorage.setItem("userID", userId);
    }
    return userId;
  };

  const generateUUID = () => {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
      const r = (Math.random() * 16) | 0;
      const v = c === "x" ? r : (r & 0x3) | 0x8;
      return v.toString(16);
    });
  };

  const userID = getUserID();

  const sessionIdInput = document.getElementById("session-id");
  const questionInput = document.getElementById("questionInput");
  const askQuestionButton = document.getElementById("askQuestionButton");
  const chatMessages = document.getElementById("chatMessages");
  const sendButtonText = document.getElementById("sendButtonText");
  const loadingSpinner = document.getElementById("loadingSpinner");
  const copyTranscriptButton = document.getElementById("copyTranscriptButton");
  const transcriptContent = document.getElementById("transcriptContent");

  // --- Utility Functions ---

  const showToast = (message, type = 'info') => { // Default to 'info' type
    const toastContainer = document.getElementById('toastContainer'); // Assuming you have a container for toasts
    const toastElement = document.createElement('div');
    toastElement.classList.add('toast', `toast-${type}`); // Add type-specific class
    toastElement.setAttribute('role', 'alert');
    toastElement.setAttribute('aria-live', 'assertive');
    toastElement.setAttribute('aria-atomic', 'true');

    toastElement.innerHTML = `
      <div class="toast-header">
        <strong class="me-auto text-${type}">${type.charAt(0).toUpperCase() + type.slice(1)}</strong> <span id="toastCloseBtn" type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></span>
      </div>
      <div class="toast-body">
        ${message}
      </div>
    `;

    toastContainer.appendChild(toastElement);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();

    // Add an event listener to the close button to remove the toast from the DOM
    toastElement.querySelector('#toastCloseBtn').addEventListener('click', () => {
      toastContainer.removeChild(toastElement);
    });
  };

  const displayElement = (element, display = "block") => {
    element.style.display = display;
  };

  const hideElement = (element) => {
    displayElement(element, "none");
  };

  function animateText(text, element, delay = 8) {
    element.textContent = "";
    let i = 0;
    const intervalId = setInterval(() => {
      element.textContent += text.charAt(i);
      i++;
      if (i > text.length) {
        clearInterval(intervalId);
      }
    }, delay);
  }

  // --- Upload and Interaction Logic (For Video Details Page) ---

  const handleAskQuestion = async () => {
    const question = questionInput.value.trim();
    if (!question) return showToast("Please enter a question.","warning");

    try {
      // Update UI to show loading state
      askQuestionButton.disabled = true;
      questionInput.disabled = true;
      sendButtonText.style.display = "none";
      loadingSpinner.style.display = "inline-block";

      // Add user message to chat
      addUserMessage(question);

      const response = await fetch("{% url 'ask-yourtube:ask-question' %}", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          session_id: sessionIdInput.value,
        }),
      });

      const data = await response.json();
      
      addAIResponse(data.answer); 
    } catch (error) {
      console.error("Error occurred:", error);
      showToast("Something went wrong. Please try again later.","danger");
    } finally {
      // Reset UI from loading state
      askQuestionButton.disabled = false;
      questionInput.disabled = false;
      sendButtonText.style.display = "inline";
      loadingSpinner.style.display = "none";
    }
  };

  const addUserMessage = (message) => {
    const messageElement = document.createElement("div");
    messageElement.classList.add("user-message");
    messageElement.textContent = message;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight; // Scroll to bottom
    questionInput.value = ""; // Clear input field
  };

  const addAIResponse = (message) => {
    const messageContainer = document.createElement("div");
    messageContainer.classList.add("ai-message");
    chatMessages.appendChild(messageContainer);
  
    // --- Animated Text ---
    animateText(message, messageContainer);
  
    chatMessages.scrollTop = chatMessages.scrollHeight;
  };

  // --- Event Listeners (Common to both pages) ---

  if (askQuestionButton) {
    // Check if the button exists on this page
    askQuestionButton.addEventListener("click", handleAskQuestion);
  }

  questionInput.addEventListener("keyup", (event) => {
    if (event.key === "Enter") { 
      handleAskQuestion();
    }
  });
  
  // --- Copy Transcript Button Functionality ---
  if (copyTranscriptButton) {
    copyTranscriptButton.addEventListener("click", () => {
      const textToCopy = transcriptContent.textContent;

      // Copy text to clipboard (modern browsers)
      navigator.clipboard
        .writeText(textToCopy)
        .then(() => {
          // Optional: Show a success message or change button text temporarily
          copyTranscriptButton.textContent = "Copied!";
          setTimeout(() => {
            copyTranscriptButton.innerHTML = "<i class='fas fa-copy'></i> Copy Transcript";
          }, 1500); // Reset button text after 1.5 seconds
        })
        .catch((err) => {
          console.error("Failed to copy transcript: ", err);
          showToast("Failed to copy transcript.","danger")
          // Optional: Show an error message to the user
        });
    });
  }

  const savedVideosLink = document.getElementById("savedVideosLink");
  savedVideosLink.href = `{% url 'ask-yourtube:video-list' %}?user_id=${userID}`;
});
