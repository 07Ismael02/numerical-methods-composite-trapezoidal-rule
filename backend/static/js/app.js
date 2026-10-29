"use strict";

const $ = selector => document.querySelector(selector);
let currentResult = null;
const chartObservers = new Map();

function fmt(value, digits = 12) {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) return "—";
  const number = Number(value);
  if (number === 0) return "0";
  if (Math.abs(number) >= 1e6 || Math.abs(number) < 1e-6) return number.toExponential(6);
  return number.toPrecision(digits).replace(/(?:\.0+|(\.\d+?)0+)(e|$)/, "$1$2");
}

function showMessage(text, success = false) {
  const box = $("#message");
  box.textContent = text;
  box.className = `message${success ? " success" : ""}`;
  box.hidden = false;
  clearTimeout(showMessage.timer);
  showMessage.timer = setTimeout(() => { box.hidden = true; }, 6000);
}

async function requestCalculation(payload, button) {
  button.disabled = true;
  const label = button.querySelector("span");
  const original = label.textContent;
  label.textContent = "Calculando…";
  try {
    const response = await fetch("/api/trapecio", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok || !data.ok) throw new Error(data.error || "No fue posible realizar el cálculo.");
    return data;
  } finally {
    button.disabled = false;
    label.textContent = original;
  }
}

function render(data, scroll = true) {
  currentResult = data;
  $("#summary-h").textContent = fmt(data.h);
  $("#summary-result").textContent = fmt(data.aproximacion);
  $("#summary-exact").textContent = fmt(data.exacta);
  $("#summary-error").textContent = `${fmt(data.error_porcentual, 9)} %`;

  $("#step-development").innerHTML = `
    <div class="math-line">${data.calculo_h}</div>
    <div class="math-line">tᵢ = a + ih, i = 0, 1, …, ${data.n}</div>
    <div class="math-line final">Malla: [${data.malla.map(value => fmt(value, 9)).join(", ")}]</div>`;

  $("#points-body").innerHTML = data.puntos.map(point => `
    <tr><td>${point.i}</td><td>${fmt(point.x)}</td><td>${fmt(point.fx)}</td><td>${point.peso === .5 ? "½" : "1"}</td><td>${fmt(point.aporte)}</td></tr>`).join("");

  const first = data.puntos[0];
  const last = data.puntos.at(-1);
  $("#formula-development").innerHTML = `
    <div class="math-line">Tₙ = h [R(t₀)/2 + Σ R(tᵢ) + R(tₙ)/2]</div>
    <div class="math-line">T${data.n} = ${fmt(data.h)} [${fmt(first.fx)}/2 + ${fmt(data.suma_interior)} + ${fmt(last.fx)}/2]</div>
    <div class="math-line">Suma ponderada = ${fmt(data.suma_ponderada)}</div>
    <div class="math-line final">T${data.n} = ${fmt(data.h)} × ${fmt(data.suma_ponderada)} = ${fmt(data.aproximacion)} Megabits</div>`;

  $("#error-development").innerHTML = `
    <div class="math-line">D exacto = ${data.formula_exacta}</div>
    <div class="math-line">D exacto = ${fmt(data.exacta)} Megabits</div>
    <div class="math-line">Error absoluto = |${fmt(data.exacta)} − ${fmt(data.aproximacion)}| = ${fmt(data.error_absoluto)} Megabits</div>
    <div class="math-line final">Error porcentual = (${fmt(data.error_absoluto)} / |${fmt(data.exacta)}|) × 100 = ${fmt(data.error_porcentual, 9)} %</div>`;

  $("#convergence-body").innerHTML = data.convergencia.map(row => `
    <tr><td>${row.n}</td><td>${fmt(row.aproximacion)}</td><td>${fmt(row.error_absoluto)}</td><td>${fmt(row.error_porcentual, 9)} %</td></tr>`).join("");
  const note = $("#convergence-note");
  note.className = `note${data.error_disminuye ? " success" : ""}`;
  note.textContent = data.error_disminuye === true
    ? "Verificación: el error absoluto disminuye al aumentar n para la secuencia 4, 10, 50, 100 y 1000."
    : data.error_disminuye === false
      ? "En este intervalo no se verificó una disminución estricta para toda la secuencia estudiada."
      : "El intervalo está orientado de derecha a izquierda; la convergencia se presenta sin afirmar monotonía.";

  $("#results").hidden = false;
  drawFunctionChart(data);
  drawConvergenceChart(data.convergencia);
  if (scroll) $("#results").scrollIntoView({ behavior: "smooth", block: "start" });
}

