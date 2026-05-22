const form = document.querySelector("#reviewForm");
const output = document.querySelector("#reportOutput");
const copyButton = document.querySelector("#copyReport");
const reviewDateInput = document.querySelector('input[name="reviewDate"]');

const today = new Date();
const nextMonth = new Date(today.getFullYear(), today.getMonth() + 1, today.getDate());
reviewDateInput.value = formatLocalDate(nextMonth);

function formatLocalDate(date) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

function drawAllocationChart() {
  const canvas = document.querySelector("#allocationChart");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const width = canvas.width;
  const height = canvas.height;
  ctx.clearRect(0, 0, width, height);

  const bars = [
    { label: "宽基", value: 45, color: "#0f766e" },
    { label: "债券", value: 25, color: "#b9821f" },
    { label: "现金", value: 18, color: "#4c6f8f" },
    { label: "个股", value: 12, color: "#b14a5c" }
  ];

  ctx.fillStyle = "#17201d";
  ctx.font = "700 22px Arial";
  ctx.fillText("资产配置记录", 24, 38);

  ctx.font = "14px Arial";
  ctx.fillStyle = "#5a6763";
  ctx.fillText("示意图：上线后可接入真实持仓数据", 24, 62);

  bars.forEach((bar, index) => {
    const y = 102 + index * 46;
    const barWidth = Math.round((width - 180) * (bar.value / 60));
    ctx.fillStyle = "#e8efeb";
    ctx.fillRect(92, y, width - 150, 18);
    ctx.fillStyle = bar.color;
    ctx.fillRect(92, y, barWidth, 18);
    ctx.fillStyle = "#17201d";
    ctx.fillText(bar.label, 24, y + 14);
    ctx.fillText(`${bar.value}%`, width - 70, y + 14);
  });
}

function createReport(data) {
  const exitRule = data.get("exitRule") || "暂未填写，建议补充明确的调整条件。";
  return `投资复盘报告

标的：${data.get("assetName")}
类型：${data.get("assetType")}
仓位：${data.get("positionSize")}%
风险等级：${data.get("riskLevel")}
复盘日期：${data.get("reviewDate")}

买入理由：
${data.get("reason")}

卖出或调整条件：
${exitRule}

复盘问题：
1. 当初的买入理由是否仍然成立？
2. 仓位是否超过自己的风险承受能力？
3. 这笔投资是否影响了应急金和生活现金流？
4. 如果今天重新选择，还会不会买入？

提醒：本报告只用于个人记录，不构成任何投资建议。`;
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const data = new FormData(form);
  output.textContent = createReport(data);
});

copyButton.addEventListener("click", async () => {
  await navigator.clipboard.writeText(output.textContent);
  copyButton.textContent = "Copied";
  window.setTimeout(() => {
    copyButton.textContent = "Copy";
  }, 1200);
});

drawAllocationChart();
