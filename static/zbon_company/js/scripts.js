const headerContainer = document.getElementById("header-container");
const logo = document.getElementById("logo");

window.addEventListener("scroll", function () {
  const scrollPosition = window.scrollY;

  // Change header background
  if (scrollPosition > 0) {
    headerContainer.classList.add("bg-white", "dark:bg-gray-900", "border-b-2", "border-gray-200", "dark:border-gray-700");
  } else {
    headerContainer.classList.remove("bg-white", "dark:bg-gray-900", "border-b-2", "border-gray-200", "dark:border-gray-700");
  }

  // Change logo size
  if (scrollPosition > 0) {
    logo.classList.add("h-16"); // Adjust the height as needed
    logo.classList.remove("h-24"); // Adjust the height as needed
  } else {
    logo.classList.remove("h-16");
    logo.classList.add("h-24"); // Adjust the height as needed
  }
});

document.addEventListener("DOMContentLoaded", function () {
  var successModal = document.getElementById("successModal");
  if (successModal) {
    successModal.classList.remove("hidden"); // Show the modal immediately if present
  }

  // Add event listener to close button (optional)
  var closeButtons = successModal.querySelectorAll('[data-modal-toggle="successModal"]');
  closeButtons.forEach(function (closeButton) {
    closeButton.addEventListener("click", function () {
      successModal.classList.add("hidden");
    });
  });
});
