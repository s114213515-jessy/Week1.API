const navContainer = document.querySelector("#teacher-ops");
const cardsContainer = document.querySelector("#dashboard-cards");
const sectionTitle = document.querySelector("#current-section");
const cardsTitle = document.querySelector("#cards-title");
const cardsDescription = document.querySelector("#cards-description");
const sidebar = document.querySelector("#sidebar");
const sidebarBackdrop = document.querySelector("#sidebar-backdrop");
const menuButton = document.querySelector("#menu-button");
const dataBase = new URL("json/", document.baseURI);

let dashboardData;

function showError(container, message) {
  const error = document.createElement("p");
  error.className = "error-message";
  error.textContent = message;
  container.replaceChildren(error);
}

function closeSidebar() {
  sidebar.classList.remove("is-open");
  sidebarBackdrop.classList.remove("is-visible");
  menuButton.setAttribute("aria-expanded", "false");
}

function renderCards(view) {
  const dashboard = dashboardData[view];
  if (!dashboard) {
    showError(cardsContainer, "目前沒有這個功能的儀表板資料。");
    return;
  }

  sectionTitle.textContent = dashboard.label;
  cardsTitle.textContent = dashboard.heading;
  cardsDescription.textContent = dashboard.description;
  cardsContainer.replaceChildren();

  for (const card of dashboard.cards) {
    const article = document.createElement("article");
    article.className = "dashboard-card";
    article.style.setProperty("--card-color", card.color);
    article.style.setProperty("--card-tint", card.tint);

    const topLine = document.createElement("div");
    topLine.className = "card-topline";

    const icon = document.createElement("span");
    icon.className = "card-icon";
    icon.setAttribute("aria-hidden", "true");
    icon.textContent = card.icon;

    const trend = document.createElement("span");
    trend.className = "card-trend";
    trend.textContent = card.trend;
    topLine.append(icon, trend);

    const title = document.createElement("h3");
    title.className = "card-title";
    title.textContent = card.title;

    const value = document.createElement("p");
    value.className = "card-value";
    value.textContent = card.value;

    const description = document.createElement("p");
    description.className = "card-description";
    description.textContent = card.description;

    article.append(topLine, title, value, description);
    cardsContainer.append(article);
  }
}

async function loadDashboard() {
  try {
    const [operationsResponse, cardsResponse] = await Promise.all([
      fetch(new URL("teacher_ops.json", dataBase)),
      fetch(new URL("dashboard_cards.json", dataBase)),
    ]);

    if (!operationsResponse.ok || !cardsResponse.ok) {
      throw new Error("無法讀取教務系統 JSON 資料。");
    }

    const operations = await operationsResponse.json();
    dashboardData = await cardsResponse.json();

    const fragment = document.createDocumentFragment();
    for (const operation of operations.items) {
      const button = document.createElement("button");
      button.className = "nav-item";
      button.type = "button";
      button.dataset.view = operation.id;
      button.setAttribute("aria-current", operation.id === operations.default ? "page" : "false");

      const icon = document.createElement("span");
      icon.className = "nav-icon";
      icon.setAttribute("aria-hidden", "true");
      icon.textContent = operation.icon;

      const label = document.createElement("span");
      label.textContent = operation.label;

      button.append(icon, label);
      button.addEventListener("click", () => {
        navContainer.querySelectorAll(".nav-item").forEach((item) => {
          const isActive = item === button;
          item.classList.toggle("is-active", isActive);
          item.setAttribute("aria-current", isActive ? "page" : "false");
        });
        renderCards(operation.id);
        closeSidebar();
      });
      if (operation.id === operations.default) {
        button.classList.add("is-active");
      }
      fragment.append(button);
    }

    navContainer.replaceChildren(fragment);
    renderCards(operations.default);
  } catch (error) {
    showError(navContainer, error.message);
    showError(cardsContainer, error.message);
  }
}

menuButton.addEventListener("click", () => {
  const isOpen = sidebar.classList.toggle("is-open");
  sidebarBackdrop.classList.toggle("is-visible", isOpen);
  menuButton.setAttribute("aria-expanded", String(isOpen));
});

sidebarBackdrop.addEventListener("click", closeSidebar);

loadDashboard();
