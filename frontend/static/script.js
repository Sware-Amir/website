// Smooth scroll voor alle CTA buttons die naar een sectie verwijzen
document.querySelectorAll(".cta-btn").forEach(button => {
  button.addEventListener("click", (e) => {
    const targetId = button.getAttribute("data-target"); // data-target attribuut
    if (targetId) {
      const targetElement = document.getElementById(targetId);
      if (targetElement) {
        targetElement.scrollIntoView({ behavior: "smooth" });
        e.preventDefault(); // voorkomt default link scroll
      }
    }
  });
});

// Event listener voor login links (optioneel, kan weg omdat <a href> vanzelf werkt)
document.querySelectorAll(".login-link").forEach(link => {
  link.addEventListener("click", () => {
    console.log("Navigeren naar loginpagina...");
  });
});