function prepareCanvas(id, draw) {
  const canvas = document.getElementById(id);
  const redraw = () => {
    const rect = canvas.getBoundingClientRect();
    if (!rect.width || !rect.height) return;
    const ratio = window.devicePixelRatio || 1;
    canvas.width = Math.round(rect.width * ratio);
    canvas.height = Math.round(rect.height * ratio);
    const ctx = canvas.getContext("2d");
    ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
    ctx.clearRect(0, 0, rect.width, rect.height);
    draw(ctx, rect.width, rect.height);
  };
  chartObservers.get(id)?.disconnect();
  const observer = new ResizeObserver(redraw);
  observer.observe(canvas.parentElement);
  chartObservers.set(id, observer);
  redraw();
}

function drawAxes(ctx, width, height, bounds, xLabel, yLabel) {
  const pad = { left: 58, right: 18, top: 18, bottom: 48 };
  const X = x => pad.left + (x - bounds.xmin) / (bounds.xmax - bounds.xmin) * (width - pad.left - pad.right);
  const Y = y => height - pad.bottom - (y - bounds.ymin) / (bounds.ymax - bounds.ymin) * (height - pad.top - pad.bottom);
  ctx.font = "11px system-ui";
  ctx.strokeStyle = "#dce5ec";
  ctx.fillStyle = "#627286";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 5; i += 1) {
    const y = bounds.ymin + (bounds.ymax - bounds.ymin) * i / 5;
    const py = Y(y); ctx.beginPath(); ctx.moveTo(pad.left, py); ctx.lineTo(width - pad.right, py); ctx.stroke(); ctx.fillText(fmt(y, 4), 4, py + 4);
  }
  for (let i = 0; i <= 5; i += 1) {
    const x = bounds.xmin + (bounds.xmax - bounds.xmin) * i / 5;
    const px = X(x); ctx.beginPath(); ctx.moveTo(px, pad.top); ctx.lineTo(px, height - pad.bottom); ctx.stroke(); ctx.fillText(fmt(x, 4), px - 10, height - 26);
  }
  ctx.fillStyle = "#102235"; ctx.font = "bold 11px system-ui"; ctx.textAlign = "right"; ctx.fillText(xLabel, width - 18, height - 9); ctx.save(); ctx.translate(14, 20); ctx.rotate(-Math.PI / 2); ctx.textAlign = "right"; ctx.fillText(yLabel, 0, 0); ctx.restore(); ctx.textAlign = "left";
  return { X, Y, pad };
}

function drawFunctionChart(data) {
  prepareCanvas("function-chart", (ctx, width, height) => {
    const xs = data.grafica_funcion.map(p => p.x), ys = data.grafica_funcion.map(p => p.y);
    const xmin = Math.min(...xs), xmax = Math.max(...xs), yminRaw = Math.min(0, ...ys), ymaxRaw = Math.max(...ys);
    const margin = Math.max(1, (ymaxRaw - yminRaw) * .1);
    const axis = drawAxes(ctx, width, height, { xmin, xmax, ymin: yminRaw, ymax: ymaxRaw + margin }, "t (s)", "R(t) Mbps");
    for (let i = 0; i < data.puntos.length - 1; i += 1) {
      const p = data.puntos[i], q = data.puntos[i + 1];
      ctx.beginPath(); ctx.moveTo(axis.X(p.x), axis.Y(0)); ctx.lineTo(axis.X(p.x), axis.Y(p.fx)); ctx.lineTo(axis.X(q.x), axis.Y(q.fx)); ctx.lineTo(axis.X(q.x), axis.Y(0)); ctx.closePath(); ctx.fillStyle = "rgba(36,89,196,.15)"; ctx.fill(); ctx.strokeStyle = "rgba(36,89,196,.48)"; ctx.stroke();
    }
    ctx.beginPath(); data.grafica_funcion.forEach((p, i) => i ? ctx.lineTo(axis.X(p.x), axis.Y(p.y)) : ctx.moveTo(axis.X(p.x), axis.Y(p.y))); ctx.strokeStyle = "#0b8494"; ctx.lineWidth = 3; ctx.stroke();
    data.puntos.forEach(p => { ctx.beginPath(); ctx.arc(axis.X(p.x), axis.Y(p.fx), 4.5, 0, Math.PI * 2); ctx.fillStyle = "#e9ad27"; ctx.fill(); ctx.strokeStyle = "white"; ctx.lineWidth = 2; ctx.stroke(); });
  });
}

