const teacherNavigation = document.querySelector("#teacherNavigation");
const dashboardCards = document.querySelector("#dashboardCards");
const pageTitle = document.querySelector("#pageTitle");
const pageDescription = document.querySelector("#pageDescription");
const navigationPreview = document.querySelector("#navigationPreview");
const statusMessage = document.querySelector("#statusMessage");
const menuToggle = document.querySelector("#menuToggle");
const sidebar = document.querySelector("#sidebar");
const sidebarClose = document.querySelector("#sidebarClose");
const sidebarBackdrop = document.querySelector("#sidebarBackdrop");
const accountToggle = document.querySelector("#accountToggle");
const accountPanel = document.querySelector("#accountPanel");
const themeToggle = document.querySelector("#themeToggle");
const changeMessageButton = document.querySelector("#changeMessageButton");
const message = document.querySelector("#message");

let operations = [];
let cardsByPage = {};
let messageVersion = 0;

async function readJson(path) {
  const response = await fetch(path);
  if (!response.ok) {
    throw new Error(`載入 ${path} 失敗：HTTP ${response.status}`);
  }
  return response.json();
}

function validatePageData(operationsData, cardsData) {
  if (!Array.isArray(operationsData.items) || operationsData.items.length === 0) {
    throw new Error("teacher_ops.json 必須包含至少一個功能項目。");
  }
  if (typeof cardsData !== "object" || cardsData === null || Array.isArray(cardsData)) {
    throw new Error("dashboard_cards.json 必須是依功能 ID 分組的物件。");
  }

  for (const item of operationsData.items) {
    if (
      typeof item.id !== "string" ||
      typeof item.label !== "string" ||
      typeof item.description !== "string"
    ) {
      throw new Error("每個功能項目都必須包含 id、label 與 description。");
    }
    if (!Array.isArray(cardsData[item.id])) {
      throw new Error(`dashboard_cards.json 缺少「${item.id}」功能的卡片陣列。`);
    }
  }

  operations = operationsData.items;
  cardsByPage = cardsData;
}

function showNavigationPreview(item) {
  navigationPreview.textContent = item.description;
}

function setActiveNavigation(item) {
  for (const button of teacherNavigation.querySelectorAll(".nav-button")) {
    const isActive = button.dataset.pageId === item.id;
    button.classList.toggle("is-active", isActive);
    if (isActive) {
      button.setAttribute("aria-current", "page");
    } else {
      button.removeAttribute("aria-current");
    }
  }
}

function createNavigationItem(item) {
  const button = document.createElement("button");
  button.className = "nav-button";
  button.type = "button";
  button.dataset.pageId = item.id;
  button.setAttribute("aria-current", "false");

  const icon = document.createElement("span");
  icon.className = "nav-icon";
  icon.setAttribute("aria-hidden", "true");
  icon.textContent = item.icon ?? "•";

  const label = document.createElement("span");
  label.textContent = item.label;

  button.append(icon, label);
  button.addEventListener("mouseenter", () => showNavigationPreview(item));
  button.addEventListener("mouseleave", () => {
    navigationPreview.textContent = "選擇功能以查看內容";
  });
  button.addEventListener("focus", () => showNavigationPreview(item));
  button.addEventListener("blur", () => {
    navigationPreview.textContent = "選擇功能以查看內容";
  });
  button.addEventListener("click", () => showPage(item));
  return button;
}

function renderNavigation() {
  teacherNavigation.replaceChildren();
  for (const item of operations) {
    teacherNavigation.append(createNavigationItem(item));
  }
}

function setSelectedCard(selectedCard) {
  for (const button of dashboardCards.querySelectorAll(".card-select")) {
    const isSelected = button === selectedCard;
    button.closest(".dashboard-card").classList.toggle("is-selected", isSelected);
    button.setAttribute("aria-pressed", String(isSelected));
  }
}

function createDashboardCard(cardData) {
  const article = document.createElement("article");
  article.className = "dashboard-card";
  const selectButton = document.createElement("button");
  selectButton.className = "card-select";
  selectButton.type = "button";
  selectButton.setAttribute("aria-pressed", "false");

  const topline = document.createElement("div");
  topline.className = "card-topline";

  const icon = document.createElement("span");
  icon.className = "card-icon";
  icon.setAttribute("aria-hidden", "true");
  icon.textContent = cardData.icon ?? "•";

  const detailToggle = document.createElement("button");
  detailToggle.className = "detail-toggle";
  detailToggle.type = "button";
  detailToggle.textContent = "查看說明";
  detailToggle.setAttribute("aria-expanded", "false");

  const detail = document.createElement("p");
  detail.className = "card-detail";
  detail.textContent = cardData.detail;
  detail.hidden = true;
  detailToggle.addEventListener("click", () => toggleDetail(detailToggle, detail));

  topline.append(icon);

  const value = document.createElement("p");
  value.className = "card-value";
  value.textContent = cardData.value;

  const title = document.createElement("h3");
  title.textContent = cardData.title;

  const description = document.createElement("p");
  description.textContent = cardData.description;

  selectButton.append(topline, value, title, description);
  selectButton.addEventListener("click", () => setSelectedCard(selectButton));
  article.append(selectButton, detailToggle, detail);
  return article;
}

