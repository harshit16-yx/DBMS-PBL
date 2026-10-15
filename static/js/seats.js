/**
 * Bus Reservation System - Seat Selector Interaction
 * Minimal, clean vanilla JavaScript without external dependencies
 */

document.addEventListener("DOMContentLoaded", function () {
  const seatButtons = document.querySelectorAll(".seat-item.seat-free");
  const hiddenInput = document.getElementById("selectedSeatId");
  const displayLabel = document.getElementById("selectedSeatLabel");
  const submitBtn = document.getElementById("submitBookingBtn");

  if (!seatButtons.length || !hiddenInput) {
    return;
  }

  seatButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      const seatId = this.getAttribute("data-seat-id");
      const seatNo = this.getAttribute("data-seat-no");

      // Check if already selected
      if (this.classList.contains("seat-selected")) {
        this.classList.remove("seat-selected");
        hiddenInput.value = "";
        if (displayLabel) displayLabel.textContent = "None selected";
        if (submitBtn) submitBtn.disabled = true;
        return;
      }

      // Remove selected class from all seats
      seatButtons.forEach(function (s) {
        s.classList.remove("seat-selected");
      });

      // Select clicked seat
      this.classList.add("seat-selected");
      hiddenInput.value = seatId;
      if (displayLabel) displayLabel.textContent = seatNo;
      if (submitBtn) submitBtn.disabled = false;
    });
  });
});
