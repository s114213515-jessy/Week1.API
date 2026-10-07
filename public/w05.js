const demoMenuToggle = document.querySelector("#demoMenuToggle");
const demoSidebar = document.querySelector("#demoSidebar");
const demoCloseButton = document.querySelector("#demoCloseButton");
const demoMessageButton = document.querySelector("#demoMessageButton");
const demoMessage = document.querySelector("#demoMessage");
const practiceStatus = document.querySelector("#practiceStatus");

function openDemoSidebar() {
  demoSidebar.hidden = false;
  demoMenuToggle.setAttribute("aria-expanded", "true");
  demoMenuToggle.textContent = "側邊欄已開啟";
  practiceStatus.textContent =
    "Event: Menu click → Function: openDemoSidebar() → DOM: 顯示選單並更新 aria-expanded。";
}

function closeDemoSidebar() {
  demoSidebar.hidden = true;
  demoMenuToggle.setAttribute("aria-expanded", "false");
  demoMenuToggle.textContent = "開啟模擬選單";
  practiceStatus.textContent =
    "Event: 關閉按鈕或 Escape → Function: closeDemoSidebar() → DOM: 隱藏選單並重設 aria-expanded。";
}

function changeDemoMessage() {
  demoMessage.textContent = "提示已更新：你已追蹤 Event → Function → DOM。";
  practiceStatus.textContent =
    "Event: 更新提示 click → Function: changeDemoMessage() → DOM: 更新提示文字的 textContent。";
}

function handleDemoKeydown(event) {
  if (event.key === "Escape" && !demoSidebar.hidden) {
    closeDemoSidebar();
    demoMenuToggle.focus();
  }
}

demoMenuToggle.addEventListener("click", openDemoSidebar);
demoCloseButton.addEventListener("click", closeDemoSidebar);
demoMessageButton.addEventListener("click", changeDemoMessage);
document.addEventListener("keydown", handleDemoKeydown);