function renderDashboard(pageId) {
  dashboardCards.replaceChildren();
  for (const cardData of cardsByPage[pageId]) {
    dashboardCards.append(createDashboardCard(cardData));
  }
}

function showPage(item) {
  pageTitle.textContent = item.label;
  pageDescription.textContent = item.description;
  navigationPreview.textContent = item.description;
  setActiveNavigation(item);
  renderDashboard(item.id);
  closeSidebar();
  statusMessage.textContent = `${item.label}已開啟。`;
}

function openSidebar() {
  sidebar.classList.add("is-open");
  sidebarBackdrop.hidden = false;
  menuToggle.setAttribute("aria-expanded", "true");
  menuToggle.setAttribute("aria-label", "關閉功能選單");
  sidebarClose.focus();
}

function closeSidebar() {
  sidebar.classList.remove("is-open");
  sidebarBackdrop.hidden = true;
  menuToggle.setAttribute("aria-expanded", "false");
  menuToggle.setAttribute("aria-label", "開啟功能選單");
}

function toggleDetail(button, detail) {
  const isExpanded = button.getAttribute("aria-expanded") === "true";
  button.setAttribute("aria-expanded", String(!isExpanded));
  button.textContent = isExpanded ? "查看說明" : "收合說明";
  detail.hidden = isExpanded;
}

function toggleAccountPanel() {
  const isExpanded = accountToggle.getAttribute("aria-expanded") === "true";
  accountToggle.setAttribute("aria-expanded", String(!isExpanded));
  accountPanel.hidden = isExpanded;
}

function closeAccountPanel() {
  accountToggle.setAttribute("aria-expanded", "false");
  accountPanel.hidden = true;
}

function toggleTheme() {
  const isDark = document.body.classList.toggle("theme-dark");
  themeToggle.setAttribute("aria-pressed", String(isDark));
  themeToggle.textContent = isDark ? "淺色模式" : "深色模式";
}

function changeMessage() {
  const messages = [
    "已完成更新，請繼續查看本週工作。",
    "提示已更新：先處理最重要的一件事。",
  ];
  message.textContent = messages[messageVersion % messages.length];
  messageVersion += 1;
}

function handleDocumentKeydown(event) {
  if (event.key === "Escape") {
    const sidebarWasOpen = sidebar.classList.contains("is-open");
    closeSidebar();
    closeAccountPanel();
    if (sidebarWasOpen) {
      menuToggle.focus();
    }
  }
}

function handleDocumentClick(event) {
  if (!event.target.closest(".account-menu")) {
    closeAccountPanel();
  }
}

async function loadPageData() {
  try {
    const [operationsData, cardsData] = await Promise.all([
      readJson("json/teacher_ops.json"),
      readJson("json/dashboard_cards.json"),
    ]);
    validatePageData(operationsData, cardsData);
    renderNavigation();
    const defaultPage =
      operations.find((item) => item.id === "dashboard") ?? operations[0];
    showPage(defaultPage);
    dashboardCards.setAttribute("aria-busy", "false");
  } catch (error) {
    console.error("無法初始化教務儀表板：", error);
    dashboardCards.setAttribute("aria-busy", "false");
    statusMessage.textContent =
      "頁面資料載入失敗。請確認 JSON 檔案路徑與格式，並查看開發者工具。";
  }
}

menuToggle.addEventListener("click", openSidebar);
sidebarClose.addEventListener("click", closeSidebar);
sidebarBackdrop.addEventListener("click", closeSidebar);
accountToggle.addEventListener("click", toggleAccountPanel);
document.querySelector("#accountAction").addEventListener("click", () => {
  closeAccountPanel();
  statusMessage.textContent = "帳戶資訊為展示功能，尚未連接登入服務。";
});
themeToggle.addEventListener("click", toggleTheme);
changeMessageButton.addEventListener("click", changeMessage);
document.addEventListener("keydown", handleDocumentKeydown);
document.addEventListener("click", handleDocumentClick);

loadPageData();