function drawConvergenceChart(rows) {
  prepareCanvas("convergence-chart", (ctx, width, height) => {
    const valid = rows.filter(row => row.n > 0 && row.error_absoluto > 0).sort((a, b) => a.n - b.n);
    const points = valid.map(row => ({ x: Math.log10(row.n), y: Math.log10(row.error_absoluto), row }));
    let xmin = Math.min(...points.map(p => p.x)), xmax = Math.max(...points.map(p => p.x));
    let ymin = Math.min(...points.map(p => p.y)), ymax = Math.max(...points.map(p => p.y));
    if (xmin === xmax) { xmin -= .5; xmax += .5; } if (ymin === ymax) { ymin -= .5; ymax += .5; }
    const axis = drawAxes(ctx, width, height, { xmin, xmax, ymin: ymin - .15, ymax: ymax + .15 }, "log₁₀(n)", "log₁₀(error)");
    ctx.beginPath(); points.forEach((p, i) => i ? ctx.lineTo(axis.X(p.x), axis.Y(p.y)) : ctx.moveTo(axis.X(p.x), axis.Y(p.y))); ctx.strokeStyle = "#2459c4"; ctx.lineWidth = 3; ctx.stroke();
    points.forEach(p => { ctx.beginPath(); ctx.arc(axis.X(p.x), axis.Y(p.y), 5, 0, Math.PI * 2); ctx.fillStyle = "#e9ad27"; ctx.fill(); ctx.fillStyle = "#102235"; ctx.font = "bold 10px system-ui"; ctx.fillText(`n=${p.row.n}`, axis.X(p.x) + 7, axis.Y(p.y) - 7); });
  });
}

function procedureText(data) {
  const rows = data.puntos.map(p => `i=${p.i}: t_i=${fmt(p.x)}, R(t_i)=${fmt(p.fx)}, peso=${p.peso}, aporte=${fmt(p.aporte)}`).join("\n");
  return `REGLA DEL TRAPECIO COMPUESTO\n${data.funcion}\nIntervalo: [${fmt(data.a)}, ${fmt(data.b)}], n=${data.n}\n${data.calculo_h}\nMalla: [${data.malla.map(x => fmt(x)).join(", ")}]\n\n${rows}\n\nT_n = h [R(t_0)/2 + sum R(t_i) + R(t_n)/2]\nSuma ponderada = ${fmt(data.suma_ponderada)}\nT_${data.n} = ${fmt(data.aproximacion)} Megabits\nD_exacta = ${fmt(data.exacta)} Megabits\nError absoluto = ${fmt(data.error_absoluto)}\nError porcentual = ${fmt(data.error_porcentual)} %`;
}

const form = $("#trapecio-form");
const calculateButton = $("#calculate-button");

form.addEventListener("submit", async event => {
  event.preventDefault();
  $("#message").hidden = true;
  try {
    const data = await requestCalculation({ a: Number($("#a").value), b: Number($("#b").value), n: Number($("#n").value) }, calculateButton);
    render(data, true);
  } catch (error) {
    $("#results").hidden = true;
    showMessage(error.message);
  }
});

$("#official-button").addEventListener("click", () => {
  $("#a").value = 0; $("#b").value = 12; $("#n").value = 4;
  form.requestSubmit(calculateButton);
});

form.addEventListener("input", () => { $("#results").hidden = true; });

$("#copy-button").addEventListener("click", async () => {
  if (!currentResult) return;
  try {
    await navigator.clipboard.writeText(procedureText(currentResult));
    showMessage("Procedimiento copiado al portapapeles.", true);
  } catch (_) {
    showMessage("El navegador no permitió copiar automáticamente.");
  }
});

form.requestSubmit(calculateButton);

